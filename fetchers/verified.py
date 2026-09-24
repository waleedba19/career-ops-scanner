"""
Verified sources — fetchers for the candidates that the live `Probe Sources`
workflow confirmed respond with jobs from the GitHub Actions runner IP
(state/source_probe.md, first run 2026-09-06: 47 ok / 150).

Design rules (same as fetchers/social.py):
- Plain aiohttp, no API keys unless the env var is present (keyed aggregators
  silently return [] when their secret is missing — they light up the moment
  the secret is added to the repo).
- Every fetcher is *precision-first*: it asks the source for the candidate's
  own profile terms (arabic translator / proofreader / localization ...) instead of
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
    "bilingual translator",
    "proofreader editor",
]
FREELANCE_QUERIES = [
    "arabic translation",
    "arabic english localization",
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

# Real posting detail (guest fragment) — NOT the search-filter tag. LinkedIn's
# f_WT=2 only proves the employer TAGGED the role as remote; the posting text
# decides. We fetch each posting so the worldwide gate / AI / email see truth.
_LI_JOB_VIEW = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
# Real guest cards: "/jobs/view/4465128678" (numeric) or "/jobs/view/<slug>-4465128678",
# or carry the id in data-entity-urn. Match either form so the detail fetch fires.
_LI_JOBID = re.compile(r"urn:li:jobPosting:(\d+)|/jobs/view/[^\s?#\"]*?(\d{6,})(?=[?#\"\s]|$)", re.I)
_LI_WORKPLACE_TAG = re.compile(r'class="[^"]*job-posting__workplace-type[^"]*"[^>]*>\s*([^<]+?)\s*<', re.I)
_LI_DESC_MARKUP = re.compile(r'class="show-more-less-html__markup"[^>]*>([\s\S]*?)</div>', re.I)
_LI_DESC_CLASSIC = re.compile(r'class="description__text[^"]*"[^>]*>([\s\S]*?)</div>', re.I)


def _workplace_infer(desc: str) -> str:
    """Workplace from the posting text: on-site > hybrid > remote by evidence.

    The f_WT=2 search filter only means the employer TAGGED the role Remote —
    it says nothing about reality, so the description is the truth. Remote is
    the default ONLY with no contrary evidence.
    """
    t = (desc or "").lower()
    # Explicit hybrid self-identification, or a per-week office split — these
    # come first because they are the poster's own words about the model
    # ("Hybrid role…", "3 days in office").
    hybrid = re.compile(
        r"\bhybrid\s+(role|position|posting|model|schedule|arrangement|setup|working\s+arrangement)"
        r"|\d+\s+days?\s+(a\s+week\s+)?(in[ -]office|on[ -]site|on\s+site)", re.I)
    onsite = re.compile(
        r"\bin[- ]office\s+role\b|\bin[- ]office\b|on[- ]site\b|on site\b|office[- ]based|"
        r"work\s+from\s+(the\s+)?office|work\s+in[- ]person|"
        r"must\s+(be|report|work)\s+(in|at)\s+the\s+office|office\s+\bin\b|"
        r"attend\s+(the\s+)?office|in[- ]person\s+(work|requirement|role)", re.I)
    if hybrid.search(t):
        return "Hybrid"
    if onsite.search(t):
        return "On-site"
    return "Remote"


def _linkedin_location(city: str, wtag: str, desc: str, verified: bool) -> str:
    """Truthful location for a LinkedIn guest-search job.

    verified=True  → posting detail was fetched; use its real workplace tag /
                     description prefix before the card city.
    verified=False → could not fetch; NEVER assert Remote from the f_WT=2
                     filter alone — return the real city so the worldwide gate
                     and AI audit can judge honestly instead.
    """
    city = (city or "").strip() or "See posting"
    if not verified:
        return city
    wt = (wtag or "").strip().lower()
    if wt in ("on-site", "onsite"):
        return f"On-site — {city}"
    if wt == "hybrid":
        return f"Hybrid — {city}"
    if wt == "remote":
        return f"Remote — {city}"
    w = _workplace_infer(desc or "")
    if w != "Remote":
        return f"{w} — {city}"
    return f"Remote — {city}"


async def _linkedin_detail(session: aiohttp.ClientSession, url: str) -> tuple[bool, str, str]:
    """Fetch the real posting detail (guest fragment). → (ok, description, workplace_tag).
    Never raises; anti-bot (999/429) or transport errors → (False, "", "").
    """
    m = _LI_JOBID.search(url or "")
    if not m:
        return False, "", ""
    job_id = m.group(1) or m.group(2)
    if not job_id:
        return False, "", ""
    status, body = await _get_text(session, _LI_JOB_VIEW.format(job_id=job_id))
    if status != 200:
        return False, "", ""
    desc = ""
    for rx in (_LI_DESC_MARKUP, _LI_DESC_CLASSIC):
        fm = rx.search(body)
        if fm:
            desc = _clean(fm.group(1))
            break
    if not desc:
        desc = _clean(re.sub(r"<[^>]+>", " ", body))[:3000]
    wt = _LI_WORKPLACE_TAG.search(body)
    return True, desc[:3000], (wt.group(1).strip() if wt else "")


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
    # Budget the per-posting detail fetches so a burst can't blow the 429 limit.
    detail_budget = 18
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
            j["matched_query"] = q
            city = j.get("location") or "See posting"
            ok, desc, wtag = False, "", ""
            if detail_budget > 0:
                ok, desc, wtag = await _linkedin_detail(session, j["url"])
                detail_budget -= 1
                await asyncio.sleep(0.7)  # pace; LinkedIn rate-limits per IP
            # Real description (may legitimately be "") — never the search query.
            j["description"] = desc
            # Truthful location — f_WT=2 alone is NOT proof of remote.
            j["location"] = _linkedin_location(city, wtag, desc, ok)
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
JOBICY_TAGS = ["translation", "writing", "localization"]


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
    for q in ("arabic translator", "bilingual translator"):
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
               "&results_per_page=50&what_or=arabic%20translator%20bilingual%20proofreader%20localization%20linguist"
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
    for q in ("arabic translator", "bilingual translator", "proofreader"):
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


# ============================================================================
# NEW BATCH FETCHERS — Added for source expansion
# ============================================================================

async def fetch_upwork(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Upwork RSS feed."""
    url = "https://www.upwork.com/ab/feed/jobs/rss?q=remote&sort=recency"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:50]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Upwork Client",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "upwork",
            })
    return jobs


async def fetch_stackoverflow(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Stack Overflow Jobs RSS."""
    url = "https://stackoverflow.com/jobs/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:50]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": _extract_tag(item, "author") or "Stack Overflow Job",
                "url": link,
                "location": _extract_tag(item, "location") or "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "stackoverflow",
            })
    return jobs


async def fetch_github_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from GitHub Jobs API."""
    url = "https://jobs.github.com/positions.json"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    try:
        data = json.loads(body)
    except:
        return []
    
    jobs = []
    for item in data[:50]:
        jobs.append({
            "title": _clean(item.get("title", ""))[:160],
            "company": _clean(item.get("company", "")),
            "url": item.get("url", ""),
            "location": item.get("location", "Remote"),
            "posted": item.get("created_at", ""),
            "description": _clean(item.get("description", ""))[:500],
            "salary": "",
            "source": "github_jobs",
        })
    return jobs


async def fetch_hackernews(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Hacker News Who's Hiring."""
    url = "https://hacker-news.firebaseio.com/v0/jobstories.json"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    try:
        ids = json.loads(body)
    except:
        return []
    
    jobs = []
    for job_id in ids[:30]:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{job_id}.json"
        item_status, item_body = await _get_text(session, item_url)
        if item_status == 200:
            try:
                item = json.loads(item_body)
                if item and item.get("title"):
                    jobs.append({
                        "title": _clean(item.get("title", ""))[:160],
                        "company": "Hacker News Poster",
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={job_id}"),
                        "location": "Remote",
                        "posted": datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc).isoformat() if item.get("time") else "",
                        "description": _clean(item.get("text", ""))[:500] if item.get("text") else "",
                        "salary": "",
                        "source": "hackernews",
                    })
            except:
                pass
    return jobs


async def fetch_indeed(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Indeed RSS feed."""
    url = "https://www.indeed.com/rss?q=remote&sort=date"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:50]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Indeed Job",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "indeed",
            })
    return jobs


async def fetch_landing_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Landing Jobs RSS."""
    url = "https://landing.jobs/blog/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Landing Jobs",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "landing_jobs",
            })
    return jobs


async def fetch_flexjobs(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from FlexJobs RSS."""
    url = "https://www.flexjobs.com/blog/feed/"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "FlexJobs",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "flexjobs",
            })
    return jobs


async def fetch_remote_co(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Remote.co RSS."""
    url = "https://remote.co/feed/"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Remote.co Job",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "remote_co",
            })
    return jobs


async def fetch_toptal(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Toptal RSS."""
    url = "https://www.toptal.com/careers/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Toptal",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "toptal",
            })
    return jobs


async def fetch_wellfound(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Wellfound (AngelList) RSS."""
    url = "https://wellfound.com/role"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    # Parse HTML for job listings
    cards = re.findall(r'<a[^>]+href="(/company/[^"]+/jobs/[^"]+)"[^>]*>([\s\S]*?)</a>', body)
    for href, inner in cards[:30]:
        url = f"https://wellfound.com{href}" if not href.startswith("http") else href
        parts = [p for p in (_clean(x) for x in re.split(r"<(?:br|/p|/div|/span|/h\d)[^>]*>", inner, flags=re.I)) if p]
        if parts:
            jobs.append({
                "title": parts[0][:160] if parts else "Startup Role",
                "company": parts[1] if len(parts) > 1 else "Startup",
                "url": url,
                "location": "Remote",
                "posted": "",
                "description": " ".join(parts[1:])[:500] if len(parts) > 1 else "",
                "salary": "",
                "source": "wellfound",
            })
    return jobs


async def fetch_edtech_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from EdTech Careers RSS."""
    url = "https://www.edtechcareers.com/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "EdTech Company",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "edtech_jobs",
            })
    return jobs


async def fetch_translation_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from ProZ RSS for translation jobs."""
    url = "https://www.proz.com/jobs/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "ProZ Client",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "translation_jobs",
            })
    arabic_jobs = [j for j in jobs if 'arabic' in (j.get('title','') + ' ' + j.get('description','')).lower()]
    return arabic_jobs[:50]


async def fetch_writing_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Writing Jobs RSS."""
    url = "https://www.writingjobs.com/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Writing Client",
                "url": link,
                "location": "Remote",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "writing_jobs",
            })
    return jobs


async def fetch_bayt(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Bayt.com HTML."""
    url = "https://www.bayt.com/en/international/jobs/"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    cards = re.findall(r'<div[^>]+class="[^"]*job[^"]*"[^>]*>([\s\S]*?)</div>', body)
    for card in cards[:30]:
        title_match = re.search(r'<h2[^>]*>([\s\S]*?)</h2>', card)
        link_match = re.search(r'href="([^"]+)"', card)
        if title_match and link_match:
            title = _clean(title_match.group(1))
            link = link_match.group(1)
            if not link.startswith("http"):
                link = f"https://www.bayt.com{link}"
            jobs.append({
                "title": title[:160],
                "company": "Bayt.com Job",
                "url": link,
                "location": "MENA",
                "posted": "",
                "description": "",
                "salary": "",
                "source": "bayt",
            })
    return jobs


async def fetch_gulftalent(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from GulfTalent HTML."""
    url = "https://www.gulftalent.com/jobs"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    cards = re.findall(r'<div[^>]+class="[^"]*job[^"]*"[^>]*>([\s\S]*?)</div>', body)
    for card in cards[:30]:
        title_match = re.search(r'<h2[^>]*>([\s\S]*?)</h2>', card)
        link_match = re.search(r'href="([^"]+)"', card)
        if title_match and link_match:
            title = _clean(title_match.group(1))
            link = link_match.group(1)
            if not link.startswith("http"):
                link = f"https://www.gulftalent.com{link}"
            jobs.append({
                "title": title[:160],
                "company": "GulfTalent Job",
                "url": link,
                "location": "Gulf",
                "posted": "",
                "description": "",
                "salary": "",
                "source": "gulftalent",
            })
    return jobs


async def fetch_naukrigulf(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from NaukriGulf HTML."""
    url = "https://www.naukrigulf.com/jobs"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    cards = re.findall(r'<div[^>]+class="[^"]*job[^"]*"[^>]*>([\s\S]*?)</div>', body)
    for card in cards[:30]:
        title_match = re.search(r'<h2[^>]*>([\s\S]*?)</h2>', card)
        link_match = re.search(r'href="([^"]+)"', card)
        if title_match and link_match:
            title = _clean(title_match.group(1))
            link = link_match.group(1)
            if not link.startswith("http"):
                link = f"https://www.naukrigulf.com{link}"
            jobs.append({
                "title": title[:160],
                "company": "NaukriGulf Job",
                "url": link,
                "location": "Gulf",
                "posted": "",
                "description": "",
                "salary": "",
                "source": "naukrigulf",
            })
    return jobs


async def fetch_mostaql(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Mostaql RSS (Arabic freelance)."""
    url = "https://www.mostaql.com/jobs/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "Mostaql Client",
                "url": link,
                "location": "MENA",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "mostaql",
            })
    return jobs


async def fetch_for9a(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from For9a RSS (Arabic freelance)."""
    url = "https://for9a.com/jobs/feed"
    status, body = await _get_text(session, url)
    if status != 200:
        return []
    
    jobs = []
    items = re.findall(r"<item>[\s\S]*?</item>", body)
    for item in items[:30]:
        title = _extract_tag(item, "title")
        link = _extract_tag(item, "link")
        desc = _extract_tag(item, "description")
        if title and link:
            jobs.append({
                "title": _clean(title)[:160],
                "company": "For9a Client",
                "url": link,
                "location": "MENA",
                "posted": _extract_tag(item, "pubDate") or "",
                "description": _clean(desc)[:500] if desc else "",
                "salary": "",
                "source": "for9a",
            })
    return jobs


# ============================================================================
# BATCH FETCHERS — These call the individual board fetchers in parallel
# ============================================================================

async def fetch_greenhouse_batch(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Greenhouse boards."""
    from .greenhouse import GREENHOUSE_BOARDS, fetch_greenhouse_board
    tasks = [fetch_greenhouse_board(session, name, slug) for name, slug in GREENHOUSE_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_lever_batch(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Lever boards."""
    from .lever import LEVER_BOARDS, fetch_lever_board
    tasks = [fetch_lever_board(session, name, slug) for name, slug in LEVER_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_ashby_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Ashby boards."""
    from .ashby import ASHBY_BOARDS
    tasks = [fetch_ashby_board(session, name, slug) for name, slug in ASHBY_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_workable_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Workable boards."""
    from .workable import WORKABLE_BOARDS
    tasks = [fetch_workable_board(session, name, slug) for name, slug in WORKABLE_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_smartrecruiters_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all SmartRecruiters boards."""
    from .smartrecruiters import SMARTRECRUITERS_BOARDS
    tasks = [fetch_smartrecruiters_board(session, name, slug) for name, slug in SMARTRECRUITERS_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_recruitee_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Recruitee boards."""
    from .recruitee import RECRUITEE_BOARDS
    tasks = [fetch_recruitee_board(session, name, slug) for name, slug in RECRUITEE_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_teamtailor_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all TeamTailor boards."""
    from .teamtailor import TEAMTAILOR_BOARDS
    tasks = [fetch_teamtailor_board(session, name, slug) for name, slug in TEAMTAILOR_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_bamboohr_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all BambooHR boards."""
    from .bamboohr import BAMBOOHR_BOARDS
    tasks = [fetch_bamboohr_board(session, name, slug) for name, slug in BAMBOOHR_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_jobvite_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Jobvite boards."""
    from .jobvite import JOBVITE_BOARDS
    tasks = [fetch_jobvite_board(session, name, slug) for name, slug in JOBVITE_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]


async def fetch_personio_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from all Personio boards."""
    from .personio import PERSONIO_BOARDS
    tasks = [fetch_personio_board(session, name, slug) for name, slug in PERSONIO_BOARDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [j for r in results if isinstance(r, list) for j in r]
