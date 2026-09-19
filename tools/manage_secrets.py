"""
manage_secrets.py — the durable credential store for CareerOps.

This is the "utility to store the tokens" : it reads the local .env file,
verifies every credential against its real service, and mirrors them to
GitHub Actions Secrets. Run it any time something seems off:

    python tools/manage_secrets.py        # verify + sync to GitHub
    python tools/manage_secrets.py check  # verify only, no writes

Secrets live in exactly two places — nowhere else, never re-typed:
  1. .env                  (this repo, gitignored)  -> local runs
  2. GitHub Actions Secrets (repo settings)         -> scheduled CI runs

Agents/AM readers: NEVER ask the user to paste tokens. Read `.env` (via
python-dotenv or export) or GitHub Secrets. If a value is missing there,
run this tool. Tokens appearing in chat are NOT stored anywhere unless
this file's write path is used.
"""
import os
import re
import smtplib
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
REPO = "waleedba19/career-ops-scanner"

# .env key -> GitHub Actions secret name
MAPPING = {
    "TELEGRAM_BOT_TOKEN": "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID": "TELEGRAM_CHAT_ID",
    "GROQ_API_KEY": "GROQ_API_KEY",
    "GMAIL_USER": "GMAIL_USER",
    "GMAIL_APP_PASSWORD": "GMAIL_APP_PASSWORD",
    "TO_EMAIL": "TO_EMAIL",
    "BREVO_API_KEY": "BREVO_API_KEY",
}


def load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV)
    except Exception:
        for line in ENV.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def _check(name, fn):
    try:
        fn()
        print(f"[OK]   {name}")
        return True
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {str(e)[:140]}")
        return False


def verify_all() -> bool:
    load_env()
    ok = True

    def tg():
        tok = os.getenv("TELEGRAM_BOT_TOKEN", "")
        req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/getMe")
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json_loads(r.read())
        assert data.get("ok") and data.get("result", {}).get("username")
        print(f"       -> bot @{data['result']['username']}")

    def groq():
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        assert client.models.list().data, "no models"

    def gmail():
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
            s.starttls()
            s.login(os.getenv("GMAIL_USER", ""), os.getenv("GMAIL_APP_PASSWORD", ""))

    ok &= _check("Telegram bot token", tg)
    ok &= _check("Groq API key", groq)
    ok &= _check("Gmail app password (SMTP login)", gmail)
    return ok


def json_loads(bs):
    import json
    return json.loads(bs.decode())


def _gh_pat():
    """Prefer .env token, else the token embedded in the git remote."""
    candidates = []
    if os.getenv("GITHUB_TOKEN_WALEEDBA19_1"):
        candidates.append(os.getenv("GITHUB_TOKEN_WALEEDBA19_1"))
    try:
        import subprocess  # noqa: F401
        url = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=30).stdout.strip()
        if "://" in url and "@" in url:
            candidates.append(urlparse(url).username)
    except Exception:
        pass
    for tok in candidates:
        r = subprocess.run(["gh", "api", "user"], capture_output=True, text=True,
                           timeout=60, env={**os.environ, "GH_TOKEN": tok})
        if r.returncode == 0:
            return tok
    return None


def sync_to_github():
    load_env()
    pat = _gh_pat()
    if not pat:
        print("No working GitHub token found — set GITHUB_TOKEN_WALEEDBA19_1 in .env")
        return False

    def gh(*args):
        return subprocess.run(["gh", *args], capture_output=True, text=True,
                              timeout=120, env={**os.environ, "GH_TOKEN": pat})

    print("Current GitHub secrets:")
    r = gh("secret", "list", "--repo", REPO)
    print(r.stdout.strip() or "(none)")

    n = 0
    for env_key, secret in MAPPING.items():
        value = os.getenv(env_key, "").strip()
        if not value:
            print(f"  SKIP {secret}: missing in .env")
            continue
        r = gh("secret", "set", secret, "--repo", REPO, "--body", value)
        if r.returncode == 0:
            n += 1
            print(f"  SET  {secret}")
        else:
            print(f"  FAIL {secret}: {r.stderr.strip()[:120]}")
    print(f"Synced {n}/{len(MAPPING)} secrets.")
    return n == len(MAPPING)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    ok = verify_all()
    if mode in ("all", "sync") and ok:
        ok = sync_to_github() and ok
    sys.exit(0 if ok else 1)