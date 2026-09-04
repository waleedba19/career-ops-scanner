"""
CareerOps Excel Generator
Produces XML-based Excel (.xls) with 5 sheets:
  1. All Jobs — full dump of everything scanned
  2. Fresh Matches — accumulated 75-100% matches across all scans
  3. Applications — track which jobs you've applied to
  4. Cover Letters — generated cover letters for each match
  5. Daily Log — all scan runs
Same format and styling as the Cloudflare Worker.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HISTORY_FILE = Path(__file__).parent / "output" / "fresh_matches_history.json"
APPLICATIONS_FILE = Path(__file__).parent / "output" / "applications.json"


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


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


def merge_fresh_matches(current: list[dict], history: list[dict]) -> list[dict]:
    """Merge current matches with history, deduplicate by URL, keep latest scan date."""
    seen = {}
    # Load history first
    for m in history:
        url = m.get("url", "")
        if url:
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

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = scan_time or now.strftime("%I:%M %p")
    scan_date = now.isoformat()
    total_scanned = len(all_jobs) or scan_info.get("all_count", 0)

    # Hour-based scan slot
    hour = now.hour
    if hour < 11:
        scan_slot = "Morning (5 AM)"
    elif hour < 18:
        scan_slot = "Afternoon (12 PM)"
    else:
        scan_slot = "Night (8 PM)"

    # ---- Tag current matches with scan_date ----
    for j in jobs:
        j["scan_date"] = scan_date

    # ---- Load and merge Fresh Matches history ----
    history = load_fresh_history()
    all_fresh = merge_fresh_matches(jobs, history)
    save_fresh_history(all_fresh)

    # ---- Fresh Matches rows (Sheet 2) — accumulated across all scans ----
    fresh_rows = []
    for i, j in enumerate(all_fresh):
        fresh = get_freshness(j.get("posted"))
        rec = get_recommendation(j.get("score", 0))
        scan_dt = j.get("scan_date", "")[:10]  # Just the date part
        url = j.get("url", "")
        applied_status = get_application_status(url)
        cover_path = j.get("cover_letter_path", "")
        fresh_rows.append(f'''
    <Row ss:StyleID="green">
      <Cell><Data ss:Type="Number">{i + 1}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("company", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("title", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("category", ""))}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(j.get("location") or "Remote")}</Data></Cell>
      <Cell><Data ss:Type="String">{j.get("score", 0)}%</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(fresh["label"])}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(rec)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(applied_status)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(cover_path)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(scan_dt)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(url)}</Data></Cell>
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
            cs = get_match_score(j.get("title", ""), "")
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

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
  xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <Styles>
    <Style ss:ID="header"><Font ss:Bold="1" ss:Color="#FFFFFF" ss:Size="11"/><Interior ss:Color="#0d1b2a" ss:Pattern="Solid"/></Style>
    <Style ss:ID="green"><Interior ss:Color="#dcfce7" ss:Pattern="Solid"/></Style>
    <Style ss:ID="red"><Interior ss:Color="#fef2f2" ss:Pattern="Solid"/></Style>
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
      </Row>
      {dump_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 2: Fresh Matches (accumulated 75-100% across all scans) -->
  <Worksheet ss:Name="Fresh Matches">
    <Table>
      <Column ss:Width="40"/><Column ss:Width="150"/><Column ss:Width="280"/><Column ss:Width="100"/>
      <Column ss:Width="140"/><Column ss:Width="60"/><Column ss:Width="100"/><Column ss:Width="100"/>
      <Column ss:Width="100"/><Column ss:Width="200"/><Column ss:Width="100"/><Column ss:Width="420"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Fresh Matches - {date_str} {time_str} (accumulated across all scans)</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">All jobs matching 75-100% from every scan. Sort by score, then by scan date. Column I: mark Applied/Maybe/Rejected.</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">#</Data></Cell><Cell><Data ss:Type="String">Company</Data></Cell>
        <Cell><Data ss:Type="String">Role</Data></Cell>
        <Cell><Data ss:Type="String">Category</Data></Cell><Cell><Data ss:Type="String">Location</Data></Cell><Cell><Data ss:Type="String">Match</Data></Cell>
        <Cell><Data ss:Type="String">Freshness</Data></Cell><Cell><Data ss:Type="String">Recommendation</Data></Cell>
        <Cell><Data ss:Type="String">Applied?</Data></Cell><Cell><Data ss:Type="String">Cover Letter</Data></Cell>
        <Cell><Data ss:Type="String">Found On</Data></Cell><Cell><Data ss:Type="String">Apply URL</Data></Cell>
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

  <!-- Sheet 5: Daily Log (accumulated across scans) -->
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
