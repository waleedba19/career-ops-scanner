"""
CareerOps Notifier — Professional Telegram + Email (Brevo)
Redesigned for clean, professional presentation.
"""

import base64
import html as html_mod
import os
import re
import asyncio
import time
from datetime import datetime, timedelta, timezone

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
# Gmail SMTP delivery (preferred — no IP restrictions, free)
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCAN_LABELS = [
    {"time": "09:00", "label": "Morning Delivery", "emoji": "\u2600\ufe0f"},
    {"time": "18:00", "label": "Evening Delivery", "emoji": "\U0001f319"},
]


def get_scan_label() -> dict:
    """Pick the current slot label from Libya local time (UTC+2).

    The two crons fire at 07:00/16:00 UTC = 09:00/18:00 Libya, so the band split
    sits at 13:00 Libya (midday, between the two deliveries). Using UTC here
    mislabels any run that GitHub Actions delays past the UTC/Libya boundary.
    """
    h = now_libya().hour
    if h < 13:
        return SCAN_LABELS[0]
    return SCAN_LABELS[1]


def next_scan_time() -> str:
    """Human phrase for the next scheduled scan, in Libya local time.

    The crons are 07:00/16:00 UTC = 09:00/18:00 Libya. Returning raw UTC clock
    times told the user the wrong hour (and the wrong day after 18:00 Libya).
    """
    now = now_libya()
    h = now.hour
    slots = [SCAN_LABELS[0]["time"], SCAN_LABELS[1]["time"]]
    slot_hours = [int(s.split(":")[0]) for s in slots]
    for hour, label in zip(slot_hours, slots):
        if h < hour:
            return f"{label} Libya today"
    return f"{slots[0]} Libya tomorrow"


# ---------------------------------------------------------------------------
# Human voice — rotated openers/closers so back-to-back digests don't read
# like the same template twice. Selection is time-derived, so it varies per
# run but stays reproducible for a given run.
# ---------------------------------------------------------------------------

HUMAN_GREETINGS = {
    "Morning Delivery": (
        "Good morning — early shift done, so today's freshest posts are already at the top.",
        "Morning — the overnight queue is sorted and the first wave of new postings is in.",
        "Hi — I went through the new posts so you can start the day with a clear list, not a pile.",
    ),
    "Evening Delivery": (
        "Evening — the boards refreshed this hour, so I ran the late pass and sorted what matters.",
        "Evening — I chased down everything posted since the morning scan.",
        "End-of-day check: I pulled the fresh wave before it got buried under re-postings.",
    ),
}

HUMAN_CLOSINGS = (
    "Take care — I'll keep the boards under watch.",
    "See you at the next scan; I've got the watch from here.",
    "You've got the details, I've got the monitoring.",
    "Rest easy — the next cycle is already queued.",
)

# Zero-match copy, rotated by scan number so consecutive runs differ.
NO_MATCH_NOTES = (
    "No new position passed all four gates this cycle. I checked {all_count:,} "
    "listings — {fresh_count} were fresh — and none cleared the bar. I'll flag "
    "you the moment one does; no near-miss noise.",
    "Quiet cycle: {all_count:,} reviewed, {fresh_count} fresh, zero that cleared "
    "every gate. The filters are doing their job — when something real shows up, "
    "you'll hear from me first.",
    "Nothing new passed the full gate this time ({all_count:,} reviewed, "
    "{fresh_count} fresh). Rather than send you half-fits, I'm holding the line — "
    "the next qualifying role lands here the moment it does.",
)


def pick_greeting(label: dict) -> str:
    now = now_libya()
    pool = HUMAN_GREETINGS.get(label.get("label"), HUMAN_GREETINGS["Morning Delivery"])
    return pool[(now.hour + now.minute) % len(pool)]


def pick_closing() -> str:
    now = now_libya()
    return HUMAN_CLOSINGS[(now.minute + now.second) % len(HUMAN_CLOSINGS)]


def pick_no_match_note(scan_num: int, all_count: int, fresh_count: int) -> str:
    # scan_num increments every run, so modulo guarantees two consecutive runs
    # never repeat the same wording (a hash could cluster on the same index).
    idx = scan_num % len(NO_MATCH_NOTES)
    return NO_MATCH_NOTES[idx].format(all_count=all_count, fresh_count=fresh_count)


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
    elif job.get("email"):
        lines.append(f"\u2709\ufe0f Contact Email: {job['email']}")
    website = job.get("company_website","")
    if website:
        lines.append(f"\U0001f310 Company Website: {website}")
    elif job.get("company"):
        lines.append(f"\U0001f310 Website: look up \"{job['company']}\"")
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


# Libya live time (Africa/Tripoli, UTC+2 — no DST since 2013).
# The scanner's notify phase imports now_libya() from this module to stamp
# user-facing Excel / email dates in Libya time, never raw UTC.
LIBYA_TZ = timezone(timedelta(hours=2))


def now_libya() -> datetime:
    """Current time in Libya (Africa/Tripoli, UTC+2)."""
    return datetime.now(LIBYA_TZ)


def fresh_window_phrase() -> str:
    """Human phrase for the fresh-match window (e.g. 'the last 8 hours') — tracks live config."""
    try:
        from config import MAX_AGE_FRESH_HOURS
        h = float(MAX_AGE_FRESH_HOURS)
    except Exception:
        h = 8.0
    if h < 1:
        return f"the last {int(h * 60)} minutes"
    if h < 24:
        return f"the last {int(h)} hours"
    return f"the last {int(h / 24)} days"


def gates_line() -> str:
    """Human-readable filter gates — always in sync with the live config."""
    try:
        from config import MAX_AGE_FRESH_HOURS
        from scanner import MIN_MATCH_SCORE
        h = float(MAX_AGE_FRESH_HOURS)
        if h < 1:
            window = f"within {int(h * 60)} min"
        elif h < 24:
            window = f"within {int(h)} hours"
        else:
            window = f"within {int(h / 24)} days"
        return (f"{MIN_MATCH_SCORE}%+ CV match \u00b7 posted {window} \u00b7 "
                f"open worldwide \u00b7 no visa/residency restrictions")
    except Exception:
        return "65%+ CV match \u00b7 posted within 8 hours \u00b7 open worldwide \u00b7 no visa/residency restrictions"


def near_miss_label() -> str:
    """Score band for the close-matches section — tracks live config.

    The heading used to be hardcoded "50-74%" while the pipeline actually
    collected NEAR_MISS_MIN..NEAR_MISS_MAX (40-49), so the label never
    described the rows beneath it.
    """
    try:
        from config import NEAR_MISS_MIN, NEAR_MISS_MAX
        return f"{NEAR_MISS_MIN}-{NEAR_MISS_MAX}%"
    except Exception:
        return "close matches"


def match_range_label() -> str:
    """Match-score range for copy — tracks the live config threshold."""
    try:
        from config import MIN_MATCH_SCORE
        return f"{MIN_MATCH_SCORE}-100%"
    except Exception:
        return "65-100%"


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
    # User-facing stamps are Libya local time, never raw UTC — a run that
    # GitHub Actions delays past 22:00 UTC would otherwise be dated a day early.
    libya_now = now_libya()
    date = libya_now.strftime("%Y-%m-%d")
    time_str = libya_now.strftime("%H:%M Libya")
    scan_num = stats.get("total_scans", 0)
    all_count = scan_info.get("all_count", 0)
    source_count = scan_info.get("source_count", 0)
    fresh_count = scan_info.get("fresh_count", 0)
    near_all = scan_info.get("near_misses", [])
    
    msg = ""
    
    # Professional header with evolution
    msg += f"{label['emoji']} {label['label']} \u2014 {date}\n"
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
        # No matches — but show what we learned
        msg += "\u2705 0 New Matches Found\n"
        msg += "\n"
        msg += "No Arabic translation jobs found this scan.\n"
        msg += "\n"
        msg += pick_no_match_note(scan_num, all_count, fresh_count) + "\n"
        msg += "\n"
        msg += f"Gates: {gates_line()}\n"
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
            msg += f"\U0001f4a1 Additional Close Matches ({near_miss_label()})\n"
            msg += "Below your match threshold \u2014 review at your discretion:\n"
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

    # Learning summary line
    try:
        total_applied = learning.get("total_applied", 0)
        total_matches_count = stats.get("total_matches", 0)
        top_cat = ""
        if learning.get("top_skills"):
            top_cat = learning["top_skills"][0][0]
        if total_applied > 0 or total_matches_count > 0:
            msg += "\n"
            msg += f"Scan #{scan_num} | {total_matches_count} matches total"
            if top_cat:
                msg += f" | Top: {top_cat}"
            msg += "\n"
    except Exception:
        pass

    # Professional sign-off
    msg += "\n"
    msg += "\u2500" * 28 + "\n"
    msg += f"Next scan: {next_scan_time()}\n"
    msg += f"{pick_closing()}\n"
    msg += "Best regards,\n"
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
            for attempt in range(3):
                try:
                    payload = {"chat_id": TG_CHAT, "text": chunk}
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            print("Telegram message sent")
                            break
                        elif resp.status == 429:
                            await asyncio.sleep(5)
                            continue
                        else:
                            body = await resp.text()
                            print(f"Telegram HTTP {resp.status}: {body}")
                            ok = False
                            break
                except Exception as e:
                    print(f"Telegram attempt {attempt+1} error: {e}")
                    if attempt < 2:
                        await asyncio.sleep(2)
                    else:
                        ok = False
    return ok


# ---------------------------------------------------------------------------
# Email — Brevo API
# ---------------------------------------------------------------------------


def build_email(jobs: list, scan_info: dict, stats: dict) -> dict:
    """Build professional email with evolution intelligence."""
    from evolution_tracker import get_evolution_summary
    from source_manager import get_source_report
    
    _libya_now = now_libya()
    date_str = _libya_now.strftime("%A, %B %d, %Y")
    time_str = _libya_now.strftime("%I:%M %p Libya")
    greeting = pick_greeting(get_scan_label())
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
        website = j.get("company_website","")
        website_html = ""
        if website:
            website_html = f'<tr><td width="110" style="font-weight:bold;color:#0369a1;vertical-align:top">Company Website</td><td style="color:#111;vertical-align:top"><a href="{_esc(website)}" style="color:#1a5fb4;font-weight:bold">{_esc(website)}</a></td></tr>'
        elif j.get("company"):
            website_html = f'<tr><td width="110" style="font-weight:bold;color:#0369a1;vertical-align:top">Company Website</td><td style="color:#555;vertical-align:top">Search "{_esc(j.get("company"))}"</td></tr>'
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
            {website_html}
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
        jobs_html = f'''<p style="margin:14px 0;font-size:13px;color:#333;line-height:1.6">
        \u2705 <b>0 New Matches Found</b> \u2014 No new position passed every filter. Gates: {_esc(gates_line())}.
        For full transparency: of {all_count:,} job listings reviewed across {source_count} sources, only {fresh_count} were posted within {fresh_window_phrase()} \u2014 and none met every gate.
        We will keep watching the market for you; the next scan runs automatically at the next scheduled slot and any qualifying role reaches you within hours of being posted.</p>'''
    else:
        jobs_html = "".join(job_card_html(j, i) for i, j in enumerate(jobs))

    near_html = ""
    if near_all:
        near_html = f'<p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;color:#111;border-bottom:1px solid #d0d0d0;padding:16px 0 6px;margin-top:18px">Additional Close Matches ({near_miss_label()})</p>'
        near_html += '<p style="margin:8px 0 0;font-size:12px;color:#555">Below your match threshold \u2014 review at your discretion.</p>'
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

    # Learning summary HTML for email
    learning_summary_html = ""
    try:
        from learning_module import get_learning_insights
        li = get_learning_insights()
        total_applied = li.get("total_applied", 0)
        acceptance_rate = li.get("acceptance_rate", 0)
        top_cat = li["top_skills"][0][0] if li.get("top_skills") else ""
        top_comp = li["top_companies"][0][0] if li.get("top_companies") else ""
        if total_applied > 0 or stats.get("total_matches", 0) > 0:
            learning_summary_html = (
                '<tr><td style="padding:12px 28px;border-top:1px solid #e0e0e0">'
                '<p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;font-weight:bold;color:#111;margin:0 0 8px">'
                '\U0001f4a1 Learning Intelligence</p>'
                '<table width="100%" cellpadding="4" cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333">'
                f'<tr><td style="font-weight:bold;width:140">Total Applied</td><td>{total_applied}</td></tr>'
                f'<tr><td style="font-weight:bold">Interview Rate</td><td>{acceptance_rate}%</td></tr>'
                f'<tr><td style="font-weight:bold">Total Matches</td><td>{stats.get("total_matches", 0)}</td></tr>'
                f'<tr><td style="font-weight:bold">Top Category</td><td>{_esc(top_cat) if top_cat else "N/A"}</td></tr>'
                f'<tr><td style="font-weight:bold">Top Company</td><td>{_esc(top_comp) if top_comp else "N/A"}</td></tr>'
                '</table></td></tr>'
            )
    except Exception:
        pass

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
        {learning_summary_html}
        <tr><td style="padding:16px 28px 20px;border-top:1px solid #e0e0e0">
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333;margin:0;line-height:1.6">
            About the workbook: the attached Excel file contains 6 sheets \u2014 All Jobs (full dump), Fresh Matches ({match_range_label()} only), Applications (track your status), Cover Letters (generated for each match), Learning (intelligence dashboard), and Daily Log.
          </p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;margin:16px 0 0;line-height:1.6">
            The next scan is at <b>{next_scan_time()}</b>.
          </p>
          <p style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#111;margin:16px 0 0;line-height:1.6">
            Best regards,<br>
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
    text = f"{greeting}\n\n"
    text += "CAREEROPS SERVICES \u2014 Personal Job Search Assistant\n"
    text += f"{date_str} \xB7 {time_str} \xB7 Scan #{scan_num}\n\n"
    text += f"This cycle we reviewed {all_count:,} job listings across {source_count} sources and found {len(jobs)} new match{'es' if len(jobs) != 1 else ''}{suffix}.\n\n"

    if not jobs:
        text += "\u2705 0 New Matches Found\n"
        text += f"No new position passed every filter. Gates: {gates_line()}. Of those reviewed, only {fresh_count} were posted within {fresh_window_phrase()} \u2014 and none met every gate. We will keep watching.\n\n"
    else:
        for i, j in enumerate(jobs):
            text += format_job_card(j, i) + "\n\n"

    if near_all:
        text += f"\nADDITIONAL CLOSE MATCHES ({near_miss_label()})\n"
        text += "Below your match threshold \u2014 review at your discretion:\n\n"
        for j in near_all[:6]:
            from scanner import get_freshness
            fresh = get_freshness(j.get("posted"))
            salary = j.get("salary") or "Not specified"
            text += f"[{j.get('score', 0)}%] {j.get('title', '')} \u2014 {j.get('company', '')}\n"
            text += f"   Location: {j.get('location', 'Remote') or 'Remote'} \xB7 Pay: {salary} \xB7 Posted: {fresh['label']}\n"
            text += f"   Review: {j.get('url', '')}\n\n"

    if unapplied_text:
        text += unapplied_text

    text += f"About the workbook: the attached Excel file contains 6 sheets \u2014 All Jobs (full dump), Fresh Matches ({match_range_label()} only), Applications (track your status), Cover Letters (generated for each match), Learning (intelligence dashboard), and Daily Log.\n\n"
    text += f"The next scan is at {next_scan_time()}.\n\n"
    text += "Best regards,\nCareerOps Services \u2014 your personal job search assistant.\n"

    return {"html": html, "text": text}


def send_email_via_gmail(subject: str, text_body: str, html_body: str, excel_path: str | None = None, pdf_paths: list[str] | None = None) -> bool:
    """Send via Gmail SMTP (smtplib) — no IP restrictions, free, 500/day limit."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.utils import formataddr

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Waleed Zedco", GMAIL_USER))
    msg["To"] = TO_EMAIL
    # Sanitize lone surrogates (mangled emoji) so UTF-8 encoding never fails
    text_body = text_body.encode("utf-8", errors="replace").decode("utf-8")
    html_body = html_body.encode("utf-8", errors="replace").decode("utf-8")
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    def _attach(path, max_size):
        if path and os.path.exists(path) and os.path.getsize(path) < max_size:
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="octet-stream")
            part.add_header("Content-Disposition", "attachment", filename=os.path.basename(path))
            msg.attach(part)
            return True
        return False

    attached = 0
    if excel_path and _attach(excel_path, 5_000_000):
        attached += 1
    if pdf_paths:
        for p in pdf_paths[:10]:
            if _attach(p, 1_000_000):
                attached += 1
    print(f"Gmail attachments: {attached}")

    for attempt in range(3):
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
                server.starttls()
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, [TO_EMAIL], msg.as_string())
            print("Gmail email sent")
            return True
        except Exception as e:
            print(f"Gmail attempt {attempt+1} error: {e}")
            if attempt < 2:
                time.sleep(2)
    return False


async def send_email(subject: str, text_body: str, html_body: str, excel_path: str | None = None, pdf_paths: list[str] | None = None) -> bool:
    if not TO_EMAIL:
        print("Email skipped: no TO_EMAIL configured")
        return False

    # Preferred: Gmail SMTP (no IP restrictions, works from any runner IP)
    if GMAIL_USER and GMAIL_APP_PASSWORD:
        try:
            ok = await asyncio.to_thread(send_email_via_gmail, subject, text_body, html_body, excel_path, pdf_paths)
            if ok:
                return True
            print("Gmail failed — falling back to Brevo")
        except Exception as e:
            print(f"Gmail path error: {e} — falling back to Brevo")

    # Fallback: Brevo API
    if not BREVO_KEY:
        print("Email skipped: no Gmail or Brevo configured")
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
            for attempt in range(3):
                try:
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
                        if resp.status in (200, 201):
                            return True
                        elif resp.status == 429:
                            await asyncio.sleep(5)
                            continue
                        else:
                            print(f"Brevo FAILED: {resp.status} - {data}")
                            break
                except Exception as e:
                    print(f"Email attempt {attempt+1} error: {e}")
                    if attempt < 2:
                        await asyncio.sleep(2)
        return False
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
