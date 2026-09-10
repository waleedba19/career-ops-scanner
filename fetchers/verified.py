"""
Verified sources — fetchers for the candidates that the live `Probe Sources`
workflow confirmed respond with jobs from the GitHub Actions runner IP
(state/source_probe.md, first run 2026-09-06: 47 ok / 150).

Design rules (same as fetchers/social.py):
- Plain aiohttp, no API keys unless the env var is present (keyed aggregators
  silently return [] when their secret is missing — they light up the moment
  the secret is added to the repo).
- Every fetcher is *precision-first*: it asks the source for the candidate's
  own profile terms (arabic translator / esl / proofreader ...) instead of
  pulling a firehose and filtering afterwards.
- Never raise. Blocked (403/429/999), timeouts and parse errors return [].
- Pure parsers are separated from I/O so they can be unit-tested offline.
- Honest dates: `posted` is "" when the source does not give one — the
  scanner treats unknown as fresh, so we never fabricate timestamps.
- Honest locations: pass through what the source says so the worldwide gate
  (is_open_worldwide) can do its job.
"""
from __future__ import annotations

import asyncio
import html as _html
import os
import re
from datetime import datetime, timedelta, timezone

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.5",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.6",
}
TIMEOUT = aiohttp.ClientTimeout(total=15)

# The candidate's profile, as search terms. Kept short on purpose: each term is
# one HTTP request on most sources.
PROFILE_QUERIES = [
    "arabic translator",
    "arabic linguist",
    "esl teacher online",
    "proofreader editor",
]
FREELANCE_QUERIES = [
    "arabic translation",
    "english teacher",
    "proofreading editing",
]


def _clean(s: str) -> str:
    s = _html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _strip_html(s: str) -> str:
    return _clean(s)


async def _get_text(session: aiohttp.ClientSession, url: str, **kw) -> tuple[int, str]:
    """GET → (status, body). Never raises; (0, '') on transport error."""
    try:
        async with session.get(url, headers=kw.pop("headers", HEADERS), timeout=kw.pop("timeout", TIMEOUT), **kw) as r:
            return r.status, await r.text(errors="ignore")
    except Exception:
        return 0, ""


async def _get_json(session: aiohttp.ClientSession, url: str, **kw):
    try:
        async with session.get(url, headers=kw.pop("headers", HEADERS), timeout=kw.pop("timeout", TIMEOUT), **kw) as r:
            if r.status != 200:
                return r.status, None
            return 200, await r.json(content_type=None)
    except Exception:
        return 0, None


# ───────────────────────────────────────────────────────────────────────────
# 1. LinkedIn — public guest search (no login, no key)
#    Probe: 4/4 queries returned 10 fresh remote jobs each from the runner.
#    Limits: ~10 pages per IP before 429; we use 1 page × 4 queries.
#    HTTP 999 = LinkedIn anti-bot → stop the whole fetcher immediately.
# ───────────────────────────────────────────────────────────────────────────

LI_URL = ("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
          "?keywords={q}&location=Worldwide&f_WT=2&f_TPR=r86400&start=0")

_LI_CARD = re.compile(r'<li[^>]*>\s*<div[^>]*class="[^"]*base-card[^"]*"[\s\S]*?</li>', re.I)
_LI_LINK = re.compile(r'<a[^>]+class="[^"]*base-card__full-link[^"]*"[^>]+href="([^"]+)"', re.I)
_LI_TITLE = re.compile(r'class="[^"]*base-search-card__title[^"]*"[^>]*>([\s\S]*?)</h3>', re.I)
_LI_COMPANY = re.compile(r'class="[^"]*base-search-card__subtitle[^"]*"[^>]*>([\s\S]*?)</h4>', re.I)
_LI_LOCATION = re.compile(r'class="[^"]*job-search-card__location[^"]*"[^>]*>([\s\S]*?)</span>', re.I)
_LI_TIME = re.compile(r'<time[^>]+datetime="([^"]+)"', re.I)


def parse_linkedin_guest(html: str) -> list[dict]:
    """Pure parser for the guest search HTML fragment."""
    out: list[dict] = []
    cards = _LI_CARD.findall(html or "")
    if not cards:  # fallback: split on full-link anchors
        cards = re.split(r'(?=<a[^>]+class="[^"]*base-card__full-link)', html or "")[1:]
    for card in cards:
        m = _LI_LINK.search(card)
        t = _LI_TITLE.search(card)
        if not m or not t:
            continue
        url = _html.unescape(m.group(1)).split("?")[0]
        title = _clean(t.group(1))
        if not title or not url.startswith("http"):
            continue
        c = _LI_COMPANY.search(card)
        loc = _LI_LOCATION.search(card)
        tm = _LI_TIME.search(card)
        out.append({
            "title": title[:160],
            "company": _clean(c.group(1)) if c else "LinkedIn",
            "url": url,
            "location": _clean(loc.group(1)) if loc else "Remote",
            "posted": tm.group(1) if tm else "",
            "description": "",  # guest search has no description; enrichment happens downstream
            "salary": "",
            "source": "linkedin",
        })
    return out


async def fetch_linkedin_guest(session: aiohttp.ClientSession) -> list[dict]:
    jobs: list[dict] = []
    seen: set[str] = set()
    for q in PROFILE_QUERIES:
        url = LI_URL.format(q=q.replace(" ", "%20"))
        status, body = await _get_text(session, url)
        if status == 999:
            print("  LinkedIn: HTTP 999 (anti-bot) — stopping for this run")
            break
        if status == 429:
            print("  LinkedIn: HTTP 429 — backing off")
            await asyncio.sleep(3)
            continue
        if status != 200:
            continue
        for j in parse_linkedin_guest(body):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            # The query carries f_WT=2 (LinkedIn's own "Remote" workplace filter), so the
            # card location is the poster's city, not an on-site requirement. Say so —
            # otherwise "Dubai, United Arab Emirates" trips the City, Country heuristic.
            if not re.search(r"remote", j["location"], re.I):
                j["location"] = f"Remote — {j['location']}"
            # NEVER echo the search query into the description: the scorer reads it and
            # would grade "Chinese Translator" as a 100-point Arabic match. Neutral text →
            # scoring is title-only (honest), and `matched_query` is kept for the report.
            j["description"] = "Remote (LinkedIn workplace filter). Open the posting for the full description."
            j["matched_query"] = q
            jobs.append(j)
        await asyncio.sleep(1.2)  # pace like a human
    print(f"  LinkedIn guest: {len(jobs)} jobs from {len(PROFILE_QUERIES)} queries")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 2. Freelancer.com — public projects API (keyword-precise; the generic RSS
#    already converts at 17 % and produces >50 % of all matches)
# ───────────────────────────────────────────────────────────────────────────

FL_URL = ("https://www.freelancer.com/api/projects/0.1/projects/active/"
          "?query={q}&limit=30&compact=true&full_description=true")  # probe-verified shape (default sort = newest)


def parse_freelancer_projects(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    projects = ((payload.get("result") or {}).get("projects")) or []
    for p in projects:
        if not isinstance(p, dict):
            continue
        title = (p.get("title") or "").strip()
        seo = p.get("seo_url") or ""
        if not title or not seo:
            continue
        ts = p.get("time_submitted") or p.get("time_updated")
        posted = ""
        if isinstance(ts, (int, float)):
            try:
                posted = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            except Exception:
                posted = ""
        budget = p.get("budget") or {}
        cur = (p.get("currency") or {}).get("code") or ""
        salary = ""
        if isinstance(budget, dict) and budget.get("minimum") is not None:
            salary = f"{budget.get('minimum')}-{budget.get('maximum') or ''} {cur}".strip("- ")
        out.append({
            "title": title[:160],
            "company": "Freelancer.com",
            "url": f"https://www.freelancer.com/projects/{seo}",
            "location": "Remote (Worldwide)",
            "posted": posted,
            "description": _clean(p.get("description") or p.get("preview_description") or "")[:2000],
            "salary": salary,
            "source": "freelancer",
        })
    return out


async def fetch_freelancer_api(session: aiohttp.ClientSession) -> list[dict]:
    jobs: list[dict] = []
    seen: set[str] = set()
    for q in FREELANCE_QUERIES:
        status, data = await _get_json(session, FL_URL.format(q=q.replace(" ", "%20")))
        if status != 200:
            continue
        for j in parse_freelancer_projects(data):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    print(f"  Freelancer API: {len(jobs)} projects from {len(FREELANCE_QUERIES)} queries")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 3. Jobicy — tag-filtered feed (probe: tag=translation → 44 items incl.
#    'Translation Project Manager'); complements the generic geo=anywhere pull
# ───────────────────────────────────────────────────────────────────────────

JOBICY_TAG_URL = "https://jobicy.com/api/v2/remote-jobs?count=50&tag={tag}"
JOBICY_TAGS = ["translation", "teaching", "writing"]


def parse_jobicy(payload, source: str = "jobicy") -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("jobs") or []:
        if not isinstance(j, dict) or not j.get("jobTitle"):
            continue
        salary = ""
        if j.get("salaryMin") and j.get("salaryMax"):
            salary = f"{j['salaryMin']}-{j['salaryMax']} {j.get('salaryCurrency', '')} / {j.get('salaryPeriod', 'yearly')}"
        out.append({
            "title": j.get("jobTitle", ""),
            "company": j.get("companyName", ""),
            "url": j.get("url", ""),
            "location": j.get("jobGeo") or "Remote",
            "posted": j.get("pubDate", ""),
            "description": _clean(j.get("jobDescription") or j.get("jobExcerpt") or "")[:3000],
            "salary": salary,
            "source": source,
        })
    return out


async def fetch_jobicy_tags(session: aiohttp.ClientSession) -> list[dict]:
    jobs: list[dict] = []
    seen: set[str] = set()
    for tag in JOBICY_TAGS:
        status, data = await _get_json(session, JOBICY_TAG_URL.format(tag=tag))
        if status != 200:
            continue
        for j in parse_jobicy(data):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    print(f"  Jobicy tags: {len(jobs)} jobs from {len(JOBICY_TAGS)} tags")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 4. Working Nomads — structured JSON (replaces the HTML/RSS scrape)
# ───────────────────────────────────────────────────────────────────────────

WN_URL = "https://www.workingnomads.com/api/exposed_jobs/"


def parse_workingnomads(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, list):
        return out
    for j in payload:
        if not isinstance(j, dict) or not j.get("title") or not j.get("url"):
            continue
        out.append({
            "title": j.get("title", "").strip()[:160],
            "company": (j.get("company_name") or "Working Nomads").strip(),
            "url": j.get("url", ""),
            "location": (j.get("location") or "Remote").strip(),
            "posted": j.get("pub_date") or "",
            "description": _clean(j.get("description") or "")[:3000],
            "salary": "",
            "source": "workingnomads",
        })
    return out


async def fetch_workingnomads_json(session: aiohttp.ClientSession) -> list[dict]:
    status, data = await _get_json(session, WN_URL)
    jobs = parse_workingnomads(data) if status == 200 else []
    print(f"  Working Nomads JSON: {len(jobs)} jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 5. Impactpool — UN / NGO search (probe: 'Interpreter – Arabic/Sudanese
#    Arabic (IRC)', 'Interpreter (Arabic) (IOM)'). Server-rendered cards.
# ───────────────────────────────────────────────────────────────────────────

IMPACTPOOL_URL = "https://www.impactpool.org/search?q={q}"
IMPACTPOOL_QUERIES = ["arabic interpreter", "arabic translator", "translation"]
_IP_CARD = re.compile(r'<a[^>]+href="(https?://www\.impactpool\.org/jobs/\d+|/jobs/\d+)"[^>]*>([\s\S]*?)</a>', re.I)


def parse_impactpool(html: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for href, inner in _IP_CARD.findall(html or ""):
        url = href if href.startswith("http") else "https://www.impactpool.org" + href
        if url in seen:
            continue
        # card text is: title / org / location / grade separated by block tags
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        parts = [p for p in parts if not re.fullmatch(r"(closing today|new|remote)", p, re.I)]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        org = parts[1] if len(parts) > 1 else "Impactpool"
        loc = parts[2] if len(parts) > 2 else ""
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": org[:120],
            "url": url,
            "location": loc or "See posting",
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "impactpool",
        })
    return out


async def fetch_impactpool(session: aiohttp.ClientSession) -> list[dict]:
    jobs: list[dict] = []
    seen: set[str] = set()
    for q in IMPACTPOOL_QUERIES:
        status, body = await _get_text(session, IMPACTPOOL_URL.format(q=q.replace(" ", "+")))
        if status != 200:
            continue
        for j in parse_impactpool(body):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    print(f"  Impactpool: {len(jobs)} UN/NGO postings")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 6. The Muse — public API, no key (probe: 20 items in Writing & Editing)
# ───────────────────────────────────────────────────────────────────────────

MUSE_URL = "https://www.themuse.com/api/public/jobs?page={page}&category={cat}"
MUSE_CATEGORIES = ["Writing%20and%20Editing", "Education"]


def parse_themuse(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("results") or []:
        if not isinstance(j, dict) or not j.get("name"):
            continue
        locs = [l.get("name", "") for l in (j.get("locations") or []) if isinstance(l, dict)]
        refs = j.get("refs") or {}
        out.append({
            "title": j.get("name", "")[:160],
            "company": ((j.get("company") or {}).get("name") or "The Muse").strip(),
            "url": refs.get("landing_page") or "",
            "location": ", ".join(locs) or "See posting",
            "posted": j.get("publication_date") or "",
            "description": _clean(j.get("contents") or "")[:3000],
            "salary": "",
            "source": "themuse",
        })
    return [j for j in out if j["url"]]


async def fetch_themuse(session: aiohttp.ClientSession) -> list[dict]:
    jobs: list[dict] = []
    for cat in MUSE_CATEGORIES:
        status, data = await _get_json(session, MUSE_URL.format(page=1, cat=cat))
        if status != 200:
            continue
        jobs.extend(parse_themuse(data))
    # Muse is mostly on-site US roles; keep only remote-flagged ones to avoid noise
    jobs = [j for j in jobs if re.search(r"remote|flexible|anywhere", j["location"], re.I)]
    print(f"  The Muse: {len(jobs)} remote jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 7. Generic ATS adapters — Ashby / Workable / SmartRecruiters
#    (Greenhouse & Lever already exist in scanner.py). Each takes a list of
#    (display_name, slug) from config, exactly like GREENHOUSE_COMPANIES.
# ───────────────────────────────────────────────────────────────────────────

def parse_ashby(payload, company: str) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("jobs") or []:
        if not isinstance(j, dict) or not j.get("title"):
            continue
        loc = j.get("location") or ""
        if j.get("isRemote"):
            loc = f"Remote — {loc}" if loc else "Remote"
        out.append({
            "title": j.get("title", "")[:160],
            "company": company,
            "url": j.get("jobUrl") or j.get("applyUrl") or "",
            "location": loc or "See posting",
            "posted": j.get("publishedAt") or "",
            "description": _clean(j.get("descriptionPlain") or j.get("descriptionHtml") or "")[:3000],
            "salary": "",
            "source": "ashby",
        })
    return [j for j in out if j["url"]]


async def fetch_ashby_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, data = await _get_json(session, f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
    return parse_ashby(data, company) if status == 200 else []


def parse_workable(payload, company: str) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("jobs") or []:
        if not isinstance(j, dict) or not j.get("title"):
            continue
        loc_bits = [j.get("city") or "", j.get("country") or ""]
        loc = ", ".join(b for b in loc_bits if b)
        if j.get("remote") or (j.get("workplace") or "").lower() == "remote":
            loc = f"Remote — {loc}" if loc else "Remote"
        out.append({
            "title": j.get("title", "")[:160],
            "company": company,
            "url": j.get("url") or j.get("shortlink") or j.get("application_url") or "",
            "location": loc or "See posting",
            "posted": j.get("published_on") or j.get("created_at") or "",
            "description": _clean(j.get("description") or "")[:3000],
            "salary": "",
            "source": "workable",
        })
    return [j for j in out if j["url"]]


async def fetch_workable_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, data = await _get_json(session, f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true")
    return parse_workable(data, company) if status == 200 else []


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", s or "")


def parse_smartrecruiters(payload, company: str) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("content") or []:
        if not isinstance(j, dict) or not j.get("name"):
            continue
        loc = j.get("location") or {}
        bits = [loc.get("city") or "", loc.get("country") or ""] if isinstance(loc, dict) else []
        loc_s = ", ".join(b for b in bits if b)
        if isinstance(loc, dict) and loc.get("remote"):
            loc_s = f"Remote — {loc_s}" if loc_s else "Remote"
        jid = j.get("id") or ""
        out.append({
            "title": j.get("name", "")[:160],
            "company": company,
            "url": f"https://jobs.smartrecruiters.com/{j.get('company', {}).get('identifier', '') or slugify(company)}/{jid}" if jid else "",
            "location": loc_s or "See posting",
            "posted": j.get("releasedDate") or "",
            "description": "",  # list endpoint has no description; downstream enrichment
            "salary": "",
            "source": "smartrecruiters",
        })
    return [j for j in out if j["url"]]


async def fetch_smartrecruiters_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    # the list endpoint supports a keyword filter → precision, not a firehose
    jobs: list[dict] = []
    seen: set[str] = set()
    for q in ("arabic", "translator", "linguist", "localization", "english teacher", "editor"):
        status, data = await _get_json(
            session, f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?q={q.replace(' ', '%20')}&limit=50")
        if status != 200:
            continue
        for j in parse_smartrecruiters(data, company):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 8. Keyed aggregators — the sanctioned route to Indeed / LinkedIn / Glassdoor
#    inventory. Each returns [] until its secret exists.
# ───────────────────────────────────────────────────────────────────────────

def parse_jsearch(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("data") or []:
        if not isinstance(j, dict) or not j.get("job_title"):
            continue
        loc = ", ".join(x for x in (j.get("job_city"), j.get("job_state"), j.get("job_country")) if x)
        if j.get("job_is_remote"):
            loc = f"Remote — {loc}" if loc else "Remote"
        salary = ""
        if j.get("job_min_salary") and j.get("job_max_salary"):
            salary = f"{j['job_min_salary']}-{j['job_max_salary']} {j.get('job_salary_currency', '')} / {j.get('job_salary_period', '')}".strip()
        out.append({
            "title": j.get("job_title", "")[:160],
            "company": j.get("employer_name") or "",
            "url": j.get("job_apply_link") or j.get("job_google_link") or "",
            "location": loc or "See posting",
            "posted": j.get("job_posted_at_datetime_utc") or "",
            "description": _clean(j.get("job_description") or "")[:3000],
            "salary": salary,
            "source": f"jsearch:{(j.get('job_publisher') or 'google').lower()}",
        })
    return [j for j in out if j["url"]]


async def fetch_jsearch(session: aiohttp.ClientSession) -> list[dict]:
    key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not key:
        return []
    hdrs = {**HEADERS, "X-RapidAPI-Key": key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
    jobs: list[dict] = []
    seen: set[str] = set()
    # Free plan has a small monthly cap: 2 queries × 3 runs/day ≈ 180 calls/month.
    for q in ("arabic translator", "esl teacher online"):
        url = ("https://jsearch.p.rapidapi.com/search?query={q}&page=1&num_pages=1"
               "&remote_jobs_only=true&date_posted=today").format(q=q.replace(" ", "%20"))
        status, data = await _get_json(session, url, headers=hdrs)
        if status != 200:
            print(f"  JSearch: HTTP {status}")
            continue
        for j in parse_jsearch(data):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    print(f"  JSearch (Google for Jobs → Indeed/LinkedIn/Glassdoor): {len(jobs)} jobs")
    return jobs


def parse_adzuna(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("results") or []:
        if not isinstance(j, dict) or not j.get("title"):
            continue
        salary = ""
        if j.get("salary_min") and j.get("salary_max"):
            salary = f"{int(j['salary_min'])}-{int(j['salary_max'])}"
        out.append({
            "title": _clean(j.get("title", ""))[:160],
            "company": ((j.get("company") or {}).get("display_name") or "").strip(),
            "url": j.get("redirect_url") or "",
            "location": ((j.get("location") or {}).get("display_name") or "See posting").strip(),
            "posted": j.get("created") or "",
            "description": _clean(j.get("description") or "")[:3000],
            "salary": salary,
            "source": "adzuna",
        })
    return [j for j in out if j["url"]]


async def fetch_adzuna(session: aiohttp.ClientSession) -> list[dict]:
    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    if not app_id or not app_key:
        return []
    jobs: list[dict] = []
    seen: set[str] = set()
    # 1,000 free calls/month → 2 countries × 3 runs/day ≈ 180 calls/month.
    for country in ("gb", "us"):
        url = (f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={app_id}&app_key={app_key}"
               "&results_per_page=50&what_or=arabic%20translator%20esl%20proofreader%20localization%20linguist"
               "&sort_by=date&content-type=application/json")
        status, data = await _get_json(session, url)
        if status != 200:
            print(f"  Adzuna {country}: HTTP {status}")
            continue
        for j in parse_adzuna(data):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    print(f"  Adzuna: {len(jobs)} jobs")
    return jobs


def parse_jooble(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("jobs") or []:
        if not isinstance(j, dict) or not j.get("title"):
            continue
        out.append({
            "title": _clean(j.get("title", ""))[:160],
            "company": (j.get("company") or "").strip(),
            "url": j.get("link") or "",
            "location": (j.get("location") or "See posting").strip(),
            "posted": j.get("updated") or "",
            "description": _clean(j.get("snippet") or "")[:2000],
            "salary": (j.get("salary") or "").strip(),
            "source": "jooble",
        })
    return [j for j in out if j["url"]]


async def fetch_jooble(session: aiohttp.ClientSession) -> list[dict]:
    key = os.getenv("JOOBLE_API_KEY", "").strip()
    if not key:
        return []
    jobs: list[dict] = []
    seen: set[str] = set()
    for q in ("arabic translator", "esl teacher", "proofreader"):
        try:
            async with session.post(f"https://jooble.org/api/{key}", json={"keywords": q, "location": "remote"},
                                    headers={**HEADERS, "Content-Type": "application/json"}, timeout=TIMEOUT) as r:
                if r.status != 200:
                    print(f"  Jooble: HTTP {r.status}")
                    continue
                data = await r.json(content_type=None)
        except Exception as e:
            print(f"  Jooble: {e}")
            continue
        for j in parse_jooble(data):
            if j["url"] in seen:
                continue
            seen.add(j["url"])
            jobs.append(j)
    print(f"  Jooble: {len(jobs)} jobs")
    return jobs


def parse_reliefweb(payload) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for item in payload.get("data") or []:
        f = (item or {}).get("fields") or {}
        if not f.get("title"):
            continue
        src = f.get("source") or []
        org = src[0].get("name", "") if src and isinstance(src[0], dict) else ""
        countries = f.get("country") or []
        loc = ", ".join(c.get("name", "") for c in countries if isinstance(c, dict)) or "See posting"
        out.append({
            "title": f.get("title", "")[:160],
            "company": org or "ReliefWeb",
            "url": f.get("url") or f.get("url_alias") or "",
            "location": loc,
            "posted": ((f.get("date") or {}).get("created")) or "",
            "description": _clean(f.get("body") or "")[:3000],
            "salary": "",
            "source": "reliefweb",
        })
    return [j for j in out if j["url"]]


async def fetch_reliefweb(session: aiohttp.ClientSession) -> list[dict]:
    appname = os.getenv("RELIEFWEB_APPNAME", "").strip()
    if not appname:
        return []
    url = (f"https://api.reliefweb.int/v2/jobs?appname={appname}&query[value]=arabic%20AND%20(translator%20OR%20interpreter%20OR%20translation)"
           "&limit=40&sort[]=date.created:desc"
           "&fields[include][]=title&fields[include][]=url&fields[include][]=source.name"
           "&fields[include][]=date.created&fields[include][]=country.name&fields[include][]=body")
    status, data = await _get_json(session, url)
    jobs = parse_reliefweb(data) if status == 200 else []
    print(f"  ReliefWeb: {len(jobs)} UN/NGO jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 9. Remowork — curated remote Arabic jobs board (probe: 209 items)
# ───────────────────────────────────────────────────────────────────────────

REMOWORK_URL = "https://remowork.life/jobs/languages/arabic"
_REMOWORK_CARD = re.compile(r'<a[^>]+href="(https?://remowork\.life/jobs/[^"]+)"[^>]*>([\s\S]*?)</a>', re.I)


def parse_remowork(html: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for href, inner in _REMOWORK_CARD.findall(html or ""):
        url = href if href.startswith("http") else "https://remowork.life" + href
        if url in seen or "/jobs/" not in url:
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        company = parts[1] if len(parts) > 1 else "Remowork"
        loc = parts[2] if len(parts) > 2 else "Remote"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company[:120],
            "url": url,
            "location": loc or "Remote",
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "remowork",
        })
    return out


async def fetch_remowork(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, REMOWORK_URL)
    jobs = parse_remowork(body) if status == 200 else []
    print(f"  Remowork: {len(jobs)} Arabic remote jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 10. ESLbase — ESL teaching jobs (probe: 44 items)
# ───────────────────────────────────────────────────────────────────────────

ESLBASE_URL = "https://www.eslbase.com/teaching-jobs"
_ESLBASE_CARD = re.compile(r'<a[^>]+href="(https?://www\.eslbase\.com/teaching-jobs/[^"]+)"[^>]*>([\s\S]*?)</a>', re.I)


def parse_eslbase(html: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for href, inner in _ESLBASE_CARD.findall(html or ""):
        url = href if href.startswith("http") else "https://www.eslbase.com" + href
        if url in seen:
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        company = parts[1] if len(parts) > 1 else "ESL School"
        loc = parts[2] if len(parts) > 2 else "See posting"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company[:120],
            "url": url,
            "location": loc or "See posting",
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "eslbase",
        })
    return out


async def fetch_eslbase(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, ESLBASE_URL)
    jobs = parse_eslbase(body) if status == 200 else []
    print(f"  ESLbase: {len(jobs)} ESL jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 11. Recruitee — ATS adapter (new)
# ───────────────────────────────────────────────────────────────────────────

def parse_recruitee(payload, company: str) -> list[dict]:
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    for j in payload.get("offers") or []:
        if not isinstance(j, dict) or not j.get("title"):
            continue
        loc = j.get("location") or ""
        if j.get("remote"):
            loc = f"Remote — {loc}" if loc else "Remote"
        out.append({
            "title": j.get("title", "")[:160],
            "company": company,
            "url": j.get("careers_url") or j.get("apply_url") or "",
            "location": loc or "See posting",
            "posted": j.get("created_at") or "",
            "description": _clean(j.get("description") or "")[:3000],
            "salary": "",
            "source": "recruitee",
        })
    return [j for j in out if j["url"]]


async def fetch_recruitee_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, data = await _get_json(session, f"https://{slug}.recruitee.com/api/offers/")
    return parse_recruitee(data, company) if status == 200 else []


# ───────────────────────────────────────────────────────────────────────────
# 12. Teamtailor — ATS adapter (new)
# ───────────────────────────────────────────────────────────────────────────

def parse_teamtailor_rss(xml: str, company: str) -> list[dict]:
    out: list[dict] = []
    items = re.findall(r'<item>([\s\S]*?)</item>', xml or "")
    for item in items:
        title_m = re.search(r'<title[^>]*>([\s\S]*?)</title>', item)
        link_m = re.search(r'<link[^>]*>([\s\S]*?)</link>', item)
        desc_m = re.search(r'<description[^>]*>([\s\S]*?)</description>', item)
        if not title_m or not link_m:
            continue
        title = _clean(title_m.group(1))
        url = _clean(link_m.group(1))
        desc = _clean(desc_m.group(1)) if desc_m else ""
        if not title or not url:
            continue
        out.append({
            "title": title[:160],
            "company": company,
            "url": url,
            "location": "See posting",
            "posted": "",
            "description": desc[:2000],
            "salary": "",
            "source": "teamtailor",
        })
    return out


async def fetch_teamtailor_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, body = await _get_text(session, f"https://{slug}.teamtailor.com/jobs.rss")
    return parse_teamtailor_rss(body, company) if status == 200 else []


# ───────────────────────────────────────────────────────────────────────────
# 13. EU Remote Jobs — RSS feed (free, no key)
# ───────────────────────────────────────────────────────────────────────────

EUREMOTEJOBS_URL = "https://euremotejobs.com/?feed=job_feed"


def parse_rss_generic(xml: str, source: str) -> list[dict]:
    """Generic RSS parser for job feeds."""
    out: list[dict] = []
    items = re.findall(r'<item>([\s\S]*?)</item>', xml or "")
    for item in items:
        title_m = re.search(r'<title[^>]*>([\s\S]*?)</title>', item)
        link_m = re.search(r'<link[^>]*>([\s\S]*?)</link>', item)
        desc_m = re.search(r'<description[^>]*>([\s\S]*?)</description>', item)
        pub_m = re.search(r'<pubDate[^>]*>([\s\S]*?)</pubDate>', item)
        if not title_m or not link_m:
            continue
        title = _clean(title_m.group(1))
        url = _clean(link_m.group(1))
        desc = _clean(desc_m.group(1)) if desc_m else ""
        posted = _clean(pub_m.group(1)) if pub_m else ""
        if not title or not url:
            continue
        out.append({
            "title": title[:160],
            "company": source,
            "url": url,
            "location": "Remote",
            "posted": posted,
            "description": desc[:2000],
            "salary": "",
            "source": source,
        })
    return out


async def fetch_euremotejobs(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, EUREMOTEJOBS_URL)
    jobs = parse_rss_generic(body, "euremotejobs") if status == 200 else []
    print(f"  EU Remote Jobs: {len(jobs)} jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 14. Remote Job Leads — RSS feed (free, no key)
# ───────────────────────────────────────────────────────────────────────────

REMOTEJOBLEADS_URL = "https://www.remotejobleads.com/feed/"


async def fetch_remotejobleads(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, REMOTEJOBLEADS_URL)
    jobs = parse_rss_generic(body, "remotejobleads") if status == 200 else []
    print(f"  Remote Job Leads: {len(jobs)} jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 15. DailyRemote — HTML scrape (free, no key)
# ───────────────────────────────────────────────────────────────────────────

DAILYREMOTE_URL = "https://dailyremote.com/remote-jobs"
_DAILYREMOTE_CARD = re.compile(r'<a[^>]+href="(https?://dailyremote\.com/remote-jobs/[^"]+)"[^>]*>([\s\S]*?)</a>', re.I)


def parse_dailyremote(html: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for href, inner in _DAILYREMOTE_CARD.findall(html or ""):
        url = href if href.startswith("http") else "https://dailyremote.com" + href
        if url in seen or "/remote-jobs/" not in url:
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        company = parts[1] if len(parts) > 1 else "DailyRemote"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company[:120],
            "url": url,
            "location": "Remote",
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "dailyremote",
        })
    return out


async def fetch_dailyremote(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, DAILYREMOTE_URL)
    jobs = parse_dailyremote(body) if status == 200 else []
    print(f"  DailyRemote: {len(jobs)} jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 16. Dynamite Jobs — HTML scrape (free, no key)
# ───────────────────────────────────────────────────────────────────────────

DYNAMITEJOBS_URL = "https://dynamitejobs.com/remote-jobs"
_DYNAMITE_CARD = re.compile(r'<a[^>]+href="(https?://dynamitejobs\.com/remote-jobs/[^"]+)"[^>]*>([\s\S]*?)</a>', re.I)


def parse_dynamitejobs(html: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for href, inner in _DYNAMITE_CARD.findall(html or ""):
        url = href if href.startswith("http") else "https://dynamitejobs.com" + href
        if url in seen or "/remote-jobs/" not in url:
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        company = parts[1] if len(parts) > 1 else "Dynamite Jobs"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company[:120],
            "url": url,
            "location": "Remote",
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "dynamitejobs",
        })
    return out


async def fetch_dynamitejobs(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, DYNAMITEJOBS_URL)
    jobs = parse_dynamitejobs(body) if status == 200 else []
    print(f"  Dynamite Jobs: {len(jobs)} jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 17. Europe Remotely — HTML scrape (free, no key)
# ───────────────────────────────────────────────────────────────────────────

EUROPEREMOTELY_URL = "https://europeremotely.com/"
_EUROPE_CARD = re.compile(r'<a[^>]+href="(https?://europeremotely\.com/[^"]+)"[^>]*>([\s\S]*?)</a>', re.I)


def parse_europeremotely(html: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for href, inner in _EUROPE_CARD.findall(html or ""):
        url = href if href.startswith("http") else "https://europeremotely.com" + href
        if url in seen or "/job" not in url.lower():
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        company = parts[1] if len(parts) > 1 else "Europe Remotely"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company[:120],
            "url": url,
            "location": "Remote (Europe)",
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "europeremotely",
        })
    return out


async def fetch_europeremotely(session: aiohttp.ClientSession) -> list[dict]:
    status, body = await _get_text(session, EUROPEREMOTELY_URL)
    jobs = parse_europeremotely(body) if status == 200 else []
    print(f"  Europe Remotely: {len(jobs)} jobs")
    return jobs


# ───────────────────────────────────────────────────────────────────────────
# 18. BambooHR — ATS adapter (HTML-based)
# ───────────────────────────────────────────────────────────────────────────

def parse_bamboohr_html(html: str, company: str) -> list[dict]:
    """Parse BambooHR careers page (HTML). Looks for job cards with title + link."""
    out: list[dict] = []
    seen: set[str] = set()
    # BambooHR uses structured job cards — look for links to /jobs/ or /careers/
    cards = re.findall(r'<a[^>]+href="(/jobs/[^"]+|/careers/[^"]+)"[^>]*>([\s\S]*?)</a>', html or "", re.I)
    for href, inner in cards:
        url = f"https://{company}.bamboohr.com" + href if not href.startswith("http") else href
        if url in seen:
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        loc = parts[1] if len(parts) > 1 else "See posting"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company,
            "url": url,
            "location": loc,
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "bamboohr",
        })
    # Fallback: look for JSON-LD JobPosting
    if not out:
        ld = re.findall(r'"@type"\s*:\s*"JobPosting"[\s\S]{0,400}?"title"\s*:\s*"([^"]{3,120})"', html or "")
        url_m = re.findall(r'"@type"\s*:\s*"JobPosting"[\s\S]{0,400}?"url"\s*:\s*"([^"]+)"', html or "")
        for i, title in enumerate(ld):
            url = url_m[i] if i < len(url_m) else ""
            if url and url not in seen:
                seen.add(url)
                out.append({
                    "title": title[:160],
                    "company": company,
                    "url": url,
                    "location": "See posting",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "bamboohr",
                })
    return out


async def fetch_bamboohr_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, body = await _get_text(session, f"https://{slug}.bamboohr.com/careers/list")
    return parse_bamboohr_html(body, company) if status == 200 else []


# ───────────────────────────────────────────────────────────────────────────
# 22. Jobvite — ATS adapter (new)
# ───────────────────────────────────────────────────────────────────────────

def parse_jobvite_rss(xml: str, company: str) -> list[dict]:
    out: list[dict] = []
    items = re.findall(r'<item>([\s\S]*?)</item>', xml or "")
    for item in items:
        title_m = re.search(r'<title[^>]*>([\s\S]*?)</title>', item)
        link_m = re.search(r'<link[^>]*>([\s\S]*?)</link>', item)
        desc_m = re.search(r'<description[^>]*>([\s\S]*?)</description>', item)
        if not title_m or not link_m:
            continue
        title = _clean(title_m.group(1))
        url = _clean(link_m.group(1))
        desc = _clean(desc_m.group(1)) if desc_m else ""
        if not title or not url:
            continue
        out.append({
            "title": title[:160],
            "company": company,
            "url": url,
            "location": "See posting",
            "posted": "",
            "description": desc[:2000],
            "salary": "",
            "source": "jobvite",
        })
    return out


async def fetch_jobvite_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, body = await _get_text(session, f"https://jobs.jobvite.com/{slug}/search?nl=1&format=rss")
    return parse_jobvite_rss(body, company) if status == 200 else []


# ───────────────────────────────────────────────────────────────────────────
# 23. Personio — ATS adapter (new)
# ───────────────────────────────────────────────────────────────────────────

def parse_personio_html(html: str, company: str) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    # Personio uses structured job cards
    cards = re.findall(r'<a[^>]+href="(/job-offer/[^"]+)"[^>]*>([\s\S]*?)</a>', html or "")
    for href, inner in cards:
        url = f"https://{company}.jobs.personio.com" + href if not href.startswith("http") else href
        if url in seen:
            continue
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if not parts:
            continue
        title = parts[0]
        if len(title) < 5:
            continue
        loc = parts[1] if len(parts) > 1 else "See posting"
        seen.add(url)
        out.append({
            "title": title[:160],
            "company": company,
            "url": url,
            "location": loc,
            "posted": "",
            "description": " · ".join(parts[1:])[:500],
            "salary": "",
            "source": "personio",
        })
    return out


async def fetch_personio_board(session: aiohttp.ClientSession, company: str, slug: str) -> list[dict]:
    status, body = await _get_text(session, f"https://{slug}.jobs.personio.com/search?query=")
    return parse_personio_html(body, company) if status == 200 else []
