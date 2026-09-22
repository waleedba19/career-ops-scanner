"""
mistake_memory.py — the system's scar tissue.

Every run the scanner records what went wrong (AI poor-fit verdicts, directory/
aggregator email domains, expired false leads, user rejections) into a
persistent ledger (state/mistakes.json). The Groq prompt then reads back this
ledger each scan, so the AI is told "you/we have already flagged these" and
judges repeat offenders strictly BEFORE anything is delivered.

The ledger is capped and deduped so it stays small and current; the feedback
loop closes when the user marks applications (Applied/Rejected) — those also
land here and feed the AI's strictness.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PATH = Path(os.getenv("CAREEROPS_STATE_DIR", ROOT / "state")) / "mistakes.json"

MAX_ENTRIES = 200
MAX_COMPANIES = 60
MAX_DOMAINS = 40


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path | None = None) -> dict:
    p = path or DEFAULT_PATH
    try:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"companies": {}, "domains": {}, "categories": {}, "titles": [], "updated": ""}


def save(data: dict, path: Path | None = None):
    data["updated"] = _now()
    (path or DEFAULT_PATH).parent.mkdir(parents=True, exist_ok=True)
    (path or DEFAULT_PATH).write_text(json.dumps(data, indent=2, default=str),
                                      encoding="utf-8")


def note_mistake(job: dict, reason: str, path: Path | None = None) -> dict:
    """Record a mistake pattern so future scans/AI audit avoid it."""
    data = load(path)
    company = str(job.get("company") or "").strip()
    if company:
        bucket = data["companies"].setdefault(company, [])
        entry = {"reason": reason, "date": _now()}
        if entry not in bucket:
            bucket.append(entry)
        data["companies"][company] = bucket[-MAX_ENTRIES:]

    domain = str(job.get("email_directory") or "").strip() or \
        str((job.get("hiring_email") or "").split("@")[-1]).strip()
    if domain and "." in domain:
        dm = data["domains"].setdefault(domain, [])
        e = {"reason": reason, "date": _now()}
        if e not in dm:
            dm.append(e)
        data["domains"][domain] = dm[-MAX_ENTRIES:]

    cat = str(job.get("category") or "").strip()
    if cat:
        data["categories"][cat] = data["categories"].get(cat, 0) + 1

    title = str(job.get("title") or "").strip()
    if title and len(title) > 3:
        existing = [t for t in data["titles"] if t.get("title") == title]
        if not existing:
            data["titles"].append({"title": title, "reason": reason, "date": _now()})
        data["titles"] = data["titles"][-MAX_ENTRIES:]

    # keep size bounded
    if len(data["companies"]) > MAX_COMPANIES:
        data["companies"] = dict(sorted(data["companies"].items(),
                                  key=lambda kv: kv[1][-1].get("date", ""))[-MAX_COMPANIES:])
    if len(data["domains"]) > MAX_DOMAINS:
        data["domains"] = dict(sorted(data["domains"].items(),
                                key=lambda kv: kv[1][-1].get("date", ""))[-MAX_DOMAINS:])

    save(data, path)
    return data


def block_context(path: Path | None = None, limit: int = 6) -> str:
    """Short, prompt-safe summary of known mistakes to feed the AI."""
    data = load(path)
    parts = []
    comps = sorted(data.get("companies", {}).items(),
                   key=lambda kv: kv[1][-1].get("date", ""))[-limit:]
    for company, entries in comps:
        reasons = sorted({e.get("reason", "") for e in entries})[:2]
        parts.append(f"{company} ({'; '.join(reasons)})")
    doms = list(data.get("domains", {}).keys())[-limit:]
    if doms:
        parts.append("domains: " + ", ".join(doms))
    cats = sorted(data.get("categories", {}).items(), key=lambda kv: -kv[1])[:4]
    if cats:
        parts.append("weak categories: " + ", ".join(f"{c} (x{n})" for c, n in cats))
    if not parts:
        return "No known mistakes recorded yet."
    return "Previously flagged (be strict on these): " + " | ".join(parts)


def is_known_bad_company(company: str, path: Path | None = None) -> bool:
    return bool(company and load(path).get("companies", {}).get(str(company).strip()))


def is_known_bad_domain(domain: str, path: Path | None = None) -> bool:
    return bool(domain and load(path).get("domains", {}).get(str(domain).strip().lower()))