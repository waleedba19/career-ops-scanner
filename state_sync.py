"""
State Sync — persistent memory for GitHub Actions runs.

GitHub Actions runners are ephemeral: the output/ directory is wiped
after every run, so dedup, application tracking, learning data, and the
evolution brain were lost between scans. This module syncs the scanner's
state files to a state/ folder in the repo via the GitHub Contents API,
giving the system real memory that survives from run to run.

Only active inside GitHub Actions (GITHUB_ACTIONS env var set). Locally
it is a no-op, so local scans keep working unchanged.
"""

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"

# (local file under output/, repo path under state/)
STATE_FILES = [
    "applications.json",
    "learning_data.json",
    "evolution_brain.json",
    "source_performance.json",
    "source_registry.json",
    "daily_log.json",
    "fresh_matches_history.json",
    "scan_history_acum.json",
    "scan_history.json",
    "seen_urls.json",
    "smart_seen.json",
    "company_cache/company_data.json",
    # Written by company_board_probe.py; read by scanner._load_valid_slugs().
    # Without this the probe result is discarded every run.
    "valid_company_slugs.json",
]

_HEADERS = {
    "User-Agent": "careerops-state-sync",
    "Accept": "application/vnd.github+json",
}


def _api() -> tuple[str, str] | None:
    """Return (api contents base url, token) if running in GitHub Actions."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not os.getenv("GITHUB_ACTIONS") or not token or not repo:
        return None
    return f"https://api.github.com/repos/{repo}/contents", token


def _get_sha(base: str, token: str, url: str) -> str | None:
    """Fetch the current blob SHA of a repo file (None if it doesn't exist)."""
    try:
        req = urllib.request.Request(url, headers={**_HEADERS, "Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("sha")
    except Exception:
        return None


def _is_not_found(exc: Exception) -> bool:
    """True if the error is an HTTP 404 (file not on remote yet — first run)."""
    return getattr(exc, "code", None) == 404


def _fetch_content(base: str, token: str, rel: str) -> bytes:
    """Fetch a state file's raw bytes from the repo.

    The Contents API omits ``content`` for blobs over ~1 MiB (returning
    ``"content": ""`` plus a ``download_url``), which previously made large
    files like smart_seen.json restore as empty bytes. Handle both paths and
    fail loudly if we genuinely cannot get content — never return empty bytes
    for a file that exists on the remote.
    """
    url = f"{base}/state/{rel}"
    req = urllib.request.Request(url, headers={**_HEADERS, "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    raw = data.get("content")
    if data.get("encoding") == "base64" and raw:
        return base64.b64decode(raw)
    if data.get("download_url"):
        with urllib.request.urlopen(data["download_url"], timeout=30) as r2:
            return r2.read()
    raise ValueError(f"no content returned for state/{rel}")


def _write_validated(dest: Path, content: bytes) -> None:
    """Validate JSON then atomically replace dest — never clobber good state."""
    json.loads(content.decode("utf-8"))  # raises if corrupt
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_bytes(content)
    tmp.replace(dest)  # atomic swap


def download_state() -> int:
    """Fetch state files from the repo's state/ folder into output/.

    Returns the number restored, or -1 if any file failed. A file that simply
    does not exist yet on the remote (first run) is not a failure;
    decode/transport/validation errors are.
    """
    api = _api()
    if not api:
        return 0
    base, token = api
    restored = 0
    failed = 0
    for rel in STATE_FILES:
        try:
            content = _fetch_content(base, token, rel)
            _write_validated(OUTPUT_DIR / rel, content)
            restored += 1
        except Exception as e:
            if _is_not_found(e):
                print(f"  [state] download {rel}: not present on remote (first run), skipping")
            else:
                print(f"  [state] download {rel}: {e}")
                failed += 1
    print(f"[state] restored {restored}/{len(STATE_FILES)} state files ({failed} failed)")
    return -1 if failed else restored


def _put_file(base: str, token: str, rel: str, src: Path, message: str) -> None:
    """Upload a single file to the repo, retrying once on a 409 SHA conflict.

    A 409 means the remote file changed between our SHA lookup and the PUT
    (e.g. an overlapping run committed first). Re-fetch the SHA and retry once;
    the shared workflow concurrency group should make this rare.
    """
    url = f"{base}/state/{rel}"
    for attempt in range(2):
        body: dict = {
            "message": message,
            "content": base64.b64encode(src.read_bytes()).decode("ascii"),
        }
        sha = _get_sha(base, token, url)
        if sha:
            body["sha"] = sha
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="PUT",
            headers={**_HEADERS, "Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status in (200, 201):
                    return
        except Exception as e:
            if getattr(e, "code", None) == 409 and attempt == 0:
                print(f"  [state] upload {rel}: conflict, retrying with fresh SHA")
                continue
            raise
    raise RuntimeError(f"upload {rel}: conflict persisted after retry")


def upload_state() -> int:
    """Upload local state files to the repo's state/ folder.

    Returns the number uploaded, or -1 if any failed.
    """
    api = _api()
    if not api:
        return 0
    base, token = api
    uploaded = 0
    failed = 0
    for rel in STATE_FILES:
        src = OUTPUT_DIR / rel
        if not src.exists():
            continue
        try:
            _put_file(base, token, rel, src, f"careerops: update {rel}")
            uploaded += 1
        except Exception as e:
            print(f"  [state] upload {rel}: {e}")
            failed += 1
    print(f"[state] uploaded {uploaded} state files ({failed} failed)")
    return -1 if failed else uploaded


PROBE_FILES = ["source_probe.md", "source_probe.json"]


def upload_probe() -> int:
    """Upload the latest source-probe report (output/source_probe.*) to state/."""
    api = _api()
    if not api:
        return 0
    base, token = api
    uploaded = 0
    failed = 0
    for rel in PROBE_FILES:
        src = OUTPUT_DIR / rel
        if not src.exists():
            continue
        try:
            _put_file(base, token, rel, src, f"careerops: source probe report ({rel})")
            uploaded += 1
        except Exception as e:
            print(f"  [state] upload {rel}: {e}")
            failed += 1
    print(f"[state] uploaded {uploaded} probe report files ({failed} failed)")
    return -1 if failed else uploaded


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "download":
        sys.exit(1 if download_state() < 0 else 0)
    elif cmd == "upload":
        sys.exit(1 if upload_state() < 0 else 0)
    elif cmd == "upload-probe":
        sys.exit(1 if upload_probe() < 0 else 0)
    else:
        print("Usage: python state_sync.py [download|upload|upload-probe]")
        sys.exit(2)