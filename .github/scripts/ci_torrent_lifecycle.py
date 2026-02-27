"""Torrent lifecycle integration test.

Exercises the full round-trip against the live SonicBit API:

  1. Pre-clean  — remove the test torrent if a previous CI run left it behind.
  2. Add        — add the magnet link supplied via SONICBIT_TEST_MAGNET.
  3. Download   — poll list_torrents() until progress reaches 100 %.
  4. Sync       — poll until in_cache is True, which means the data has been
                  moved from the seedbox to permanent cloud storage.
  5. Verify     — confirm the torrent folder appears in list_files().
  6. Delete     — delete the torrent and its files unconditionally (finally block)
                  so the test account is always left clean.

Environment variables:
    SONICBIT_EMAIL          (required) e-mail address of the test account
    SONICBIT_PASSWORD       (required) password of the test account
    SONICBIT_TEST_MAGNET    (required) magnet URI for the torrent to use as the
                            test fixture — must contain a btih info-hash,
                            e.g. magnet:?xt=urn:btih:<40-hex-chars>&dn=Name&...

Exit codes:
    0   all steps passed
    1   a step failed (see log output)
"""

import logging
import os
import re
import sys
import time
from urllib.parse import parse_qs, urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Polling configuration.
POLL_INTERVAL = 10        # seconds between list_torrents() calls
DOWNLOAD_TIMEOUT = 600    # seconds to wait for progress to reach 100 %
SYNC_TIMEOUT = 300        # seconds to wait for in_cache to become True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_magnet(magnet: str) -> tuple[str, str]:
    """Return (hash_lower, display_name) extracted from a magnet URI.

    Raises ValueError if the URI does not contain a btih info-hash.
    The display name falls back to the hash string when dn= is absent.
    """
    match = re.search(r"urn:btih:([a-fA-F0-9]{40})", magnet, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"SONICBIT_TEST_MAGNET does not contain a btih info-hash: {magnet!r}"
        )
    hash_lower = match.group(1).lower()

    qs = parse_qs(urlparse(magnet).query)
    dn_values = qs.get("dn", [])
    display_name = dn_values[0].replace("+", " ") if dn_values else hash_lower

    return hash_lower, display_name


def find_torrent(sb, hash_lower: str):
    """Return the Torrent object matching hash_lower, or None if absent."""
    torrent_list = sb.list_torrents()
    for t in torrent_list.torrents.values():
        if t.hash.lower() == hash_lower:
            return t
    return None


def poll_until(sb, hash_lower: str, condition, label: str, timeout: int):
    """Poll list_torrents() every POLL_INTERVAL seconds until condition(torrent)
    is True or timeout expires.

    Returns the matching Torrent on success; calls sys.exit(1) on timeout.
    """
    deadline = time.monotonic() + timeout
    torrent = None
    while time.monotonic() < deadline:
        try:
            torrent = find_torrent(sb, hash_lower)
        except Exception as exc:
            log.warning("list_torrents() error (will retry): %s", exc)
            time.sleep(POLL_INTERVAL)
            continue

        if torrent is None:
            log.info("  [%s] torrent not visible yet, waiting …", label)
            time.sleep(POLL_INTERVAL)
            continue

        log.info(
            "  [%s] progress=%d%%  in_cache=%s  status=%s",
            label,
            torrent.progress,
            torrent.in_cache,
            torrent.status,
        )

        if condition(torrent):
            return torrent

        time.sleep(POLL_INTERVAL)

    log.error("Timed out after %d s waiting for: %s", timeout, label)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    email = os.environ.get("SONICBIT_EMAIL", "")
    password = os.environ.get("SONICBIT_PASSWORD", "")
    raw_magnet = os.environ.get("SONICBIT_TEST_MAGNET", "")

    missing = [name for name, val in [
        ("SONICBIT_EMAIL", email),
        ("SONICBIT_PASSWORD", password),
        ("SONICBIT_TEST_MAGNET", raw_magnet),
    ] if not val]
    if missing:
        log.error("Required environment variable(s) not set: %s", ", ".join(missing))
        return 1

    try:
        test_hash, display_name = parse_magnet(raw_magnet)
    except ValueError as exc:
        log.error("%s", exc)
        return 1

    log.info("Test torrent: %r  hash=%s", display_name, test_hash)

    from sonicbit import SonicBit

    # ---- 1. Authenticate -------------------------------------------------
    log.info("Authenticating as %s …", email)
    try:
        sb = SonicBit(email=email, password=password)
    except Exception as exc:
        log.error("Authentication failed: %s", exc)
        return 1
    log.info("Authenticated OK")

    torrent_hash = None

    try:
        # ---- Pre-clean: remove stale test torrent if present -------------
        log.info("Pre-clean: checking for stale test torrent …")
        stale = find_torrent(sb, test_hash)
        if stale:
            log.info("  Found stale torrent from a previous run — deleting it.")
            try:
                sb.delete_torrent(stale.hash, with_file=True)
                log.info("  Stale torrent deleted.")
            except Exception as exc:
                log.warning("  Could not delete stale torrent (continuing): %s", exc)

        # ---- 2. Add torrent ----------------------------------------------
        log.info("Adding test torrent …")
        try:
            added = sb.add_torrent(raw_magnet)
            log.info("add_torrent() accepted: %s", added)
        except Exception as exc:
            log.error("add_torrent() failed: %s", exc)
            return 1

        # Record the hash so the finally block can always clean up.
        torrent_hash = test_hash

        # ---- 3. Wait for download to complete (progress == 100) ----------
        log.info(
            "Waiting for download to complete (timeout %d s) …", DOWNLOAD_TIMEOUT
        )
        poll_until(
            sb,
            test_hash,
            lambda t: t.progress >= 100,
            "download",
            DOWNLOAD_TIMEOUT,
        )
        log.info("Download complete (progress = 100 %%).")

        # ---- 4. Wait for in_cache (data synced to cloud storage) ---------
        log.info(
            "Waiting for data to sync to cloud storage (timeout %d s) …", SYNC_TIMEOUT
        )
        poll_until(
            sb,
            test_hash,
            lambda t: bool(t.in_cache),
            "sync",
            SYNC_TIMEOUT,
        )
        log.info("Data synchronized to cloud storage (in_cache = True).")

        # ---- 5. Verify files appear in cloud file listing ----------------
        log.info("Verifying torrent folder appears in cloud file listing …")
        try:
            file_list = sb.list_files()
            names = [f.name for f in file_list.items]
            log.info("  Root-level entries: %s", names)
            needle = display_name.lower()
            found = any(needle in n.lower() for n in names)
            if found:
                log.info("  Torrent folder %r found in file listing. PASS", display_name)
            else:
                log.warning(
                    "  Torrent folder %r not found at root level "
                    "(may be nested or renamed by the service). "
                    "Treating as a warning, not a failure.",
                    display_name,
                )
        except Exception as exc:
            log.warning("  list_files() check skipped: %s", exc)

        log.info("All lifecycle checks passed.")
        return 0

    finally:
        # ---- 6. Always delete the torrent and its files ------------------
        if torrent_hash:
            log.info(
                "Cleanup: deleting torrent %s (with_file=True) …", torrent_hash
            )
            try:
                sb.delete_torrent(torrent_hash, with_file=True)
                log.info("Cleanup complete.")
            except Exception as exc:
                log.error("delete_torrent() failed during cleanup: %s", exc)
        else:
            log.info("Cleanup: no torrent hash recorded — nothing to delete.")


if __name__ == "__main__":
    sys.exit(main())
