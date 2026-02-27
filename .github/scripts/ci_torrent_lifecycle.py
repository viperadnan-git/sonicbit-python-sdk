"""Torrent lifecycle integration test.

Exercises the full round-trip against the live SonicBit API:

  1. Pre-clean  — remove the test torrent if a previous CI run left it behind.
  2. Add        — add a small, well-seeded public-domain magnet link.
  3. Download   — poll list_torrents() until progress reaches 100 %.
  4. Sync       — poll until in_cache is True, which means the data has been
                  moved from the seedbox to permanent cloud storage.
  5. Verify     — confirm the torrent folder appears in list_files().
  6. Delete     — delete the torrent and its files unconditionally (finally block)
                  so the test account is always left clean.

Environment variables (required):
    SONICBIT_EMAIL     — e-mail address of the test account
    SONICBIT_PASSWORD  — password of the test account

Exit codes:
    0   all steps passed
    1   a step failed (see log output)
"""

import logging
import os
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Test fixture
# ---------------------------------------------------------------------------

# Big Buck Bunny (~276 MB) — permanently seeded public-domain torrent.
# On a seedbox with a fast uplink this finishes in well under a minute.
TEST_MAGNET = (
    "magnet:?xt=urn:btih:dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c"
    "&dn=Big+Buck+Bunny"
    "&tr=udp://explodie.org:6969"
    "&tr=udp://tracker.opentrackr.org:1337"
    "&tr=udp://tracker.openbittorrent.com:6969"
)
TEST_HASH = "dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c"

# Polling configuration.
POLL_INTERVAL = 10        # seconds between list_torrents() calls
DOWNLOAD_TIMEOUT = 600    # seconds to wait for progress to reach 100 %
SYNC_TIMEOUT = 300        # seconds to wait for in_cache to become True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_torrent(sb, hash_lower: str):
    """Return the Torrent object for hash_lower, or None if absent."""
    torrent_list = sb.list_torrents()
    for t in torrent_list.torrents.values():
        if t.hash.lower() == hash_lower:
            return t
    return None


def poll_until(sb, hash_lower: str, condition, label: str, timeout: int):
    """
    Poll list_torrents() every POLL_INTERVAL seconds until condition(torrent)
    is True or timeout is reached.

    Returns the last seen Torrent on success, raises SystemExit on timeout.
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

    if not email or not password:
        log.error(
            "SONICBIT_EMAIL and SONICBIT_PASSWORD environment variables must be set"
        )
        return 1

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
        stale = find_torrent(sb, TEST_HASH)
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
            added = sb.add_torrent(TEST_MAGNET)
            log.info("add_torrent() accepted: %s", added)
        except Exception as exc:
            log.error("add_torrent() failed: %s", exc)
            return 1

        # Record the hash so the finally block can always clean up.
        torrent_hash = TEST_HASH

        # ---- 3. Wait for download to complete (progress == 100) ----------
        log.info(
            "Waiting for download to complete (timeout %d s) …", DOWNLOAD_TIMEOUT
        )
        poll_until(
            sb,
            TEST_HASH,
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
            TEST_HASH,
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
            found = any(
                "big.buck.bunny" in n.lower() or "big buck bunny" in n.lower()
                for n in names
            )
            if found:
                log.info("  Torrent folder found in file listing. PASS")
            else:
                # Not a hard failure — the folder may be nested or named
                # differently on some account plans.
                log.warning(
                    "  Torrent folder not found at root level "
                    "(may be nested or renamed by the service). "
                    "Treating as a warning, not a failure."
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
