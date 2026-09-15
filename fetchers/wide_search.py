"""
Worldwide Arabic Translation Job Search Engine — V2
Uses ONLY sources that are verified to work from CI runners.
No broken APIs, no blocked sites, no waste.
"""

import re
import json
import asyncio
from pathlib import Path

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

TIMEOUT = aiohttp.ClientTimeout(total=20)

# ── WIDE SEARCH QUERIES — used by worldwide Arabic job search ──
SEARCH_QUERIES = [
    "arabic translator remote jobs",
    "arabic english translator remote",
    "arabic localization remote jobs hiring",
    "ESL teacher arabic speaking remote",
    "bilingual arabic english remote jobs hiring",
    "arabic content writer remote jobs",
    "arabic data annotation remote jobs",
    "arabic language expert remote",
    "MENA translation remote jobs",
    "arabic nlp data remote",
    "arabic transcription remote jobs",
    "arabic virtual assistant remote",
    "remote arabic interpreter jobs",
    "arabic proofreader remote hiring",
    "arabic remote work from home jobs",
    "mena language services remote",
    "arabic ai data labeling remote",
    "right to left arabic localization remote",
]


def _clean_html(text: str) -> str:
    """Remove HTML tags, decode entities."""
    import html as html_mod
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", str(text))
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_mod.unescape(text)
    return re.sub(r"\s+", " ", text).strip()[:2000]


def _is_arabic_text(text: str) -> bool:
    """Check if text contains Arabic script or Arabic-related keywords."""
    # Check for Arabic Unicode characters (U+0600–U+06FF)
    if re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", text):
        return True
    # Check for English Arabic-related keywords
    keywords = [
        "arabic", "translator", "translation", "interpreter", "linguist",
        "locali", "esl", "efl", "tesol", "tefl",
        "bilingual", "multilingual", "language expert",
        "proofreader", "editor", "content writer",
        "data entry", "virtual assistant", "teaching", "tutor",
        "عربي", "ترجم", "لغة", "تعليم",
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


# ── VERIFIED WORKING SOURCES ──

async def fetch_for9a(session: aiohttp.ClientSession) -> list[dict]:
    """For9a — Arabic freelance platform. Scrape translation category specifically."""
    jobs = []
    # For9a translation/editing category
    FOR9A_PAGES = [
        "https://for9a.com/jobs/fields/%D9%88%D8%B8%D8%A7%D8%A6%D9%81-%D8%A7%D9%84%D8%AA%D8%AC%D9%85%D9%8A%D9%84-%D9%88%D8%A7%D9%84%D9%85%D9%88%D8%B6%D8%A9",
        "https://for9a.com/jobs/fields/%D9%88%D8%B8%D8%A7%D8%A6%D9%81-%D8%A7%D9%84%D8%B5%D8%AD%D8%A7%D9%81%D8%A9-%D9%88%D8%A7%D9%84%D8%AA%D8%AD%D8%B1%D9%8A%D8%B1-%D9%88%D8%A7%D9%84%D8%AA%D8%B1%D8%AC%D9%85%D8%A9",
        "https://for9a.com/jobs/fields/%D9%88%D8%B8%D8%A7%D8%A6%D9%81-%D8%A7%D9%84%D8%A5%D8%AF%D8%A7%D8%B1%D9%8A%D8%A9",
        "https://for9a.com/jobs/remote-jobs",
    ]
    for page_url in FOR9A_PAGES:
        try:
            async with session.get(page_url, headers=HEADERS, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    continue
                html = await resp.text()
                # Individual job links have numeric IDs: /jobs/12345
                job_links = re.findall(
                    r'href="(/jobs/\d+[^"]*)"',
                    html, re.I
                )
                seen_local = set()
                for href in job_links:
                    if href in seen_local:
                        continue
                    seen_local.add(href)
                    url = f"https://for9a.com{href}"
                    # Extract title from surrounding context
                    pattern = rf'href="{re.escape(href)}"[^>]*>([^<]+)<'
                    title_m = re.search(pattern, html)
                    title = title_m.group(1).strip() if title_m else href.split("/")[-1]
                    jobs.append({
                        "title": title,
                        "company": "For9a",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": title,
                        "salary": "",
                        "source": "for9a",
                    })
        except Exception:
            pass

    print(f"  For9a: {len(jobs)} jobs")
    return jobs


async def fetch_mostaql(session: aiohttp.ClientSession) -> list[dict]:
    """Mostaql — Arabic freelance platform."""
    jobs = []
    try:
        async with session.get("https://mostaql.com/projects", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                print(f"  Mostaql: HTTP {resp.status}")
                return []
            html = await resp.text()

            job_links = re.findall(
                r'<a[^>]+href="(/projects/\d+[^"]*)"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, inner in job_links:
                title = re.sub(r"<[^>]+>", "", inner).strip()
                if not title or len(title) < 3:
                    continue
                url = f"https://mostaql.com{href}" if href.startswith("/") else href
                jobs.append({
                    "title": title,
                    "company": "Mostaql",
                    "url": url,
                    "location": "Remote",
                    "posted": "",
                    "description": title,
                    "salary": "",
                    "source": "mostaql",
                })

            print(f"  Mostaql: {len(jobs)} jobs")
    except Exception as e:
        print(f"  Mostaql: {e}")
    return jobs


async def fetch_wuzzuf(session: aiohttp.ClientSession) -> list[dict]:
    """Wuzzuf — Egyptian job board with Arabic jobs."""
    jobs = []
    try:
        async with session.get(
            "https://wuzzuf.net/jobs?q=arabic+translation&sort=relevance",
            headers=HEADERS, timeout=TIMEOUT
        ) as resp:
            if resp.status != 200:
                print(f"  Wuzzuf: HTTP {resp.status}")
                return []
            html = await resp.text()

            # Wuzzuf job cards
            job_links = re.findall(
                r'<a[^>]+href="(https://wuzzuf\.net/job/[^"]+)"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, inner in job_links:
                title = re.sub(r"<[^>]+>", "", inner).strip()
                if not title or len(title) < 3:
                    continue
                jobs.append({
                    "title": title,
                    "company": "Wuzzuf",
                    "url": href,
                    "location": "Remote",
                    "posted": "",
                    "description": title,
                    "salary": "",
                    "source": "wuzzuf",
                })

            print(f"  Wuzzuf: {len(jobs)} jobs")
    except Exception as e:
        print(f"  Wuzzuf: {e}")
    return jobs


async def fetch_linkedin_arabic(session: aiohttp.ClientSession) -> list[dict]:
    """LinkedIn guest API — search for Arabic translation jobs."""
    jobs = []
    queries = [
        "arabic+translator",
        "arabic+translation",
        "ESL+teacher+arabic",
        "bilingual+arabic+english",
        "arabic+localization",
        "arabic+interpreter",
        "arabic+content+writer",
        "arabic+data+annotation",
        "arabic+nlp",
        "arabic+language+expert",
        "arabic+virtual+assistant",
        "arabic+proofreader",
        "arabic+transcription",
        "MENA+translation",
        "arabic+remote",
    ]

    for query in queries:
        try:
            url = (
                f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={query}&location=Remote&f_TPR=r604800&start=0"
            )
            async with session.get(url, headers={
                **HEADERS,
                "Referer": "https://www.linkedin.com/jobs/",
            }, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    continue
                html = await resp.text()

                # LinkedIn job cards
                cards = re.findall(
                    r'<li[^>]*class="[^"]*reusable-search__result-container[^"]*"[^>]*>([\s\S]*?)</li>',
                    html
                )
                for card in cards:
                    title_m = re.search(r'<h3[^>]*>([\s\S]*?)</h3>', card)
                    link_m = re.search(r'href="(https://www\.linkedin\.com/jobs/view/[^"]+)"', card)
                    company_m = re.search(r'<a[^>]*class="[^"]*hidden-nested-link[^"]*"[^>]*>([\s\S]*?)</a>', card)
                    loc_m = re.search(r'<span[^>]*class="[^"]*job-search-field__top-text[^"]*"[^>]*>([\s\S]*?)</span>', card)

                    title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""
                    link = link_m.group(1).split("?")[0] if link_m else ""
                    company = re.sub(r"<[^>]+>", "", company_m.group(1)).strip() if company_m else ""
                    location = re.sub(r"<[^>]+>", "", loc_m.group(1)).strip() if loc_m else "Remote"

                    if title and link:
                        jobs.append({
                            "title": title,
                            "company": company or "LinkedIn",
                            "url": link,
                            "location": location,
                            "posted": "",
                            "description": f"LinkedIn job: {title}",
                            "salary": "",
                            "source": "linkedin",
                        })

            await asyncio.sleep(1)  # Be polite to LinkedIn

        except Exception as e:
            print(f"  LinkedIn error '{query}': {e}")

    # Deduplicate by URL
    seen = set()
    unique = []
    for j in jobs:
        if j["url"] not in seen:
            seen.add(j["url"])
            unique.append(j)

    print(f"  LinkedIn: {len(unique)} Arabic jobs")
    return unique


async def fetch_remoteok_arabic(session: aiohttp.ClientSession) -> list[dict]:
    """RemoteOK — filter for Arabic/translation jobs."""
    jobs = []
    try:
        async with session.get("https://remoteok.com/api", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            if not isinstance(data, list):
                return []

            for item in data:
                if not isinstance(item, dict) or not item.get("position"):
                    continue
                tags = " ".join(item.get("tags", [])).lower()
                title = item.get("position", "").lower()
                desc = _clean_html(item.get("description", "")).lower()
                combined = f"{tags} {title} {desc}"

                if "arabic" in combined or "translator" in combined or "translation" in combined or "esl" in combined or "bilingual" in combined:
                    posted = ""
                    if item.get("date"):
                        try:
                            from datetime import datetime, timezone
                            posted = datetime.fromtimestamp(item["date"], tz=timezone.utc).isoformat()
                        except Exception:
                            pass

                    jobs.append({
                        "title": item.get("position", ""),
                        "company": item.get("company", ""),
                        "url": item.get("url") or item.get("apply_url", ""),
                        "location": item.get("location", "Remote"),
                        "posted": posted,
                        "description": _clean_html(item.get("description", "")),
                        "salary": item.get("salary", ""),
                        "source": "remoteok",
                    })

        print(f"  RemoteOK: {len(jobs)} Arabic/translation jobs")
    except Exception as e:
        print(f"  RemoteOK: {e}")
    return jobs


async def fetch_go_transcript(session: aiohttp.ClientSession) -> list[dict]:
    """GoTranscript — translation jobs."""
    jobs = []
    try:
        async with session.get("https://gotranscript.com/translation-jobs", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()

            # Look for job listings
            job_blocks = re.findall(
                r'<a[^>]+href="(https://gotranscript\.com/translation-jobs/[^"]+)"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, inner in job_blocks:
                title = re.sub(r"<[^>]+>", "", inner).strip()
                if title and len(title) > 3:
                    jobs.append({
                        "title": title,
                        "company": "GoTranscript",
                        "url": href,
                        "location": "Remote",
                        "posted": "",
                        "description": title,
                        "salary": "",
                        "source": "gotranscript",
                    })

            print(f"  GoTranscript: {len(jobs)} jobs")
    except Exception as e:
        print(f"  GoTranscript: {e}")
    return jobs


async def fetch_smartcat_market(session: aiohttp.ClientSession) -> list[dict]:
    """Smartcat marketplace — translation jobs."""
    jobs = []
    try:
        async with session.get("https://smartcat.com/marketplace", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()

            # Smartcat job/project cards
            cards = re.findall(
                r'<a[^>]+href="(/marketplace/[^"]*)"[^>]*class="[^"]*job[^"]*"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, inner in cards:
                title = re.sub(r"<[^>]+>", "", inner).strip()
                if title and len(title) > 3:
                    url = f"https://smartcat.com{href}" if href.startswith("/") else href
                    jobs.append({
                        "title": title,
                        "company": "Smartcat",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": title,
                        "salary": "",
                        "source": "smartcat",
                    })

            print(f"  Smartcat: {len(jobs)} jobs")
    except Exception as e:
        print(f"  Smartcat: {e}")
    return jobs


async def fetch_worldwide_arabic_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """
    Main entry point: fetch Arabic translation jobs from ALL verified free sources.
    Only sources that are confirmed working from CI runners.
    """
    print("  Starting worldwide Arabic job search (verified sources only)...")

    results = await asyncio.gather(
        fetch_for9a(session),
        fetch_mostaql(session),
        fetch_wuzzuf(session),
        fetch_linkedin_arabic(session),
        fetch_remoteok_arabic(session),
        fetch_go_transcript(session),
        fetch_smartcat_market(session),
        return_exceptions=True,
    )

    all_jobs = []
    for r in results:
        if isinstance(r, list):
            all_jobs.extend(r)
        elif isinstance(r, Exception):
            print(f"  Source error: {r}")

    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        url = job.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)

    # For9a/Mostaql/Wuzzuf are Arabic platforms — keep ALL their jobs
    # For other sources, filter to Arabic-relevant only
    arabic_sources = {"for9a", "mostaql", "wuzzuf"}
    final_jobs = []
    for job in unique_jobs:
        source = job.get("source", "")
        if source in arabic_sources:
            final_jobs.append(job)  # Arabic platform — keep all
        elif _is_arabic_text(f"{job.get('title','')} {job.get('description','')}"):
            final_jobs.append(job)  # Has Arabic keywords — keep

    print(f"  Worldwide search: {len(final_jobs)} Arabic jobs (from {len(unique_jobs)} unique)")
    return final_jobs
