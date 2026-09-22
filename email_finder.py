"""
email_finder.py — find the employer's real hiring email, not the board relay.

A job-board listing usually shows the board's relay address (or none at all),
which is useless for a direct application. This module:

  1. resolves the employer's OWN domain — from the job URL when it is already on
     the employer site, otherwise via a free DuckDuckGo search on the company
     name (Groq cannot browse, so search supplies the site; regex supplies the
     address);
  2. fetches the employer root + /contact + /careers + /about and harvests emails;
  3. filters board/relay/stop addresses and prefers careers/jobs/hr inboxes;
  4. only pattern-guesses (careers@domain …) after the domain is known.

Free forever: DuckDuckGo HTML + aiohttp + regex. Never raises; a job whose
email cannot be found is returned unchanged.
"""
from __future__ import annotations

import asyncio
import re
from urllib.parse import urlparse, parse_qs, unquote

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

from company_intel.collector import (
    extract_emails_from_text,
    is_job_board_domain,
    guess_emails_for_domain,
    domain_from_url,
    mx_verified,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.6",
}

CONTACT_PATHS = ["", "/contact", "/contact-us", "/careers", "/about", "/jobs"]

# Domains that are never an employer inbox.
NON_EMPLOYER_DOMAINS = {
    "facebook.com", "twitter.com", "x.com", "instagram.com", "linkedin.com",
    "youtube.com", "wikipedia.org", "crunchbase.com", "glassdoor.com",
    "indeed.com", "google.com", "bing.com", "duckduckgo.com", "tiktok.com",
    "pinterest.com", "medium.com", "github.com", "gmail.com", "yahoo.com",
    "reddit.com", "apple.com", "microsoft.com", "amazon.com", "cloudflare.com",
    "example.com", "sentry.io", "wix.com", "wixstatic.com", "wordpress.com",
    "godaddy.com", "gravatar.com", "schema.org", "w3.org", "googletagmanager.com",
}

# Business-directory / aggregator domains. A mailbox on one of these is NOT the
# employer's inbox — careers@findglocal.com (a directory page for a fake/DARPAN
# posting) bounced with "User unknown", 2026-09-22. These domains commonly HAVE
# MX records, so mx_verified() alone is not enough: directory existence != a
# working employer mailbox. Never present a guessed or harvested address on one
# of these as a "verified" hiring email.
DIRECTORY_DOMAINS = frozenset({
    "findglocal.com", "cybo.com", "dancor.com", "theorg.com", "zoominfo.com",
    "signalhire.com", "rocketreach.co", "craft.co", "f6s.com", "builtin.com",
    "wellfound.com", "startup.jobs", "qualityportal.com", "glueup.com",
    "yellowpages.com", "yelp.com", "brownbook.net", "tuugo.net", "pitchbook.com",
    "dnb.com", "tracxn.com", "googleusercontent.com", "56kmod",
})

EMAIL_STOP_TOKENS = (
    "noreply", "no-reply", "donotreply", "do-not-reply", "postmaster", "abuse",
    "privacy", "legal", "dpo", "newsletter", "marketing", "unsubscribe",
    "bounce", "mailer", "notifications", "webmaster", "hostmaster",
)

# Placeholder / dummy addresses that appear on template sites.
PLACEHOLDER_DOMAINS = {
    "email.com", "example.com", "example.org", "domain.com", "yourdomain.com",
    "company.com", "test.com", "mail.com", "site.com", "website.com",
}
PLACEHOLDER_LOCALS = (
    "janedoe", "johndoe", "jane.doe", "john.doe", "yourname", "your.name",
    "youremail", "your.email", "firstname", "lastname", "someone", "username",
    "sample", "user", "test", "name", "email",
)

PREFERRED_PREFIXES = [
    "careers", "jobs", "hiring", "recruitment", "recruit", "talent", "hr",
    "people", "apply", "join", "work", "contact", "info", "hello", "office",
]

# Legal/descriptive suffixes stripped before inferring a company domain.
_COMPANY_SUFFIX_RE = re.compile(
    r"\b(inc|llc|ltd|limited|corp|corporation|co|company|gmbh|s\.?a|sarl|bv|nv|"
    r"ag|pty|plc|group|holdings?|solutions?|technolog(?:y|ies)|services?|agency|"
    r"studios?|media|labs?|global|international|systems?|software|consulting)\b",
    re.I,
)


def _company_slug(company: str) -> str:
    name = _COMPANY_SUFFIX_RE.sub(" ", company or "")
    return re.sub(r"[^a-z0-9]", "", name.lower())


def infer_domains(company: str) -> list[str]:
    """Candidate employer domains guessed from the company name (no search)."""
    slug = _company_slug(company)
    if len(slug) < 3:
        return []
    return [slug + tld for tld in (".com", ".io", ".co", ".net", ".org")]


def _domain_of(url: str) -> str:
    return domain_from_url(url or "")


def _is_usable_domain(domain: str) -> bool:
    if not domain or "." not in domain:
        return False
    if is_job_board_domain(domain):
        return False
    d = domain.lower()
    if d in DIRECTORY_DOMAINS or any(d.endswith("." + b) for b in DIRECTORY_DOMAINS):
        return False
    return not any(d == b or d.endswith("." + b) for b in NON_EMPLOYER_DOMAINS)


def _clean_email(e: str) -> str:
    return (e or "").lower().strip(".,;:()<>[]\"'")


def _is_stop_email(e: str) -> bool:
    if not e or "@" not in e:
        return True
    if e.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")):
        return True
    if "sentry" in e or "wixpress" in e:
        return True
    local, _, dom = e.partition("@")
    if any(tok in local for tok in EMAIL_STOP_TOKENS):
        return True
    if dom in PLACEHOLDER_DOMAINS or local in PLACEHOLDER_LOCALS:
        return True
    if local.replace(".", "").replace("_", "") in ("janedoe", "johndoe", "yourname", "youremail"):
        return True
    return False


def _best_email(emails: list[str]) -> str:
    def prio(e: str) -> int:
        prefix = e.split("@")[0]
        for i, p in enumerate(PREFERRED_PREFIXES):
            if prefix == p:
                return i
        for i, p in enumerate(PREFERRED_PREFIXES):
            if prefix.startswith(p):
                return len(PREFERRED_PREFIXES) + i
        return 999
    return sorted(emails, key=prio)[0]


async def _get(session, url: str, timeout: int = 8) -> str:
    if session is None or not url:
        return ""
    try:
        async with session.get(
            url, headers=HEADERS, ssl=False, allow_redirects=True,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as r:
            if r.status != 200:
                return ""
            ct = (r.headers.get("Content-Type") or "").lower()
            if ct and "html" not in ct and "text" not in ct and "json" not in ct:
                return ""
            return await r.text(errors="ignore")
    except Exception:
        return ""


def _ddg_links(html: str, limit: int = 25) -> list[str]:
    links = re.findall(r'href="([^"]+)"[^>]*class="[^"]*result__a', html, re.I)
    if not links:
        links = re.findall(r'href="([^"]+)"', html, re.I)
    out, seen = [], set()
    for link in links:
        if "uddg=" in link:
            try:
                raw = "https:" + link if link.startswith("//") else link
                q = parse_qs(urlparse(raw).query).get("uddg", [""])[0]
                link = unquote(q)
            except Exception:
                pass
        if link.startswith("//"):
            link = "https:" + link
        if link.startswith("http") and link not in seen:
            seen.add(link)
            out.append(link)
        if len(out) >= limit:
            break
    return out


def _domain_from_link(link: str) -> str:
    try:
        netloc = urlparse(link).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


async def _ddg(session, query: str) -> list[str]:
    if session is None:
        return []
    try:
        async with session.post(
            "https://html.duckduckgo.com/html/", data={"q": query},
            headers=HEADERS, ssl=False, timeout=aiohttp.ClientTimeout(total=8),
        ) as r:
            if r.status == 200:
                links = _ddg_links(await r.text(errors="ignore"))
                if links:
                    return links
    except Exception:
        pass
    try:
        async with session.get(
            "https://lite.duckduckgo.com/lite/", params={"q": query},
            headers=HEADERS, ssl=False, timeout=aiohttp.ClientTimeout(total=8),
        ) as r:
            if r.status == 200:
                return _ddg_links(await r.text(errors="ignore"))
    except Exception:
        pass
    return []


async def discover_company_domain(session, job: dict, cache: dict) -> tuple[str, str, str]:
    """Resolve the employer domain. Returns (domain, contact_url, source)."""
    company = (job.get("company") or "").strip().lower()
    if company and company in cache:
        return cache[company]

    result = ("", "", "")
    job_domain = _domain_of(job.get("url", ""))
    if _is_usable_domain(job_domain):
        result = (job_domain, job.get("url", ""), "job_url")
    else:
        website = job.get("company_website") or ""
        wd = _domain_of(website)
        if _is_usable_domain(wd):
            result = (wd, website, "company_website")
        elif job.get("company"):
            for query in (f"{job['company']} official website",
                          f"{job['company']} careers contact"):
                for link in await _ddg(session, query):
                    dom = _domain_from_link(link)
                    if _is_usable_domain(dom):
                        result = (dom, link, "search")
                        break
                if result[0]:
                    break
            # Search can be blocked (datacenter IPs). Fall back to a DNS-verified
            # guess of the company's own domain so harvesting still runs.
            if not result[0]:
                for cand in infer_domains(job.get("company", "")):
                    if mx_verified(cand):
                        result = (cand, f"https://{cand}", "dns")
                        break

    if company:
        cache[company] = result
    return result


async def harvest_emails(session, domain: str, contact_url: str = "") -> list[str]:
    found, seen = [], set()
    urls = []
    if contact_url and _is_usable_domain(_domain_of(contact_url)):
        urls.append(contact_url)
    for path in CONTACT_PATHS:
        urls.append(f"https://{domain}{path}")
    for url in urls:
        html = await _get(session, url)
        if not html:
            continue
        for email in extract_emails_from_text(html):
            email = _clean_email(email)
            if not email or email in seen:
                continue
            if _is_stop_email(email) or is_job_board_domain(email.split("@")[-1]):
                continue
            seen.add(email)
            found.append(email)
        if len(found) >= 4:
            break
    return found


async def find_company_email(session, job: dict, cache: dict | None = None) -> dict:
    """Populate hiring_email / all_emails / email_source / company_domain on a job."""
    cache = cache if cache is not None else {}
    try:
        emails = [
            _clean_email(e)
            for e in extract_emails_from_text(
                (job.get("description") or "") + " " + (job.get("url") or "")
            )
        ]
        emails = [
            e for e in emails
            if e and not _is_stop_email(e) and not is_job_board_domain(e.split("@")[-1])
        ]
        source = "posting" if emails else ""

        domain, contact_url, domain_source = await discover_company_domain(session, job, cache)

        # A directory/aggregator domain is NOT the employer's inbox. MX records
        # exist on them (so mx_verified passes) but careers@findglocal.com
        # bounced "User unknown". Tag it and stop — unless the job description
        # itself carried a real address.
        if domain in DIRECTORY_DOMAINS and source != "posting":
            job["email_directory"] = domain
            job["email_verified"] = False
            job["email_guessed"] = False
            job.setdefault("hiring_email", "")
            return job

        if not emails and domain:
            for e in await harvest_emails(session, domain, contact_url):
                if e not in emails:
                    emails.append(e)
            if emails:
                source = domain_source or "harvested"

        guessed = False
        if not emails and domain and _is_usable_domain(domain):
            emails = [g for g in guess_emails_for_domain(domain)[:5] if not _is_stop_email(g)]
            guessed = bool(emails)
            source = "guess"

        if domain:
            job["company_domain"] = domain
        if emails:
            best = _best_email(emails)
            job["hiring_email"] = best
            job["all_emails"] = list(dict.fromkeys(emails))[:5]
            job["email_guessed"] = guessed
            job["email_source"] = source or "harvested"
            try:
                job["email_verified"] = mx_verified(best.split("@")[-1])
            except Exception:
                job["email_verified"] = False
    except Exception:
        job.setdefault("hiring_email", "")
        job.setdefault("email_guessed", False)
    return job


async def enrich_jobs_with_emails(session, jobs: list[dict],
                                  max_jobs: int = 10, concurrency: int = 5) -> list[dict]:
    if not jobs:
        return jobs
    targets = jobs[:max_jobs]
    cache: dict = {}
    sem = asyncio.Semaphore(max(1, concurrency))

    async def run(job):
        async with sem:
            return await find_company_email(session, job, cache)

    await asyncio.gather(*(run(j) for j in targets), return_exceptions=True)
    return jobs
