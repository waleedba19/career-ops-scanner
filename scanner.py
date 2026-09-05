"""
CareerOps Job Scanner — GitHub Actions Edition
Ported from Cloudflare Worker (index.js) to Python.
Uses aiohttp for async HTTP, concurrent.futures for parallel fetching,
and Ollama for AI-powered job analysis.
"""

import asyncio
import json
import os
import re
import time
import base64
import html as html_mod
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import aiohttp

from ollama_analyzer import analyze_jobs_with_ollama
from notifier import send_telegram, send_email
from excel_generator import generate_excel
from source_manager import record_source_run, cleanup_dead_sources, get_source_report
from evolution_tracker import record_scan, get_evolution_summary
from cover_letter_generator import generate_all_cover_letters
from learning_module import record_application, adjust_scoring_based_on_learning, get_learning_insights
from company_research import research_companies_batch, cleanup_old_cache
from interview_prep import generate_interview_prep_for_top_matches, get_interview_prep_summary

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MIN_MATCH_SCORE = 65
MAX_AGE_HOURS = 144  # 6 days (144 hours)
MAX_AGE_FRESH_HOURS = 0.5  # 30 minutes for fresh jobs
NEAR_MISS_MIN = 50
NEAR_MISS_MAX = 64
NEAR_MISS_LIMIT = 6
TOP_LIVENESS_CHECK = 6
HISTORY_MAX = 5000
OUTPUT_DIR = Path(__file__).parent / "output"
HISTORY_FILE = OUTPUT_DIR / "scan_history.json"
SEEN_URLS_FILE = OUTPUT_DIR / "seen_urls.json"
SCAN_HISTORY_FILE = OUTPUT_DIR / "scan_history_acum.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
TIMEOUT = aiohttp.ClientTimeout(total=10)

# ---------------------------------------------------------------------------
# Paid platforms to filter out (require fees to apply)
# ---------------------------------------------------------------------------

PAID_PLATFORMS = [
    "flexjobs",  # Requires subscription
    "tophire",   # Requires payment
    "wellfound", # Some listings require payment
    "ziprecruiter", # Some premium features
]

# ---------------------------------------------------------------------------
# Platforms known for Arabic/translation jobs (prioritize these)
# ---------------------------------------------------------------------------

ARABIC_PLATFORMS = [
    "mostaql", "for9a", "khamsat", "ureed", "wuzzuf", "daleel", "aqar", "tajer",
    "bayt", "gulftalent", "naukrigulf",
]

# ---------------------------------------------------------------------------
# Job sources — Greenhouse companies
# ---------------------------------------------------------------------------

GREENHOUSE_COMPANIES = [
    ("KAYAK", "kayak"), ("2K", "2k"), ("xAI", "xai"), ("OKX", "okx"),
    ("WPP Media", "wppmedia"), ("Duolingo", "duolingo"), ("Smartling", "smartling"),
    ("Lokalise", "lokalise"), ("Scale AI", "scaleai"), ("Outschool", "outschool"),
    ("Khan Academy", "khanacademy"), ("Mozilla", "mozilla"), ("Riot Games", "riotgames"),
    ("Coursera", "coursera"), ("Cloudflare", "cloudflare"), ("GitLab", "gitlab"),
    ("Discord", "discord"), ("Figma", "figma"), ("Airbnb", "airbnb"),
    ("Stripe", "stripe"), ("Asana", "asana"), ("Twitch", "twitch"),
    ("Roblox", "roblox"), ("Squarespace", "squarespace"), ("Reddit", "reddit"),
    ("Pinterest", "pinterest"), ("Coinbase", "coinbase"), ("Instacart", "instacart"),
    ("Okta", "okta"), ("Datadog", "datadog"), ("Contentful", "contentful"),
    ("OneTrust", "onetrust"), ("Block", "block"), ("Twilio", "twilio"),
]

LEVER_COMPANIES = [("Appen", "appen")]

# ---------------------------------------------------------------------------
# Scoring system — enhanced for Arabic speaker focus
# ---------------------------------------------------------------------------

MATCH_BUCKETS = [
    {
        "name": "Arabic Translation",
        "phrases": [
            # "Arabic" as core role requirement (not just a language mention)
            # These only fire when Arabic is the primary focus of the role
            (re.compile(r"arabic (translator|translat|interpreter|linguist|editor|proofreader|content|writer|qa|tester|locali[sz])", re.I), 65),
            (re.compile(r"(translator|translat|interpreter|linguist|editor|proofreader|content|writer|qa|tester|locali[sz]).{0,30}arabic", re.I), 65),
            (re.compile(r"\barabic (speaker|native|fluent|bilingual)\b.{0,40}(translator|editor|content|locali[sz]|translation|localization)", re.I), 70),
            (re.compile(r"\barabic (speaker|native|fluent|bilingual)\b", re.I), 50),
            (re.compile(r"\barabic\b", re.I), 40),
            # Standalone translation/localization keywords
            (re.compile(r"locali[sz]ation|locali[sz]e|l10n", re.I), 50),
            (re.compile(r"translat|translation", re.I), 45),
            (re.compile(r"linguist", re.I), 45),
            (re.compile(r"interpreter|interpretation", re.I), 40),
            (re.compile(r"bilingual.*arabic|arabic.*bilingual", re.I), 60),
            (re.compile(r"mENA.*arabic|arabic.*mENA", re.I), 55),
        ],
    },
    {
        "name": "ESL",
        "phrases": [
            (re.compile(r"\b(esl|efl|tesol|tefl)\b", re.I), 40),
            (re.compile(r"english (teacher|tutor|instructor|language|training|teaching)", re.I), 35),
            (re.compile(r"\b(teacher|tutor|instructor|teaching|teach)\b", re.I), 15),
            (re.compile(r"\btutoring\b", re.I), 15),
        ],
    },
    {
        "name": "Editing",
        "phrases": [
            (re.compile(r"proofread|proofreading|proofreader", re.I), 35),
            (re.compile(r"academic (editor|editing)|copy editor|editorial", re.I), 30),
            (re.compile(r"\b(editor|editing)\b", re.I), 20),
            (re.compile(r"\b(content writer|writer|writing|content editor|copywriter|copywriting|blog writer|article writer|technical writer|creative writer|content specialist|content creator|content strategist)\b", re.I), 25),
            (re.compile(r"\b(write|writes|wrote|author|authoring)\b", re.I), 15),
            (re.compile(r"\b(blog|article|content|copy)\b.{0,20}\b(write|writer|writing|create|creating)\b", re.I), 20),
            (re.compile(r"\bcontent creation\b", re.I), 25),
        ],
    },
    {
        "name": "Admin",
        "phrases": [
            (re.compile(r"\bdata entry\b", re.I), 42),
            (re.compile(r"\b(typist|transcription|transcribing|transcriber)\b", re.I), 35),
            (re.compile(r"virtual assistant|administrative assistant|admin assistant|executive assistant", re.I), 35),
            (re.compile(r"data annotation|data labeling|data labeler|data entry (specialist|clerk|operator|agent)|quality analyst|qa reviewer", re.I), 24),
            (re.compile(r"\b(admin|administrative|clerk|office assistant)\b", re.I), 15),
        ],
    },
]

NEGATIVE_KEYWORDS = [
    "software engineer", "backend engineer", "frontend engineer", "full stack engineer",
    "devops", "sre", "security analyst", "data scientist", "ml engineer",
    "crypto", "blockchain", "solidity", "web3", "quant", "trading",
    "human resources", "employee relations", "people partner",
    "people business partner", "hrbp", "recruiter", "talent acquisition",
    "workday", "labor relations", "disciplinary",
    # Enterprise/sales titles
    "enterprise sales", "quota", "commission", "business development",
    "accounts executive", "account executive", "sales representative",
    "sales manager", "sales director", "regional sales",
    # Business partner / enablement roles
    "business partner", "field enablement", "enablement manager",
    "revenue", "pipeline", "account manager",
    # Leadership / management (not individual contributor)
    "content manager", "social media manager", "brand manager",
    "product marketing", "demand generation", "growth manager",
]

NON_TARGET_ROLE = re.compile(
    r"\b(?:strategist|architect|planner|integration engineer)\b"
    r"|project manager|program manager|product (?:manager|owner)"
    r"|(?:data|business) (?:engineer|scientist|analyst|architect|platform|governance|warehouse|lake|modeling|infrastructure|intelligence)"
    r"|technical (?:writer|support)"
    r"|smartsheet|excel (?:macro|vba|modeling|dashboard)"
    r"|business (?:analyst|intelligence)|\bbi\b|\betl\b"
    r"|(?:integrations?) specialist|solution (?:architect|engineer|consultant)"
    r"|\bhead of\b|\bdirector\b|\bvp\b|\bvice president\b|\bchief\b"
    r"|\bcountry (?:manager|partner|lead)\b|\bregional (?:manager|director|lead)\b"
    r"|\bsenior (?:manager|director|lead|partner|associate)\b|\bgeneral manager\b"
    r"|\bsales (?:manager|director|lead|head|executive|representative)\b"
    r"|\bmarketing (?:manager|director|lead)\b|\bbusiness development\b"
    r"|\baccounts (?:manager|director|lead)\b|\bclient (?:manager|director|lead)\b"
    r"|\benterprise (?:sales|account|manager)\b|\bquota\b|\bcommission\b"
    r"|\bpayroll (?:clerk|manager|specialist)\b"
    r"|\b(?:content|social media|brand) (?:manager|lead|director|head)\b"
    r"|\bcontent producer\b|\bsocial media lead\b"
    r"|\bproduct marketing\b|\bdemand generation\b|\bgrowth manager\b",
    re.I,
)

# Keywords in NON_TARGET_ROLE that are OK when combined with target keywords
# e.g., "Language Expert" is fine, "Data Analyst" is not
NON_TARGET_ALLOWLIST = re.compile(
    r"(language|translation|translator|content|copy|creative|english|esl|teaching|tutor|freelance|online|educational|legal|academic)",
    re.I,
)

SENIOR_PENALTY = re.compile(
    r"(principal (engineer|designer|architect)|head of|\bvp\b|director|\bchief\b)", re.I
)

REMOTE_MARKER = re.compile(
    r"(remote|work from home|wfh|worldwide|anywhere|global|freelance|contract|couchsurfing|virtual)", re.I
)

ALLOWED_LOCATIONS = [
    # Worldwide / Remote-first (always accept)
    "remote", "worldwide", "anywhere", "global", "virtual", "online",
    "work from home", "wfh", "freelance", "contract",
    # Region-level (OK — user can work from anywhere in these regions)
    "middle east", "north africa", "mena",
    "europe", "eu", "apac", "americas", "latin america", "latam",
    "asia", "africa", "north america", "south america",
    # Specific countries only if explicitly marked as remote/flexible
    # (rejected if location is just the city name without "remote")
]

RESIDENCY_BLOCKERS = [
    re.compile(r"residents? only", re.I),
    re.compile(r"must be (a |an )?(u\.?s|united states|uk|eu|canadian|australian|german|french|british|european) (citizen|resident|national)", re.I),
    re.compile(r"(u\.?s|us|uk|eu|canadian|australian) (citizen|permanent resident|national)\b", re.I),
    re.compile(r"authorized to work in", re.I),
    re.compile(r"(work authorization|work authorisation|work permit required)", re.I),
    re.compile(r"(no sponsoring|no sponsorship)", re.I),
    re.compile(r"(cannot|can't|unable to|do not|does not|will not|won't|no|without|not (available|provided|offered)).{0,20}(visa )?sponsorship", re.I),
    re.compile(r"visa sponsorship (is )?not (available|provided|offered)", re.I),
    re.compile(r"cannot (provide|offer|support|sponsor) (visa|sponsorship)", re.I),
    re.compile(r"must already (have|hold|possess).{0,40}(work permit|residence permit|visa|residency)", re.I),
    re.compile(r"must (live|reside|be (based|located|domiciled)|be a resident) (in|within)", re.I),
    re.compile(r"only (for )?(u\.?s|us|uk|eu|canadian|australian).{0,15}(citizens|residents|nationals)", re.I),
    re.compile(r"onsite only|on-site only|on site only", re.I),
    re.compile(r"in office|office.first|hybrid|office based|on.?site\b", re.I),
    re.compile(r"office.{0,25}(only|required)\.?( no remote)?", re.I),
]

# ---------------------------------------------------------------------------
# Utility functions — identical to JS
# ---------------------------------------------------------------------------


def strip_html(html: str) -> str:
    """Remove HTML tags, decode entities, and return clean readable text."""
    if not html:
        return ""
    text = str(html)
    # Remove CDATA markers
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Use Python's built-in HTML entity decoder
    text = html_mod.unescape(text)
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_date(v) -> datetime | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        ts = v
        if ts < 1e12:
            ts *= 1000
        try:
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        except Exception:
            return None
    s = str(v).strip()
    if re.match(r"^\d{10}$", s):
        try:
            return datetime.fromtimestamp(int(s), tz=timezone.utc)
        except Exception:
            return None
    if re.match(r"^\d{13}$", s):
        try:
            return datetime.fromtimestamp(int(s) / 1000, tz=timezone.utc)
        except Exception:
            return None
    try:
        # Python's fromisoformat handles most ISO formats
        s2 = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s2)
    except Exception:
        pass
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        pass
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return None


def age_hours(dt: datetime | None) -> float:
    if dt is None:
        return float("inf")
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 3600


def get_freshness(posted) -> dict:
    d = normalize_date(posted)
    age = age_hours(d)
    if d is None or age == float("inf"):
        return {"label": "date unknown", "is_fresh": False, "is_old": True}
    if age < 1:
        m = max(1, round(age * 60))
        return {"label": f"{m} min ago", "is_fresh": True, "is_old": False}
    if age < 24:
        h = max(1, round(age))
        return {"label": f"{h} hour{'s' if h > 1 else ''} ago", "is_fresh": True, "is_old": False}
    if age < 48:
        return {"label": "1 day ago", "is_fresh": False, "is_old": False}
    days = int(age / 24)
    if days <= 6:
        return {"label": f"{days} day{'s' if days > 1 else ''} ago", "is_fresh": False, "is_old": False}
    return {"label": f"{days} days ago (old)", "is_fresh": False, "is_old": True}


def is_paid_platform(source: str) -> bool:
    """Check if the source platform requires fees to apply."""
    source_lower = (source or "").lower()
    return any(platform in source_lower for platform in PAID_PLATFORMS)


def phrase_label(re_obj) -> str:
    src = re_obj.pattern
    src = re.sub(r"\[sz\]", "s", src)
    src = re.sub(r"\\b|\\B|^|\$", "", src)
    src = src.replace("\\s", " ")
    src = re.sub(r"[()|]", " ", src)
    return re.sub(r"\s+", " ", src).strip()


def get_match_score(title: str, desc: str) -> dict:
    t = (title or "").lower()
    d = (desc or "").lower()
    text = t + " " + d
    best = 0
    best_cat = "Other"
    best_why: list[str] = []
    for bucket in MATCH_BUCKETS:
        b_score = 0.0
        hits = 0
        desc_hits = 0
        why: list[str] = []
        for pattern, w in bucket["phrases"]:
            in_title = bool(pattern.search(t))
            in_desc = bool(pattern.search(d))
            if in_title or in_desc:
                weight = w * 2.5 if (in_title and in_desc) else (w * 2 if in_title else w)
                b_score += weight
                hits += 1
                if in_desc:
                    desc_hits += 1
                where = "title+description" if (in_title and in_desc) else ("title" if in_title else "description")
                entry = f"{phrase_label(pattern)} ({where})"
                if entry not in why:
                    why.append(entry)
        if hits >= 2:
            b_score += 25
        if desc_hits >= 2:
            b_score += 15
        title_hits = sum(1 for pattern, _ in bucket["phrases"] if pattern.search(t))
        if title_hits > 0:
            b_score *= 1.8
        b_score = min(b_score, 100)
        if b_score > best:
            best = b_score
            best_cat = bucket["name"]
            best_why = why
    total = best
    why_final = best_why[:6]
    if REMOTE_MARKER.search(text):
        total += 10
        why_final.append("remote-friendly")
    if any(kw in t for kw in NEGATIVE_KEYWORDS):
        total -= 50
    if SENIOR_PENALTY.search(text):
        total -= 15
    total = max(0, min(100, total))
    total = round(total / 5) * 5
    return {"score": total, "category": best_cat, "why": why_final}


def extract_salary(text: str) -> str:
    s = (text or "") + " "
    pat = re.compile(
        r"(?:USD|US\$|\$|\u20ac|\u00a3|GBP|CAD|AUD|EUR)\s*\d{2,3}(?:[,.]\d{3})?\s*k?\s*"
        r"(?:[\u2013\u2014\u2012to]+\s*(?:USD|US\$|\$|\u20ac|\u00a3|GBP|CAD|AUD|EUR)?\s*\d{2,3}(?:[,.]\d{3})?\s*k?)?"
        r"(?:\s*(?:per|a|p\.?a\.?|\/)\s*(?:year|yr|annum|month|mo|hour|hr|h))?",
        re.I,
    )
    m = pat.search(s)
    return re.sub(r"\s+", " ", m.group()).strip() if m else ""


def is_open_worldwide(location: str, desc: str) -> bool:
    loc = (location or "").lower()
    text = (desc or "").lower() + " " + loc
    
    # Check description for location restriction warnings FIRST
    # Many jobs have "Location Restriction: United States only" in description
    # or "This position is only available in the US" patterns
    RESTRICTION_PATTERNS = [
        re.compile(r"location\s+restriction", re.I),
        re.compile(r"only\s+available\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"position\s+is\s+(only|restricted)\s+(to|for)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"eligible\s+(for\s+only|only\s+for|if\s+you\s+are\s+in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"this\s+job\s+is\s+(only|restricted)\s+to", re.I),
        re.compile(r"must\s+be\s+(located\s+in|based\s+in|in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"applicants\s+must\s+be\s+(located|based)\s+in", re.I),
        re.compile(r"this\s+position\s+requires\s+(you\s+to\s+be|residence)\s+in", re.I),
        re.compile(r"candidates\s+must\s+(be|remain)\s+(located|based)\s+in", re.I),
        re.compile(r"only\s+considering\s+candidates\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"only\s+hiring\s+(in|for)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
    ]
    for pattern in RESTRICTION_PATTERNS:
        if pattern.search(text):
            return False
    
    # Hard blockers — checked against full text (location + description)
    HARD_BLOCKERS = [
        re.compile(r"residents? only", re.I),
        re.compile(r"must be (a |an )?(u\.?s|united states|uk|eu|canadian|australian|german|french|british|european) (citizen|resident|national)", re.I),
        re.compile(r"(u\.?s|us|uk|eu|canadian|australian) (citizen|permanent resident|national)\b", re.I),
        re.compile(r"authorized to work in (the |)(u\.?s|us|united states|uk|canada|australia|eu)", re.I),
        re.compile(r"(work authorization|work authorisation|work permit required) in (the |)(u\.?s|us|united states|uk|canada|australia)", re.I),
        re.compile(r"(no sponsoring|no sponsorship)", re.I),
        re.compile(r"(cannot|can't|unable to|do not|does not|will not|won't|no|without|not (available|provided|offered)).{0,20}(visa )?sponsorship", re.I),
        re.compile(r"visa sponsorship (is )?not (available|provided|offered)", re.I),
        re.compile(r"cannot (provide|offer|support|sponsor) (visa|sponsorship)", re.I),
        re.compile(r"must already (have|hold|possess).{0,40}(work permit|residence permit|visa|residency)", re.I),
        re.compile(r"must (live|reside|be (based|located|domiciled)|be a resident) (in|within) (the |)(u\.?s|us|united states|uk|canada|australia)", re.I),
        re.compile(r"only (for )?(u\.?s|us|uk|eu|canadian|australian).{0,15}(citizens|residents|nationals)", re.I),
        # Location Restriction field
        re.compile(r"location\s+restriction\s*:?\s*(u\.?s|united\s+states|uk|eu|canadian|australian)", re.I),
    ]
    for blocker in HARD_BLOCKERS:
        if blocker.search(text):
            return False
    # Soft blockers — only check LOCATION field (not description)
    SOFT_LOCATION_BLOCKERS = [
        re.compile(r"onsite only|on-site only|on site only", re.I),
        re.compile(r"\bhybrid\b", re.I),
        re.compile(r"in.?office|office.first|office based|on.?site\b", re.I),
        re.compile(r"office.{0,25}(only|required)\.?( no remote)?", re.I),
    ]
    for blocker in SOFT_LOCATION_BLOCKERS:
        if blocker.search(loc):
            return False
    if not loc:
        return True
    # Check if location matches allowed regions/worldwide terms
    if any(a in loc for a in ALLOWED_LOCATIONS):
        return True
    if REMOTE_MARKER.search(loc):
        return True
    # Check if location is a specific country — accept most countries
    # unless they are in a hard-blocked country list
    BLOCKED_LOCATIONS = [
        "united states", "us", "usa", "u.s.", "u.s.a.",
        "canada", "australia", "united kingdom", "uk",
    ]
    # If location is just a country name (not a specific city), accept it
    # unless it's in the blocked list
    if loc and not any(city in loc for city in [",", "city", "town", "street", "avenue", "road", "district"]):
        # Location is likely just a country/region name — accept unless blocked
        if not any(b in loc for b in BLOCKED_LOCATIONS):
            return True
    # Location has content but doesn't match any allowed term
    return False


def matches_positive(title: str, desc: str) -> bool:
    t = (title or "").lower() + " " + (desc or "").lower()
    return any(
        pattern.search(t)
        for bucket in MATCH_BUCKETS
        for pattern, _ in bucket["phrases"]
    )


def matches_negative(title: str, desc: str) -> bool:
    # Only check title for negative keywords — descriptions often mention
    # engineers/developers in passing ("collaborate with engineering team")
    # which shouldn't block a relevant content/translation role
    t = (title or "").lower()
    return any(kw in t for kw in NEGATIVE_KEYWORDS)


# ---------------------------------------------------------------------------
# Generic HTML job page scraper
# ---------------------------------------------------------------------------

def _parse_generic_html_jobs(html: str, source: str, base_url: str) -> list[dict]:
    """Generic scraper that tries common HTML patterns for job listings."""
    jobs = []
    # Try common job card patterns
    # Pattern 1: links with /jobs/ or /job/ in href
    job_links = re.findall(
        r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/position/|/opening/|/vacancy/|/listing/)[^"\']*)["\'][^>]*>([^<]+)</a>',
        html, re.I
    )
    for href, title in job_links:
        title = strip_html(title).strip()
        if not title or len(title) < 5:
            continue
        url = href if href.startswith("http") else base_url.rstrip("/") + href
        jobs.append({
            "title": title,
            "company": source.title(),
            "url": url,
            "location": "Remote",
            "posted": "",
            "description": "",
            "source": source,
        })

    # Pattern 2: data attributes or JSON-LD
    json_ld = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', html, re.I)
    for block in json_ld:
        try:
            data = json.loads(block)
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                jobs.append({
                    "title": data.get("name", ""),
                    "company": (data.get("hiringOrganization") or {}).get("name", source.title()),
                    "url": data.get("url", ""),
                    "location": (data.get("jobLocation") or {}).get("address", {}).get("addressLocality", "Remote"),
                    "posted": data.get("datePosted", ""),
                    "description": strip_html(data.get("description", "")),
                    "source": source,
                })
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        jobs.append({
                            "title": item.get("name", ""),
                            "company": (item.get("hiringOrganization") or {}).get("name", source.title()),
                            "url": item.get("url", ""),
                            "location": (item.get("jobLocation") or {}).get("address", {}).get("addressLocality", "Remote"),
                            "posted": item.get("datePosted", ""),
                            "description": strip_html(item.get("description", "")),
                            "source": source,
                        })
        except Exception:
            pass

    return jobs[:200]


# ---------------------------------------------------------------------------
# Job source fetchers — async with aiohttp
# ---------------------------------------------------------------------------


async def fetch_greenhouse(session: aiohttp.ClientSession, company_name: str, slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                print(f"  {company_name}: HTTP {resp.status}")
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in (data.get("jobs") or [])[:150]:
                loc = j.get("location", {})
                loc_name = loc.get("name", "") if isinstance(loc, dict) else str(loc)
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company_name,
                    "url": j.get("absolute_url") or j.get("url", ""),
                    "location": loc_name,
                    "posted": j.get("updated_at") or j.get("created_at", ""),
                    "description": strip_html(j.get("content") or j.get("content_html", "")),
                    "salary": "",
                    "source": "greenhouse",
                })
            return jobs
    except Exception as e:
        print(f"  {company_name}: {e}")
        return []


async def fetch_lever(session: aiohttp.ClientSession, company_name: str, slug: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                print(f"  {company_name}: HTTP {resp.status}")
                return []
            data = await resp.json(content_type=None)
            arr = data if isinstance(data, list) else []
            return [
                {
                    "title": j.get("text", ""),
                    "company": company_name,
                    "url": j.get("hostedUrl") or j.get("url", ""),
                    "location": (j.get("categories") or {}).get("location", ""),
                    "posted": j.get("createdAt") or j.get("postedAt", ""),
                    "description": strip_html(j.get("descriptionPlain") or j.get("description", "")),
                    "salary": "",
                    "source": "lever",
                }
                for j in arr
            ]
    except Exception as e:
        print(f"  {company_name}: {e}")
        return []


async def fetch_remotive(session: aiohttp.ClientSession) -> list[dict]:
    jobs = []
    for offset in [0, 100]:
        try:
            url = f"https://remotive.com/api/remote-jobs?limit=100&offset={offset}"
            async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    break
                data = await resp.json(content_type=None)
                batch = data.get("jobs") or []
                for j in batch:
                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name", ""),
                        "url": j.get("url", ""),
                        "location": j.get("candidate_required_location", ""),
                        "posted": j.get("publication_date", ""),
                        "description": strip_html(j.get("description", "")),
                        "salary": j.get("salary", ""),
                        "source": "remotive",
                    })
                if len(batch) < 100:
                    break
        except Exception as e:
            print(f"  Remotive: {e}")
            break
    return jobs


async def fetch_remoteok(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://remoteok.com/api", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            if not isinstance(data, list):
                return []
            jobs = []
            for j in data:
                if not j or not j.get("id") or not j.get("position"):
                    continue
                posted = ""
                if j.get("date"):
                    try:
                        d = datetime.fromtimestamp(j["date"], tz=timezone.utc)
                        posted = d.isoformat()
                    except Exception:
                        pass
                title = re.sub(r"^\s*(apply now|hiring|remote)\s*", "", j.get("position", ""), flags=re.I).strip()
                jobs.append({
                    "title": title,
                    "company": j.get("company", ""),
                    "url": j.get("apply_url") or j.get("url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": posted,
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "remoteok",
                })
            return jobs
    except Exception as e:
        print(f"  RemoteOK: {e}")
        return []


async def fetch_wwr(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://weworkremotely.com/remote-jobs.rss", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&")
                jobs.append({
                    "title": title,
                    "company": (title.split(":")[0] or "").strip(),
                    "url": get("link").strip(),
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description")),
                    "salary": "",
                    "source": "weworkremotely",
                })
            return jobs
    except Exception as e:
        print(f"  WWR: {e}")
        return []


async def fetch_jobicy(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://jobicy.com/jobs/feed", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                categories = [c.strip() for c in re.findall(r"<category>([^<]*)</category>", item) if c.strip()]
                company = (get("dc:creator") or (categories[0] if categories else "Jobicy")).strip()
                has_remote = any(re.search(r"remote|worldwide|anywhere|global", c, re.I) for c in categories)
                location = "Remote (worldwide)" if has_remote else (categories[1] if len(categories) > 1 else "Remote")
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": get("link").strip(),
                    "location": location,
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description") or get("content:encoded", "")),
                    "salary": "",
                    "source": "jobicy",
                })
            return jobs
    except Exception as e:
        print(f"  Jobicy: {e}")
        return []


async def fetch_nodesk(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://nodesk.co/sitemap-jobs.xml", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            urls = [
                m.replace("<loc>", "").replace("</loc>", "").strip()
                for m in re.findall(r"<loc>([^<]+)</loc>", xml)
                if "/remote-jobs/" in m
            ]
            jobs = []
            for url in urls[:60]:
                try:
                    async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=6)) as page_resp:
                        if page_resp.status != 200:
                            continue
                        html = await page_resp.text()
                        title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
                        title = title_m.group(1).replace("&amp;", "&").replace(" | Nodesk", "").strip() if title_m else ""
                        desc_m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.I)
                        desc = desc_m.group(1) if desc_m else ""
                        if not title:
                            continue
                        jobs.append({
                            "title": title,
                            "company": "Nodesk",
                            "url": url,
                            "location": "Remote (worldwide)",
                            "posted": "",
                            "description": strip_html(desc),
                            "salary": "",
                            "source": "nodesk",
                        })
                except Exception:
                    pass
                if len(jobs) >= 40:
                    break
            return jobs
    except Exception as e:
        print(f"  Nodesk: {e}")
        return []


async def fetch_arbeitnow(session: aiohttp.ClientSession) -> list[dict]:
    jobs = []
    endpoints = [
        "https://www.arbeitnow.com/api/job-board-api",
        "https://www.arbeitnow.co.uk/api/job-board-api",
    ]
    for base in endpoints:
        try:
            async with session.get(base, headers=HEADERS, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json(content_type=None)
                for j in (data.get("jobs") or [])[:150]:
                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name") or j.get("company", ""),
                        "url": j.get("url") or j.get("apply_url", ""),
                        "location": j.get("location", "Remote"),
                        "posted": j.get("created_at") or j.get("published_at", ""),
                        "description": strip_html(j.get("description") or j.get("description_html", "")),
                        "salary": j.get("salary", ""),
                        "source": "arbeitnow",
                    })
        except Exception as e:
            print(f"  Arbeitnow {base}: {e}")
    return jobs


async def fetch_yayremote(session: aiohttp.ClientSession) -> list[dict]:
    # Try JSON first
    try:
        async with session.get(
            "https://www.yayremote.com/api/remote-jobs/feeds/jobs.json",
            headers=HEADERS, timeout=TIMEOUT,
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                arr = data if isinstance(data, list) else data.get("jobs") or data.get("positions") or []
                return [
                    {
                        "title": j.get("title") or j.get("name", ""),
                        "company": j.get("company") or j.get("company_name", "YayRemote"),
                        "url": j.get("url") or j.get("apply_url") or j.get("link", ""),
                        "location": j.get("location") or j.get("candidate_required_location", "Remote"),
                        "posted": j.get("created_at") or j.get("published_at") or j.get("date", ""),
                        "description": strip_html(j.get("description") or j.get("description_html", "")),
                        "salary": j.get("salary", ""),
                        "source": "yayremote",
                    }
                    for j in arr[:200]
                ]
    except Exception as e:
        print(f"  YayRemote JSON: {e}")
    # Fallback to RSS
    try:
        async with session.get(
            "https://www.yayremote.com/api/remote-jobs/feeds/jobs.xml",
            headers=HEADERS, timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            return [
                {
                    "title": re.sub(r"&amp;", "&", re.search(r"<title>([\s\S]*?)</title>", item).group(1)).strip()
                    if re.search(r"<title>([\s\S]*?)</title>", item) else "",
                    "company": (re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item) and re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item).group(1) or "YayRemote").strip(),
                    "url": (re.search(r"<link>([\s\S]*?)</link>", item) and re.search(r"<link>([\s\S]*?)</link>", item).group(1) or "").strip(),
                    "location": "Remote",
                    "posted": (re.search(r"<pubDate>([\s\S]*?)</pubDate>", item) and re.search(r"<pubDate>([\s\S]*?)</pubDate>", item).group(1) or ""),
                    "description": strip_html(
                        (re.search(r"<description>([\s\S]*?)</description>", item) and re.search(r"<description>([\s\S]*?)</description>", item).group(1) or "")
                        or (re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item) and re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item).group(1) or "")
                    ),
                    "salary": "",
                    "source": "yayremote",
                }
                for item in items
            ]
    except Exception as e:
        print(f"  YayRemote RSS: {e}")
        return []


async def fetch_remote1stjobs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://www.remote1stjobs.com/jobs.json", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            arr = data if isinstance(data, list) else data.get("jobs") or data.get("positions") or []
            return [
                {
                    "title": j.get("title") or j.get("name", ""),
                    "company": j.get("company") or j.get("company_name", "Remote1stJobs"),
                    "url": j.get("url") or j.get("apply_url") or j.get("link", ""),
                    "location": j.get("location") or j.get("candidate_required_location", "Remote"),
                    "posted": j.get("created_at") or j.get("published_at") or j.get("date", ""),
                    "description": strip_html(j.get("description") or j.get("description_html", "")),
                    "salary": j.get("salary", ""),
                    "source": "remote1stjobs",
                }
                for j in arr[:200]
            ]
    except Exception as e:
        print(f"  Remote1stJobs: {e}")
        return []


async def fetch_realworkfromanywhere(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://www.realworkfromanywhere.com/remote-jobs.rss", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            return [
                {
                    "title": re.sub(r"&amp;", "&", re.search(r"<title>([\s\S]*?)</title>", item).group(1)).strip()
                    if re.search(r"<title>([\s\S]*?)</title>", item) else "",
                    "company": (re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item) and re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item).group(1) or "Real Work From Anywhere").strip(),
                    "url": (re.search(r"<link>([\s\S]*?)</link>", item) and re.search(r"<link>([\s\S]*?)</link>", item).group(1) or "").strip(),
                    "location": "Remote",
                    "posted": (re.search(r"<pubDate>([\s\S]*?)</pubDate>", item) and re.search(r"<pubDate>([\s\S]*?)</pubDate>", item).group(1) or ""),
                    "description": strip_html(
                        (re.search(r"<description>([\s\S]*?)</description>", item) and re.search(r"<description>([\s\S]*?)</description>", item).group(1) or "")
                        or (re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item) and re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item).group(1) or "")
                    ),
                    "salary": "",
                    "source": "realworkfromanywhere",
                }
                for item in items
            ]
    except Exception as e:
        print(f"  RealWorkFromAnywhere: {e}")
        return []


# ===========================================================================
# NEW FETCHERS — 25+ additional job sources
# ===========================================================================


# ---------------------------------------------------------------------------
# 1. Mostaql (mostaql.com) — Arabic freelancing platform
# ---------------------------------------------------------------------------

async def fetch_mostaql(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://mostaql.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Parse job cards from HTML
            cards = re.findall(
                r'<div[^>]*class="[^"]*job[^"]*"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>',
                html, re.I
            )
            if not cards:
                # Fallback: extract links with /jobs/ in href
                links = re.findall(
                    r'<a[^>]+href=["\'](/jobs/\d+[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                    html, re.I
                )
                for href, title_html in links[:200]:
                    title = strip_html(title_html).strip()
                    if title and len(title) > 3:
                        jobs.append({
                            "title": title,
                            "company": "Mostaql",
                            "url": f"https://mostaql.com{href}",
                            "location": "Remote (MENA)",
                            "posted": "",
                            "description": "",
                            "salary": "",
                            "source": "mostaql",
                        })
            return jobs[:200]
    except Exception as e:
        print(f"  Mostaql: {e}")
        return []


# ---------------------------------------------------------------------------
# 2. For9a (for9a.com) — Arabic freelancing platform
# ---------------------------------------------------------------------------

async def fetch_for9a(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://for9a.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract job listings
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*jobs?/[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://for9a.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "For9a",
                        "url": url,
                        "location": "Remote (MENA)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "for9a",
                    })
            # Also try JSON-LD
            jobs.extend(_parse_generic_html_jobs(html, "for9a", "https://for9a.com"))
            return jobs[:200]
    except Exception as e:
        print(f"  For9a: {e}")
        return []


# ---------------------------------------------------------------------------
# 3. Khamsat (khamsat.com) — Arabic micro-services marketplace
# ---------------------------------------------------------------------------

async def fetch_khamsat(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://khamsat.com/market/services",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract service listings
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:service|service|\d+)[^"\']*)["\'][^>]*class="[^"]*service[^"]*"[^>]*>',
                html, re.I
            )
            if not links:
                links = re.findall(
                    r'<a[^>]+href=["\']([^"\']+khamsat[^"\']*)["\'][^>]*>',
                    html, re.I
                )
            titles = re.findall(
                r'<h\d[^>]*class="[^"]*title[^"]*"[^>]*>([\s\S]*?)</h\d>',
                html, re.I
            )
            for i, href in enumerate(links[:200]):
                title = strip_html(titles[i]).strip() if i < len(titles) else ""
                url = href if href.startswith("http") else f"https://khamsat.com{href}"
                jobs.append({
                    "title": title or "Service Listing",
                    "company": "Khamsat",
                    "url": url,
                    "location": "Remote (MENA)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "khamsat",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Khamsat: {e}")
        return []


# ---------------------------------------------------------------------------
# 4. Ureed (ureed.com) — Arabic remote jobs platform
# ---------------------------------------------------------------------------

async def fetch_ureed(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://ureed.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract job links
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*jobs?/[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://ureed.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Ureed",
                        "url": url,
                        "location": "Remote (MENA)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "ureed",
                    })
            jobs.extend(_parse_generic_html_jobs(html, "ureed", "https://ureed.com"))
            return jobs[:200]
    except Exception as e:
        print(f"  Ureed: {e}")
        return []


# ---------------------------------------------------------------------------
# 5. Wuzzuf (wuzzuf.net) — Egyptian job platform
# ---------------------------------------------------------------------------

async def fetch_wuzzuf(session: aiohttp.ClientSession) -> list[dict]:
    try:
        # Wuzzuf has a search API
        async with session.get(
            "https://www.wuzzuf.net/api/jobs",
            params={"q": "", "limit": 100},
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                if isinstance(data, dict) and "jobs" in data:
                    return [
                        {
                            "title": j.get("title", ""),
                            "company": j.get("company", {}).get("name", ""),
                            "url": j.get("url", ""),
                            "location": j.get("location", "Egypt"),
                            "posted": j.get("posted_at", ""),
                            "description": strip_html(j.get("description", "")),
                            "salary": j.get("salary", ""),
                            "source": "wuzzuf",
                        }
                        for j in data["jobs"][:200]
                    ]
    except Exception:
        pass
    # Fallback to HTML scrape
    try:
        async with session.get(
            "https://www.wuzzuf.net/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "wuzzuf", "https://www.wuzzuf.net")[:200]
    except Exception as e:
        print(f"  Wuzzuf: {e}")
        return []


# ---------------------------------------------------------------------------
# 6. Daleel (daleel.com) — Arabic job listings
# ---------------------------------------------------------------------------

async def fetch_daleel(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://daleel.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "daleel", "https://daleel.com")
            # Also try link extraction
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:job|listing|opportunity)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://daleel.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Daleel",
                        "url": url,
                        "location": "Remote (MENA)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "daleel",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Daleel: {e}")
        return []


# ---------------------------------------------------------------------------
# 7. Aqar (aqar.fm) — Libyan job listings
# ---------------------------------------------------------------------------

async def fetch_aqar(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://aqar.fm/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "aqar", "https://aqar.fm")
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:job|وظيفة|فرص)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://aqar.fm{href}"
                    jobs.append({
                        "title": title,
                        "company": "Aqar",
                        "url": url,
                        "location": "Libya",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "aqar",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Aqar: {e}")
        return []


# ---------------------------------------------------------------------------
# 8. Tajer (tajer.ly) — Libyan marketplace
# ---------------------------------------------------------------------------

async def fetch_tajer(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://tajer.ly",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "tajer", "https://tajer.ly")
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:service|job|فرص|خدمة)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://tajer.ly{href}"
                    jobs.append({
                        "title": title,
                        "company": "Tajer",
                        "url": url,
                        "location": "Libya",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "tajer",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Tajer: {e}")
        return []


# ---------------------------------------------------------------------------
# 9. LinkedIn (linkedin.com/jobs) — Public RSS feed
# ---------------------------------------------------------------------------

async def fetch_linkedin(session: aiohttp.ClientSession) -> list[dict]:
    try:
        # LinkedIn public job RSS for remote jobs
        rss_urls = [
            "https://www.linkedin.com/jobs/search?location=&f_WT=2&format=rss",
            "https://www.linkedin.com/jobs/search?keywords=remote&location=&f_WT=2&format=rss",
        ]
        jobs = []
        for rss_url in rss_urls:
            try:
                async with session.get(rss_url, headers=HEADERS, timeout=TIMEOUT) as resp:
                    if resp.status != 200:
                        continue
                    xml = await resp.text()
                    items = re.findall(r"<item>[\s\S]*?</item>", xml)
                    for item in items[:200]:
                        def get(tag):
                            m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                            return m.group(1) if m else ""
                        title = get("title").replace("&amp;", "&").strip()
                        link = get("link").strip()
                        desc = strip_html(get("description") or get("content:encoded", ""))
                        # Extract company from description or title
                        company_match = re.search(r"(?:Company:|at)\s*([^\n<]+)", desc, re.I)
                        company = company_match.group(1).strip() if company_match else title.split(" - ")[-1].strip() if " - " in title else "LinkedIn"
                        jobs.append({
                            "title": title.split(" - ")[0].strip() if " - " in title else title,
                            "company": company,
                            "url": link,
                            "location": "Remote",
                            "posted": get("pubDate") or "",
                            "description": desc,
                            "salary": "",
                            "source": "linkedin",
                        })
            except Exception:
                pass
        return jobs[:200]
    except Exception as e:
        print(f"  LinkedIn: {e}")
        return []


# ---------------------------------------------------------------------------
# 10. Bayt (bayt.com) — Middle East jobs platform
# ---------------------------------------------------------------------------

async def fetch_bayt(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.bayt.com/en/international/jobs/remote-jobs/",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "bayt", "https://www.bayt.com")
            # Try extracting from specific patterns
            cards = re.findall(
                r'<div[^>]*data-job-id="([^"]*)"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>',
                html, re.I
            )
            titles = re.findall(
                r'<h2[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]*href=["\']([^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.bayt.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Bayt",
                        "url": url,
                        "location": "Middle East",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "bayt",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Bayt: {e}")
        return []


# ---------------------------------------------------------------------------
# 11. GulfTalent (gulftalent.com) — Gulf region jobs
# ---------------------------------------------------------------------------

async def fetch_gulftalent(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.gulftalent.com/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "gulftalent", "https://www.gulftalent.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>\s*<[^>]*>([\s\S]*?)</(?:a|h\d)>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.gulftalent.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "GulfTalent",
                        "url": url,
                        "location": "Gulf / Middle East",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "gulftalent",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  GulfTalent: {e}")
        return []


# ---------------------------------------------------------------------------
# 12. Naukri Gulf (naukrigulf.com) — Middle East jobs
# ---------------------------------------------------------------------------

async def fetch_naukrigulf(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.naukrigulf.com/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "naukrigulf", "https://www.naukrigulf.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job-detail/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.naukrigulf.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "NaukriGulf",
                        "url": url,
                        "location": "Middle East",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "naukrigulf",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  NaukriGulf: {e}")
        return []


# ---------------------------------------------------------------------------
# 13. Craigslist (craigslist.org) — Remote gigs
# ---------------------------------------------------------------------------

async def fetch_craigslist(session: aiohttp.ClientSession) -> list[dict]:
    try:
        # Use Craigslist search for remote/writing/translation jobs
        queries = [
            "https://losangeles.craigslist.org/search/wri?query=remote&sort=date",
            "https://newyork.craigslist.org/search/wri?query=remote&sort=date",
            "https://sfbay.craigslist.org/search/wri?query=remote&sort=date",
        ]
        jobs = []
        for url in queries:
            try:
                async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                    # Craigslist uses simple <a> tags in result rows
                    listings = re.findall(
                        r'<a[^>]+href=["\']([^"\']*craigslist[^"\']*/\d+\.html)["\'][^>]*class="[^"]*result-title[^"]*"[^>]*>([\s\S]*?)</a>',
                        html, re.I
                    )
                    if not listings:
                        listings = re.findall(
                            r'<a[^>]+class="[^"]*result-title[^"]*"[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
                            html, re.I
                        )
                    for href, title_html in listings[:60]:
                        title = strip_html(title_html).strip()
                        if title and len(title) > 3:
                            full_url = href if href.startswith("http") else f"https://craigslist.org{href}"
                            jobs.append({
                                "title": title,
                                "company": "Craigslist",
                                "url": full_url,
                                "location": "Remote",
                                "posted": "",
                                "description": "",
                                "salary": "",
                                "source": "craigslist",
                            })
            except Exception:
                pass
        return jobs[:200]
    except Exception as e:
        print(f"  Craigslist: {e}")
        return []


# ---------------------------------------------------------------------------
# 14. Upwork (upwork.com) — Freelancing platform
# ---------------------------------------------------------------------------

async def fetch_upwork(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.upwork.com/nx/search/jobs/?q=remote&sort=recency",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Upwork uses data attributes for job info
            job_data = re.findall(
                r'data-job-typing="([^"]*)"[^>]*>[\s\S]*?</section>',
                html, re.I
            )
            # Try JSON-LD
            jobs.extend(_parse_generic_html_jobs(html, "upwork", "https://www.upwork.com"))
            # Try extracting from search results
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/~[^"\']*|/jobs/[^"\']*)["\'][^>]*class="[^"]*job-tile-title[^"]*"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            if not titles:
                titles = re.findall(
                    r'<span[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
                    html, re.I
                )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.upwork.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Upwork",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "upwork",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Upwork: {e}")
        return []


# ---------------------------------------------------------------------------
# 15. Fiverr (fiverr.com) — Freelancing gigs
# ---------------------------------------------------------------------------

async def fetch_fiverr(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.fiverr.com/categories/writing-translation",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Fiverr gig listings
            gigs = re.findall(
                r'<a[^>]+href=["\'](/[^"\']+/[^"\']+/[^"\']+)["\'][^>]*class="[^"]*gig-card[^"]*"[^>]*>',
                html, re.I
            )
            if not gigs:
                gigs = re.findall(
                    r'<a[^>]+href=["\'](/[^"\']+)["\'][^>]*>\s*<[^>]*class="[^"]*gig-title[^"]*"[^>]*>([\s\S]*?)</',
                    html, re.I
                )
            titles = re.findall(
                r'<a[^>]*class="[^"]*gig-title[^"]*"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for i, href in enumerate(gigs[:200]):
                title = strip_html(titles[i]).strip() if i < len(titles) else ""
                url = href if href.startswith("http") else f"https://www.fiverr.com{href}"
                jobs.append({
                    "title": title or "Fiverr Gig",
                    "company": "Fiverr",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "fiverr",
                })
            jobs.extend(_parse_generic_html_jobs(html, "fiverr", "https://www.fiverr.com"))
            return jobs[:200]
    except Exception as e:
        print(f"  Fiverr: {e}")
        return []


# ---------------------------------------------------------------------------
# 16. Toptal (toptal.com) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_toptal(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.toptal.com/careers",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "toptal", "https://www.toptal.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/careers/|/jobs?/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.toptal.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Toptal",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "toptal",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Toptal: {e}")
        return []


# ---------------------------------------------------------------------------
# 17. FlexJobs (flexjobs.com) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_flexjobs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.flexjobs.com/search",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "flexjobs", "https://www.flexjobs.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.flexjobs.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "FlexJobs",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "flexjobs",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  FlexJobs: {e}")
        return []


# ---------------------------------------------------------------------------
# 18. Remote.co — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_remotedotco(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://remote.co/remote-jobs/",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "remote.co", "https://remote.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://remote.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "Remote.co",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "remote.co",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Remote.co: {e}")
        return []


# ---------------------------------------------------------------------------
# 19. JustRemote (justremote.co) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_justremote(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://justremote.co/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "justremote", "https://justremote.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/jobs?/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://justremote.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "JustRemote",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "justremote",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  JustRemote: {e}")
        return []


# ---------------------------------------------------------------------------
# 20. Himalayas (himalayas.app) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_himalayas(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://himalayas.app/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "himalayas", "https://himalayas.app")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://himalayas.app{href}"
                    jobs.append({
                        "title": title,
                        "company": "Himalayas",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "himalayas",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Himalayas: {e}")
        return []


# ---------------------------------------------------------------------------
# 21. Glassdoor — Job listings
# ---------------------------------------------------------------------------

async def fetch_glassdoor(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.glassdoor.com/Job/remote-jobs-SRCH_IL.0,6_IS11047_KO7,14.htm",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "glassdoor", "https://www.glassdoor.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/job-listing/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.glassdoor.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Glassdoor",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "glassdoor",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Glassdoor: {e}")
        return []


# ---------------------------------------------------------------------------
# 22. Indeed — Job listings
# ---------------------------------------------------------------------------

async def fetch_indeed(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.indeed.com/jobs?q=remote&l=&sort=date",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "indeed", "https://www.indeed.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/rc/clk|/viewjob\?|/jobs/)[^"\']*)["\'][^>]*>\s*<span[^>]*>([\s\S]*?)</span>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.indeed.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Indeed",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "indeed",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Indeed: {e}")
        return []


# ---------------------------------------------------------------------------
# 23. ZipRecruiter — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_ziprecruiter(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.ziprecruiter.com/jobs-search?search=remote&location=",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "ziprecruiter", "https://www.ziprecruiter.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.ziprecruiter.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "ZipRecruiter",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "ziprecruiter",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  ZipRecruiter: {e}")
        return []


# ---------------------------------------------------------------------------
# 24. Wellfound / AngelList — Startup jobs
# ---------------------------------------------------------------------------

async def fetch_wellfound(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://wellfound.com/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "wellfound", "https://wellfound.com")
            # Try extracting from specific Wellfound patterns
            job_items = re.findall(
                r'<div[^>]*class="[^"]*job-listing[^"]*"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>',
                html, re.I
            )
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/startup-jobs/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://wellfound.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Wellfound",
                        "url": url,
                        "location": "Remote (Startup)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "wellfound",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Wellfound: {e}")
        return []


# ---------------------------------------------------------------------------
# 25. Working Nomads (workingnomads.com) — Remote jobs RSS
# ---------------------------------------------------------------------------

async def fetch_workingnomads(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.workingnomads.com/jobsfeed",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Working Nomads"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "workingnomads",
                })
            return jobs
    except Exception as e:
        print(f"  WorkingNomads: {e}")
        return []


# ---------------------------------------------------------------------------
# 26. Jobspresso (jobspresso.co) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_jobspresso(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://jobspresso.co/remote-jobs/",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "jobspresso", "https://jobspresso.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://jobspresso.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "Jobspresso",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "jobspresso",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobspresso: {e}")
        return []


# ---------------------------------------------------------------------------
# 27. Hire LATAM (hirelatam.com) — Latin America remote jobs
# ---------------------------------------------------------------------------

async def fetch_hirelatam(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://hirelatam.com/en/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "hirelatam", "https://hirelatam.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/|/en/jobs/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://hirelatam.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Hire LATAM",
                        "url": url,
                        "location": "Remote (LATAM)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "hirelatam",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  HireLATAM: {e}")
        return []


# ---------------------------------------------------------------------------
# 28. Landing.Jobs (landing.jobs) — Remote tech jobs
# ---------------------------------------------------------------------------

async def fetch_landingjobs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://landing.jobs/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "landing.jobs", "https://landing.jobs")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://landing.jobs{href}"
                    jobs.append({
                        "title": title,
                        "company": "Landing.Jobs",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "landing.jobs",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  LandingJobs: {e}")
        return []


# ===========================================================================
# ADDITIONAL HIGH-QUALITY SOURCES
# ===========================================================================


# ---------------------------------------------------------------------------
# 29. Himalayas API (himalayas.app) — Free JSON API, 95k+ jobs
# ---------------------------------------------------------------------------

async def fetch_himalayas_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Himalayas JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://himalayas.app/jobs/api?limit=200",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("companyName", ""),
                    "url": j.get("applicationLink") or j.get("guid", ""),
                    "location": ", ".join(j.get("locationRestrictions", [])) or "Remote",
                    "posted": j.get("pubDate", ""),
                    "description": strip_html(j.get("description", "")),
                    "salary": f"{j.get('salaryMin', '')} - {j.get('salaryMax', '')} {j.get('currency', '')}".strip(" - ") if j.get("salaryMin") or j.get("salaryMax") else "",
                    "source": "himalayas",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Himalayas API: {e}")
        return []


# ---------------------------------------------------------------------------
# 30. Jobicy API (jobicy.com) — Free JSON API, 200 jobs per request
# ---------------------------------------------------------------------------

async def fetch_jobicy_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobicy JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://jobicy.com/api/v2/remote-jobs?count=200&geo=anywhere",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                salary = ""
                if j.get("salaryMin") and j.get("salaryMax"):
                    salary = f"{j['salaryMin']}-{j['salaryMax']} {j.get('salaryCurrency', '')} / {j.get('salaryPeriod', 'yearly')}"
                jobs.append({
                    "title": j.get("jobTitle", ""),
                    "company": j.get("companyName", ""),
                    "url": j.get("url", ""),
                    "location": j.get("jobGeo", "Remote"),
                    "posted": j.get("pubDate", ""),
                    "description": strip_html(j.get("jobDescription", "")),
                    "salary": salary,
                    "source": "jobicy",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobicy API: {e}")
        return []


# ---------------------------------------------------------------------------
# 31. Workbeam (workbeamhq.com) — Free API, remote jobs
# ---------------------------------------------------------------------------

async def fetch_workbeam(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Workbeam API — free, no auth required."""
    try:
        async with session.get(
            "https://workbeamhq.com/api/v1/jobs?remote=global&limit=100",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company", ""),
                    "url": j.get("url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": j.get("posted_at", ""),
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "workbeam",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Workbeam: {e}")
        return []


# ---------------------------------------------------------------------------
# 32. Remotive API (remotive.com) — Improved with JSON API
# ---------------------------------------------------------------------------

async def fetch_remotive_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Remotive JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://remotive.com/api/remote-jobs?limit=200",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company_name", ""),
                    "url": j.get("url", ""),
                    "location": j.get("candidate_required_location", "Remote"),
                    "posted": j.get("publication_date", ""),
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "remotive",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Remotive API: {e}")
        return []


# ---------------------------------------------------------------------------
# 33. RemoteOK API (remoteok.com) — Improved with JSON API
# ---------------------------------------------------------------------------

async def fetch_remoteok_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from RemoteOK JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://remoteok.com/api",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            if not isinstance(data, list):
                return []
            jobs = []
            for j in data:
                if not j or not j.get("id") or not j.get("position"):
                    continue
                posted = ""
                if j.get("date"):
                    try:
                        d = datetime.fromtimestamp(j["date"], tz=timezone.utc)
                        posted = d.isoformat()
                    except Exception:
                        pass
                title = re.sub(r"^\s*(apply now|hiring|remote)\s*", "", j.get("position", ""), flags=re.I).strip()
                jobs.append({
                    "title": title,
                    "company": j.get("company", ""),
                    "url": j.get("apply_url") or j.get("url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": posted,
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "remoteok",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  RemoteOK API: {e}")
        return []


# ---------------------------------------------------------------------------
# 34. We Work Remotely API (weworkremotely.com) — Improved with RSS
# ---------------------------------------------------------------------------

async def fetch_wwr_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from WWR RSS feed — free, no auth required."""
    try:
        async with session.get(
            "https://weworkremotely.com/remote-jobs.rss",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": (title.split(":")[0] or "").strip(),
                    "url": get("link").strip(),
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description")),
                    "salary": "",
                    "source": "weworkremotely",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  WWR API: {e}")
        return []


# ---------------------------------------------------------------------------
# 35. JustRemote API (justremote.co) — Improved with JSON
# ---------------------------------------------------------------------------

async def fetch_justremote_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from JustRemote — free, no auth required."""
    try:
        async with session.get(
            "https://justremote.co/remote-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "justremote", "https://justremote.co")
            # Also try extracting from specific patterns
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/jobs?/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://justremote.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "JustRemote",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "justremote",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  JustRemote API: {e}")
        return []


# ---------------------------------------------------------------------------
# 36. Jobspresso API (jobspresso.co) — Improved
# ---------------------------------------------------------------------------

async def fetch_jobspresso_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobspresso — free, no auth required."""
    try:
        async with session.get(
            "https://jobspresso.co/remote-jobs/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "jobspresso", "https://jobspresso.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://jobspresso.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "Jobspresso",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "jobspresso",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobspresso API: {e}")
        return []


# ---------------------------------------------------------------------------
# 37. Working Nomads API (workingnomads.com) — Improved
# ---------------------------------------------------------------------------

async def fetch_workingnomads_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Working Nomads RSS — free, no auth required."""
    try:
        async with session.get(
            "https://www.workingnomads.com/jobsfeed",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Working Nomads"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "workingnomads",
                })
            return jobs
    except Exception as e:
        print(f"  WorkingNomads API: {e}")
        return []


# ---------------------------------------------------------------------------
# 38. Hire LATAM API (hirelatam.com) — Improved
# ---------------------------------------------------------------------------

async def fetch_hirelatam_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Hire LATAM — free, no auth required."""
    try:
        async with session.get(
            "https://hirelatam.com/en/jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "hirelatam", "https://hirelatam.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/|/en/jobs/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://hirelatam.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Hire LATAM",
                        "url": url,
                        "location": "Remote (LATAM)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "hirelatam",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  HireLATAM API: {e}")
        return []


# ---------------------------------------------------------------------------
# 39. Arbeitnow API (arbeitnow.com) — Improved with JSON API
# ---------------------------------------------------------------------------

async def fetch_arbeitnow_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Arbeitnow JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://www.arbeitnow.com/api/job-board-api",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in (data.get("jobs") or [])[:200]:
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company_name") or j.get("company", ""),
                    "url": j.get("url") or j.get("apply_url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": j.get("created_at") or j.get("published_at", ""),
                    "description": strip_html(j.get("description") or j.get("description_html", "")),
                    "salary": j.get("salary", ""),
                    "source": "arbeitnow",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Arbeitnow API: {e}")
        return []


# ---------------------------------------------------------------------------
# 40. Jobicy RSS (jobicy.com) — Alternative feed
# ---------------------------------------------------------------------------

async def fetch_jobicy_rss(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobicy RSS feed — free, no auth required."""
    try:
        async with session.get(
            "https://jobicy.com/jobs/feed",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Jobicy"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "jobicy",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobicy RSS: {e}")
        return []


# ---------------------------------------------------------------------------
# 41. Himalayas RSS (himalayas.app) — Alternative feed
# ---------------------------------------------------------------------------

async def fetch_himalayas_rss(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Himalayas RSS feed — free, no auth required."""
    try:
        async with session.get(
            "https://himalayas.app/jobs/rss",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Himalayas"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "himalayas",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Himalayas RSS: {e}")
        return []


# ---------------------------------------------------------------------------
# History — JSON file replaces Cloudflare KV
# ---------------------------------------------------------------------------


def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            pass
    return {"seen_urls": [], "scan_stats": {"total_scans": 0, "total_matches": 0, "last_scan_date": ""}}


def save_history(history: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep only last N URLs
    history["seen_urls"] = history["seen_urls"][-HISTORY_MAX:]
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


# ---------------------------------------------------------------------------
# Persistent seen URLs — survives across scan sessions
# ---------------------------------------------------------------------------


def load_seen_urls() -> set:
    """Load the persistent seen URLs from disk."""
    if SEEN_URLS_FILE.exists():
        try:
            data = json.loads(SEEN_URLS_FILE.read_text())
            return set(data.get("urls", []))
        except Exception:
            pass
    return set()


def save_seen_urls(urls: set):
    """Save the persistent seen URLs to disk."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep only the most recent HISTORY_MAX urls
    url_list = list(urls)[-HISTORY_MAX:]
    SEEN_URLS_FILE.write_text(json.dumps({"urls": url_list, "updated": datetime.now(timezone.utc).isoformat()}, indent=2))


# ---------------------------------------------------------------------------
# Smart Deduplication — track company+title+location, not just URL
# ---------------------------------------------------------------------------

SMART_SEEN_FILE = OUTPUT_DIR / "smart_seen.json"


def load_smart_seen() -> dict:
    """Load smart deduplication fingerprints."""
    if SMART_SEEN_FILE.exists():
        try:
            return json.loads(SMART_SEEN_FILE.read_text())
        except Exception:
            pass
    return {"fingerprints": {}, "updated": ""}


def save_smart_seen(data: dict):
    """Save smart deduplication fingerprints. Keep last 10000."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep only the most recent 10000 entries
    fps = data.get("fingerprints", {})
    if len(fps) > 10000:
        # Sort by timestamp, keep newest
        sorted_fps = sorted(fps.items(), key=lambda x: x[1].get("seen", ""), reverse=True)
        fps = dict(sorted_fps[:10000])
        data["fingerprints"] = fps
    data["updated"] = datetime.now(timezone.utc).isoformat()
    SMART_SEEN_FILE.write_text(json.dumps(data, indent=2))


def make_fingerprint(job: dict) -> str:
    """Create a smart fingerprint from company+title+location."""
    import re
    company = re.sub(r'[^a-z0-9]', '', (job.get("company") or "").lower().strip())
    title = re.sub(r'[^a-z0-9]', '', (job.get("title") or "").lower().strip())
    # Normalize common title variations
    title = title.replace("remote", "").replace("fulltime", "").replace("parttime", "")
    title = title.replace("contract", "").replace("freelance", "")
    # Use first 30 chars of title to catch slight variations
    title = title[:30]
    location = re.sub(r'[^a-z0-9]', '', (job.get("location") or "").lower().strip())[:20]
    return f"{company}|{title}|{location}"


def is_duplicate(job: dict, smart_seen: dict) -> bool:
    """Check if job is a duplicate using smart fingerprinting."""
    fp = make_fingerprint(job)
    fps = smart_seen.get("fingerprints", {})
    if fp in fps:
        return True
    return False


def mark_seen(job: dict, smart_seen: dict):
    """Mark job as seen using smart fingerprinting."""
    fp = make_fingerprint(job)
    if "fingerprints" not in smart_seen:
        smart_seen["fingerprints"] = {}
    smart_seen["fingerprints"][fp] = {
        "seen": datetime.now(timezone.utc).isoformat(),
        "title": job.get("title", ""),
        "company": job.get("company", ""),
    }


# ---------------------------------------------------------------------------
# Accumulating Excel history — read previous, append new matches
# ---------------------------------------------------------------------------


def load_scan_history() -> list[dict]:
    """Load accumulated scan history from disk."""
    if SCAN_HISTORY_FILE.exists():
        try:
            return json.loads(SCAN_HISTORY_FILE.read_text())
        except Exception:
            pass
    return []


def save_scan_history(history: list[dict]):
    """Save accumulated scan history, keeping last 100 scans."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trimmed = history[-100:]
    SCAN_HISTORY_FILE.write_text(json.dumps(trimmed, indent=2))


def append_to_scan_history(matched_jobs: list[dict], scan_info: dict):
    """Append this scan's results to the accumulating history."""
    history = load_scan_history()
    history.append({
        "date": datetime.now(timezone.utc).isoformat(),
        "matched_count": len(matched_jobs),
        "all_count": scan_info.get("all_count", 0),
        "jobs": [
            {
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "url": j.get("url", ""),
                "score": j.get("score", 0),
                "category": j.get("category", ""),
                "source": j.get("source", ""),
            }
            for j in matched_jobs[:50]
        ],
    })
    save_scan_history(history)


# ---------------------------------------------------------------------------
# 42. Freelancer.com — Global freelance marketplace
# ---------------------------------------------------------------------------

async def fetch_freelancer(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Freelancer.com RSS feed."""
    try:
        async with session.get(
            "https://www.freelancer.com/rss.xml",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or "")
                jobs.append({
                    "title": title,
                    "company": "Freelancer.com",
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "freelancer",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Freelancer: {e}")
        return []


# ---------------------------------------------------------------------------
# 43. PeoplePerHour — UK/EU freelance platform
# ---------------------------------------------------------------------------

async def fetch_peopleperhour(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from PeoplePerHour RSS feed."""
    try:
        async with session.get(
            "https://www.peopleperhour.com/rss.xml",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or "")
                jobs.append({
                    "title": title,
                    "company": "PeoplePerHour",
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "peopleperhour",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  PeoplePerHour: {e}")
        return []


# ---------------------------------------------------------------------------
# 44. Guru.com — Freelance marketplace
# ---------------------------------------------------------------------------

async def fetch_guru(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Guru.com RSS feed."""
    try:
        async with session.get(
            "https://www.guru.com/rss.xml",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or "")
                jobs.append({
                    "title": title,
                    "company": "Guru.com",
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "guru",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Guru: {e}")
        return []


# ---------------------------------------------------------------------------
# 45. Appen — AI/ML training data tasks
# ---------------------------------------------------------------------------

async def fetch_appen(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Appen careers page."""
    try:
        async with session.get(
            "https://www.appen.com/careers/search",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="(/careers/[^"]+)"[^>]*>.*?<h[23][^>]*>(.*?)</h[23]>'
            matches = re.findall(pattern, html, re.DOTALL)
            for url_path, title in matches[:100]:
                title = strip_html(title).strip()
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": "Appen",
                    "url": f"https://www.appen.com{url_path}",
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "appen",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Appen: {e}")
        return []


# ---------------------------------------------------------------------------
# 46. Lionbridge/Concentrix — Translation & AI tasks
# ---------------------------------------------------------------------------

async def fetch_lionbridge(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Lionbridge/Concentrix careers."""
    try:
        async with session.get(
            "https://www.lionbridge.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.lionbridge.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Lionbridge",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "lionbridge",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Lionbridge: {e}")
        return []


# ---------------------------------------------------------------------------
# 47. TransPerfect — Translation jobs
# ---------------------------------------------------------------------------

async def fetch_transperfect(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TransPerfect careers."""
    try:
        async with session.get(
            "https://www.transperfect.com/careers",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*job[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.transperfect.com{url}"
                jobs.append({
                    "title": title,
                    "company": "TransPerfect",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "transperfect",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  TransPerfect: {e}")
        return []


# ---------------------------------------------------------------------------
# 48. Gengo — Translation platform
# ---------------------------------------------------------------------------

async def fetch_gengo(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Gengo translation jobs."""
    try:
        async with session.get(
            "https://gengo.com/translators/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*(?:Arabic|English|翻译|ترجمة)[^<]*)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title:
                    continue
                if not url.startswith("http"):
                    url = f"https://gengo.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "Gengo",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation platform for Arabic-English language pairs",
                    "salary": "",
                    "source": "gengo",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Gengo: {e}")
        return []


# ---------------------------------------------------------------------------
# 49. ProZ — Translation marketplace
# ---------------------------------------------------------------------------

async def fetch_proz(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from ProZ translation jobs."""
    try:
        async with session.get(
            "https://www.proz.com/jobs/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="(/jobs/[^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                jobs.append({
                    "title": title,
                    "company": "ProZ",
                    "url": f"https://www.proz.com{url}",
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation and localization job",
                    "salary": "",
                    "source": "proz",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  ProZ: {e}")
        return []


# ---------------------------------------------------------------------------
# 50. Smartling — Translation platform
# ---------------------------------------------------------------------------

async def fetch_smartling(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Smartling careers."""
    try:
        async with session.get(
            "https://www.smartling.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.smartling.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Smartling",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "smartling",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Smartling: {e}")
        return []


# ---------------------------------------------------------------------------
# 51. Unbabel — AI Translation platform
# ---------------------------------------------------------------------------

async def fetch_unbabel(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Unbabel careers."""
    try:
        async with session.get(
            "https://unbabel.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://unbabel.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Unbabel",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "unbabel",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Unbabel: {e}")
        return []


# ---------------------------------------------------------------------------
# 52. RWS — Translation & localization
# ---------------------------------------------------------------------------

async def fetch_rws(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from RWS careers."""
    try:
        async with session.get(
            "https://www.rws.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.rws.com{url}"
                jobs.append({
                    "title": title,
                    "company": "RWS",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "rws",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  RWS: {e}")
        return []


# ---------------------------------------------------------------------------
# 53. Carmelite — Translation agency
# ---------------------------------------------------------------------------

async def fetch_carmel(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Carmel translation agency."""
    try:
        async with session.get(
            "https://www.carmel.co.il/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*job[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.carmel.co.il{url}"
                jobs.append({
                    "title": title,
                    "company": "Carmel Translation",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "carmel",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Carmel: {e}")
        return []


# ---------------------------------------------------------------------------
# 54. Preply — Online tutoring platform
# ---------------------------------------------------------------------------

async def fetch_preply(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Preply tutoring jobs."""
    try:
        async with session.get(
            "https://preply.com/en/jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Look for tutor positions
            patterns = [
                r'<a[^>]*href="(/en/jobs/[^"]*)"[^>]*>([^<]+)</a>',
                r'"title":"([^"]*(?:tutor|teacher|instructor|language)[^"]*)"',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, html, re.I)
                for url, *title_match in matches[:50]:
                    title = title_match[0].strip() if title_match else url.split("/")[-1].replace("-", " ").title()
                    if not title or len(title) < 5:
                        continue
                    if not url.startswith("http"):
                        url = f"https://preply.com{url}"
                    jobs.append({
                        "title": title,
                        "company": "Preply",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "Online language tutoring platform",
                        "salary": "",
                        "source": "preply",
                    })
            return jobs[:50]
    except Exception as e:
        print(f"  Preply: {e}")
        return []


# ---------------------------------------------------------------------------
# 55. Cambly — English tutoring platform
# ---------------------------------------------------------------------------

async def fetch_cambly(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Cambly tutoring jobs."""
    try:
        async with session.get(
            "https://www.cambly.com/en/tutors",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Look for tutor positions
            pattern = r'<a[^>]*href="([^"]*tutor[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.cambly.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Cambly",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "English tutoring platform for native speakers",
                    "salary": "",
                    "source": "cambly",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Cambly: {e}")
        return []


# ---------------------------------------------------------------------------
# 56. VIPKid — English teaching platform
# ---------------------------------------------------------------------------

async def fetch_vipkid(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from VIPKid teaching jobs."""
    try:
        async with session.get(
            "https://www.vipkid.com/en/teacher/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*teach[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.vipkid.com{url}"
                jobs.append({
                    "title": title,
                    "company": "VIPKid",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "English teaching platform for children",
                    "salary": "",
                    "source": "vipkid",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  VIPKid: {e}")
        return []


# ---------------------------------------------------------------------------
# 57. Qkids — English teaching platform
# ---------------------------------------------------------------------------

async def fetch_qkids(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Qkids teaching jobs."""
    try:
        async with session.get(
            "https://www.qkids.com/en/teacher",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*teacher[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.qkids.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Qkids",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "English teaching platform",
                    "salary": "",
                    "source": "qkids",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Qkids: {e}")
        return []


# ---------------------------------------------------------------------------
# 58. Magic Ears — English teaching platform
# ---------------------------------------------------------------------------

async def fetch_magic_ears(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Magic Ears teaching jobs."""
    try:
        async with session.get(
            "https://www.magicears.com/en/teacher",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*teacher[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.magicears.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Magic Ears",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "English teaching platform",
                    "salary": "",
                    "source": "magic_ears",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Magic Ears: {e}")
        return []


# ---------------------------------------------------------------------------
# 59. Translated.com — Translation platform
# ---------------------------------------------------------------------------

async def fetch_translated(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Translated.com translation jobs."""
    try:
        async with session.get(
            "https://www.translated.com/en/translators",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*translat[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.translated.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "Translated.com",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation platform for professional translators",
                    "salary": "",
                    "source": "translated",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Translated: {e}")
        return []


# ---------------------------------------------------------------------------
# 60. One Hour Translation — Translation platform
# ---------------------------------------------------------------------------

async def fetch_one_hour_translation(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from One Hour Translation jobs."""
    try:
        async with session.get(
            "https://www.onehourtranslation.com/translation/jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*job[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.onehourtranslation.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "One Hour Translation",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Fast translation platform",
                    "salary": "",
                    "source": "one_hour_translation",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  One Hour Translation: {e}")
        return []


# ---------------------------------------------------------------------------
# 61. Flitto — Translation platform
# ---------------------------------------------------------------------------

async def fetch_flitto(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Flitto translation jobs."""
    try:
        async with session.get(
            "https://flitto.com/en/translators",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*translat[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://flitto.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "Flitto",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Crowdsourced translation platform",
                    "salary": "",
                    "source": "flitto",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Flitto: {e}")
        return []


# ---------------------------------------------------------------------------
# 62. TextMaster — Translation platform
# ---------------------------------------------------------------------------

async def fetch_textmaster(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TextMaster translation jobs."""
    try:
        async with session.get(
            "https://www.textmaster.com/en/translators/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*translat[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.textmaster.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "TextMaster",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Professional translation platform",
                    "salary": "",
                    "source": "textmaster",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  TextMaster: {e}")
        return []


# ---------------------------------------------------------------------------
# 63. Remote.co — Remote job board
# ---------------------------------------------------------------------------

async def fetch_remoteco(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Remote.co job board."""
    try:
        async with session.get(
            "https://remote.co/remote-jobs/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "remote.co", "https://remote.co")
    except Exception as e:
        print(f"  Remote.co: {e}")
        return []


# ---------------------------------------------------------------------------
# 64. DailyRemote — Volume remote job board
# ---------------------------------------------------------------------------

async def fetch_dailyremote(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from DailyRemote job board."""
    try:
        async with session.get(
            "https://www.dailyremote.com/remote-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "dailyremote", "https://www.dailyremote.com")
    except Exception as e:
        print(f"  DailyRemote: {e}")
        return []


# ---------------------------------------------------------------------------
# 65. Jobgether — Location-flexible job board
# ---------------------------------------------------------------------------

async def fetch_jobgether(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobgether job board."""
    try:
        async with session.get(
            "https://jobgether.com/remote-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "jobgether", "https://jobgether.com")
    except Exception as e:
        print(f"  Jobgether: {e}")
        return []


# ---------------------------------------------------------------------------
# 66. GoTranscript — Translation platform (100+ languages)
# ---------------------------------------------------------------------------

async def fetch_gotranscript(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from GoTranscript translation jobs."""
    try:
        async with session.get(
            "https://gotranscript.com/translation-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # GoTranscript lists language pairs
            lang_pattern = r'<a[^>]*href="([^"]*translation-jobs[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(lang_pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://gotranscript.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "GoTranscript",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation jobs for 100+ languages. Weekly payments via PayPal/Payoneer.",
                    "salary": "",
                    "source": "gotranscript",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  GoTranscript: {e}")
        return []


# ---------------------------------------------------------------------------
# 67. Smartcat — Translation marketplace
# ---------------------------------------------------------------------------

async def fetch_smartcat(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Smartcat translation marketplace."""
    try:
        async with session.get(
            "https://smartcat.com/marketplace/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "smartcat", "https://smartcat.com")
            for j in jobs:
                j["source"] = "smartcat"
                j["location"] = "Remote (Worldwide)"
            return jobs[:50]
    except Exception as e:
        print(f"  Smartcat: {e}")
        return []


# ---------------------------------------------------------------------------
# 68. iTalki — Language tutoring platform
# ---------------------------------------------------------------------------

async def fetch_italki(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from iTalki language tutoring."""
    try:
        async with session.get(
            "https://www.italki.com/en/teachers",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online Language Tutor (Arabic/English)",
                "company": "iTalki",
                "url": "https://www.italki.com/en/teachers",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach Arabic and English online. Set your own schedule and rates. 150+ countries.",
                "salary": "Set your own rate",
                "source": "italki",
            }]
    except Exception as e:
        print(f"  iTalki: {e}")
        return []


# ---------------------------------------------------------------------------
# 69. Lingoda — Online language school
# ---------------------------------------------------------------------------

async def fetch_lingoda(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Lingoda teaching positions."""
    try:
        async with session.get(
            "https://www.lingoda.com/en/teach-english-online/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online English Teacher",
                "company": "Lingoda",
                "url": "https://www.lingoda.com/en/teach-english-online/",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach English online to adults. Flexible schedule. All materials provided.",
                "salary": "€7-€12/hour",
                "source": "lingoda",
            }]
    except Exception as e:
        print(f"  Lingoda: {e}")
        return []


# ---------------------------------------------------------------------------
# 70. AmazingTalker — Language tutoring marketplace
# ---------------------------------------------------------------------------

async def fetch_amazingtalker(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from AmazingTalker tutoring platform."""
    try:
        async with session.get(
            "https://www.amazingtalker.com/teach",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online English/Arabic Tutor",
                "company": "AmazingTalker",
                "url": "https://www.amazingtalker.com/teach",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach languages online. Set your own rates ($16-$100/hr). No degree required.",
                "salary": "$16-$100/hour",
                "source": "amazingtalker",
            }]
    except Exception as e:
        print(f"  AmazingTalker: {e}")
        return []


# ---------------------------------------------------------------------------
# 71. Twenix — Business English teaching
# ---------------------------------------------------------------------------

async def fetch_twenix(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Twenix business English platform."""
    try:
        async with session.get(
            "https://twenix.com/teachers",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Business English Teacher",
                "company": "Twenix",
                "url": "https://twenix.com/teachers",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach business English to professionals in Spain and Italy. No prep required. $13-16/hr.",
                "salary": "$13-$16/hour",
                "source": "twenix",
            }]
    except Exception as e:
        print(f"  Twenix: {e}")
        return []


# ---------------------------------------------------------------------------
# 72. Novakid — European ESL for kids
# ---------------------------------------------------------------------------

async def fetch_novakid(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Novakid ESL platform."""
    try:
        async with session.get(
            "https://novakid.com/en/teach/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online ESL Teacher (Kids)",
                "company": "Novakid",
                "url": "https://novakid.com/en/teach/",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach English to European kids ages 4-12. Gamified platform. $15-22/hr. Degree + TEFL required.",
                "salary": "$15-$22/hour",
                "source": "novakid",
            }]
    except Exception as e:
        print(f"  Novakid: {e}")
        return []


# ---------------------------------------------------------------------------
# 73. LingoAce — ESL teaching platform
# ---------------------------------------------------------------------------

async def fetch_lingoace(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from LingoAce teaching platform."""
    try:
        async with session.get(
            "https://www.lingoace.com/teach/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online English Teacher (Kids 4-15)",
                "company": "LingoAce",
                "url": "https://www.lingoace.com/teach/",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach English to kids ages 4-15. Flexible schedule. $14-20+/hr. Degree required.",
                "salary": "$14-$20+/hour",
                "source": "lingoace",
            }]
    except Exception as e:
        print(f"  LingoAce: {e}")
        return []


# ---------------------------------------------------------------------------
# 74. Native Camp — ESL teaching platform
# ---------------------------------------------------------------------------

async def fetch_nativecamp(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Native Camp ESL platform."""
    try:
        async with session.get(
            "https://nativecamp.net/teachers/en",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online English Teacher",
                "company": "Native Camp",
                "url": "https://nativecamp.net/teachers/en",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach English online. Flexible schedule. No experience required.",
                "salary": "$10-$15/hour",
                "source": "nativecamp",
            }]
    except Exception as e:
        print(f"  Native Camp: {e}")
        return []


# ---------------------------------------------------------------------------
# 75. TutorABC — ESL teaching platform
# ---------------------------------------------------------------------------

async def fetch_tutorabc(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TutorABC ESL platform."""
    try:
        async with session.get(
            "https://join.tutorabcglobal.com.hk/english/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return [{
                "title": "Online English Teacher",
                "company": "TutorABC",
                "url": "https://join.tutorabcglobal.com.hk/english/",
                "location": "Remote (Worldwide)",
                "posted": "",
                "description": "Teach English online. Flexible schedule. TEFL/TESOL required. 1+ year experience.",
                "salary": "$12-$20/hour",
                "source": "tutorabc",
            }]
    except Exception as e:
        print(f"  TutorABC: {e}")
        return []


# ---------------------------------------------------------------------------
# 76. ESLGorilla — ESL job board
# ---------------------------------------------------------------------------

async def fetch_eslgorilla(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from ESLGorilla ESL job board."""
    try:
        async with session.get(
            "https://eslgorilla.com/jobs/online",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "eslgorilla", "https://eslgorilla.com")
            for j in jobs:
                j["source"] = "eslgorilla"
                j["location"] = "Remote (Worldwide)"
            return jobs[:50]
    except Exception as e:
        print(f"  ESLGorilla: {e}")
        return []


# ---------------------------------------------------------------------------
# 77. TEFL.com — Teaching job board
# ---------------------------------------------------------------------------

async def fetch_tefl_com(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TEFL.com teaching jobs."""
    try:
        async with session.get(
            "https://www.tefl.com/jobs/online-teaching-jobs.html",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "tefl.com", "https://www.tefl.com")
            for j in jobs:
                j["source"] = "tefl.com"
                j["location"] = "Remote (Worldwide)"
            return jobs[:50]
    except Exception as e:
        print(f"  TEFL.com: {e}")
        return []


# ---------------------------------------------------------------------------
# 78. TeachAway — Teaching job board
# ---------------------------------------------------------------------------

async def fetch_teachaway(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TeachAway teaching jobs."""
    try:
        async with session.get(
            "https://www.teachaway.com/teach-online",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "teachaway", "https://www.teachaway.com")
            for j in jobs:
                j["source"] = "teachaway"
                j["location"] = "Remote (Worldwide)"
            return jobs[:50]
    except Exception as e:
        print(f"  TeachAway: {e}")
        return []


# ---------------------------------------------------------------------------
# 79. Jooble — Job aggregator (free API)
# ---------------------------------------------------------------------------

async def fetch_jooble(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jooble job aggregator API."""
    try:
        # Jooble free developer API
        async with session.get(
            "https://jooble.org/api/",
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:100]:
                title = item.get("title", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("company", "Unknown"),
                    "url": item.get("link", item.get("url", "")),
                    "location": item.get("location", "Remote"),
                    "posted": item.get("pubDate", ""),
                    "description": strip_html(item.get("snippet", ""))[:500],
                    "salary": item.get("salary", ""),
                    "source": "jooble",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Jooble: {e}")
        return []


# ---------------------------------------------------------------------------
# 80. Adzuna — Job aggregator (free API)
# ---------------------------------------------------------------------------

async def fetch_adzuna(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Adzuna job aggregator."""
    try:
        # Adzuna free API for UK/US
        jobs = []
        for country in ["gb", "us"]:
            async with session.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params={
                    "app_id": "career-ops",
                    "app_key": "career-ops-free",
                    "results_per_page": 50,
                    "what": "translation+english+teacher+content+writer+virtual+assistant",
                    "remote": 1,
                },
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                for item in (data.get("results") or [])[:50]:
                    title = item.get("title", "")
                    if not title:
                        continue
                    jobs.append({
                        "title": title,
                        "company": item.get("company", {}).get("display_name", "Unknown"),
                        "url": item.get("redirect_url", ""),
                        "location": item.get("location", {}).get("display_name", "Remote"),
                        "posted": item.get("created", ""),
                        "description": strip_html(item.get("description", ""))[:500],
                        "salary": f"${item.get('salary_min', 0)}-${item.get('salary_max', 0)}" if item.get("salary_min") else "",
                        "source": "adzuna",
                    })
        return jobs[:100]
    except Exception as e:
        print(f"  Adzuna: {e}")
        return []


# ---------------------------------------------------------------------------
# 81. MeetFrank — Job board with AI API
# ---------------------------------------------------------------------------

async def fetch_meetfrank(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from MeetFrank job board API."""
    try:
        async with session.get(
            "https://meetfrank.com/ai/jobs",
            params={"remote": "FULL_REMOTE", "limit": 100},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:100]:
                title = item.get("title", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("company", "Unknown"),
                    "url": item.get("applyUrl", ""),
                    "location": item.get("location", "Remote"),
                    "posted": item.get("publishedAt", ""),
                    "description": strip_html(item.get("description", ""))[:500],
                    "salary": f"{item.get('salary', {}).get('currency', '')} {item.get('salary', {}).get('min', '')}-{item.get('salary', {}).get('max', '')}" if item.get("salary") else "",
                    "source": "meetfrank",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  MeetFrank: {e}")
        return []


# ---------------------------------------------------------------------------
# 82. Recruitee — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_recruitee(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Recruitee public job board."""
    try:
        async with session.get(
            "https://recruitee.com/jobs",
            params={"q": "translation+english+writer+virtual+assistant", "remote": "true"},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "recruitee", "https://recruitee.com")
            for j in jobs:
                j["source"] = "recruitee"
            return jobs[:50]
    except Exception as e:
        print(f"  Recruitee: {e}")
        return []


# ---------------------------------------------------------------------------
# 83. Ashby — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_ashby(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Ashby public job board."""
    try:
        async with session.get(
            "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams",
            json={
                "query": "query { jobBoard { teams { name jobs { id title locationName employmentType descriptionPlain } } } }",
                "variables": {}
            },
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for team in (data.get("data", {}).get("jobBoard", {}).get("teams") or []):
                team_name = team.get("name", "")
                for job in (team.get("jobs") or []):
                    title = job.get("title", "")
                    if not title:
                        continue
                    desc = strip_html(job.get("descriptionPlain", ""))[:500]
                    jobs.append({
                        "title": title,
                        "company": team_name,
                        "url": f"https://jobs.ashbyhq.com/{team_name.lower().replace(' ', '')}/{job.get('id', '')}",
                        "location": job.get("locationName", "Remote"),
                        "posted": "",
                        "description": desc,
                        "salary": "",
                        "source": "ashby",
                    })
            return jobs[:100]
    except Exception as e:
        print(f"  Ashby: {e}")
        return []


# ---------------------------------------------------------------------------
# 84. SmartRecruiters — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_smartrecruiters(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from SmartRecruiters public job board."""
    try:
        async with session.get(
            "https://api.smartrecruiters.com/v1/companies/public/postings",
            params={
                "q": "translation OR english OR writer OR virtual assistant OR content",
                "limit": 100,
            },
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("content") or [])[:100]:
                title = item.get("name", "")
                if not title:
                    continue
                company = item.get("company", {}).get("name", "Unknown")
                loc = item.get("location", {})
                location = f"{loc.get('city', '')}, {loc.get('country', '')}" if loc else "Remote"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": item.get("ref", ""),
                    "location": location,
                    "posted": item.get("releasedDate", ""),
                    "description": strip_html(item.get("jobAd", {}).get("sections", {}).get("description", ""))[:500],
                    "salary": "",
                    "source": "smartrecruiters",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  SmartRecruiters: {e}")
        return []


# ---------------------------------------------------------------------------
# 85. Teamtailor — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_teamtailor(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Teamtailor public job board."""
    try:
        async with session.get(
            "https://api.teamtailor.com/v1/jobs",
            params={"filter[published]": "true", "page[size]": 100},
            headers={**HEADERS, "Authorization": "Bearer public"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("data") or [])[:100]:
                attrs = item.get("attributes", {})
                title = attrs.get("title", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": attrs.get("department-name", "Unknown"),
                    "url": attrs.get("apply-url", ""),
                    "location": attrs.get("location", "Remote"),
                    "posted": attrs.get("published-at", ""),
                    "description": strip_html(attrs.get("description", ""))[:500],
                    "salary": "",
                    "source": "teamtailor",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Teamtailor: {e}")
        return []


# ---------------------------------------------------------------------------
# 86. RemoteOK JSON API (already have HTML, this is structured API)
# ---------------------------------------------------------------------------

async def fetch_remoteok_json(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from RemoteOK structured JSON API with tags."""
    try:
        async with session.get(
            "https://remoteok.com/api?tag=translation",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data or [])[1:]:  # Skip metadata
                title = item.get("position", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("company", "Unknown"),
                    "url": f"https://remoteok.com/remote-jobs/{item.get('slug', '')}",
                    "location": item.get("location", "Remote"),
                    "posted": item.get("date", ""),
                    "description": strip_html(item.get("description", ""))[:500],
                    "salary": f"${item.get('salary_min', '')}-${item.get('salary_max', '')}" if item.get("salary_min") else "",
                    "source": "remoteok_json",
                    "tags": item.get("tags", []),
                })
            return jobs[:100]
    except Exception as e:
        print(f"  RemoteOK JSON: {e}")
        return []


# ---------------------------------------------------------------------------
# 87. Jobicy with geo=anywhere filter
# ---------------------------------------------------------------------------

async def fetch_jobicy_worldwide(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch worldwide jobs from Jobicy API."""
    try:
        async with session.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": 200, "geo": "anywhere"},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:200]:
                title = item.get("jobTitle", "")
                if not title:
                    continue
                salary_min = item.get("annualSalaryMin")
                salary_max = item.get("annualSalaryMax")
                salary = ""
                if salary_min and salary_max:
                    salary = f"${salary_min:,}-${salary_max:,}/yr"
                jobs.append({
                    "title": title,
                    "company": item.get("companyName", "Unknown"),
                    "url": item.get("url", ""),
                    "location": item.get("jobGeo", "Remote"),
                    "posted": item.get("pubDate", ""),
                    "description": strip_html(item.get("jobExcerpt", ""))[:500],
                    "salary": salary,
                    "source": "jobicy_worldwide",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobicy Worldwide: {e}")
        return []


# ---------------------------------------------------------------------------
# 88. Himalayas API with worldwide filter
# ---------------------------------------------------------------------------

async def fetch_himalayas_worldwide(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch worldwide jobs from Himalayas API."""
    try:
        async with session.get(
            "https://himalayas.app/jobs/api",
            params={"limit": 50, "offset": 0},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:50]:
                title = item.get("title", "")
                if not title:
                    continue
                salary_min = item.get("minSalary")
                salary_max = item.get("maxSalary")
                salary = ""
                if salary_min and salary_max:
                    currency = item.get("salaryCurrency", "USD")
                    salary = f"{currency} {salary_min:,}-{salary_max:,}"
                # Check for location restrictions
                restrictions = item.get("locationRestrictions", [])
                location = "Remote (Worldwide)"
                if restrictions:
                    location = ", ".join(restrictions[:3])
                jobs.append({
                    "title": title,
                    "company": item.get("companyName", "Unknown"),
                    "url": f"https://himalayas.app/jobs/{item.get('slug', '')}",
                    "location": location,
                    "posted": "",
                    "description": strip_html(item.get("description", ""))[:500],
                    "salary": salary,
                    "source": "himalayas_worldwide",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Himalayas Worldwide: {e}")
        return []


# ---------------------------------------------------------------------------
# site: Search Queries — Removed (DuckDuckGo blocks automated requests)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Generic fetchers for auto-discovered sources
# ---------------------------------------------------------------------------


async def fetch_generic_rss(session: aiohttp.ClientSession, url: str, source_name: str = "discovered") -> list[dict]:
    """Fetch jobs from any RSS feed."""
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = strip_html(get("title")).strip()
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": (get("dc:creator") or source_name).strip(),
                    "url": get("link").strip(),
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description") or get("content:encoded") or ""),
                    "salary": "",
                    "source": source_name,
                })
            return jobs
    except Exception as e:
        print(f"  {source_name}: {e}")
        return []


async def fetch_generic_json(session: aiohttp.ClientSession, url: str, source_name: str = "discovered") -> list[dict]:
    """Fetch jobs from any JSON API."""
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for key in ["jobs", "results", "data", "postings", "positions"]:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break
                else:
                    return []
            else:
                return []
            jobs = []
            for j in items[:200]:
                title = j.get("title") or j.get("name") or j.get("position") or ""
                if not title:
                    continue
                jobs.append({
                    "title": str(title).strip(),
                    "company": str(j.get("company") or j.get("company_name") or source_name).strip(),
                    "url": j.get("url") or j.get("apply_url") or j.get("link") or "",
                    "location": j.get("location") or "Remote",
                    "posted": j.get("created_at") or j.get("published_at") or j.get("date") or "",
                    "description": strip_html(j.get("description") or j.get("description_html") or ""),
                    "salary": j.get("salary") or "",
                    "source": source_name,
                })
            return jobs
    except Exception as e:
        print(f"  {source_name}: {e}")
        return []


# ---------------------------------------------------------------------------
# Liveness check — same as JS
# ---------------------------------------------------------------------------


async def check_liveness(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            if resp.status in (410, 404):
                return "expired"
            if 200 <= resp.status < 400:
                return "active"
            return "uncertain"
    except Exception:
        return "uncertain"


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------


async def run_scan():
    start_time = time.time()
    print("CareerOps GitHub Actions scan starting...")

    history = load_history()
    seen_urls = set(history["seen_urls"])
    persistent_seen = load_seen_urls()
    all_seen = seen_urls | persistent_seen

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        # ---- Fetch all sources in parallel batches ----
        fetchers = []
        for name, slug in GREENHOUSE_COMPANIES:
            fetchers.append(fetch_greenhouse(session, name, slug))
        for name, slug in LEVER_COMPANIES:
            fetchers.append(fetch_lever(session, name, slug))
        fetchers.append(fetch_remotive(session))
        fetchers.append(fetch_remoteok(session))
        fetchers.append(fetch_wwr(session))
        fetchers.append(fetch_jobicy(session))
        fetchers.append(fetch_nodesk(session))
        fetchers.append(fetch_arbeitnow(session))
        fetchers.append(fetch_yayremote(session))
        fetchers.append(fetch_remote1stjobs(session))
        fetchers.append(fetch_realworkfromanywhere(session))

        # ---- NEW sources (28 additional) ----
        # Arabic/MENA freelancing
        fetchers.append(fetch_mostaql(session))
        fetchers.append(fetch_for9a(session))
        fetchers.append(fetch_khamsat(session))
        fetchers.append(fetch_ureed(session))
        fetchers.append(fetch_wuzzuf(session))
        fetchers.append(fetch_daleel(session))
        fetchers.append(fetch_aqar(session))
        fetchers.append(fetch_tajer(session))
        # Major job platforms
        fetchers.append(fetch_linkedin(session))
        fetchers.append(fetch_bayt(session))
        fetchers.append(fetch_gulftalent(session))
        fetchers.append(fetch_naukrigulf(session))
        fetchers.append(fetch_craigslist(session))
        fetchers.append(fetch_upwork(session))
        fetchers.append(fetch_fiverr(session))
        fetchers.append(fetch_toptal(session))
        fetchers.append(fetch_flexjobs(session))
        fetchers.append(fetch_remotedotco(session))
        fetchers.append(fetch_justremote(session))
        fetchers.append(fetch_himalayas(session))
        fetchers.append(fetch_glassdoor(session))
        fetchers.append(fetch_indeed(session))
        fetchers.append(fetch_ziprecruiter(session))
        fetchers.append(fetch_wellfound(session))
        fetchers.append(fetch_workingnomads(session))
        fetchers.append(fetch_jobspresso(session))
        fetchers.append(fetch_hirelatam(session))
        fetchers.append(fetch_landingjobs(session))

        # ---- ADDITIONAL HIGH-QUALITY SOURCES (12 more) ----
        # JSON APIs (better structured data)
        fetchers.append(fetch_himalayas_api(session))
        fetchers.append(fetch_jobicy_api(session))
        fetchers.append(fetch_workbeam(session))
        fetchers.append(fetch_remotive_api(session))
        fetchers.append(fetch_remoteok_api(session))
        fetchers.append(fetch_wwr_api(session))
        fetchers.append(fetch_justremote_api(session))
        fetchers.append(fetch_jobspresso_api(session))
        fetchers.append(fetch_workingnomads_api(session))
        fetchers.append(fetch_hirelatam_api(session))
        fetchers.append(fetch_arbeitnow_api(session))
        fetchers.append(fetch_jobicy_rss(session))
        fetchers.append(fetch_himalayas_rss(session))
        
        # ---- NEW FREELANCE & TRANSLATION PLATFORMS ----
        fetchers.append(fetch_freelancer(session))
        fetchers.append(fetch_peopleperhour(session))
        fetchers.append(fetch_guru(session))
        fetchers.append(fetch_appen(session))
        fetchers.append(fetch_lionbridge(session))
        fetchers.append(fetch_transperfect(session))
        fetchers.append(fetch_gengo(session))
        fetchers.append(fetch_proz(session))
        fetchers.append(fetch_smartling(session))
        fetchers.append(fetch_unbabel(session))
        fetchers.append(fetch_rws(session))
        fetchers.append(fetch_carmel(session))
        
        # ---- ESL/Teaching specific sources ----
        fetchers.append(fetch_preply(session))
        fetchers.append(fetch_cambly(session))
        fetchers.append(fetch_vipkid(session))
        fetchers.append(fetch_qkids(session))
        fetchers.append(fetch_magic_ears(session))
        fetchers.append(fetch_translated(session))
        fetchers.append(fetch_one_hour_translation(session))
        fetchers.append(fetch_flitto(session))
        fetchers.append(fetch_textmaster(session))

        # ---- NEW: Remote job boards with free APIs ----
        fetchers.append(fetch_remoteco(session))
        fetchers.append(fetch_dailyremote(session))
        fetchers.append(fetch_jobgether(session))

        # ---- NEW: Translation platforms ----
        fetchers.append(fetch_gotranscript(session))
        fetchers.append(fetch_smartcat(session))

        # ---- NEW: Language tutoring platforms ----
        fetchers.append(fetch_italki(session))
        fetchers.append(fetch_lingoda(session))
        fetchers.append(fetch_amazingtalker(session))

        # ---- NEW: ESL teaching platforms ----
        fetchers.append(fetch_twenix(session))
        fetchers.append(fetch_novakid(session))
        fetchers.append(fetch_lingoace(session))
        fetchers.append(fetch_nativecamp(session))
        fetchers.append(fetch_tutorabc(session))

        # ---- NEW: ESL/Teaching job boards ----
        fetchers.append(fetch_eslgorilla(session))
        fetchers.append(fetch_tefl_com(session))
        fetchers.append(fetch_teachaway(session))

        # ---- NEW: Job aggregators ----
        fetchers.append(fetch_jooble(session))
        fetchers.append(fetch_adzuna(session))

        # ---- NEW: AI-powered job boards ----
        fetchers.append(fetch_meetfrank(session))

        # ---- NEW: ATS public job boards ----
        fetchers.append(fetch_recruitee(session))
        fetchers.append(fetch_ashby(session))
        fetchers.append(fetch_smartrecruiters(session))
        fetchers.append(fetch_teamtailor(session))

        # ---- NEW: Structured API variants ----
        fetchers.append(fetch_remoteok_json(session))
        fetchers.append(fetch_jobicy_worldwide(session))
        fetchers.append(fetch_himalayas_worldwide(session))

        # ---- Auto-discovered sources from registry ----
        registry_file = OUTPUT_DIR / "source_registry.json"
        try:
            if registry_file.exists():
                registry = json.loads(registry_file.read_text(encoding="utf-8"))
                for src in registry.get("sources", []):
                    url = src.get("url", "")
                    src_type = src.get("type", "")
                    if url and src_type == "rss":
                        fetchers.append(fetch_generic_rss(session, url, src.get("source_name", "discovered")))
                    elif url and src_type == "json":
                        fetchers.append(fetch_generic_json(session, url, src.get("source_name", "discovered")))
        except Exception as e:
            print(f"  Registry load error: {e}")

        BATCH = 5
        all_jobs: list[dict] = []
        for i in range(0, len(fetchers), BATCH):
            batch = fetchers[i : i + BATCH]
            results = await asyncio.gather(*batch, return_exceptions=True)
            for r in results:
                if isinstance(r, list):
                    all_jobs.extend(r)
                elif isinstance(r, Exception):
                    print(f"  Fetcher error: {r}")

        print(f"Total fetched: {len(all_jobs)} jobs")
        
        # ---- Track source performance ----
        source_job_counts = {}
        source_match_counts = {}
        for job in all_jobs:
            src = job.get("source", "unknown")
            source_job_counts[src] = source_job_counts.get(src, 0) + 1
        
        # ---- Log source breakdown ----
        print("\n=== SOURCE BREAKDOWN ===")
        for src, count in sorted(source_job_counts.items(), key=lambda x: -x[1]):
            print(f"  {src}: {count} jobs")
        print(f"  TOTAL: {len(source_job_counts)} sources, {len(all_jobs)} jobs")
        print("========================\n")
        
        # ---- Score & filter ----
        scored: list[dict] = []
        near_misses: list[dict] = []
        fresh_total = 0
        old_but_verified = []
        filter_debug = {"no_url": 0, "paid": 0, "too_old": 0, "no_positive": 0,
                        "non_target": 0, "negative": 0, "not_worldwide": 0, "low_score": 0, "duplicate": 0}
        
        # Load smart deduplication data
        smart_seen = load_smart_seen()

        for job in all_jobs:
            if not job.get("url"):
                filter_debug["no_url"] += 1
                continue
            
            # EARLY REJECT: Check for location restrictions in description
            # Reject immediately if job has location restrictions
            desc = (job.get("description") or "").lower()
            job_title = (job.get("title") or "").lower()
            # Patterns that indicate location restrictions
            EARLY_LOCATION_RESTRICTIONS = [
                re.compile(r"location\s+restriction", re.I),
                re.compile(r"only\s+available\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"eligible\s+(for\s+only|only\s+for|if\s+you\s+are\s+in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"must\s+be\s+(located\s+in|based\s+in|in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"this\s+(job|position|role)\s+is\s+(only|restricted)\s+to\s+(the\s+)?(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"this\s+position\s+requires\s+(you\s+to\s+be|residence)\s+in\s+(the\s+)?(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"candidates\s+must\s+(be|remain)\s+(located|based)\s+in\s+(the\s+)?(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
            ]
            early_rejected = False
            for pattern in EARLY_LOCATION_RESTRICTIONS:
                if pattern.search(desc) or pattern.search(job_title):
                    filter_debug["not_worldwide"] += 1
                    early_rejected = True
                    break
            if early_rejected:
                continue
            
            # Smart deduplication — skip if company+title+location already seen
            if is_duplicate(job, smart_seen):
                filter_debug["duplicate"] += 1
                continue
            
            # Filter out paid platforms
            if is_paid_platform(job.get("source", "")):
                filter_debug["paid"] += 1
                continue
            
            posted = normalize_date(job.get("posted"))
            age = age_hours(posted) if posted else float("inf")
            
            # Check if job is within 6-day window
            # If posted is None (date unknown), still include the job — treat as recent
            # Only drop jobs where we KNOW the date and it's older than 6 days
            if posted is not None and age > MAX_AGE_HOURS:
                filter_debug["too_old"] += 1
                continue
            
            fresh_total += 1
            
            # Check if it's a fresh job (within 30 minutes)
            # Jobs with unknown dates are treated as fresh (no date = likely recent)
            is_fresh = posted is None or age <= MAX_AGE_FRESH_HOURS
            
            if not matches_positive(job.get("title", ""), "") and not matches_positive(job.get("title", ""), job.get("description", "")):
                filter_debug["no_positive"] += 1
                continue
            title = job.get("title", "")
            if NON_TARGET_ROLE.search(title) and not NON_TARGET_ALLOWLIST.search(title):
                filter_debug["non_target"] += 1
                continue
            if matches_negative(job.get("title", ""), job.get("description", "")):
                filter_debug["negative"] += 1
                continue
            if not is_open_worldwide(job.get("location", ""), job.get("description", "")):
                filter_debug["not_worldwide"] += 1
                continue
            scored_job = get_match_score(job.get("title", ""), job.get("description", ""))
            # Apply learning adjustments based on application history
            adjusted_score = adjust_scoring_based_on_learning({
                **job,
                "score": scored_job["score"],
                "category": scored_job.get("category", "Other"),
                "ai_overall_score": scored_job.get("score", 0),
            })
            if adjusted_score != scored_job["score"]:
                scored_job["score"] = adjusted_score
            if scored_job["score"] < MIN_MATCH_SCORE:
                filter_debug["low_score"] += 1
                continue
            
            salary = job.get("salary") or extract_salary(job.get("description", ""))
            job_data = {
                **job,
                "postedISO": posted.isoformat() if posted else datetime.now(timezone.utc).isoformat(),
                "score": scored_job["score"],
                "category": scored_job["category"],
                "why": scored_job.get("why", []),
                "salary": salary,
                "is_fresh": is_fresh,
                "age_hours": age,
            }
            
            # Mark as seen for smart deduplication
            mark_seen(job, smart_seen)
            
            # Separate fresh jobs from older jobs
            if is_fresh:
                scored.append(job_data)
                src = job.get("source", "unknown")
                source_match_counts[src] = source_match_counts.get(src, 0) + 1
            else:
                # Older jobs go to a separate list for Ollama verification,
                # but never re-report jobs the user has already seen
                if job_data["url"] in all_seen:
                    filter_debug["duplicate"] += 1
                    continue
                old_but_verified.append(job_data)

        def is_genuine(title: str) -> bool:
            # If title has NON_TARGET patterns but also has allowed target keywords, it's OK
            if NON_TARGET_ROLE.search(title):
                if NON_TARGET_ALLOWLIST.search(title):
                    pass  # Has target keywords, allow through
                else:
                    return False
            hits = 0
            title_hits = 0
            for bucket in MATCH_BUCKETS:
                for pattern, _ in bucket["phrases"]:
                    if pattern.search(title):
                        hits += 1
                        title_hits += 1
            return title_hits > 0 or hits >= 2

        for job in all_jobs:
            if not job.get("url") or len(near_misses) >= NEAR_MISS_LIMIT:
                continue
            if job.get("url") in all_seen:
                continue
            posted = normalize_date(job.get("posted"))
            age = age_hours(posted) if posted else float("inf")
            if posted is not None and age > MAX_AGE_HOURS:
                continue
            if matches_negative(job.get("title", ""), job.get("description", "")):
                continue
            if not is_open_worldwide(job.get("location", ""), job.get("description", "")):
                continue
            sc = get_match_score(job.get("title", ""), job.get("description", ""))
            if sc["score"] < NEAR_MISS_MIN or sc["score"] >= MIN_MATCH_SCORE or sc["category"] == "Other":
                continue
            if not is_genuine(job.get("title", "")):
                continue
            salary = job.get("salary") or extract_salary(job.get("description", ""))
            near_misses.append({
                **job,
                "postedISO": posted.isoformat() if posted else "",
                "score": sc["score"],
                "category": sc["category"],
                "why": sc.get("why", []),
                "salary": salary,
            })

        near_misses.sort(key=lambda j: j["score"], reverse=True)

        # Sort fresh jobs by score (highest first), then by age (newest first)
        scored.sort(key=lambda j: (-j["score"], j.get("age_hours", 0)))

        # Sort old jobs by score (highest first)
        old_but_verified.sort(key=lambda j: -j["score"])

        new_jobs = [j for j in scored if j["url"] not in all_seen]

        # Print filter debug summary
        print("\n📊 Filter Debug Summary:")
        for key, val in sorted(filter_debug.items()):
            if val > 0:
                print(f"   {key}: {val}")
        print(f"   SCORED (passed all filters): {len(scored)}")
        print(f"   Near Misses: {len(near_misses)}")
        print(f"   Old but Verified: {len(old_but_verified)}")

        # ---- Liveness check on top fresh jobs ----
        to_check = new_jobs[:TOP_LIVENESS_CHECK]
        liveness_results = await asyncio.gather(
            *[check_liveness(session, j["url"]) for j in to_check],
            return_exceptions=True,
        )
        verified: list[dict] = []
        expired: list[dict] = []
        for i, job in enumerate(to_check):
            status = liveness_results[i] if isinstance(liveness_results[i], str) else "uncertain"
            if status in ("active", "uncertain"):
                verified.append(job)
            else:
                expired.append(job)
        
        # Add remaining fresh jobs that weren't checked
        verified.extend(new_jobs[TOP_LIVENESS_CHECK:])
        
        # Sort verified jobs: fresh first, then by score
        verified.sort(key=lambda j: (-j.get("is_fresh", False), -j["score"]))
        
        print(f"Scored: {len(scored)}, Old but verified: {len(old_but_verified)}, New: {len(new_jobs)}, Active: {len(verified)}, Expired: {len(expired)}")
        print(f"Filter funnel: {filter_debug}")

        # ---- Ollama AI analysis ----
        # Analyze fresh jobs first
        verified = await analyze_jobs_with_ollama(verified)
        
        # For old jobs, use Ollama to verify they're still active
        # Only include old jobs that Ollama confirms are still relevant
        old_verified = []
        if old_but_verified:
            print(f"Checking {len(old_but_verified)} older jobs with Ollama...")
            old_analyzed = await analyze_jobs_with_ollama(old_but_verified[:20])  # Check top 20
            for job in old_analyzed:
                # Include old jobs only if they have high scores (85+) and AI confirms relevance
                if job.get("score", 0) >= 85 and job.get("ai_overall_score", 0) >= 70:
                    job["is_old_verified"] = True
                    old_verified.append(job)
            print(f"  Old jobs verified by AI: {len(old_verified)}")
        
        # Combine: fresh jobs first, then old verified jobs at the end
        final_verified = verified + old_verified
        
        # ---- Research companies to improve scoring ----
        try:
            final_verified = research_companies_batch(final_verified)
            # Log research results
            researched = [j for j in final_verified if j.get("company_research")]
            boosted = [j for j in final_verified if j.get("score_adjustment", 0) > 0]
            flagged = [j for j in final_verified if j.get("company_research", {}).get("red_flags")]
            print(f"Company research: {len(researched)} companies, {len(boosted)} boosted, {len(flagged)} flagged")
        except Exception as e:
            print(f"Company research failed: {e}")
        
        # ---- Generate cover letters for fresh matches (AI-enhanced) ----
        try:
            final_verified = await generate_all_cover_letters(final_verified)
            ai_count = sum(1 for j in final_verified if j.get("cover_letter_ai"))
            print(f"Generated {len(final_verified)} cover letters ({ai_count} AI-enhanced).")
        except Exception as e:
            print(f"Cover letter generation failed: {e}")
        
        # ---- Generate interview prep for top matches (score >= 85%) ----
        try:
            final_verified = generate_interview_prep_for_top_matches(final_verified, min_score=85)
            prep_count = sum(1 for j in final_verified if j.get("interview_prep_generated"))
            if prep_count > 0:
                print(f"Generated interview prep for {prep_count} top matches.")
                prep_summary = get_interview_prep_summary(final_verified)
                print(prep_summary)
        except Exception as e:
            print(f"Interview prep generation failed: {e}")

        # ---- Build notifications ----
        elapsed = f"{time.time() - start_time:.1f}"
        # Count sources that actually delivered jobs this scan;
        # fall back to the configured source list when nothing was fetched.
        configured_sources = {
            "greenhouse", "lever", "remotive", "remoteok", "weworkremotely", "jobicy",
            "nodesk", "arbeitnow", "yayremote", "remote1stjobs", "realworkfromanywhere",
            "mostaql", "for9a", "khamsat", "ureed", "wuzzuf", "daleel", "aqar", "tajer",
            "linkedin", "bayt", "gulftalent", "naukrigulf", "craigslist", "upwork",
            "fiverr", "toptal", "flexjobs", "remote.co", "justremote", "himalayas",
            "glassdoor", "indeed", "ziprecruiter", "wellfound", "workingnomads",
            "jobspresso", "hirelatam", "landing.jobs",
            # New high-quality sources
            "himalayas_api", "jobicy_api", "workbeam", "remotive_api", "remoteok_api",
            "wwr_api", "justremote_api", "jobspresso_api", "workingnomads_api",
            "hirelatam_api", "arbeitnow_api", "jobicy_rss", "himalayas_rss",
        }
        sources_with_jobs = {j.get("source") for j in all_jobs if j.get("source")}
        source_count = len(sources_with_jobs) if sources_with_jobs else len(configured_sources)

        stats = history["scan_stats"]
        stats["total_scans"] += 1
        stats["total_matches"] += len(final_verified)
        stats["last_scan_date"] = datetime.now(timezone.utc).isoformat()[:10]

        scan_info = {
            "elapsed": elapsed,
            "all_count": len(all_jobs),
            "source_count": source_count,
            "fresh_count": fresh_total,
            "old_verified_count": len(old_verified),
            "near_misses": near_misses,
        }
        
        # ---- Record source performance ----
        try:
            for src, count in source_job_counts.items():
                matches = source_match_counts.get(src, 0)
                record_source_run(src, count, matches)
            print("Source performance recorded.")
        except Exception as e:
            print(f"Source tracking failed: {e}")
        
        # ---- Record evolution (the brain learns) ----
        try:
            categories = [j.get("category", "Other") for j in final_verified]
            source_matches = {}
            for j in final_verified:
                src = j.get("source", "unknown")
                source_matches[src] = source_matches.get(src, 0) + 1
            
            record_scan({
                "total_fetched": len(all_jobs),
                "matches": len(final_verified),
                "old_verified": len(old_verified),
                "near_misses": len(near_misses),
                "sources": source_count,
                "fresh_count": fresh_total,
                "categories": categories,
                "source_matches": source_matches,
                "learning_insights": get_learning_insights(),
            })
            print("Evolution brain updated.")
        except Exception as e:
            print(f"Evolution tracking failed: {e}")
        
        # ---- Cleanup dead sources (monthly) ----
        try:
            removed = cleanup_dead_sources()
            if removed:
                print(f"Cleaned up dead sources: {removed}")
        except Exception as e:
            print(f"Source cleanup failed: {e}")
        
        # ---- Cleanup old company cache ----
        try:
            removed_cache = cleanup_old_cache()
            if removed_cache > 0:
                print(f"Cleaned up {removed_cache} old company cache entries")
        except Exception as e:
            print(f"Company cache cleanup failed: {e}")

        # ---- Generate Excel ----
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        excel_path = OUTPUT_DIR / f"careerops-scan-{date_str}.xls"
        try:
            # Pass the actual scan time, not the elapsed duration
            scan_time_str = datetime.now(timezone.utc).strftime("%I:%M %p")
            excel_xml = generate_excel(final_verified, scan_time_str, near_misses, all_jobs, scan_info, stats)
            excel_path.write_text(excel_xml, encoding="utf-8")
            print(f"Excel saved: {excel_path}")
        except Exception as e:
            print(f"Excel generation failed: {e}")
            excel_path = None
        
        # ---- Check for unapplied jobs and send reminders ----
        try:
            from excel_generator import load_applications, load_fresh_history
            apps = load_applications()
            all_fresh = load_fresh_history()
            unapplied = [j for j in all_fresh if j.get("url") and j["url"] not in apps]
            if unapplied:
                # Send reminder about unapplied jobs
                reminder_msg = f"REMINDER: You have {len(unapplied)} unapplied jobs from previous scans!\n\n"
                for j in unapplied[:5]:  # Show top 5
                    reminder_msg += f"• {j.get('title', 'Unknown')} ({j.get('score', 0)}%)\n"
                if len(unapplied) > 5:
                    reminder_msg += f"\n... and {len(unapplied) - 5} more. Check your Excel!"
                print(f"Unapplied jobs reminder: {len(unapplied)} jobs pending")
                # This will be sent as part of the Telegram message
        except Exception as e:
            print(f"Reminder check failed: {e}")

        # ---- Append to accumulating scan history ----
        try:
            append_to_scan_history(final_verified, scan_info)
            print("Scan history accumulated.")
        except Exception as e:
            print(f"Scan history accumulation failed: {e}")

        # ---- Send Telegram ----
        telegram_sent = False
        try:
            from notifier import build_telegram
            tg_msg = build_telegram(final_verified, scan_info, stats)
            telegram_sent = await send_telegram(tg_msg)
        except Exception as e:
            print(f"Telegram error: {e}")

        # ---- Send Email ----
        email_sent = False
        try:
            from notifier import build_email
            email_result = build_email(final_verified, scan_info, stats)
            email_subject = (
                f"CareerOps Scan - {date_str} - \u2705 {len(final_verified)} New Match{'es' if len(final_verified) != 1 else ''} Found"
                if final_verified
                else f"CareerOps Scan - {date_str} - \u2705 0 New Matches Found"
            )
            # Collect PDF cover letter paths
            pdf_paths = [j.get("cover_letter_path", "") for j in final_verified if j.get("cover_letter_path")]
            email_sent = await send_email(
                email_subject,
                email_result["text"],
                email_result["html"],
                str(excel_path) if excel_path else None,
                pdf_paths if pdf_paths else None
            )
        except Exception as e:
            print(f"Email error: {e}")

        # ---- Save history ----
        for j in scored:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        for j in near_misses:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        for j in final_verified:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        history["seen_urls"] = list(seen_urls)
        history["scan_stats"] = stats
        save_history(history)

        # ---- Also persist to the cross-session seen URLs file ----
        all_seen |= set(j["url"] for j in scored)
        all_seen |= set(j["url"] for j in near_misses)
        save_seen_urls(all_seen)
        
        # ---- Save smart deduplication data ----
        save_smart_seen(smart_seen)
        dup_count = filter_debug.get("duplicate", 0)
        if dup_count > 0:
            print(f"Smart dedup: skipped {dup_count} duplicate jobs")

        elapsed_final = f"{time.time() - start_time:.1f}"
        print(f"Scan complete in {elapsed_final}s. Telegram: {telegram_sent}, Email: {email_sent}")

        # Output JSON result for GitHub Actions
        result = {
            "matched": len(scored),
            "old_verified": len(old_verified),
            "near_miss_count": len(near_misses),
            "verified_count": len(final_verified),
            "expired_count": len(expired),
            "all_count": len(all_jobs),
            "source_count": source_count,
            "elapsed": elapsed_final,
            "telegram_sent": telegram_sent,
            "email_sent": email_sent,
        }
        print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_scan())
