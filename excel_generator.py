"""
CareerOps Excel Generator
Produces XML-based Excel (.xls) with 3 sheets:
  1. All Jobs — full dump of everything scanned
  2. Fresh Matches — 75-100% only
  3. Daily Log
Same format and styling as the Cloudflare Worker.
"""

from datetime import datetime, timezone
from typing import Any


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def get_recommendation(score: int) -> str:
    if score >= 90:
        return "STRONG MATCH - Clear fit with your CV. We recommend applying."
    if score >= 80:
        return "GOOD MATCH - Strong overlap with your profile. We recommend reviewing and applying."
    return "MODERATE MATCH - Review job requirements before applying."


def generate_excel(
    jobs: list[dict],
    scan_time: str,
    near_misses: list[dict],
    all_jobs: list[dict],
    scan_info: dict,
    stats: dict,
) -> str:
    """Generate the full XML-based Excel spreadsheet."""
    from scanner import get_freshness, get_match_score

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = scan_time or now.strftime("%I:%M %p")
    total_scanned = len(all_jobs) or scan_info.get("all_count", 0)

    # Hour-based scan slot
    hour = now.hour
    if hour < 11:
        scan_slot = "Morning (5 AM)"
    elif hour < 18:
        scan_slot = "Afternoon (12 PM)"
    else:
        scan_slot = "Night (8 PM)"

    # ---- Fresh Matches rows (Sheet 2) ----
    fresh_rows = []
    for i, j in enumerate(jobs):
        fresh = get_freshness(j.get("posted"))
        rec = get_recommendation(j.get("score", 0))
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
      <Cell><Data ss:Type="String">{_esc(j.get("url", ""))}</Data></Cell>
    </Row>''')

    # ---- Near Miss rows (added to All Jobs) ----
    # ---- All Jobs rows (Sheet 1) ----
    # Build lookup for scored jobs
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

    # ---- Daily Log row (Sheet 3) ----
    daily_row = f'''
    <Row>
      <Cell><Data ss:Type="String">{_esc(date_str)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(scan_slot)}</Data></Cell>
      <Cell><Data ss:Type="Number">{total_scanned}</Data></Cell>
      <Cell><Data ss:Type="Number">{len(jobs)}</Data></Cell>
      <Cell><Data ss:Type="String">{_esc(time_str)}</Data></Cell>
    </Row>'''

    dump_rows_str = "".join(dump_rows) if dump_rows else '<Row><Cell><Data ss:Type="String">No jobs fetched this scan.</Data></Cell></Row>'
    fresh_rows_str = "".join(fresh_rows) if fresh_rows else '<Row><Cell><Data ss:Type="String">No fresh matches this scan.</Data></Cell></Row>'

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

  <!-- Sheet 2: Fresh Matches (75-100% only) -->
  <Worksheet ss:Name="Fresh Matches">
    <Table>
      <Column ss:Width="40"/><Column ss:Width="150"/><Column ss:Width="280"/><Column ss:Width="100"/>
      <Column ss:Width="140"/><Column ss:Width="60"/><Column ss:Width="100"/><Column ss:Width="300"/><Column ss:Width="420"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Fresh Matches - {date_str} {time_str}</Data></Cell></Row>
      <Row><Cell><Data ss:Type="String">Only jobs posted within 24 hours and matching 75-100%. Sorted by match score.</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">#</Data></Cell><Cell><Data ss:Type="String">Company</Data></Cell>
        <Cell><Data ss:Type="String">Role</Data></Cell>
        <Cell><Data ss:Type="String">Category</Data></Cell><Cell><Data ss:Type="String">Location</Data></Cell><Cell><Data ss:Type="String">Match</Data></Cell>
        <Cell><Data ss:Type="String">Freshness</Data></Cell><Cell><Data ss:Type="String">Recommendation</Data></Cell><Cell><Data ss:Type="String">Apply URL</Data></Cell>
      </Row>
      {fresh_rows_str}
    </Table>
  </Worksheet>

  <!-- Sheet 3: Daily Log -->
  <Worksheet ss:Name="Daily Log">
    <Table>
      <Column ss:Width="120"/><Column ss:Width="160"/><Column ss:Width="100"/><Column ss:Width="120"/><Column ss:Width="100"/>
      <Row ss:StyleID="title"><Cell><Data ss:Type="String">Daily Scan Log</Data></Cell></Row>
      <Row ss:StyleID="header">
        <Cell><Data ss:Type="String">Date</Data></Cell><Cell><Data ss:Type="String">Scan Slot</Data></Cell>
        <Cell><Data ss:Type="String">Total Scanned</Data></Cell><Cell><Data ss:Type="String">Fresh Matches</Data></Cell><Cell><Data ss:Type="String">Time (UTC)</Data></Cell>
      </Row>
      {daily_row}
    </Table>
  </Worksheet>
</Workbook>'''
