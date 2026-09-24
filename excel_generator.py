"""
CareerOps Excel Generator
Produces XML-based Excel (.xls) with 6 sheets — now with deep free-forever intel (email, urgency, desperation, opportunity, pain):
  1. All Jobs — full dump of everything scanned
  2. Fresh Matches — accumulated matches at or above the configured threshold
  3. Applications — track which jobs you've applied to
  4. Cover Letters — generated cover letters for each match
  5. Learning — intelligence dashboard
  6. Daily Log — all scan runs
Same format and styling as the Cloudflare Worker.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

HISTORY_FILE = Path(__file__).parent / "output" / "fresh_matches_history.json"
APPLICATIONS_FILE = Path(__file__).parent / "output" / "applications.json"

# The user reads these sheets in Libya (UTC+2). Stamping them in UTC dated a
# delayed 20:00 UTC run a day early, so the digest showed e.g. 5 Sept while the
# user's local day was already the 6th.
LIBYA_TZ = timezone(timedelta(hours=2))


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def min_score_label() -> str:
    """Match-threshold range for sheet descriptions — tracks the live config."""
    try:
        from config import MIN_MATCH_SCORE
        return f"{MIN_MATCH_SCORE}-100%"
    except Exception:
        return "50-100%"


def get_recommendation(score: int) -> str:
    if score >= 90:
        return "STRONG MATCH - Clear fit with your CV. We recommend applying."
    if score >= 80:
        return "GOOD MATCH - Strong overlap with your profile. We recommend reviewing and applying."
    return "MODERATE MATCH - Review job requirements before applying."


def load_fresh_history() -> list[dict]:
    """Load accumulated fresh matches from previous scans."""
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def save_fresh_history(matches: list[dict]):
    """Save accumulated fresh matches across scans."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(matches, indent=2, default=str), encoding="utf-8")


def load_applications() -> dict:
    """Load application tracking data. Returns dict keyed by URL."""
    try:
        if APPLICATIONS_FILE.exists():
            data = json.loads(APPLICATIONS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def save_applications(apps: dict):
    """Save application tracking data."""
    APPLICATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    APPLICATIONS_FILE.write_text(json.dumps(apps, indent=2, default=str), encoding="utf-8")


def mark_applied(url: str, status: str = "Applied", notes: str = ""):
    """Mark a job as applied. Status: Applied, Maybe, Rejected, Interview, Offer."""
    apps = load_applications()
    apps[url] = {
        "status": status,
        "applied_date": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    }
    save_applications(apps)
    
    # Record in learning module for AI improvement
    try:
        from learning_module import record_application
        # Load job data from fresh history
        fresh_history = load_fresh_history()
        job_data = next((j for j in fresh_history if j.get("url") == url), {})
        
        # If job not found in fresh history, create minimal record
        if not job_data:
            job_data = {
                "url": url,
                "title": notes or "Unknown Job",
                "company": "Unknown",
                "score": 0,
                "category": "Other",
                "source": "manual",
            }
        
        # Map status to learning module status
        learning_status = "applied" if status == "Applied" else \
                        "interviewed" if status == "Interview" else \
                        "hired" if status == "Offer" else \
                        "rejected" if status in ("Rejected", "Maybe") else "applied"
        record_application(url, job_data, learning_status)
    except Exception as e:
        print(f"Learning record failed: {e}")


def get_application_status(url: str) -> str:
    """Get application status for a job URL."""
    apps = load_applications()
    return apps.get(url, {}).get("status", "Not Applied")


def _still_qualifies(match: dict) -> bool:
    """Re-run today's gates over an accumulated match.

    The history only ever grew, so entries that were acceptable under older rules
    (teaching/ESL roles, residency-blocked postings, wrong-language leaks) stayed
    in every digest forever. Re-validating on merge retires them. Under the
    strict policy only core translation/language-work matches (or company-
    boosted roles) survive, and anything the AI firmly rejected is dropped too.
    """
    from scanner import (
        COMPANY_MIN_SCORE, MIN_MATCH_SCORE, ai_poor_fit,
        drop_unqualified_matches, get_match_score, is_open_worldwide,
    )

    title = match.get("title", "")
    desc = match.get("description", "")
    if int(match.get("score") or 0) <= 0:
        return False
    if ai_poor_fit(match) or match.get("ai_reject"):
        return False
    scored = get_match_score(title, desc)
    if scored.get("score", 0) <= 0:
        return False
    if scored.get("score", 0) < MIN_MATCH_SCORE:
        # Below the Fresh floor only a company-boosted role may remain, and it
        # must clear the lower company floor.
        if not (match.get("company_boost") and scored.get("score", 0) >= COMPANY_MIN_SCORE):
            return False
    elif scored.get("category") == "Other":
        # Above the floor but no category signal — stale/malformed row.
        return False
    # Re-stamp the row with today's recomputed score/category so a stale
    # "100%" from an earlier (looser) matcher can never be re-shown.
    match["score"] = scored["score"]
    match["category"] = scored["category"]
    if not is_open_worldwide(match.get("location", ""), desc):
        return False
    return len(drop_unqualified_matches([dict(match)])) == 1


def merge_fresh_matches(current: list[dict], history: list[dict]) -> list[dict]:
    """Merge current matches with history, deduplicate by URL, keep latest scan date."""
    seen = {}
    # Load history first, dropping entries that no longer pass the gates
    for m in history:
        url = m.get("url", "")
        if url and _still_qualifies(m):
            seen[url] = m
    # Overlay current matches (they are newer)
    for m in current:
        url = m.get("url", "")
        if url:
            existing = seen.get(url, {})
            # Keep the newer scan date
            new_date = m.get("scan_date", "")
            old_date = existing.get("scan_date", "")
            if new_date >= old_date:
                seen[url] = m
            else:
                seen[url] = existing
    # Sort by score descending, then by scan_date descending
    result = sorted(seen.values(), key=lambda x: (-x.get("score", 0), x.get("scan_date", "")), reverse=False)
    return result


def generate_excel(
    jobs: list[dict],
    scan_time: str,
    near_misses: list[dict],
    all_jobs: list[dict],
    scan_info: dict,
    stats: dict,
) -> str:
    """Generate the full XML-based Excel spreadsheet with accumulating Fresh Matches."""
    from scanner import get_freshness, get_match_score

    now = datetime.now(LIBYA_TZ)
    date_str = now.strftime("%Y-%m-%d")
    time_str = scan_time or now.strftime("%I:%M %p")
    scan_date = now.isoformat()
    total_scanned = len(all_jobs) or scan_info.get("all_count", 0)

    # Scan slot in Libya local time — ONE daily delivery at 09:00 (07:00 UTC).
    # Manual/push-window runs are out-of-band digests of the same slot.
    scan_slot = "Morning (9 AM)"

    # ---- Tag current matches with scan_date ----
    for j in jobs:
        j["scan_date"] = scan_date

    # ---- Load and merge Fresh Matches history ----
    history = load_fresh_history()
    all_fresh = merge_fresh_matches(jobs, history)
    save_fresh_history(all_fresh)

    # ---- Fresh Matches rows (Sheet 2) — accumulated across all scans — DEEP INTEL (free forever) ----
    fresh_rows = []
    expiry_days = int(os.getenv("CAREEROPS_JOB_EXPIRY_DAYS", "3"))
    for i, j in enumerate(all_fresh):
        fresh = get_freshness(j.get("posted"))
        rec = get_recommendation(j.get("score", 0))
        scan_dt = j.get("scan_date", "")[:10]  # Just the date part
        url = j.get("url", "")
        applied_status = get_application_status(url)
        cover_path = j.get("cover_letter_path", "")
        # Deep intel (free forever) — may be missing on old history rows
        hiring_email = j.get("hiring_email", "")
        email_verified = "\u2713" if j.get("email_verified") else ("guess" if hiring_email and j.get("email_guessed") else "")
        urgency = j.get("urgency_score", 0)
        desperation = j.get("desperation_index", 0)
        opportunity = j.get("opportunity_score", j.get("score",0))
        pain = j.get("pain_points", "")
        # urgency label
        urgency_label = f"{urgency} \U0001f525" if urgency >= 30 else str(urgency) if urgency else ""
        desp_label = f"{desperation} \U0001f4a5" if desperation >= 50 else str(desperation) if desperation else ""
        # Red rows = not applied yet; green rows = applied/tracked
        row_style = "applied" if applied_status != "Not Applied" else "unapplied"
        # Lifecycle status
        lifecycle_status = j.get("lifecycle_status", "")
        found_date = j.get("found_date", "")[:10]
        expires_date = j.get("expires_date", "")[:10]
        if lifecycle_status == "new":
            status_label = "NEW"
        elif lifecycle_status == "old" and expires_date:
            status_label = f"OLD (expires {expires_date})"
        elif lifecycle_status == "expired":
            status_label = "EXPIRED"
        else:
            status_label = ""
        # Why-it-fits + AI verdict (deep intel columns)
        why_text = " \u00b7 ".join((j.get("why") or [])[:4])
        ai_verdict = j.get("ai_verdict", "")
        ai_score = j.get("ai_overall_score", 0)
        ai_cell = f"{ai_verdict} ({ai_score}/100)" if ai_verdict else ""
        fresh_rows.append(f'''
    <Row ss:StyleID="{row_style}">
      <Cell><Data ss:Type="Number">{i + 1}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("company", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("title", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("category", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("location") or "Remote")}</Data></Cell>
      <Cell><Data ss:Type="String">{j.get("score", 0)}%</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(fresh["label"])}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(rec)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(applied_status)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(hiring_email)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(email_verified)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("company_website", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(hiring_email or j.get("email") or "")}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(urgency_label)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(desp_label)}</Data></Cell>
      <Cell><Data ss:Type="String">{opportunity}%</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(pain)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(cover_path)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(status_label)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(scan_dt)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(url)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(why_text)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(ai_cell)}</Data></Cell>
    </Row>''')

    # ---- All Jobs rows (Sheet 1) ----
    detailed = {}
    for j in jobs + near_misses:
        if j.get("url"):
            detailed[j["url"]] = {"category": j.get("category", "Other"), "score": j.get("score", 0)}

    dump_rows = []
    for i, j in enumerate(all_jobs):
        fresh = get_freshness(j.get("posted"))
        url = j.get("url", "")
        has_detail = url in detailed
        if has_detail:
            category = detailed[url]["category"]
            score = detailed[url]["score"]
        else:
            # Use pre-calculated match_score if available, otherwise recalculate
            score = j.get("match_score") or j.get("ai_overall_score") or 0
            category = j.get("category", "Other")
            if score == 0:
                cs = get_match_score(j.get("title", ""), j.get("description", ""))
                category = cs["category"]
                score = cs["score"]

        is_winner = any(w.get("url") == url for w in jobs)
        is_near = any(n.get("url") == url for n in near_misses)
        row_style = ' ss:StyleID="green"' if is_winner else (' ss:StyleID="red"' if score >= 50 else "")

        dump_rows.append(f'''
    <Row{row_style}>
      <Cell><Data ss:Type="Number">{i + 1}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("company", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("title", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(category)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("location") or "Remote")}</Data></Cell>
      <Cell><Data ss:Type="String">{score}%</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(fresh["label"])}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("source", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(url)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("company_website", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("hiring_email") or j.get("email") or "")}</Data></Cell>
    </Row>''')

    # ---- Daily Log rows (Sheet 3) — accumulate across scans ----
    daily_rows = []
    # Add current scan with enhanced stats
    old_verified_count = scan_info.get("old_verified_count", 0)
    near_miss_count = len(near_misses)
    source_count = scan_info.get("source_count", 0)
    
    daily_rows.append(f'''
    <Row>
      <Cell><Data ss:Type="String">{_esc(date_str)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(scan_slot)}</Data></Cell>
      <Cell><Data ss:Type="Number">{total_scanned}</Data></Cell>
      <Cell><Data ss:Type="Number">{len(jobs)}</Data></Cell>
      <Cell><Data ss:Type="Number">{old_verified_count}</Data></Cell>
      <Cell><Data ss:Type="Number">{near_miss_count}</Data></Cell>
      <Cell><Data ss:Type="Number">{source_count}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(time_str)}</Data></Cell>
    </Row>''')
    # Add previous daily log entries from history
    daily_log_file = HISTORY_FILE.parent / "daily_log.json"
    try:
        if daily_log_file.exists():
            prev_logs = json.loads(daily_log_file.read_text(encoding="utf-8"))
            for log in prev_logs[-50:]:  # Keep last 50 entries
                daily_rows.append(f'''
    <Row>
      <Cell><Data ss:Type="String">{_esc(log.get("date", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(log.get("slot", ""))}</Data></Cell>
      <Cell><Data ss:Type="Number">{log.get("scanned", 0)}</Data></Cell>
      <Cell><Data ss:Type="Number">{log.get("matches", 0)}</Data></Cell>
      <Cell><Data ss:Type="Number">{log.get("old_verified", 0)}</Data></Cell>
      <Cell><Data ss:Type="Number">{log.get("near_misses", 0)}</Data></Cell>
      <Cell><Data ss:Type="Number">{log.get("sources", 0)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(log.get("time", ""))}</Data></Cell>
    </Row>''')
    except Exception:
        pass
    # Save current log entry
    daily_log_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        prev_logs = []
        if daily_log_file.exists():
            prev_logs = json.loads(daily_log_file.read_text(encoding="utf-8"))
        prev_logs.append({
            "date": date_str,
            "slot": scan_slot,
            "scanned": total_scanned,
            "matches": len(jobs),
            "old_verified": old_verified_count,
            "near_misses": near_miss_count,
            "sources": source_count,
            "time": time_str
        })
        daily_log_file.write_text(json.dumps(prev_logs[-100:], indent=2), encoding="utf-8")
    except Exception:
        pass

    dump_rows_str = "".join(dump_rows) if dump_rows else '<Row><Cell><Data ss:Type="String">No jobs fetched this scan.</Data></Cell></Row>'
    fresh_rows_str = "".join(fresh_rows) if fresh_rows else '<Row><Cell><Data ss:Type="String">No fresh matches yet.</Data></Cell></Row>'
    daily_rows_str = "".join(daily_rows) if daily_rows else '<Row><Cell><Data ss:Type="String">No scans yet.</Data></Cell></Row>'
    
    # ---- Applications tracking sheet ----
    apps = load_applications()
    app_rows = []
    for url, data in apps.items():
        status = data.get("status", "Not Applied")
        applied_date = data.get("applied_date", "")[:10]
        notes = data.get("notes", "")
        app_rows.append(f'''
    <Row>
      <Cell><Data ss:Type="String">{_esc(url)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(status)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(applied_date)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(notes)}</Data></Cell>
    </Row>''')
    app_rows_str = "".join(app_rows) if app_rows else '<Row><Cell><Data ss:Type="String">No applications tracked yet. Mark jobs as Applied in the Fresh Matches sheet.</Data></Cell></Row>'
    
    # ---- Cover Letters sheet ----
    cover_rows = []
    for i, j in enumerate(all_fresh):
        letter = j.get("cover_letter", "")
        pdf_path = j.get("cover_letter_path", "")
        if letter or pdf_path:
            cover_rows.append(f'''
    <Row>
      <Cell><Data ss:Type="Number">{i + 1}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("company", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("title", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("score", 0))}%</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(pdf_path)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(letter[:300] if letter else "PDF attached to email")}</Data></Cell>
    </Row>''')
    cover_rows_str = "".join(cover_rows) if cover_rows else '<Row><Cell><Data ss:Type="String">No cover letters generated yet.</Data></Cell></Row>'

    # ---- Learning sheet (Sheet 6) ----
    try:
        from learning_module import load_learning_data, get_learning_insights
        from evolution_tracker import _load_brain
        from source_manager import _load_registry
        from company_patterns import get_top_companies
        ld = load_learning_data()
        li = get_learning_insights()
        brain = _load_brain()
        reg = _load_registry()

        total_scans = brain.get("total_scans", 0)
        total_matches = brain.get("total_matches", 0)
        total_applied = len(ld.get("applied_jobs", []))
        acceptance_rate = ld.get("acceptance_rate", 0)

        learning_rows = []
        # Summary stats
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Summary</Data></Cell><Cell><Data ss:Type="String">Value</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Total Scans</Data></Cell><Cell><Data ss:Type="Number">{total_scans}</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Total Matches</Data></Cell><Cell><Data ss:Type="Number">{total_matches}</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Total Applied</Data></Cell><Cell><Data ss:Type="Number">{total_applied}</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Acceptance Rate</Data></Cell><Cell><Data ss:Type="String">{acceptance_rate}%</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Streak Days</Data></Cell><Cell><Data ss:Type="Number">{brain.get("streak_days", 0)}</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Best Day Matches</Data></Cell><Cell><Data ss:Type="Number">{brain.get("best_day_matches", 0)}</Data></Cell></Row>''')
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Best Day Date</Data></Cell><Cell><Data ss:Type="String">{_esc(brain.get("best_day_date", ""))}</Data></Cell></Row>''')
        # Blank separator
        learning_rows.append(f'''<Row></Row>''')
        # Top categories (skill_preferences)
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Top Categories</Data></Cell><Cell><Data ss:Type="String">Applications</Data></Cell></Row>''')
        for cat, count in sorted(ld.get("skill_preferences", {}).items(), key=lambda x: -x[1])[:10]:
            learning_rows.append(f'''<Row><Cell><Data ss:Type="String">{_esc(cat)}</Data></Cell><Cell><Data ss:Type="Number">{count}</Data></Cell></Row>''')
        # Blank separator
        learning_rows.append(f'''<Row></Row>''')
        # Top companies (company_preferences)
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Top Companies</Data></Cell><Cell><Data ss:Type="String">Applications</Data></Cell></Row>''')
        for comp, count in sorted(ld.get("company_preferences", {}).items(), key=lambda x: -x[1])[:10]:
            learning_rows.append(f'''<Row><Cell><Data ss:Type="String">{_esc(comp)}</Data></Cell><Cell><Data ss:Type="Number">{count}</Data></Cell></Row>''')
        # Blank separator
        learning_rows.append(f'''<Row></Row>''')
        # Top sources (source_performance.json)
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Top Sources</Data></Cell><Cell><Data ss:Type="String">Matches</Data></Cell><Cell><Data ss:Type="String">Fetched</Data></Cell></Row>''')
        src_ranked = sorted(reg.get("sources", {}).items(), key=lambda x: x[1].get("total_matches", 0), reverse=True)[:10]
        for name, src_data in src_ranked:
            learning_rows.append(f'''<Row><Cell><Data ss:Type="String">{_esc(name)}</Data></Cell><Cell><Data ss:Type="Number">{src_data.get("total_matches", 0)}</Data></Cell><Cell><Data ss:Type="Number">{src_data.get("total_fetched", 0)}</Data></Cell></Row>''')
        # Blank separator
        learning_rows.append(f'''<Row></Row>''')
        # Top companies from company_patterns
        learning_rows.append(f'''<Row><Cell><Data ss:Type="String">Company Pattern Top Companies</Data></Cell><Cell><Data ss:Type="String">Matches</Data></Cell><Cell><Data ss:Type="String">Last Match</Data></Cell></Row>''')
        for cp in get_top_companies(limit=10):
            learning_rows.append(f'''<Row><Cell><Data ss:Type="String">{_esc(cp["name"])}</Data></Cell><Cell><Data ss:Type="Number">{cp["total_matches"]}</Data></Cell><Cell><Data ss:Type="String">{_esc(cp["last_match"])}</Data></Cell></Row>''')
    except Exception as e:
        learning_rows = [f'''<Row><Cell><Data ss:Type="String">Learning data not available: {_esc(str(e))}</Data></Cell></Row>''']

    learning_rows_str = "".join(learning_rows)

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
  xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <Styles>
    <Style ss:ID="header"><Font ss:Bold="1" ss:Color="#FFFFFF" ss:Size="11"/><Interior ss:Color="#0d1b2a" ss:Pattern="Solid"/></Style>
    <Style ss:ID="green"><Interior ss:Color="#dcfce7" ss:Pattern="Solid"/></Style>
    <Style ss:ID="red"><Interior ss:Color="#fef2f2" ss:Pattern="Solid"/></Style>
    <Style ss:ID="unapplied"><Interior ss:Color="#fee2e2" ss:Pattern="Solid"/><Font ss:Color="#b91c1c" ss:Bold="1"/></Style>
    <Style ss:ID="applied"><Interior ss:Color="#dcfce7" ss:Pattern="Solid"/><Font ss:Color="#166534" ss:Bold="1"/></Style>
    <Style ss:ID="title"><Font ss:Bold="1" ss:Size="14" ss:Color="#0d1b2a"/></Style>
  </Styles>

  <!-- Sheet 1: All Jobs (full dump of everything scanned) -->
  <Worksheet ss:Name="All Jobs">
    <Table>
      <Column ss:Width="40"/><Column ss:Width="150"/><Column ss:Width="280"/><Column ss:Width="100"/>
      <Column ss:Width="140"/><Column ss:Width="60"/><Column ss:Width="100"/><Column ss:Width="80"/><Column ss:Width="420"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">CareerOps Full Scan - {date_str} ({total_scanned} jobs scanned)</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">Green = Fresh &amp; Ready to Apply | Red = Lower confidence / review first | White = not a close match</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">#</Data></Cell><Cell><Data ss:Type="String">Company</Data></Cell>
        <Cell><Data ss:Type="String">Role</Data></Cell><Cell><Data ss:Type="String">Category</Data></Cell>
        <Cell><Data ss:Type="String">Location</Data></Cell><Cell><Data ss:Type="String">Match</Data></Cell>
        <Cell><Data ss:Type="String">Freshness</Data></Cell><Cell><Data ss:Type="String">Source</Data></Cell><Cell><Data ss:Type="String">Apply URL</Data></Cell>
        <Cell><Data ss:Type="String">Company Website</Data></Cell><Cell><Data ss:Type="String">Contact Email</Data></Cell>
      </Row>
      {dump_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 2: Fresh Matches — DEEP INTEL (free forever): email, urgency, desperation, opportunity, pain -->
  <Worksheet ss:Name="Fresh Matches">
    <Table>
      <Column ss:Width="40"/><Column ss:Width="150"/><Column ss:Width="280"/><Column ss:Width="100"/>
      <Column ss:Width="140"/><Column ss:Width="60"/><Column ss:Width="100"/><Column ss:Width="120"/>
      <Column ss:Width="100"/><Column ss:Width="180"/>      <Column ss:Width="70"/><Column ss:Width="70"/>
      <Column ss:Width="70"/><Column ss:Width="70"/><Column ss:Width="220"/><Column ss:Width="200"/>
      <Column ss:Width="120"/><Column ss:Width="100"/><Column ss:Width="420"/>
      <Column ss:Width="380"/><Column ss:Width="120"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Fresh Matches - {date_str} {time_str} (accumulated, deep intel — free forever)</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">All {min_score_label()} matches. RED=not applied — apply now! GREEN=applied. Includes Hiring Email, Company Website, Contact Email, Urgency, Desperation, Opportunity, Pain Points, Why-it-fits and AI Verdict. No paid API.</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">#</Data></Cell><Cell><Data ss:Type="String">Company</Data></Cell>
        <Cell><Data ss:Type="String">Role</Data></Cell>
        <Cell><Data ss:Type="String">Category</Data></Cell><Cell><Data ss:Type="String">Location</Data></Cell><Cell><Data ss:Type="String">Match</Data></Cell>
        <Cell><Data ss:Type="String">Freshness</Data></Cell><Cell><Data ss:Type="String">Recommendation</Data></Cell>
        <Cell><Data ss:Type="String">Applied?</Data></Cell><Cell><Data ss:Type="String">Hiring Email</Data></Cell>
        <Cell><Data ss:Type="String">Verified</Data></Cell><Cell><Data ss:Type="String">Company Website</Data></Cell><Cell><Data ss:Type="String">Contact Email</Data></Cell>
        <Cell><Data ss:Type="String">Urgency</Data></Cell>
        <Cell><Data ss:Type="String">Desperation</Data></Cell><Cell><Data ss:Type="String">Opportunity</Data></Cell>
        <Cell><Data ss:Type="String">Pain Points / Why They Need You</Data></Cell><Cell><Data ss:Type="String">Cover Letter</Data></Cell>
        <Cell><Data ss:Type="String">Status</Data></Cell>
        <Cell><Data ss:Type="String">Found On</Data></Cell><Cell><Data ss:Type="String">Apply URL</Data></Cell>
        <Cell><Data ss:Type="String">Why This Fits</Data></Cell><Cell><Data ss:Type="String">AI Verdict</Data></Cell>
      </Row>
      {fresh_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 3: Applications (track your applications) -->
  <Worksheet ss:Name="Applications">
    <Table>
      <Column ss:Width="420"/><Column ss:Width="120"/><Column ss:Width="120"/><Column ss:Width="300"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Application Tracker</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">Track which jobs you've applied to. Update status: Applied, Maybe, Rejected, Interview, Offer.</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">Job URL</Data></Cell><Cell><Data ss:Type="String">Status</Data></Cell>
        <Cell><Data ss:Type="String">Applied Date</Data></Cell><Cell><Data ss:Type="String">Notes</Data></Cell>
      </Row>
      {app_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 4: Cover Letters (generated for each match) -->
  <Worksheet ss:Name="Cover Letters">
    <Table>
      <Column ss:Width="40"/><Column ss:Width="150"/><Column ss:Width="280"/><Column ss:Width="60"/><Column ss:Width="400"/><Column ss:Width="600"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Generated Cover Letters</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">PDF cover letters attached to email. Download from email or use the file path in column E.</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">#</Data></Cell><Cell><Data ss:Type="String">Company</Data></Cell>
        <Cell><Data ss:Type="String">Role</Data></Cell><Cell><Data ss:Type="String">Score</Data></Cell>
        <Cell><Data ss:Type="String">PDF Path</Data></Cell><Cell><Data ss:Type="String">Preview</Data></Cell>
      </Row>
      {cover_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 5: Learning (learning data and insights) -->
  <Worksheet ss:Name="Learning">
    <Table>
      <Column ss:Width="200"/><Column ss:Width="120"/><Column ss:Width="120"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Learning Intelligence - {date_str}</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">Data from learning_module, evolution_brain, source_performance, and company_patterns</Data></Cell></Row>
      {learning_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 6: Daily Log (accumulated across scans) -->
  <Worksheet ss:Name="Daily Log">
    <Table>
      <Column ss:Width="120"/><Column ss:Width="160"/><Column ss:Width="100"/><Column ss:Width="120"/><Column ss:Width="120"/><Column ss:Width="120"/><Column ss:Width="100"/><Column ss:Width="100"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Daily Scan Log (accumulated)</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">Date</Data></Cell><Cell><Data ss:Type="String">Scan Slot</Data></Cell>
        <Cell><Data ss:Type="String">Total Scanned</Data></Cell><Cell><Data ss:Type="String">Fresh Matches</Data></Cell>
        <Cell><Data ss:Type="String">Old Verified</Data></Cell><Cell><Data ss:Type="String">Near Misses</Data></Cell>
        <Cell><Data ss:Type="String">Sources</Data></Cell><Cell><Data ss:Type="String">Time (UTC)</Data></Cell>
      </Row>
      {daily_rows_str}
    </Table>
  </Worksheet>
</Workbook>'''
