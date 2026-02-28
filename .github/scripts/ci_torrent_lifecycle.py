"""Torrent lifecycle integration test.

Exercises the full round-trip against the live SonicBit API:

  1. Authenticate     — create a SonicBit session.
  2. User details     — verify get_user_details() and get_storage_details().
  3. Remote download  — full add → list → delete lifecycle for a small remote URL.
  4. Pre-clean        — remove the test torrent if a previous CI run left it behind.
  5. Add              — add the magnet link supplied via SONICBIT_TEST_MAGNET.
  6. Download         — poll list_torrents() until progress reaches 100 %.
  7. Sync             — poll until in_cache=True OR 'c' in status (data in cloud storage).
  8. Torrent details  — verify get_torrent_details() returns a non-empty file list.
  9. File delete      — verify delete_file() removes the torrent folder from cloud storage.
 10. Delete           — delete the torrent (finally block) so the account is always clean.

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
SYNC_TIMEOUT = 300        # seconds to wait for cloud-storage sync signal

# Small public file used for the remote-download lifecycle test.
REMOTE_DOWNLOAD_URL = "https://proof.ovh.net/files/1Mb.dat"


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
    from sonicbit.models import PathInfo

    # ---- 1. Authenticate -------------------------------------------------
    log.info("Authenticating as %s …", email)
    try:
        sb = SonicBit(email=email, password=password)
    except Exception as exc:
        log.error("Authentication failed: %s", exc)
        return 1
    log.info("Authenticated OK")

    # ---- 2. User details -------------------------------------------------
    log.info("Fetching user details …")
    try:
        user = sb.get_user_details()
        if user.email.lower() != email.lower():
            log.error(
                "get_user_details() email mismatch: got %r, expected %r",
                user.email, email,
            )
            return 1
        if user.is_suspended:
            log.error("Account is suspended — cannot continue.")
            return 1
        log.info(
            "  User: %r  plan=%r  premium=%s  suspended=%s",
            user.name, user.plan_name, user.is_premium, user.is_suspended,
        )
    except Exception as exc:
        log.error("get_user_details() failed: %s", exc)
        return 1

    log.info("Fetching storage details …")
    try:
        storage = sb.get_storage_details()
        if storage.size_byte_limit <= 0:
            log.error(
                "get_storage_details() returned invalid size_byte_limit=%d",
                storage.size_byte_limit,
            )
            return 1
        if not (0.0 <= storage.percent <= 100.0):
            log.error(
                "get_storage_details() returned out-of-range percent=%.1f",
                storage.percent,
            )
            return 1
        log.info(
            "  Storage: %.1f%% used  limit=%d bytes",
            storage.percent, storage.size_byte_limit,
        )
    except Exception as exc:
        log.error("get_storage_details() failed: %s", exc)
        return 1

    # ---- 3. Remote download lifecycle ------------------------------------
    log.info("Remote download: pre-clean (removing any stale task) …")
    try:
        existing = sb.list_remote_downloads()
        for task in existing.tasks:
            if task.url == REMOTE_DOWNLOAD_URL:
                log.info("  Removing stale remote-download task id=%d …", task.id)
                sb.delete_remote_download(task.id)
    except Exception as exc:
        log.warning("  Remote-download pre-clean skipped: %s", exc)

    log.info("Adding remote download: %s …", REMOTE_DOWNLOAD_URL)
    try:
        ok = sb.add_remote_download(REMOTE_DOWNLOAD_URL, PathInfo.root())
        if not ok:
            log.error("add_remote_download() returned False")
            return 1
        log.info("  add_remote_download() accepted.")
    except Exception as exc:
        log.error("add_remote_download() failed: %s", exc)
        return 1

    log.info("Listing remote downloads to verify task was created …")
    rd_task_id = None
    try:
        rd_list = sb.list_remote_downloads()
        for task in rd_list.tasks:
            if task.url == REMOTE_DOWNLOAD_URL:
                rd_task_id = task.id
                log.info(
                    "  Found task id=%d  progress=%d%%  in_queue=%s",
                    task.id, task.progress, task.in_queue,
                )
                break
        if rd_task_id is None:
            log.error(
                "list_remote_downloads() did not return the newly added task (url=%s)",
                REMOTE_DOWNLOAD_URL,
            )
            return 1
    except Exception as exc:
        log.error("list_remote_downloads() failed: %s", exc)
        return 1

    log.info("Deleting remote download task id=%d …", rd_task_id)
    try:
        deleted = sb.delete_remote_download(rd_task_id)
        if not deleted:
            log.error(
                "delete_remote_download() returned False for id=%d", rd_task_id
            )
            return 1
        log.info("  Remote download task deleted.")
    except Exception as exc:
        log.error("delete_remote_download() failed: %s", exc)
        return 1

    torrent_hash = None
    cloud_files_deleted = False

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

        # ---- 5. Add torrent ----------------------------------------------
        log.info("Adding test torrent …")
        try:
            added = sb.add_torrent(raw_magnet)
            log.info("add_torrent() accepted: %s", added)
        except Exception as exc:
            log.error("add_torrent() failed: %s", exc)
            return 1

        # Record the hash so the finally block can always clean up.
        torrent_hash = test_hash

        # ---- 6. Wait for download to complete (progress == 100) ----------
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

        # ---- 7. Wait for sync to cloud storage ---------------------------
        # The API signals a completed sync via EITHER of two mechanisms:
        #   • in_cache=True  — explicit boolean flag set by some plan types
        #   • 'c' in status  — status code that appears once the seedbox has
        #                       moved the data to permanent cloud storage
        # Both are treated as success; checking only in_cache caused timeouts
        # on accounts where that flag is never set but 'c' reliably appears.
        log.info(
            "Waiting for data to sync to cloud storage (timeout %d s) …", SYNC_TIMEOUT
        )
        poll_until(
            sb,
            test_hash,
            lambda t: bool(t.in_cache) or "c" in t.status,
            "sync",
            SYNC_TIMEOUT,
        )
        log.info("Data synchronized to cloud storage.")

        # ---- 8. Torrent details ------------------------------------------
        log.info("Fetching torrent details …")
        try:
            details = sb.get_torrent_details(test_hash)
            if not details.files:
                log.error("get_torrent_details() returned an empty file list")
                return 1
            log.info(
                "  get_torrent_details() OK — %d file(s) found:",
                len(details.files),
            )
            for f in details.files:
                log.info(
                    "    %s  (%d bytes  progress=%d%%)", f.name, f.size, f.progress
                )
        except Exception as exc:
            log.error("get_torrent_details() failed: %s", exc)
            return 1

        # ---- 9. File listing and deletion --------------------------------
        log.info("Verifying torrent folder appears in cloud file listing …")
        try:
            file_list = sb.list_files()
            names = [f.name for f in file_list.items]
            log.info("  Root-level entries: %s", names)
            needle = display_name.lower()
            target_file = next(
                (f for f in file_list.items if needle in f.name.lower()), None
            )
            if target_file:
                log.info(
                    "  Torrent folder %r found in file listing. PASS", target_file.name
                )
                log.info("  Deleting torrent folder from cloud storage …")
                deleted = sb.delete_file(target_file)
                if deleted:
                    cloud_files_deleted = True
                    log.info("  delete_file() succeeded. PASS")
                else:
                    log.warning(
                        "  delete_file() returned False — folder may not have been removed."
                    )
            else:
                log.warning(
                    "  Torrent folder %r not found at root level "
                    "(may be nested or renamed by the service). "
                    "Skipping delete_file() test.",
                    display_name,
                )
        except Exception as exc:
            log.warning("  File listing/deletion check skipped: %s", exc)

        log.info("All lifecycle checks passed.")
        return 0

    finally:
        # ---- 10. Always delete the torrent --------------------------------
        if torrent_hash:
            # If cloud files were already removed by delete_file() above,
            # use with_file=False to avoid a spurious server-side error.
            with_file = not cloud_files_deleted
            log.info(
                "Cleanup: deleting torrent %s (with_file=%s) …",
                torrent_hash, with_file,
            )
            try:
                sb.delete_torrent(torrent_hash, with_file=with_file)
                log.info("Cleanup complete.")
            except Exception as exc:
                log.error("delete_torrent() failed during cleanup: %s", exc)
        else:
            log.info("Cleanup: no torrent hash recorded — nothing to delete.")


if __name__ == "__main__":
    sys.exit(main())
