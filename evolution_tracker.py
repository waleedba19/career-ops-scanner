"""
Evolution Tracker — the brain that learns from every scan.
Tracks trends, calculates improvements, generates evolving messages.
Makes the system smarter over time.
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

OUTPUT_DIR = Path(__file__).parent / "output"
EVOLUTION_FILE = OUTPUT_DIR / "evolution_brain.json"


def _load_brain() -> dict:
    """Load the evolution brain."""
    try:
        if EVOLUTION_FILE.exists():
            return json.loads(EVOLUTION_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {
        "total_scans": 0,
        "total_matches": 0,
        "total_jobs_scanned": 0,
        "best_day_matches": 0,
        "best_day_date": "",
        "daily_history": [],
        "category_trends": {},
        "source_trends": {},
        "streak_days": 0,
        "last_scan_date": "",
        "user_applied": [],
        "user_callbacks": [],
        "learning_notes": [],
    }


def _save_brain(brain: dict):
    """Save the evolution brain."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EVOLUTION_FILE.write_text(json.dumps(brain, indent=2, ensure_ascii=False), encoding="utf-8")


def record_scan(stats: dict):
    """Record a scan's results into the brain."""
    brain = _load_brain()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    brain["total_scans"] += 1
    brain["total_matches"] += stats.get("matches", 0)
    brain["total_jobs_scanned"] += stats.get("total_fetched", 0)
    
    # Update best day
    if stats.get("matches", 0) > brain.get("best_day_matches", 0):
        brain["best_day_matches"] = stats["matches"]
        brain["best_day_date"] = today
    
    # Track streak
    if brain["last_scan_date"] != today:
        last = brain.get("last_scan_date", "")
        if last:
            try:
                last_dt = datetime.strptime(last, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                today_dt = datetime.strptime(today, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if (today_dt - last_dt).days == 1:
                    brain["streak_days"] = brain.get("streak_days", 0) + 1
                elif (today_dt - last_dt).days > 1:
                    brain["streak_days"] = 1
            except Exception:
                brain["streak_days"] = 1
        else:
            brain["streak_days"] = 1
        brain["last_scan_date"] = today
    
    # Daily history (keep 90 days)
    brain["daily_history"].append({
        "date": today,
        "total_fetched": stats.get("total_fetched", 0),
        "matches": stats.get("matches", 0),
        "old_verified": stats.get("old_verified", 0),
        "near_misses": stats.get("near_misses", 0),
        "sources": stats.get("sources", 0),
        "fresh_count": stats.get("fresh_count", 0),
    })
    brain["daily_history"] = brain["daily_history"][-90:]
    
    # Category trends
    for cat in stats.get("categories", []):
        if cat not in brain["category_trends"]:
            brain["category_trends"][cat] = {"count": 0, "last_seen": today}
        brain["category_trends"][cat]["count"] += 1
        brain["category_trends"][cat]["last_seen"] = today
    
    # Source trends
    for src in stats.get("source_matches", {}):
        if src not in brain["source_trends"]:
            brain["source_trends"][src] = {"matches": 0, "last_seen": today}
        brain["source_trends"][src]["matches"] += stats["source_matches"][src]
        brain["source_trends"][src]["last_seen"] = today
    
    _save_brain(brain)


def get_evolution_summary() -> str:
    """Generate an evolving summary of the system's performance."""
    brain = _load_brain()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if brain["total_scans"] == 0:
        return "🧠 First scan — building memory..."
    
    lines = []
    
    # Streak
    streak = brain.get("streak_days", 0)
    if streak > 1:
        lines.append(f"🔥 {streak}-day scanning streak!")
    
    # Overall stats
    avg_matches = brain["total_matches"] / max(brain["total_scans"], 1)
    lines.append(f"📈 {brain['total_scans']} scans | {brain['total_matches']} total matches | avg {avg_matches:.1f}/scan")
    
    # Recent trend (last 7 days)
    recent = [d for d in brain["daily_history"] if d["date"] >= (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")]
    if len(recent) >= 2:
        first_half = sum(d["matches"] for d in recent[:len(recent)//2])
        second_half = sum(d["matches"] for d in recent[len(recent)//2:])
        if second_half > first_half:
            lines.append("📊 Trending UP — more matches this week!")
        elif second_half < first_half:
            lines.append("📊 Trending down — fewer matches this week")
        else:
            lines.append("📊 Steady — consistent match rate")
    
    # Best categories
    if brain["category_trends"]:
        top_cats = sorted(brain["category_trends"].items(), key=lambda x: x[1]["count"], reverse=True)[:3]
        cat_names = ", ".join(f"{c[0]} ({c[1]['count']})" for c in top_cats)
        lines.append(f"🎯 Top categories: {cat_names}")
    
    # Best sources
    if brain["source_trends"]:
        top_srcs = sorted(brain["source_trends"].items(), key=lambda x: x[1]["matches"], reverse=True)[:3]
        src_names = ", ".join(f"{s[0]} ({s[1]['matches']})" for s in top_srcs)
        lines.append(f"🌐 Best sources: {src_names}")
    
    # Record high
    if brain.get("best_day_date"):
        lines.append(f"🏆 Record day: {brain['best_day_matches']} matches on {brain['best_day_date']}")
    
    return "\n".join(lines)


def record_user_feedback(job_url: str, action: str):
    """Record user feedback (applied, rejected, callback).
    action = 'applied' | 'rejected' | 'callback' | 'interview'
    """
    brain = _load_brain()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    entry = {"url": job_url, "action": action, "date": today}
    
    if action == "applied":
        brain["user_applied"].append(entry)
    elif action in ("callback", "interview"):
        brain["user_callbacks"].append(entry)
    
    # Keep last 200 entries
    brain["user_applied"] = brain["user_applied"][-200:]
    brain["user_callbacks"] = brain["user_callbacks"][-200:]
    
    _save_brain(brain)


def get_acceptance_rate() -> float:
    """Calculate callback rate from user applications."""
    brain = _load_brain()
    applied = len(brain.get("user_applied", []))
    callbacks = len(brain.get("user_callbacks", []))
    if applied == 0:
        return 0.0
    return (callbacks / applied) * 100


def add_learning_note(note: str):
    """Add a learning note to the brain."""
    brain = _load_brain()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    brain["learning_notes"].append({"date": today, "note": note})
    brain["learning_notes"] = brain["learning_notes"][-50:]
    _save_brain(brain)
