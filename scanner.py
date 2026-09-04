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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MIN_MATCH_SCORE = 75
MAX_AGE_HOURS = 24
NEAR_MISS_MIN = 50
NEAR_MISS_MAX = 74
NEAR_MISS_LIMIT = 6
TOP_LIVENESS_CHECK = 6
HISTORY_MAX = 5000
OUTPUT_DIR = Path(__file__).parent / "output"
HISTORY_FILE = OUTPUT_DIR / "scan_history.json"

HEADERS = {"User-Agent": "career-ops-bot/3.0"}
TIMEOUT = aiohttp.ClientTimeout(total=8)

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
# Scoring system — identical to JS worker
# ---------------------------------------------------------------------------

MATCH_BUCKETS = [
    {
        "name": "Translation",
        "phrases": [
            (re.compile(r"\barabic\b", re.I), 40),
            (re.compile(r"locali[sz]ation|locali[sz]e|l10n", re.I), 45),
            (re.compile(r"translat|translation", re.I), 35),
            (re.compile(r"linguist", re.I), 35),
            (re.compile(r"interpreter|interpretation", re.I), 30),
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
            (re.compile(r"\b(content writer|writer|writing|content editor)\b", re.I), 15),
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
    "engineer", "developer", "software", "devops", "backend", "frontend",
    "full stack", "sre", "security analyst", "data scientist", "ml engineer",
    "crypto", "blockchain", "solidity", "web3", "quant", "trading",
    "human resources", "employee relations", "people partner",
    "people business partner", "hrbp", "recruiter", "talent acquisition",
    "workday", "labor relations", "disciplinary",
]

NON_TARGET_ROLE = re.compile(
    r"(expert|consultant|strategist|architect|analyst|planning|planner|"
    r"project manager|program manager|product (manager|owner)|"
    r"integration engineer|technical (writer|support)|"
    r"data (engineer|scientist|analyst|architect|platform|governance|warehouse|lake|modeling|infrastructure)|"
    r"smartsheet|excel (macro|vba|modeling|dashboard)|"
    r"business (analyst|intelligence)|bi |etl|"
    r"integrations? specialist|solution (architect|engineer|consultant))",
    re.I,
)

SENIOR_PENALTY = re.compile(
    r"(senior|\bsr\.?\b|partner|lead|principal|head of|\bvp\b|director|manager)", re.I
)

REMOTE_MARKER = re.compile(
    r"(remote|work from home|wfh|worldwide|anywhere|global|freelance|contract|couchsurfing|virtual)", re.I
)

ALLOWED_LOCATIONS = [
    "remote", "worldwide", "anywhere", "global", "virtual", "online",
    "libya", "tripoli", "benghazi", "egypt", "middle east", "north africa",
    "mena", "uae", "dubai", "abu dhabi", "saudi", "riyadh", "jeddah",
    "qatar", "doha", "kuwait", "bahrain", "oman", "muscat", "jordan",
    "amman", "morocco", "tunisia", "algeria", "lebanon", "iraq", "syria",
    "palestine", "yemen", "sudan", "somalia",
    "united states", "u.s.", "usa", "united kingdom", "uk", "canada",
    "australia", "new zealand", "ireland", "europe", "eu", "eu countries",
    "asia", "apac", "africa", "latin america", "latam", "south america",
    "americas", "north america",
    "germany", "france", "netherlands", "belgium", "spain", "portugal",
    "italy", "poland", "sweden", "norway", "denmark", "finland", "austria",
    "switzerland", "greece", "cyprus", "czech", "romania", "hungary",
    "croatia", "bulgaria", "turkey", "ukraine", "georgia", "armenia",
    "azerbaijan", "kazakhstan", "india", "pakistan", "bangladesh",
    "sri lanka", "nepal", "philippines", "indonesia", "malaysia",
    "singapore", "thailand", "vietnam", "japan", "china", "hong kong",
    "taiwan", "south korea", "brazil", "mexico", "argentina", "chile",
    "colombia", "peru", "venezuela", "uruguay", "paraguay", "ecuador",
    "bolivia", "south africa", "nigeria", "kenya", "ghana", "ethiopia",
    "uganda", "tanzania", "zimbabwe", "zambia", "botswana", "namibia",
    "rwanda", "ivory coast", "senegal", "cameroon", "morocco", "israel",
    "iceland", "luxembourg", "malta", "slovenia", "slovakia", "lithuania",
    "latvia", "estonia", "serbia", "albania", "bosnia", "moldova",
    "belarus", "mongolia", "myanmar", "cambodia", "laos", "fiji", "mauritius",
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
        return {"label": "date unknown", "is_fresh": False}
    if age < 1:
        m = max(1, round(age * 60))
        return {"label": f"{m} min ago", "is_fresh": True}
    if age < 24:
        h = max(1, round(age))
        return {"label": f"{h} hour{'s' if h > 1 else ''} ago", "is_fresh": True}
    if age < 48:
        return {"label": "1 day ago (too old)", "is_fresh": False}
    return {"label": f"{int(age / 24)} days ago (too old)", "is_fresh": False}


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
    if any(kw in text for kw in NEGATIVE_KEYWORDS):
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
    for blocker in RESIDENCY_BLOCKERS:
        if blocker.search(text):
            return False
    if not loc:
        return True
    if any(a in loc for a in ALLOWED_LOCATIONS):
        return True
    if REMOTE_MARKER.search(loc):
        return True
    return False


def matches_positive(title: str, desc: str) -> bool:
    t = (title or "").lower() + " " + (desc or "").lower()
    return any(
        pattern.search(t)
        for bucket in MATCH_BUCKETS
        for pattern, _ in bucket["phrases"]
    )


def matches_negative(title: str, desc: str) -> bool:
    t = (title or "").lower() + " " + (desc or "").lower()
    return any(kw in t for kw in NEGATIVE_KEYWORDS)


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
                    "source": "realworkfromanywhere",
                }
                for item in items
            ]
    except Exception as e:
        print(f"  RealWorkFromAnywhere: {e}")
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

    async with aiohttp.ClientSession() as session:
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

        # ---- Score & filter ----
        scored: list[dict] = []
        near_misses: list[dict] = []
        fresh_total = 0

        for job in all_jobs:
            if not job.get("url"):
                continue
            posted = normalize_date(job.get("posted"))
            if posted is None or age_hours(posted) > MAX_AGE_HOURS:
                continue
            fresh_total += 1
            if not matches_positive(job.get("title", ""), "") and not matches_positive(job.get("title", ""), job.get("description", "")):
                continue
            if NON_TARGET_ROLE.search(job.get("title", "")):
                continue
            if matches_negative(job.get("title", ""), job.get("description", "")):
                continue
            if not is_open_worldwide(job.get("location", ""), job.get("description", "")):
                continue
            scored_job = get_match_score(job.get("title", ""), job.get("description", ""))
            if scored_job["score"] < MIN_MATCH_SCORE:
                continue
            salary = job.get("salary") or extract_salary(job.get("description", ""))
            scored.append({
                **job,
                "postedISO": posted.isoformat(),
                "score": scored_job["score"],
                "category": scored_job["category"],
                "why": scored_job.get("why", []),
                "salary": salary,
            })

        def is_genuine(title: str) -> bool:
            if NON_TARGET_ROLE.search(title):
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
            posted = normalize_date(job.get("posted"))
            if posted is None or age_hours(posted) > MAX_AGE_HOURS:
                continue
            if matches_negative(job.get("title", ""), job.get("description", "")):
                continue
            if not is_open_worldwide(job.get("location", ""), job.get("description", "")):
                continue
            sc = get_match_score(job.get("title", ""), job.get("description", ""))
            if sc["score"] < NEAR_MISS_MIN or sc["score"] >= 75 or sc["category"] == "Other":
                continue
            if not is_genuine(job.get("title", "")):
                continue
            salary = job.get("salary") or extract_salary(job.get("description", ""))
            near_misses.append({
                **job,
                "postedISO": posted.isoformat(),
                "score": sc["score"],
                "category": sc["category"],
                "why": sc.get("why", []),
                "salary": salary,
            })

        near_misses.sort(key=lambda j: j["score"], reverse=True)
        scored.sort(key=lambda j: (j["score"], -age_hours(normalize_date(j.get("postedISO")))))
        # For score primary, age secondary (lower age = fresher = sort ascending)
        scored.sort(key=lambda j: -j["score"])

        new_jobs = [j for j in scored if j["url"] not in seen_urls]

        # ---- Liveness check on top jobs ----
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
        verified.sort(key=lambda j: j["score"], reverse=True)

        print(f"Scored: {len(scored)}, New: {len(new_jobs)}, Active: {len(verified)}, Expired: {len(expired)}")

        # ---- Ollama AI analysis ----
        verified = await analyze_jobs_with_ollama(verified)

        # ---- Build notifications ----
        elapsed = f"{time.time() - start_time:.1f}"
        source_count = len(GREENHOUSE_COMPANIES) + len(LEVER_COMPANIES) + 9

        stats = history["scan_stats"]
        stats["total_scans"] += 1
        stats["total_matches"] += len(verified)
        stats["last_scan_date"] = datetime.now(timezone.utc).isoformat()[:10]

        scan_info = {
            "elapsed": elapsed,
            "all_count": len(all_jobs),
            "source_count": source_count,
            "fresh_count": fresh_total,
            "near_misses": near_misses,
        }

        # ---- Generate Excel ----
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        excel_path = OUTPUT_DIR / f"careerops-scan-{date_str}.xls"
        try:
            excel_xml = generate_excel(verified, elapsed, near_misses, all_jobs, scan_info, stats)
            excel_path.write_text(excel_xml, encoding="utf-8")
            print(f"Excel saved: {excel_path}")
        except Exception as e:
            print(f"Excel generation failed: {e}")
            excel_path = None

        # ---- Send Telegram ----
        telegram_sent = False
        try:
            from notifier import build_telegram
            tg_msg = build_telegram(verified, scan_info, stats)
            telegram_sent = await send_telegram(tg_msg)
        except Exception as e:
            print(f"Telegram error: {e}")

        # ---- Send Email ----
        email_sent = False
        try:
            from notifier import build_email
            email_result = build_email(verified, scan_info, stats)
            email_subject = (
                f"CareerOps Scan - {date_str} - \u2705 {len(verified)} New Match{'es' if len(verified) != 1 else ''} Found"
                if verified
                else f"CareerOps Scan - {date_str} - \u2705 0 New Matches Found"
            )
            email_sent = await send_email(email_subject, email_result["text"], email_result["html"], str(excel_path) if excel_path else None)
        except Exception as e:
            print(f"Email error: {e}")

        # ---- Save history ----
        for j in scored:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        for j in near_misses:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        history["seen_urls"] = list(seen_urls)
        history["scan_stats"] = stats
        save_history(history)

        elapsed_final = f"{time.time() - start_time:.1f}"
        print(f"Scan complete in {elapsed_final}s. Telegram: {telegram_sent}, Email: {email_sent}")

        # Output JSON result for GitHub Actions
        result = {
            "matched": len(scored),
            "near_miss_count": len(near_misses),
            "verified_count": len(verified),
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
