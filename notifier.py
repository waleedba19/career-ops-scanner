"""
CareerOps Notifier — Telegram + Email (Brevo)
Same formats as the original Cloudflare Worker.
"""

import base64
import html as html_mod
import os
import re
from datetime import datetime, timezone

import aiohttp


def strip_html(html_text: str) -> str:
    """Remove HTML tags, decode entities, return clean text."""
    if not html_text:
        return ""
    text = str(html_text)
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID", "")
BREVO_KEY = os.getenv("BREVO_API_KEY", "")
TO_EMAIL = os.getenv("TO_EMAIL", "")

# ---------------------------------------------------------------------------
# Helpers — same as JS worker
# ---------------------------------------------------------------------------

SCAN_LABELS = [
    {"time": "07:00", "label": "Morning Intel", "emoji": "\u2600\ufe0f"},
    {"time": "14:00", "label": "Afternoon Briefing", "emoji": "\U0001f4cb"},
    {"time": "22:00", "label": "Night Digest", "emoji": "\U0001f319"},
]


def get_scan_label() -> dict:
    h = datetime.now(timezone.utc).hour
    if h < 11:
        return SCAN_LABELS[0]
    if h < 18:
        return SCAN_LABELS[1]
    return SCAN_LABELS[2]


def next_scan_time() -> str:
    h = datetime.now(timezone.utc).hour
    if h < 5:
        return "05:00"
    if h < 12:
        return "12:00"
    if h < 20:
        return "20:00"
    return "05:00"


def get_recommendation(score: int) -> str:
    if score >= 90:
        return "STRONG MATCH - Clear fit with your CV. We recommend applying."
    if score >= 80:
        return "GOOD MATCH - Strong overlap with your profile. We recommend reviewing and applying."
    return "MODERATE MATCH - Review job requirements before applying."


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _esc_xml(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------------------
# Card formatting — same as JS
# ---------------------------------------------------------------------------


def format_card(job: dict, index: int) -> str:
    from scanner import get_freshness
    fresh = get_freshness(job.get("posted"))
    salary = job.get("salary") or "Not specified"
    rec = get_recommendation(job.get("score", 0))
    lines = [
        f"{index + 1}. \U0001f525 BEST TO APPLY RIGHT NOW",
        f"   Field: {job.get('category', '')}",
        f"   Pay: {salary}",
        f"   Age: {fresh['label']}",
        f"   Fit score: {job.get('score', 0)}%",
        f"   Recommendation: {rec}",
        f"   Source site: {job.get('source', '')}",
        f"   Apply: {job.get('url', '')}",
    ]
    why = job.get("why", [])
    if why:
        lines.append(f"   Why this fits: {', '.join(why)}")
    ai = job.get("ai_insight", "")
    if ai:
        lines.append(f"   AI Insight: {ai}")
    desc = job.get("description", "")
    if desc:
        lines.append(f"   Description: {strip_html(desc)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------


def build_telegram(jobs: list, scan_info: dict, stats: dict) -> str:
    label = get_scan_label()
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg = f"{label['emoji']} {label['label']} \u2014 {date}\n"
    msg += "CAREEROPS SERVICES \u2014 Personal Job Search Assistant\n"
    msg += "_" * 32 + "\n\n"

    if len(jobs) == 0:
        msg += "\u2705 0 New Matches Found\n"
        msg += "No new position passed every filter this cycle (75%+ match with your CV, posted within 24 hours, open to worldwide applicants, no visa or residency restrictions).\n"
        all_count = scan_info.get("all_count", 0)
        fresh_count = scan_info.get("fresh_count", 0)
        msg += f"For full transparency: of {all_count:,} listings reviewed, {fresh_count} were posted within the last 24 hours \u2014 and none met every gate.\n"
        msg += "We are keeping the market under constant watch for you. If anything qualifies, we will send it to you right away with its full details and the Excel report.\n\n"
    else:
        msg += f"\u2705 {len(jobs)} New Match{'es' if len(jobs) != 1 else ''} Found\n"
        msg += "_" * 32 + "\n\n"
        for i, j in enumerate(jobs):
            msg += format_card(j, i) + "\n\n"
        msg += "_" * 32 + "\n\n"
        msg += "Full details for each role \u2014 location, salary, why it fits your CV and how to apply \u2014 are in the accompanying email and the attached Excel report.\n\n"

    near_all = scan_info.get("near_misses", [])
    if near_all:
        msg += "Additional positions close to your profile (50-74%, below your 75% line \u2014 your decision):\n"
        for j in near_all[:5]:
            from scanner import get_freshness
            fresh = get_freshness(j.get("posted"))
            salary = j.get("salary") or "Not specified"
            msg += f"\u2022 [{j.get('score', 0)}%] {j.get('title', '')} \u2014 {j.get('company', '')}"
            if salary and salary != "Not specified":
                msg += f" \xB7 \U0001f4b0 {salary}"
            msg += "\n"
            msg += f"  \U0001f4cd {j.get('location', 'Remote') or 'Remote'} \xB7 \u23f1 {fresh['label']}\n"
            msg += f"  \U0001f517 Review: {j.get('url', '')}\n"

    msg += "About the workbook: the attached Excel file contains 3 sheets \u2014 All Jobs (full dump), Fresh Matches (75-100% only), and Daily Log.\n\n"
    msg += f"The next scan is at {next_scan_time()} today.\n\n"
    msg += "Best regards,\nCareerOps Services \u2014 your personal job search assistant."
    return msg


async def send_telegram(text: str) -> bool:
    if not TG_TOKEN or not TG_CHAT:
        print("Telegram skipped: not configured")
        return False
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    # Split into chunks of 4000 chars at line breaks
    chunks = []
    remaining = text
    while len(remaining) > 4000:
        split_at = remaining.rfind("\n", 0, 4000)
        chunks.append(remaining[: split_at if split_at > 0 else 4000])
        remaining = remaining[split_at + 1 :] if split_at > 0 else remaining[4000:]
    chunks.append(remaining)

    ok = True
    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            try:
                payload = {"chat_id": TG_CHAT, "text": chunk}
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        print(f"Telegram HTTP {resp.status}: {body}")
                        ok = False
                    else:
                        print("Telegram message sent")
            except Exception as e:
                print(f"Telegram error: {e}")
                ok = False
    return ok


# ---------------------------------------------------------------------------
# Email — Brevo API
# ---------------------------------------------------------------------------


def build_email(jobs: list, scan_info: dict, stats: dict) -> dict:
    date_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    time_str = datetime.now(timezone.utc).strftime("%I:%M %p UTC")
    scan_num = stats.get("total_scans", 0)
    all_count = scan_info.get("all_count", 0)
    source_count = scan_info.get("source_count", 0)
    fresh_count = scan_info.get("fresh_count", 0)
    near_all = scan_info.get("near_misses", [])

    def job_card(j, i):
        from scanner import get_freshness
        fresh = get_freshness(j.get("posted"))
        salary = j.get("salary") or "Not specified"
        rec = get_recommendation(j.get("score", 0))
        why_html = ""
        if j.get("why"):
            why_html = f'<tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Why this fits</td><td style="color:#111;vertical-align:top">{_esc(", ".join(j["why"]))}</td></tr>'
        ai_html = ""
        if j.get("ai_insight"):
            ai_html = f'<tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">AI Insight</td><td style="color:#111;vertical-align:top">{_esc(j["ai_insight"])}</td></tr>'
        return f'''
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #d0d0d0;border-radius:6px;margin:14px 0;font-family:Arial,Helvetica,sans-serif">
        <tr><td style="padding:14px 16px 10px;border-bottom:1px solid #e0e0e0">
          <span style="font-size:18px;font-weight:bold;color:#0d1b2a">\U0001f525 BEST TO APPLY RIGHT NOW</span>
        </td></tr>
        <tr><td style="padding:10px 16px">
          <table width="100%" cellpadding="3" cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333">
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Field</td><td style="color:#111;vertical-align:top">{_esc(j.get("category", ""))}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Pay</td><td style="color:#111;vertical-align:top">{_esc(salary)}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Age</td><td style="color:#111;vertical-align:top">{_esc(fresh["label"])}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Fit score</td><td style="color:#111;vertical-align:top">{j.get("score", 0)}%</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Recommendation</td><td style="color:#111;vertical-align:top">{_esc(rec)}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Source site</td><td style="color:#111;vertical-align:top">{_esc(j.get("source", ""))}</td></tr>
            {why_html}
            {ai_html}
          </table>
        </td></tr>
        <tr><td style="padding:0 16px 12px">
          <a href="{_esc(j.get('url', ''))}" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#1a5fb4;text-decoration:underline;font-weight:bold">Apply for this position \u2192</a>
        </td></tr>
        {f'<tr><td style="padding:0 16px 12px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;line-height:1.6"><b>Description:</b> {_esc(strip_html(j.get("description", "")))}</td></tr>' if j.get("description") else ''}
      </table>'''

    def near_card(j, i):
        from scanner import get_freshness
        fresh = get_freshness(j.get("posted"))
        salary = j.get("salary") or "Not specified"
        rec = get_recommendation(j.get("score", 0))
        return f'''
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e0e0e0;border-radius:6px;margin:10px 0;font-family:Arial,Helvetica,sans-serif">
        <tr><td style="padding:12px 16px 8px;border-bottom:1px solid #e0e0e0">
          <span style="font-size:15px;font-weight:bold;color:#555">Near Miss \u2014 {_esc(j.get("title", ""))}</span>
          <span style="font-weight:normal;color:#666;font-size:12px;margin-left:8px">{_esc(j.get("company", ""))}</span>
        </td></tr>
        <tr><td style="padding:8px 16px">
          <table width="100%" cellpadding="3" cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333">
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Field</td><td style="color:#111;vertical-align:top">{_esc(j.get("category", ""))}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Pay</td><td style="color:#111;vertical-align:top">{_esc(salary)}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Age</td><td style="color:#111;vertical-align:top">{_esc(fresh["label"])}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Fit score</td><td style="color:#111;vertical-align:top">{j.get("score", 0)}%</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Recommendation</td><td style="color:#111;vertical-align:top">{_esc(rec)}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Source site</td><td style="color:#111;vertical-align:top">{_esc(j.get("source", ""))}</td></tr>
            {f'<tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Why this fits</td><td style="color:#111;vertical-align:top">{_esc(", ".join(j.get("why", [])))}</td></tr>' if j.get("why") else ''}
          </table>
        </td></tr>
        <tr><td style="padding:0 16px 10px">
          <a href="{_esc(j.get('url', ''))}" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#666;text-decoration:underline">Review this position \u2192</a>
        </td></tr>
        {f'<tr><td style="padding:0 16px 10px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#555;line-height:1.6"><b>Description:</b> {_esc(strip_html(j.get("description", "")))}</td></tr>' if j.get("description") else ''}
      </table>'''

    # Build jobs HTML
    if not jobs:
        jobs_html = f'''<p style="margin:14px 0;font-size:13px;color:#333;line-height:1.6">
        \u2705 <b>0 New Matches Found</b> \u2014 No new position passed every filter (75%+ match with your profile, posted within 24 hours, open to worldwide applicants, no visa or residency restrictions).
        For full transparency: of {all_count:,} job listings reviewed across {source_count} sources, only {fresh_count} were posted within the last 24 hours \u2014 and none met every gate.
        We will keep watching the market for you; the next scan runs automatically at the next scheduled slot and any qualifying role reaches you within hours of being posted.</p>'''
    else:
        jobs_html = "".join(job_card(j, i) for i, j in enumerate(jobs))

    near_html = ""
    if near_all:
        near_html = f'<p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;color:#111;border-bottom:1px solid #d0d0d0;padding:16px 0 6px;margin-top:18px">Additional positions close to your profile (below your 75% line \u2014 your decision)</p>'
        near_html += '<p style="margin:8px 0 0;font-size:12px;color:#555">These roles matched your profile keywords but scored below your strict 75% threshold. We list them so nothing slips past you \u2014 review and decide yourself.</p>'
        near_html += "".join(near_card(j, i) for i, j in enumerate(near_all[:6]))

    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f7f7f7;font-family:Arial,Helvetica,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f7f7f7">
    <tr><td align="center" style="padding:24px 12px">
      <table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e0e0e0">
        <tr><td style="padding:22px 28px 10px;border-bottom:2px solid #111">
          <span style="font-family:Arial,Helvetica,sans-serif;font-size:20px;font-weight:bold;color:#111;letter-spacing:1px">CAREEROPS SERVICES</span>
          <span style="font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#888;letter-spacing:2px;margin-left:10px">PERSONAL JOB SEARCH ASSISTANT</span>
        </td></tr>
        <tr><td style="padding:18px 28px 0">
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#555;margin:0">{_esc(date_str)} \xB7 {_esc(time_str)} \xB7 Scan #{scan_num}</p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:16px;color:#111;margin:14px 0 0;line-height:1.6">
            This cycle we reviewed <b>{all_count:,} job listings</b> across {source_count} sources.
            <b>{len(jobs)} new match{'es' if len(jobs) != 1 else ''}{f', plus {len(near_all)} close position{"s" if len(near_all) != 1 else ""} for your review and consideration' if near_all else ''}</b>.
          </p>
        </td></tr>
        <tr><td style="padding:6px 28px 20px">
          {jobs_html}
          {near_html}
        </td></tr>
        <tr><td style="padding:16px 28px 20px;border-top:1px solid #e0e0e0">
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;margin:0;line-height:1.6">
            About the workbook: the attached Excel file contains 3 sheets \u2014 All Jobs (full dump), Fresh Matches (75-100% only), and Daily Log.
          </p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;margin:16px 0 0;line-height:1.6">
            The next scan is at <b>{next_scan_time()} today</b>.
          </p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;margin:16px 0 0;line-height:1.6">
            Best regards,<br>
            <b>CareerOps Services</b><br>
            <span style="font-size:12px;color:#888">Your personal job search assistant \u2014 matching is algorithmic; always review each posting before applying.</span>
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>'''

    # Text body
    text = "CAREEROPS SERVICES \u2014 Personal Job Search Assistant\n"
    text += f"{date_str} \xB7 {time_str} \xB7 Scan #{scan_num}\n\n"
    text += f"This cycle we reviewed {all_count:,} job listings across {source_count} sources and found {len(jobs)} new match{'es' if len(jobs) != 1 else ''}{f', plus {len(near_all)} close position{"s" if len(near_all) != 1 else ""} for your review and consideration' if near_all else ''}.\n\n"

    if not jobs:
        text += "\u2705 0 New Matches Found\n"
        text += f"No new position passed every filter (75%+ match, posted within 24h, open to worldwide applicants, no visa or residency restrictions). Of those reviewed, only {fresh_count} were posted within the last 24 hours \u2014 and none met every gate. We will keep watching.\n\n"
    else:
        for i, j in enumerate(jobs):
            text += format_card(j, i) + "\n\n"

    if near_all:
        text += "\nADDITIONAL POSITIONS CLOSE TO YOUR PROFILE (below your 75% line \u2014 your decision):\n"
        for j in near_all[:6]:
            from scanner import get_freshness
            fresh = get_freshness(j.get("posted"))
            salary = j.get("salary") or "Not specified"
            rec = get_recommendation(j.get("score", 0))
            text += f"[{j.get('score', 0)}%] {j.get('title', '')} \u2014 {j.get('company', '')}\n"
            text += f"   Field: {j.get('category', '')} \xB7 Pay: {salary} \xB7 Age: {fresh['label']} \xB7 Fit score: {j.get('score', 0)}%\n"
            text += f"   Recommendation: {rec}\n"
            text += f"   Source site: {j.get('source', '')}\n"
            text += f"   Review: {j.get('url', '')}\n\n"

    text += "About the workbook: the attached Excel file contains 3 sheets \u2014 All Jobs (full dump), Fresh Matches (75-100% only), and Daily Log.\n\n"
    text += f"The next scan is at {next_scan_time()} today.\n\n"
    text += "Best regards,\nCareerOps Services \u2014 your personal job search assistant.\n"

    return {"html": html, "text": text}


async def send_email(subject: str, text_body: str, html_body: str, excel_path: str | None = None) -> bool:
    if not BREVO_KEY or not TO_EMAIL:
        print("Email skipped: no BREVO_API_KEY or TO_EMAIL configured")
        return False

    payload = {
        "sender": {"email": "waleedzydeco19@gmail.com", "name": "Waleed Zedco"},
        "to": [{"email": TO_EMAIL}],
        "subject": subject,
        "textContent": text_body,
        "htmlContent": html_body,
    }

    # Add Excel attachment if available and under 5MB
    if excel_path:
        try:
            import os
            if os.path.exists(excel_path) and os.path.getsize(excel_path) < 5_000_000:
                content = open(excel_path, "rb").read()
                b64 = base64.b64encode(content).decode()
                filename = os.path.basename(excel_path)
                payload["attachment"] = [{"name": filename, "content": b64}]
        except Exception as e:
            print(f"Excel attachment failed (email still sent): {e}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.brevo.com/v3/smtp/email",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "api-key": BREVO_KEY,
                },
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                data = await resp.text()
                print(f"Brevo response: {resp.status} {data}")
                if resp.status not in (200, 201):
                    print(f"Brevo FAILED: {resp.status} - {data}")
                    return False
                return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

