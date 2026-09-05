"""
CareerOps Notifier — Professional Telegram + Email (Brevo)
Redesigned for clean, professional presentation.
"""

import base64
import html as html_mod
import os
import re
import zlib
from datetime import datetime, timedelta, timezone

import aiohttp

# ---------------------------------------------------------------------------
# Libya live time (Africa/Tripoli, UTC+2 — no DST since 2013)
# Every user-facing date/time in messages, email and Excel uses Libya time,
# never raw UTC, so a 00:11 scan in Tripoli reads as 00:11 on the 6th, not
# 22:11 on the 5th.
# ---------------------------------------------------------------------------

LIBYA_TZ = timezone(timedelta(hours=2))  # Africa/Tripoli


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_libya() -> datetime:
    """Current time in Libya (Africa/Tripoli, UTC+2)."""
    return datetime.now(LIBYA_TZ)


def libya_time_str() -> str:
    """'00:11 AM Libya (22:11 UTC)' — Libya-first, UTC in parentheses."""
    lib = now_libya()
    utc = now_utc()
    return f"{lib.strftime('%I:%M %p')} Libya ({utc.strftime('%H:%M')} UTC)"


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
# Human-live message variety — every run reads differently, no two identical
# ---------------------------------------------------------------------------

# 3 greetings per scan slot; rotate by (hour + minute) % 3 so back-to-back
# manual runs in the same slot read differently while staying natural.
HUMAN_GREETINGS = {
    "Morning Intel": (
        "Good morning — I ran the early shift before the market woke up, so today's freshest posts are already at the top of this.",
        "Morning — the overnight queue is sorted and the first wave of new postings is in your hands.",
        "Hi — early shift done. I went through the new posts so you can start the day with a clear list, not a pile.",
    ),
    "Afternoon Briefing": (
        "Afternoon — the European boards refreshed this hour, so I ran the mid-day pass and sorted what actually matters.",
        "Hey — halfway through the day. I chased down everything posted since the morning scan.",
        "Mid-day check: I pulled the fresh European wave before it got buried under re-postings.",
    ),
    "Night Digest": (
        "Late check — I stayed up so you don't have to.",
        "Night shift is running — I picked through the evening posts while you rest.",
        "Quiet-hours digest: I did the late sweep so your morning starts clear.",
    ),
}

# 4 closings; rotate by (minute + second) % 4 so they change nearly every run.
HUMAN_CLOSINGS = (
    "Take care — I'll keep the boards under watch.",
    "See you at the next scan; I've got the watch from here.",
    "You've got the details, I've got the monitoring.",
    "Rest easy — the next cycle is already queued.",
)

# 3 zero-match notes; pick by a stable hash of (date + scan number) so the
# wording changes per run but is reproducible for the same run.
NO_MATCH_NOTES = (
    "No new position passed all four gates this cycle. I checked {all_count:,} listings — {fresh_count} were fresh — and none cleared the bar. I'll flag you the moment one does; no near-miss noise.",
    "Quiet cycle: {all_count:,} reviewed, {fresh_count} fresh, zero that cleared every gate. The filters are doing their job — when something real shows up, you'll hear from me first.",
    "Nothing new passed the full gate this time ({all_count:,} reviewed, {fresh_count} fresh). Rather than send you half-fits, I'm holding the line — the next qualifying role lands here the moment it does.",
)


def pick_greeting(label: dict) -> str:
    now = now_libya()
    pool = HUMAN_GREETINGS.get(label["label"], HUMAN_GREETINGS["Morning Intel"])
    return pool[(now.hour + now.minute) % len(pool)]


def pick_closing() -> str:
    now = now_libya()
    return HUMAN_CLOSINGS[(now.minute + now.second) % len(HUMAN_CLOSINGS)]


def pick_no_match_note(date: str, scan_num: int, all_count: int, fresh_count: int) -> str:
    idx = zlib.crc32(f"{date}-{scan_num}".encode()) % len(NO_MATCH_NOTES)
    return NO_MATCH_NOTES[idx].format(all_count=all_count, fresh_count=fresh_count)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCAN_LABELS = [
    {"time": "07:00", "label": "Morning Intel", "emoji": "\u2600\ufe0f"},
    {"time": "15:00", "label": "Afternoon Briefing", "emoji": "\U0001f4cb"},
    {"time": "22:00", "label": "Night Digest", "emoji": "\U0001f319"},
]


def get_scan_label() -> dict:
    """Scan label by Libya local hour (runs at 07:00 / 15:00 / 22:00 Libya)."""
    h = now_libya().hour
    if h < 11:
        return SCAN_LABELS[0]
    if h < 18:
        return SCAN_LABELS[1]
    return SCAN_LABELS[2]


def next_scan_time() -> tuple[str, bool]:
    """Next scheduled scan in Libya time → (time_str, is_tomorrow)."""
    h = now_libya().hour
    if h < 7:
        return "07:00", False
    if h < 15:
        return "15:00", False
    if h < 22:
        return "22:00", False
    return "07:00", True


def next_scan_line() -> str:
    t, tomorrow = next_scan_time()
    return f"Next scan: {t} Libya ({'tomorrow morning' if tomorrow else 'today'})"


def get_recommendation(score: int) -> str:
    if score >= 90:
        return "\u2b50 STRONG MATCH"
    if score >= 80:
        return "\u2705 GOOD MATCH"
    return "\U0001f50d REVIEW"


def get_verdict_emoji(verdict: str) -> str:
    """Get emoji for AI verdict."""
    if not verdict:
        return ""
    verdict_lower = verdict.lower()
    if "strong" in verdict_lower:
        return "\U0001f525"
    if "good" in verdict_lower:
        return "\u2705"
    if "moderate" in verdict_lower:
        return "\U0001f4a1"
    if "weak" in verdict_lower or "poor" in verdict_lower:
        return "\u26a0\ufe0f"
    return ""


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------------------
# Professional Telegram Card Format
# ---------------------------------------------------------------------------


def format_job_card(job: dict, index: int) -> str:
    """Format a single job as a clean, professional Telegram card — now with free intel (email, urgency, desperation)."""
    from scanner import get_freshness
    fresh = get_freshness(job.get("posted"))
    salary = job.get("salary") or "Not specified"
    rec = get_recommendation(job.get("score", 0))
    source = job.get("source", "unknown")
    
    lines = []
    # Header — sort key is now opportunity if present
    opp = job.get("opportunity_score")
    if opp and opp != job.get("score",0):
        lines.append(f"\U0001f4cb {index + 1}. {rec}  (Opp {opp}% | Match {job.get('score',0)}%)")
    else:
        lines.append(f"\U0001f4cb {index + 1}. {rec}")
    lines.append("")
    lines.append(f"\U0001f4bc {job.get('title', 'Unknown')}")
    lines.append(f"\U0001f3e2 {job.get('company', 'Unknown')}")
    lines.append("")
    lines.append(f"\U0001f4cd Location: {job.get('location', 'Remote')}")
    lines.append(f"\U0001f4b0 Pay: {salary}")
    lines.append(f"\u23f1 Posted: {fresh['label']}")
    lines.append(f"\U0001f3af Fit Score: {job.get('score', 0)}%")
    if opp:
        lines.append(f"\U0001f680 Opportunity: {opp}%")
    lines.append(f"\U0001f4c2 Source: {source}")
    # Free intel
    urgency = job.get("urgency_score",0)
    desperation = job.get("desperation_index",0)
    if urgency >= 20:
        lines.append(f"\u23f0 Urgency: {urgency}/100 {'🔥 URGENT' if urgency>=30 else ''}")
    if desperation >= 30:
        lines.append(f"\U0001f4a5 Desperation: {desperation}/100 {'💥 DESPERATE' if desperation>=50 else ''}")
    hiring_email = job.get("hiring_email","")
    if hiring_email:
        ver = "✓ verified" if job.get("email_verified") else "guess" if job.get("email_guessed") else "found"
        lines.append(f"\u2709\ufe0f Hiring Email: {hiring_email} ({ver})")
    pain = job.get("pain_points","")
    if pain:
        lines.append(f"\U0001f50d Pain: {pain[:120]}")
    lines.append("")
    ai_verdict = job.get("ai_verdict", "")
    ai_score = job.get("ai_overall_score", 0)
    if ai_verdict:
        emoji = get_verdict_emoji(ai_verdict)
        lines.append(f"{emoji} AI Assessment: {ai_verdict} ({ai_score}/100)")
        ai_summary = job.get("ai_insight", "")
        if ai_summary:
            lines.append(f"\U0001f4ac {ai_summary[:150]}")
        lines.append("")
    why = job.get("why", [])
    if why:
        lines.append(f"\U0001f517 Why it fits: {', '.join(why[:3])}")
    lines.append(f"\U0001f517 Apply: {job.get('url', '')}")
    return "\n".join(lines)


def format_near_miss_card(job: dict, index: int) -> str:
    """Format a near-miss job as a compact card."""
    from scanner import get_freshness
    fresh = get_freshness(job.get("posted"))
    salary = job.get("salary") or ""
    
    lines = []
    lines.append(f"\u2022 [{job.get('score', 0)}%] {job.get('title', '')} — {job.get('company', '')}")
    if salary and salary != "Not specified":
        lines.append(f"  \U0001f4b0 {salary}")
    lines.append(f"  \U0001f4cd {job.get('location', 'Remote') or 'Remote'} \xB7 \u23f1 {fresh['label']}")
    lines.append(f"  \U0001f517 Review: {job.get('url', '')}")
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Professional Telegram Message Builder
# ---------------------------------------------------------------------------


def build_telegram(jobs: list, scan_info: dict, stats: dict) -> str:
    """Build a clean, professional Telegram message with evolution intelligence."""
    from evolution_tracker import get_evolution_summary
    from source_manager import get_source_report
    from excel_generator import load_applications, load_fresh_history
    from learning_module import get_learning_insights
    
    label = get_scan_label()
    now = now_libya()
    date = now.strftime("%Y-%m-%d")
    date_human = now.strftime("%A, %B %d, %Y")
    time_str = f"{now.strftime('%I:%M %p')} Libya ({now_utc().strftime('%H:%M')} UTC)"
    scan_num = stats.get("total_scans", 0)
    all_count = scan_info.get("all_count", 0)
    source_count = scan_info.get("source_count", 0)
    fresh_count = scan_info.get("fresh_count", 0)
    near_all = scan_info.get("near_misses", [])
    
    msg = ""
    
    # Live header — Libya date + time, then a rotating human greeting
    msg += f"{label['emoji']} {label['label']} \u2014 {date_human} \u2014 {now.strftime('%I:%M %p')} Libya\n"
    msg += f"{pick_greeting(label)}\n"
    msg += "\n"
    msg += "\U0001f4bc CAREEROPS SERVICES\n"
    msg += "AI-Powered Job Search Intelligence\n"
    msg += "\u2500" * 28 + "\n"
    msg += "\n"
    
    # Evolution summary (the "brain" learns)
    evolution = get_evolution_summary()
    if evolution and evolution != "🧠 First scan — building memory...":
        msg += f"{evolution}\n"
        msg += "\u2500" * 28 + "\n"
        msg += "\n"
    
    # Learning insights (application feedback)
    learning = get_learning_insights()
    if learning.get("total_applied", 0) > 0:
        msg += "\U0001f4a1 LEARNING INSIGHTS\n"
        msg += f"Applied: {learning['total_applied']} jobs\n"
        msg += f"Interview rate: {learning.get('acceptance_rate', 0)}%\n"
        if learning.get("top_skills"):
            top_skill = learning["top_skills"][0][0]
            msg += f"Best category: {top_skill}\n"
        msg += "\u2500" * 28 + "\n"
        msg += "\n"
    
    # Summary line
    msg += f"Scan #{scan_num} \xB7 {time_str}\n"
    msg += f"Reviewed {all_count:,} jobs across {source_count} sources\n"
    msg += "\n"
    
    # ---- Check for unapplied jobs reminder (marked red) ----
    try:
        apps = load_applications()
        all_fresh = load_fresh_history()
        unapplied = [j for j in all_fresh if j.get("url") and j["url"] not in apps]
        if unapplied:
            msg += f"\U0001f534 UNAPPLIED JOBS: {len(unapplied)} pending — apply before they expire!\n"
            for j in unapplied[:5]:
                title = j.get('title', 'Unknown')
                company = j.get('company', '')
                score = j.get('score', 0)
                msg += f"\U0001f534 [{score}%] {title} — {company}\n"
                msg += f"   {j.get('url', '')}\n"
            if len(unapplied) > 5:
                msg += f"... and {len(unapplied) - 5} more — check your Excel (red rows)\n"
            msg += "\u2500" * 28 + "\n"
            msg += "\n"
    except Exception:
        pass
    
    if len(jobs) == 0:
        # No matches — rotating human note instead of the same template
        msg += "\u2705 0 New Matches Found\n"
        msg += "\n"
        msg += pick_no_match_note(date, scan_num, all_count, fresh_count) + "\n"
        msg += "\n"
        msg += "Gates: 75%+ CV match \u00b7 posted within 30 min \u00b7 open worldwide \u00b7 no visa/residency restrictions.\n"
    else:
        # Matches found
        msg += f"\u2705 {len(jobs)} New Match{'es' if len(jobs) != 1 else ''} Found\n"
        msg += "\u2500" * 28 + "\n"
        msg += "\n"
        
        # Job cards
        for i, j in enumerate(jobs):
            msg += format_job_card(j, i) + "\n\n"
        
        msg += "\u2500" * 28 + "\n"
        msg += "\n"
        
        # Near misses section
        if near_all:
            msg += "\U0001f4a1 Additional Close Matches (50-74%)\n"
            msg += "Below your 75% threshold \u2014 review at your discretion:\n"
            msg += "\n"
            for j in near_all[:5]:
                msg += format_near_miss_card(j, 0) + "\n"
            msg += "\n"
        
        msg += "Full details in email + Excel attachment.\n"
    
    # Source intelligence
    source_report = get_source_report()
    if source_report and "No source data" not in source_report:
        msg += "\n"
        msg += "\u2500" * 28 + "\n"
        msg += source_report + "\n"
    
    # Human sign-off — rotating closing, Libya next-scan time
    msg += "\n"
    msg += "\u2500" * 28 + "\n"
    msg += f"{next_scan_line()}\n"
    msg += f"{pick_closing()}\n"
    msg += "\n"
    msg += "CareerOps Services \u2014 AI Job Search Intelligence\n"
    
    return msg


# ---------------------------------------------------------------------------
# Telegram Send
# ---------------------------------------------------------------------------


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
    """Build professional email with evolution intelligence."""
    from evolution_tracker import get_evolution_summary
    from source_manager import get_source_report
    
    now = now_libya()
    date_str = now.strftime("%A, %B %d, %Y")
    date_iso = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M %p Libya")
    greeting = pick_greeting(get_scan_label())
    closing = pick_closing()
    scan_num = stats.get("total_scans", 0)
    all_count = scan_info.get("all_count", 0)
    source_count = scan_info.get("source_count", 0)
    fresh_count = scan_info.get("fresh_count", 0)
    near_all = scan_info.get("near_misses", [])
    
    # Get evolution data
    evolution = get_evolution_summary()
    source_report = get_source_report()
    has_evolution = evolution and "First scan" not in evolution

    def job_card_html(j, i):
        from scanner import get_freshness
        fresh = get_freshness(j.get("posted"))
        salary = j.get("salary") or "Not specified"
        rec = get_recommendation(j.get("score", 0))
        # Deep intel (free forever)
        hiring_email = j.get("hiring_email","")
        urgency = j.get("urgency_score",0)
        desperation = j.get("desperation_index",0)
        opportunity = j.get("opportunity_score","")
        pain = j.get("pain_points","")
        email_html = f'<tr><td width="110" style="font-weight:bold;color:#0a7a0a;vertical-align:top">Hiring Email</td><td style="color:#111;vertical-align:top"><a href="mailto:{_esc(hiring_email)}" style="color:#0a7a0a;font-weight:bold">{_esc(hiring_email)}</a> {"✓ verified" if j.get("email_verified") else "(guess)" if j.get("email_guessed") else ""}</td></tr>' if hiring_email else ""
        urgency_html = f'<tr><td width="110" style="font-weight:bold;color:#b91c1c;vertical-align:top">Urgency</td><td style="color:#b91c1c;vertical-align:top;font-weight:bold">{urgency}/100 {"🔥 URGENT" if urgency>=30 else ""}</td></tr>' if urgency>=20 else ""
        desp_html = f'<tr><td width="110" style="font-weight:bold;color:#7c3aed;vertical-align:top">Desperation</td><td style="color:#7c3aed;vertical-align:top;font-weight:bold">{desperation}/100 {"💥 DESPERATE" if desperation>=50 else ""}</td></tr>' if desperation>=30 else ""
        opp_html = f'<tr><td width="110" style="font-weight:bold;color:#0369a1;vertical-align:top">Opportunity</td><td style="color:#0369a1;vertical-align:top;font-weight:bold">{opportunity}% (combined)</td></tr>' if opportunity and opportunity != j.get("score",0) else ""
        pain_html = f'<tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Pain Point</td><td style="color:#111;vertical-align:top;font-style:italic">{_esc(pain)}</td></tr>' if pain else ""
        # AI scoring
        ai_verdict = j.get("ai_verdict", "")
        ai_score = j.get("ai_overall_score", 0)
        ai_summary = j.get("ai_insight", "")
        
        ai_html = ""
        if ai_verdict:
            emoji = get_verdict_emoji(ai_verdict)
            ai_html = f'''
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">AI Assessment</td><td style="color:#111;vertical-align:top">{emoji} {ai_verdict} ({ai_score}/100)</td></tr>
            '''
            if ai_summary:
                ai_html += f'''
                <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">AI Summary</td><td style="color:#111;vertical-align:top;font-style:italic">{_esc(ai_summary[:200])}</td></tr>
                '''
        
        why_html = ""
        if j.get("why"):
            why_html = f'<tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Why this fits</td><td style="color:#111;vertical-align:top">{_esc(", ".join(j["why"]))}</td></tr>'
        # inject deep intel rows will be added via email_html etc
        
        return f'''
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #d0d0d0;border-radius:6px;margin:14px 0;font-family:Arial,Helvetica,sans-serif">
        <tr><td style="padding:14px 16px 10px;border-bottom:1px solid #e0e0e0">
          <span style="font-size:18px;font-weight:bold;color:#0d1b2a">{rec} — {i+1}</span>
        </td></tr>
        <tr><td style="padding:10px 16px">
          <table width="100%" cellpadding="3" cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333">
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Position</td><td style="color:#111;vertical-align:top;font-weight:bold">{_esc(j.get("title", ""))}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Company</td><td style="color:#111;vertical-align:top">{_esc(j.get("company", ""))}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Location</td><td style="color:#111;vertical-align:top">{_esc(j.get("location", "Remote"))}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Pay</td><td style="color:#111;vertical-align:top">{_esc(salary)}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Posted</td><td style="color:#111;vertical-align:top">{_esc(fresh["label"])}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Fit Score</td><td style="color:#111;vertical-align:top">{j.get("score", 0)}%</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Source</td><td style="color:#111;vertical-align:top">{_esc(j.get("source", ""))}</td></tr>
            {email_html}
            {urgency_html}
            {desp_html}
            {opp_html}
            {pain_html}
            {ai_html}
            {why_html}
          </table>
        </td></tr>
        <tr><td style="padding:0 16px 12px">
          <a href="{_esc(j.get('url', ''))}" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#1a5fb4;text-decoration:underline;font-weight:bold">Apply for this position \u2192</a>
        </td></tr>
        {f'<tr><td style="padding:0 16px 12px;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;line-height:1.6"><b>Description:</b> {_esc(strip_html(j.get("description", ""))[:500])}</td></tr>' if j.get("description") else ''}
      </table>'''

    def near_card_html(j, i):
        from scanner import get_freshness
        fresh = get_freshness(j.get("posted"))
        salary = j.get("salary") or "Not specified"
        return f'''
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e0e0e0;border-radius:6px;margin:10px 0;font-family:Arial,Helvetica,sans-serif">
        <tr><td style="padding:12px 16px 8px;border-bottom:1px solid #e0e0e0">
          <span style="font-size:15px;font-weight:bold;color:#555">{_esc(j.get("title", ""))}</span>
          <span style="font-weight:normal;color:#666;font-size:12px;margin-left:8px">{_esc(j.get("company", ""))}</span>
        </td></tr>
        <tr><td style="padding:8px 16px">
          <table width="100%" cellpadding="3" cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333">
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Score</td><td style="color:#111;vertical-align:top">{j.get("score", 0)}%</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Location</td><td style="color:#111;vertical-align:top">{_esc(j.get("location", "Remote"))}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Pay</td><td style="color:#111;vertical-align:top">{_esc(salary)}</td></tr>
            <tr><td width="110" style="font-weight:bold;color:#555;vertical-align:top">Posted</td><td style="color:#111;vertical-align:top">{_esc(fresh["label"])}</td></tr>
          </table>
        </td></tr>
        <tr><td style="padding:0 16px 10px">
          <a href="{_esc(j.get('url', ''))}" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#666;text-decoration:underline">Review this position \u2192</a>
        </td></tr>
      </table>'''

    # Build jobs HTML
    if not jobs:
        no_match_note = _esc(pick_no_match_note(date_iso, scan_num, all_count, fresh_count))
        jobs_html = f'''<p style="margin:14px 0;font-size:13px;color:#333;line-height:1.6">
        \u2705 <b>0 New Matches Found</b> \u2014 {no_match_note}
        Gates: 75%+ match with your profile \u00b7 posted within 30 minutes \u00b7 open to worldwide applicants \u00b7 no visa or residency restrictions.
        The next scan runs automatically at the next scheduled slot and any qualifying role reaches you within hours of being posted.</p>'''
    else:
        jobs_html = "".join(job_card_html(j, i) for i, j in enumerate(jobs))

    near_html = ""
    if near_all:
        near_html = f'<p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;color:#111;border-bottom:1px solid #d0d0d0;padding:16px 0 6px;margin-top:18px">Additional Close Matches (50-74%)</p>'
        near_html += '<p style="margin:8px 0 0;font-size:12px;color:#555">Below your 75% threshold \u2014 review at your discretion.</p>'
        near_html += "".join(near_card_html(j, i) for i, j in enumerate(near_all[:6]))

    # Unapplied jobs from previous scans — shown in red so they stand out
    unapplied_html = ""
    unapplied_text = ""
    try:
        from excel_generator import load_applications, load_fresh_history
        apps = load_applications()
        all_fresh = load_fresh_history()
        unapplied = [j for j in all_fresh if j.get("url") and j["url"] not in apps]
        if unapplied:
            unapplied_html = (
                '<p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:bold;'
                'color:#b91c1c;border-bottom:2px solid #dc2626;padding:16px 0 6px;margin-top:18px">'
                '\U0001f534 UNAPPLIED JOBS \u2014 {len} pending. Apply before they expire!</p>'
            ).format(len=len(unapplied))
            for j in unapplied[:5]:
                unapplied_html += f'''
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef2f2;border:1px solid #dc2626;border-radius:6px;margin:10px 0;font-family:Arial,Helvetica,sans-serif">
        <tr><td style="padding:12px 16px 8px;border-bottom:1px solid #fecaca">
          <span style="font-size:14px;font-weight:bold;color:#b91c1c">{_esc(j.get("title", ""))}</span>
          <span style="font-weight:normal;color:#991b1b;font-size:12px;margin-left:8px">{_esc(j.get("company", ""))} \u00b7 {j.get("score", 0)}%</span>
        </td></tr>
        <tr><td style="padding:0 16px 12px">
          <a href="{_esc(j.get('url', ''))}" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#b91c1c;text-decoration:underline;font-weight:bold">Apply now \u2192</a>
        </td></tr>
      </table>'''
            if len(unapplied) > 5:
                unapplied_html += f'<p style="font-size:12px;color:#b91c1c">... and {len(unapplied) - 5} more \u2014 all shown in red in the Excel sheet.</p>'
            unapplied_text = f"\U0001f534 UNAPPLIED JOBS: {len(unapplied)} pending — apply before they expire!\n\n"
            for j in unapplied[:5]:
                unapplied_text += f"\U0001f534 [{j.get('score', 0)}%] {j.get('title', '')} — {j.get('company', '')}\n"
                unapplied_text += f"   {j.get('url', '')}\n\n"
            if len(unapplied) > 5:
                unapplied_text += f"... and {len(unapplied) - 5} more — check your Excel (red rows).\n\n"
    except Exception:
        pass

    # Precompute suffix for job count message to avoid nested f-string issues
    suffix = f", plus {len(near_all)} close position{'s' if len(near_all) != 1 else ''} for your review" if near_all else ""

    # Build evolution section separately to avoid nested f-string syntax issues
    evolution_html = ""
    if has_evolution:
        source_html = ""
        if source_report and "No source data" not in source_report:
            source_html = f'<p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;color:#111;margin:16px 0 8px">\uD83D\uDCCA Source Performance</p><pre style="font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#333;margin:0;white-space:pre-wrap;line-height:1.6">{_esc(source_report)}</pre>'
        evolution_html = f'<tr><td style="padding:16px 28px 16px;border-top:1px solid #e0e0e0"><p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:bold;color:#111;margin:0 0 8px">\U0001f9e0 AI Intelligence Report</p><pre style="font-family:Arial,Helvetica,sans-serif;font-size:12px;color:#333;margin:0;white-space:pre-wrap;line-height:1.6">{_esc(evolution)}</pre>{source_html}</td></tr>'

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
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#333;margin:10px 0 0;line-height:1.6">{_esc(greeting)}</p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:16px;color:#111;margin:14px 0 0;line-height:1.6">
            This cycle we reviewed <b>{all_count:,} job listings</b> across {source_count} sources.
            <b>{len(jobs)} new match{'es' if len(jobs) != 1 else ''}{suffix}</b>.
          </p>
        </td></tr>
        <tr><td style="padding:6px 28px 20px">
          {jobs_html}
          {near_html}
          {unapplied_html}
        </td></tr>
        {evolution_html}
        <tr><td style="padding:16px 28px 20px;border-top:1px solid #e0e0e0">
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;margin:0;line-height:1.6">
            About the workbook: the attached Excel file contains 5 sheets \u2014 All Jobs (full dump), Fresh Matches (75-100% only), Applications (track your status), Cover Letters (generated for each match), and Daily Log.
          </p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;margin:16px 0 0;line-height:1.6">
            {next_scan_line()}.
          </p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;margin:16px 0 0;line-height:1.6">
            {_esc(closing)}<br>
            <b>CareerOps Services</b><br>
            <span style="font-size:12px;color:#888">AI-Powered Job Search Intelligence \u2014 matching is algorithmic; always review each posting before applying.</span>
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
    text += f"{greeting}\n\n"
    text += f"This cycle we reviewed {all_count:,} job listings across {source_count} sources and found {len(jobs)} new match{'es' if len(jobs) != 1 else ''}{suffix}.\n\n"

    if not jobs:
        text += "\u2705 0 New Matches Found\n"
        text += pick_no_match_note(date_iso, scan_num, all_count, fresh_count) + "\n\n"
    else:
        for i, j in enumerate(jobs):
            text += format_job_card(j, i) + "\n\n"

    if near_all:
        text += "\nADDITIONAL CLOSE MATCHES (50-74%)\n"
        text += "Below your 75% threshold \u2014 review at your discretion:\n\n"
        for j in near_all[:6]:
            from scanner import get_freshness
            fresh = get_freshness(j.get("posted"))
            salary = j.get("salary") or "Not specified"
            text += f"[{j.get('score', 0)}%] {j.get('title', '')} \u2014 {j.get('company', '')}\n"
            text += f"   Location: {j.get('location', 'Remote') or 'Remote'} \xB7 Pay: {salary} \xB7 Posted: {fresh['label']}\n"
            text += f"   Review: {j.get('url', '')}\n\n"

    if unapplied_text:
        text += unapplied_text

    text += "About the workbook: the attached Excel file contains 5 sheets \u2014 All Jobs (full dump), Fresh Matches (75-100% only), Applications (track your status), Cover Letters (generated for each match), and Daily Log.\n\n"
    text += f"{next_scan_line()}.\n\n"
    text += f"{closing}\n\nCareerOps Services \u2014 your personal job search assistant.\n"

    return {"html": html, "text": text}


async def send_email(subject: str, text_body: str, html_body: str, excel_path: str | None = None, pdf_paths: list[str] | None = None) -> bool:
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

    # Build attachments list
    attachments = []
    
    # Add Excel attachment if available and under 5MB
    if excel_path:
        try:
            import os
            if os.path.exists(excel_path) and os.path.getsize(excel_path) < 5_000_000:
                content = open(excel_path, "rb").read()
                b64 = base64.b64encode(content).decode()
                filename = os.path.basename(excel_path)
                attachments.append({"name": filename, "content": b64})
        except Exception as e:
            print(f"Excel attachment failed: {e}")
    
    # Add PDF cover letters (up to 10 PDFs to stay under size limit)
    if pdf_paths:
        try:
            import os
            for pdf_path in pdf_paths[:10]:  # Max 10 PDFs
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) < 1_000_000:  # 1MB each
                    content = open(pdf_path, "rb").read()
                    b64 = base64.b64encode(content).decode()
                    filename = os.path.basename(pdf_path)
                    attachments.append({"name": filename, "content": b64})
        except Exception as e:
            print(f"PDF attachment failed: {e}")
    
    if attachments:
        payload["attachment"] = attachments

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


# ---------------------------------------------------------------------------
# Application Feedback Tracking
# ---------------------------------------------------------------------------

def record_job_feedback(job_url: str, job_data: dict, status: str):
    """
    Record feedback on a job application.
    Status: applied, rejected, interviewed, hired, declined
    Called from Excel sheet when user updates application status.
    """
    from learning_module import record_application
    try:
        record_application(job_url, job_data, status)
        print(f"Recorded {status} for {job_data.get('title', 'Unknown')}")
    except Exception as e:
        print(f"Failed to record feedback: {e}")
