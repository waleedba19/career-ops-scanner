"""
Smart Source Manager — learns which sources provide the best matches.
Tracks source performance, auto-discoveres new sources, auto-removes dead ones.
Acts as the "memory" of which job sites are valuable.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

OUTPUT_DIR = Path(__file__).parent / "output"
SOURCE_REGISTRY = OUTPUT_DIR / "source_performance.json"


def _load_registry() -> dict:
    """Load source performance data."""
    try:
        if SOURCE_REGISTRY.exists():
            return json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"sources": {}, "discoveries": [], "last_cleanup": None}


def _save_registry(reg: dict):
    """Save source performance data."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


def record_source_run(source_name: str, jobs_fetched: int, matches_found: int):
    """Record how a source performed this scan."""
    reg = _load_registry()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if source_name not in reg["sources"]:
        reg["sources"][source_name] = {
            "first_seen": today,
            "total_fetched": 0,
            "total_matches": 0,
            "last_active": today,
            "consecutive_empty": 0,
            "status": "active",
            "daily_stats": [],
        }
    
    src = reg["sources"][source_name]
    src["total_fetched"] += jobs_fetched
    src["total_matches"] += matches_found
    src["last_active"] = today
    
    if matches_found > 0:
        src["consecutive_empty"] = 0
        src["status"] = "active"
    else:
        src["consecutive_empty"] += 1
        if src["consecutive_empty"] >= 14:
            src["status"] = "inactive"
        elif src["consecutive_empty"] >= 7:
            src["status"] = "weak"
    
    # Keep last 30 days of stats
    src["daily_stats"].append({
        "date": today,
        "fetched": jobs_fetched,
        "matches": matches_found,
    })
    src["daily_stats"] = src["daily_stats"][-30:]
    
    _save_registry(reg)


def get_active_sources() -> list[str]:
    """Get list of sources that are still active (not dead)."""
    reg = _load_registry()
    return [
        name for name, data in reg["sources"].items()
        if data.get("status") != "inactive"
    ]


def get_source_report() -> str:
    """Generate a human-readable source performance report."""
    reg = _load_registry()
    if not reg["sources"]:
        return "No source data yet — first scan in progress."
    
    lines = ["📊 Source Performance Report:", ""]
    
    # Sort by match rate
    ranked = sorted(
        reg["sources"].items(),
        key=lambda x: x[1].get("total_matches", 0),
        reverse=True,
    )
    
    active = sum(1 for _, s in ranked if s.get("status") == "active")
    weak = sum(1 for _, s in ranked if s.get("status") == "weak")
    inactive = sum(1 for _, s in ranked if s.get("status") == "inactive")
    
    lines.append(f"Total: {len(ranked)} sources | ✅ Active: {active} | ⚠️ Weak: {weak} | ❌ Inactive: {inactive}")
    lines.append("")
    
    # Top 5 sources
    lines.append("🏆 Top Sources (by matches found):")
    for name, data in ranked[:5]:
        m = data.get("total_matches", 0)
        f = data.get("total_fetched", 0)
        rate = f"{(m/f*100):.1f}%" if f > 0 else "0%"
        lines.append(f"  {name}: {m} matches from {f} jobs ({rate})")
    
    # Weak/inactive sources
    if weak + inactive > 0:
        lines.append("")
        lines.append("⚠️ Sources needing attention:")
        for name, data in ranked:
            status = data.get("status", "active")
            if status in ("weak", "inactive"):
                lines.append(f"  {name}: {status} (empty for {data.get('consecutive_empty', 0)} scans)")
    
    return "\n".join(lines)


def cleanup_dead_sources():
    """Remove sources that have been inactive for 30+ days."""
    reg = _load_registry()
    today = datetime.now(timezone.utc)
    
    removed = []
    for name, data in list(reg["sources"].items()):
        last_active = data.get("last_active", "")
        if last_active:
            try:
                last_date = datetime.strptime(last_active, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days_inactive = (today - last_date).days
                if days_inactive > 30 and data.get("status") == "inactive":
                    removed.append(name)
                    del reg["sources"][name]
            except Exception:
                pass
    
    reg["last_cleanup"] = today.isoformat()
    _save_registry(reg)
    return removed
