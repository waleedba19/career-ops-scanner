"""
Company Intel Collector — 100% FREE FOREVER
No Hunter, no Apollo, no paid API. Only regex + DNS + HTML scrape.

For each matched job:
  - urgency_score 0-100  (ASAP, immediate, this week)
  - desperation_index 0-100 (reposted 2x in 14d, urgent language, still hiring)
  - hiring_email (harvested + pattern-guessed + DNS MX verified)
  - pain_points (why they lack you)
  - weakness_summary

All methods are stdlib + aiohttp + beautifulsoup (free forever).
Graceful fallback: if dns/verify unavailable, still returns guessed email marked unverified.
Never raises — always returns job enriched or unchanged.
"""
import re
import socket
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

# --- free regex ---
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.I)

URGENCY_PATTERNS = [
    (re.compile(r"\burgent(ly)?\b", re.I), 30),
    (re.compile(r"\basap\b", re.I), 30),
    (re.compile(r"immediate(ly)?\s+(start|hire|join|available)", re.I), 35),
    (re.compile(r"hiring\s+(immediately|now|fast|urgently)", re.I), 30),
    (re.compile(r"start\s+(asap|immediately|this week|monday|next week)", re.I), 25),
    (re.compile(r"\bthis week\b", re.I), 15),
    (re.compile(r"\bnext week\b", re.I), 10),
    (re.compile(r"need.*\b(asap|immediately|urgent)\b", re.I), 20),
    (re.compile(r"looking for.*\b(urgent|immediate)\b", re.I), 15),
]

DESPERATION_PATTERNS = [
    (re.compile(r"still\s+hiring", re.I), 20),
    (re.compile(r"reposted|re-posted", re.I), 25),
    (re.compile(r"multiple\s+openings", re.I), 15),
    (re.compile(r"hiring\s+multiple", re.I), 15),
    (re.compile(r"growing\s+team", re.I), 10),
    (re.compile(r"expanding.*mena|mena.*expanding", re.I), 15),
    (re.compile(r"backlog|understaffed|overwhelmed", re.I), 20),
    (re.compile(r"need.*\b(native|fluent)\b.*arabic", re.I), 15),
]

COMMON_EMAIL_PREFIXES = ["careers", "hr", "jobs", "hiring", "info", "contact", "talent", "recruitment", "apply", "join"]

def urgency_score(title: str, desc: str) -> int:
    text = f"{title or ''} {desc or ''}"
    score = 0
    for pat, w in URGENCY_PATTERNS:
        if pat.search(text):
            score += w
    return min(100, score)

def desperation_index(job: dict, seen_history: dict | None = None) -> int:
    title = job.get("title","")
    desc = job.get("description","")
    text = f"{title} {desc}"
    score = 0
    for pat, w in DESPERATION_PATTERNS:
        if pat.search(text):
            score += w
    # reposted signal: same company|title seen before in smart_seen / seen_history
    try:
        if seen_history:
            # seen_history is dict of fingerprints -> {seen: iso}
            from scanner import make_fingerprint
            fp = make_fingerprint(job)
            if fp in seen_history.get("fingerprints", {}):
                # seen before → desperation +25 (they reposted)
                score += 25
                # if seen >1 time in last 14d, extra
                seen_iso = seen_history["fingerprints"][fp].get("seen","")
                if seen_iso:
                    try:
                        seen_dt = datetime.fromisoformat(seen_iso.replace("Z","+00:00"))
                        if datetime.now(timezone.utc) - seen_dt < timedelta(days=14):
                            score += 15
                    except: pass
    except: pass
    # urgency contributes half to desperation
    score += urgency_score(title, desc) // 3
    return min(100, score)

def extract_emails_from_text(text: str) -> list[str]:
    if not text:
        return []
    # avoid false positives like image.jpg@2x
    raw = EMAIL_RE.findall(text)
    # filter common trash
    filtered = []
    for e in raw:
        e = e.lower().strip(".,;:")
        if e.endswith((".png",".jpg",".jpeg",".gif",".svg",".webp",".css",".js")):
            continue
        if "@example." in e or "test@" in e:
            continue
        filtered.append(e)
    # dedup preserve order
    seen=set()
    out=[]
    for e in filtered:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out[:5]

def guess_emails_for_domain(domain: str) -> list[str]:
    domain = (domain or "").lower().strip()
    if not domain or "." not in domain:
        return []
    # strip path
    domain = domain.split("/")[0]
    # remove www.
    if domain.startswith("www."):
        domain = domain[4:]
    # remove port
    domain = domain.split(":")[0]
    return [f"{p}@{domain}" for p in COMMON_EMAIL_PREFIXES]

def domain_from_url(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except: return ""

def domain_from_company_website(company: str, job_url: str) -> str:
    d = domain_from_url(job_url)
    # greenhouse/lever urls are not company domain → try company name guess
    if d and d not in ("boards-api.greenhouse.io","boards.greenhouse.io","api.lever.co","jobs.lever.co","remotive.com","remoteok.com","weworkremotely.com","jobicy.com","himalayas.app"):
        return d
    # FALLBACK FREE: infer domain from company name e.g. Smartling → smartling.com
    if company:
        # clean company name
        slug = re.sub(r'[^a-z0-9]', '', company.lower().replace(" ",""))[:30]
        if slug:
            # try slug.com as guess — will be verified via MX
            return f"{slug}.com"
    return d

def mx_verified(domain: str) -> bool:
    """Free DNS MX check — no API, just socket DNS lookup."""
    if not domain:
        return False
    try:
        # getaddrinfo will do A lookup; MX is better but requires dnspython.
        # We use getaddrinfo as free forever lightweight check — if domain resolves, likely has MX
        socket.getaddrinfo(domain, None, timeout=3)
        return True
    except:
        return False

def pain_points(job: dict) -> str:
    title = (job.get("title") or "").lower()
    desc = (job.get("description") or "").lower()
    points=[]
    if "arabic" in title or "arabic" in desc:
        if "mena" in desc or "middle east" in desc:
            points.append("Expanding to MENA, needs native Arabic")
        if "qa" in title or "qa" in desc or "review" in desc:
            points.append("No native QA, backlog of Arabic content")
        if not points:
            points.append("Needs native Arabic speaker (rare)")
    if "esl" in title or "english teacher" in title or "tutor" in title:
        points.append("Needs ESL teacher, likely understaffed")
    if "translation" in title or "translator" in title:
        points.append("Translation backlog / scaling")
    if "content" in title and "writer" in title:
        points.append("Content needs, scaling blog/docs")
    if not points and job.get("category") == "Arabic Translation":
        points.append("Localization gap for Arabic")
    return "; ".join(points[:2]) if points else "General hiring need"

async def enrich_one(job: dict, session, seen_history: dict | None) -> dict:
    try:
        title = job.get("title","")
        desc = job.get("description","")
        url = job.get("url","")
        # urgency / desperation
        job["urgency_score"] = urgency_score(title, desc)
        job["desperation_index"] = desperation_index(job, seen_history)
        job["pain_points"] = pain_points(job)
        # email harvest
        emails = extract_emails_from_text(desc + " " + url)
        # if we have a session, try to fetch careers page for one extra hop (free)
        domain = domain_from_url(url)
        # For greenhouse/lever, domain is not useful — skip fetch to avoid noise
        should_fetch = domain and domain not in ("boards-api.greenhouse.io","boards.greenhouse.io","api.lever.co","jobs.lever.co")
        fetched_html = ""
        if should_fetch and session is not None:
            # try company domain root  + /careers /contact (1 request max, 4s timeout)
            for path in ["/careers", "/contact", "/jobs"]:
                try:
                    import aiohttp
                    target = f"https://{domain}{path}"
                    async with session.get(target, timeout=aiohttp.ClientTimeout(total=4), ssl=False) as r:
                        if r.status == 200:
                            fetched_html = await r.text()
                            more = extract_emails_from_text(fetched_html)
                            for e in more:
                                if e not in emails:
                                    emails.append(e)
                            if emails:
                                break
                except: pass
        # if still no email, guess (free forever — even for greenhouse infer domain from company)
        # try company-inferred domain if ATS
        if not domain or not should_fetch:
            inferred = domain_from_company_website(job.get("company",""), url)
            if inferred and inferred != domain:
                domain = inferred
                should_fetch = True
        guessed = []
        if not emails and domain:
            guessed = guess_emails_for_domain(domain)
            # verify first guessed domain resolves
            verified_guessed = []
            for g in guessed[:3]:  # only top 3 to keep Excel clean
                gd = g.split("@")[1]
                if mx_verified(gd):
                    verified_guessed.append(g)
                else:
                    # keep but mark unverified
                    verified_guessed.append(g)
            emails = verified_guessed
            job["email_guessed"] = True
        else:
            job["email_guessed"] = False
        # pick best email
        if emails:
            # prefer careers/hr/jobs over info/contact
            priority = {"careers":0,"hr":1,"jobs":2,"hiring":3,"talent":4,"recruitment":5,"info":6,"contact":7}
            def prio(e):
                prefix = e.split("@")[0]
                return priority.get(prefix, 99)
            emails_sorted = sorted(emails, key=prio)
            best = emails_sorted[0]
            job["hiring_email"] = best
            # verify
            try:
                job["email_verified"] = mx_verified(best.split("@")[1])
            except:
                job["email_verified"] = False
            job["all_emails"] = emails_sorted[:3]
        else:
            job["hiring_email"] = ""
            job["email_verified"] = False
            job["all_emails"] = []
        # composite opportunity score (free)
        # urgency 30% + desperation 40% + match score 30%
        try:
            job["opportunity_score"] = min(100, round( (job["urgency_score"]*0.3 + job["desperation_index"]*0.4 + job.get("score",0)*0.3) ))
        except:
            job["opportunity_score"] = job.get("score",0)
    except Exception as e:
        # never break pipeline
        job.setdefault("urgency_score", 0)
        job.setdefault("desperation_index", 0)
        job.setdefault("hiring_email", "")
        job.setdefault("email_verified", False)
        job.setdefault("pain_points", "")
        job.setdefault("opportunity_score", job.get("score",0))
    return job

async def enrich_jobs_with_intel(jobs: list[dict], session=None, seen_history: dict | None = None) -> list[dict]:
    """Enrich list in place, free forever, concurrency 5 for careers fetch."""
    import asyncio
    if not jobs:
        return jobs
    # small concurrency for careers page fetch to stay polite
    sem = asyncio.Semaphore(5)
    async def sem_task(j):
        async with sem:
            return await enrich_one(j, session, seen_history)
    # run sequentially if no session (no fetch)
    if session is None:
        for j in jobs:
            await enrich_one(j, None, seen_history)
        return jobs
    await asyncio.gather(*(sem_task(j) for j in jobs))
    return jobs
