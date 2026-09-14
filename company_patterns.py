"""
Company Pattern Tracker — learns which companies reliably have Arabic jobs.
Tracks matches per company, auto-boosts frequent matchers, auto-demotes stale ones.
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

STATE_DIR = Path(__file__).parent / "state"
PATTERNS_FILE = STATE_DIR / "company_patterns.json"


def _load_patterns() -> dict:
    try:
        if PATTERNS_FILE.exists():
            return json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"companies": {}}


def _save_patterns(data: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PATTERNS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_company_match(company: str, title: str, category: str, score: float):
    """Record that a company produced a matching job."""
    if not company or not company.strip():
        return
    data = _load_patterns()
    key = company.strip().lower()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if key not in data["companies"]:
        data["companies"][key] = {
            "name": company.strip(),
            "total_matches": 0,
            "categories": {},
            "recent_matches": [],
            "last_match": "",
        }

    c = data["companies"][key]
    c["total_matches"] += 1
    c["last_match"] = today

    # Track category distribution
    c["categories"][category] = c["categories"].get(category, 0) + 1

    # Track recent matches (last 30 days)
    c["recent_matches"].append({"date": today, "title": title, "score": score, "category": category})
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    c["recent_matches"] = [m for m in c["recent_matches"] if m["date"] >= cutoff]

    _save_patterns(data)


def get_company_priority(company: str) -> float:
    """Return a score adjustment based on past company matches.
    Returns a value between -5 and +10.
    """
    if not company or not company.strip():
        return 0.0
    data = _load_patterns()
    key = company.strip().lower()
    c = data["companies"].get(key)
    if not c:
        return 0.0

    today = datetime.now(timezone.utc).date()
    today_str = today.isoformat()
    last_match = c.get("last_match", "")

    # Auto-demote: no match in 30 days -> penalty
    if last_match:
        try:
            last_date = datetime.strptime(last_match, "%Y-%m-%d").date()
            days_since = (today - last_date).days
            if days_since > 30:
                return -3.0
        except Exception:
            pass

    # Auto-boost: 3+ matches in last 14 days -> bonus
    fourteen_days_ago = (today - timedelta(days=14)).isoformat()
    recent = [m for m in c.get("recent_matches", []) if m["date"] >= fourteen_days_ago]
    if len(recent) >= 3:
        return 8.0
    if len(recent) >= 2:
        return 5.0
    if c["total_matches"] >= 1:
        return 2.0

    return 0.0


def get_top_companies(category: str = "", limit: int = 10) -> list[dict]:
    """Return companies with most matches, optionally filtered by category."""
    data = _load_patterns()
    companies = []
    for key, c in data["companies"].items():
        if category:
            count = c["categories"].get(category, 0)
            if count == 0:
                continue
        else:
            count = c["total_matches"]
        companies.append({
            "name": c["name"],
            "total_matches": c["total_matches"],
            "category_matches": c["categories"].get(category, 0) if category else 0,
            "last_match": c.get("last_match", ""),
        })
    companies.sort(key=lambda x: -x["total_matches"])
    return companies[:limit]
