"""
Search Proxy Fetcher — Bypass blocked sites using search engines.

Instead of hitting blocked sites directly (403/429), we search
DuckDuckGo/Google for their job listings. The search results contain
job titles, snippets, and URLs — we never touch the blocked site's server.

Covers: bayt, gulftalent, mostaql, ureed, wuzzuf, proz, naukrigulf,
         dubizzle,LinkedIn (guest), Indeed, Glassdoor, Craigslist.
"""

import re
import asyncio
import urllib.parse
from datetime import datetime, timezone

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

TIMEOUT = aiohttp.ClientTimeout(total=15)

# ── Search queries: site-specific to find Arabic translation jobs ──
# Format: (query, source_name, base_url)
BLOCKED_SITE_QUERIES = [
    # Bayt.com — biggest MENA job board
    ('"arabic translator" OR "arabic english" OR "مترجم" site:bayt.com', "bayt", "https://www.bayt.com"),
    ('"translation" OR "localization" OR "linguist" site:bayt.com remote', "bayt", "https://www.bayt.com"),
    ('"bilingual" OR "arabic" "translator" site:bayt.com', "bayt", "https://www.bayt.com"),
    # GulfTalent
    ('"arabic translator" OR "translation" site:gulftalent.com', "gulftalent", "https://www.gulftalent.com"),
    ('"bilingual" OR "localization" site:gulftalent.com', "gulftalent", "https://www.gulftalent.com"),
    # Mostaql — Arabic freelancing
    ('"ترجم" OR "مترجم" OR "ترجمة" site:mostaql.com', "mostaql", "https://mostaql.com"),
    ('"arabic translation" OR "翻译" site:mostaql.com', "mostaql", "https://mostaql.com"),
    # Ureed — Arabic remote jobs
    ('"مترجم" OR "ترجمة" OR "arabic translator" site:ureed.com', "ureed", "https://ureed.com"),
    # Wuzzuf — Egyptian jobs
    ('"مترجم" OR "ترجمة" OR "translator" site:wuzzuf.net', "wuzzuf", "https://www.wuzzuf.net"),
    ('"arabic english" OR "localization" site:wuzzuf.net', "wuzzuf", "https://www.wuzzuf.net"),
    # ProZ — translation marketplace
    ('"arabic translator" OR "arabic translation" site:proz.com', "proz", "https://www.proz.com"),
    ('"english arabic" OR "arabic english translator" site:proz.com', "proz", "https://www.proz.com"),
    # NaukriGulf
    ('"arabic translator" OR "translation" site:naukrigulf.com', "naukrigulf", "https://www.naukrigulf.com"),
    # LinkedIn (guest search via Google)
    ('"arabic translator" OR "arabic english translator" site:linkedin.com/jobs remote', "linkedin", "https://www.linkedin.com"),
    ('"localization" OR "linguist" "arabic" site:linkedin.com/jobs', "linkedin", "https://www.linkedin.com"),
    # Indeed
    ('"arabic translator" OR "arabic english" site:indeed.com remote', "indeed", "https://www.indeed.com"),
    ('"translation" "arabic" site:indeed.com', "indeed", "https://www.indeed.com"),
    # Glassdoor
    ('"arabic translator" OR "localization" site:glassdoor.com', "glassdoor", "https://www.glassdoor.com"),
    # General web — catch-all for any site we missed
    ('"hiring" "arabic translator" remote 2026', "web_general", ""),
    ('"arabic english" "translator" "remote" OR "worldwide" OR "freelance"', "web_general", ""),
    ('"localization specialist" OR "l10n" "arabic" remote', "web_general", ""),
    ('"bilingual" "arabic" "translator" hiring remote', "web_general", ""),
]

# Also try Google (better results than DDG for some queries)
GOOGLE_QUERIES = [
    "arabic english translator remote jobs 2026",
    "مترجم عربي انجليزي عن بُعد",
    "arabic localization jobs worldwide hiring",
    "proz arabic translator jobs",
    "bayt.com arabic translator remote",
]


async def _fetch_ddg(session: aiohttp.ClientSession, query: str) -> list[dict]:
    """Search DuckDuckGo HTML and extract results."""
    results = []
    try:
        data = {"q": query}
        async with session.post(
            "https://html.duckduckgo.com/html/",
            data=data,
            headers=HEADERS,
            timeout=TIMEOUT,
            ssl=False,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()

            # Extract DDG result blocks
            # Pattern: <a class="result__a" href="...">Title</a>
            #          <a class="result__snippet">Snippet text</a>
            blocks = re.findall(
                r'<a[^>]+class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
                r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
                html, re.S
            )

            for href, title_html, snippet_html in blocks:
                # Decode DDG redirect URL
                url = href
                if "duckduckgo.com/l/?uddg=" in href:
                    try:
                        parsed = urllib.parse.parse_qs(
                            urllib.parse.urlparse(href).query
                        )
                        url = urllib.parse.unquote(parsed.get("uddg", [""])[0])
                    except Exception:
                        continue

                if not url.startswith("http"):
                    continue

                title = re.sub(r"<[^>]+>", "", title_html).strip()
                snippet = re.sub(r"<[^>]+>", "", snippet_html).strip()

                if not title or len(title) < 5:
                    continue

                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet[:500],
                })

            # Fallback: extract any links with job-related patterns
            if not results:
                links = re.findall(r'href="(https?://[^"]+)"', html)
                for link in links:
                    if "duckduckgo.com" in link:
                        continue
                    if any(kw in link.lower() for kw in [
                        "job", "career", "hiring", "vacancy", "position",
                        "translator", "translation", "linguist",
                    ]):
                        results.append({
                            "title": link.split("/")[-1].replace("-", " ").title()[:100],
                            "url": link,
                            "snippet": "",
                        })

    except Exception as e:
        pass

    return results[:10]


async def _fetch_google(session: aiohttp.ClientSession, query: str) -> list[dict]:
    """Search Google and extract results."""
    results = []
    try:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=10"
        async with session.get(url, headers={
            **HEADERS,
            "Accept-Language": "en-US,en;q=0.9",
        }, timeout=TIMEOUT, ssl=False) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()

            # Extract Google result links
            # Pattern: <a href="/url?q=ACTUAL_URL&..."
            links = re.findall(r'<a[^>]+href="/url\?q=([^&"]+)', html)
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.S)

            for i, link in enumerate(links[:10]):
                decoded_link = urllib.parse.unquote(link)
                if not decoded_link.startswith("http"):
                    continue
                # Skip google's own pages
                if "google.com" in decoded_link:
                    continue

                title = ""
                if i < len(titles):
                    title = re.sub(r"<[^>]+>", "", titles[i]).strip()

                if not title:
                    title = decoded_link.split("/")[-1].replace("-", " ").title()[:100]

                results.append({
                    "title": title,
                    "url": decoded_link,
                    "snippet": "",
                })

    except Exception:
        pass

    return results[:10]


def _classify_source(url: str) -> str:
    """Classify which job platform a URL belongs to."""
    url_lower = url.lower()
    if "bayt.com" in url_lower:
        return "bayt"
    if "gulftalent.com" in url_lower:
        return "gulftalent"
    if "mostaql.com" in url_lower:
        return "mostaql"
    if "ureed.com" in url_lower:
        return "ureed"
    if "wuzzuf.net" in url_lower:
        return "wuzzuf"
    if "proz.com" in url_lower:
        return "proz"
    if "naukrigulf.com" in url_lower:
        return "naukrigulf"
    if "linkedin.com" in url_lower:
        return "linkedin"
    if "indeed.com" in url_lower:
        return "indeed"
    if "glassdoor.com" in url_lower:
        return "glassdoor"
    return "web_search"


def _is_translation_job(title: str, snippet: str) -> bool:
    """Quick check if a search result is translation-related."""
    text = f"{title} {snippet}".lower()
    keywords = [
        "translat", "locali", "linguist", "bilingual", "multilingual",
        "interpreter", "arabic", "مترجم", "ترجمة", "content writer",
        "proofread", "editor", "copywriter", "content creator",
        "ai trainer", "data annotation", "language expert",
        "cat tool", "trados", "memoq", "subtitl", "caption",
    ]
    return any(kw in text for kw in keywords)


def _extract_title_from_url(url: str, fallback_title: str) -> str:
    """Extract a readable job title from a URL path."""
    path = urllib.parse.urlparse(url).path
    # Common patterns: /jobs/job-title-here, /job/12345/job-title
    parts = [p for p in path.split("/") if p and p not in ("jobs", "job", "careers", " vacancy")]

    if parts:
        last = parts[-1]
        # Try numeric ID — go one level up
        if last.isdigit() and len(parts) > 1:
            last = parts[-2]
        # Clean up
        title = last.replace("-", " ").replace("_", " ").strip()
        if len(title) > 5:
            return title[:120]

    return fallback_title


async def fetch_blocked_sites_via_search(session: aiohttp.ClientSession) -> list[dict]:
    """
    Search-based fetcher: finds jobs from blocked sites without touching them.
    Uses DuckDuckGo + Google as proxies.
    """
    all_jobs = []
    seen_urls = set()

    # Run DDG and Google searches in parallel
    ddg_tasks = []
    for query, source, base_url in BLOCKED_SITE_QUERIES:
        ddg_tasks.append(_fetch_ddg(session, query))

    google_tasks = []
    for query in GOOGLE_QUERIES:
        google_tasks.append(_fetch_google(session, query))

    # Execute all searches concurrently
    all_results = await asyncio.gather(
        *ddg_tasks, *google_tasks,
        return_exceptions=True
    )

    for result_set in all_results:
        if isinstance(result_set, Exception):
            continue
        if not isinstance(result_set, list):
            continue

        for item in result_set:
            url = item.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            title = item.get("title", "")
            snippet = item.get("snippet", "")

            # Classify source
            source = _classify_source(url)

            # Extract better title
            if len(title) < 5:
                title = _extract_title_from_url(url, snippet[:60])

            # Quick translation relevance check
            if not _is_translation_job(title, snippet):
                continue

            # Clean up title
            title = re.sub(r"\s+", " ", title).strip()
            if len(title) < 5:
                continue

            all_jobs.append({
                "title": title,
                "company": source.title(),
                "url": url,
                "location": "Remote (via search)",
                "posted": "",
                "description": snippet[:1000] if snippet else f"Found via search engine. Visit URL for full details.",
                "salary": "",
                "source": f"search_{source}",
            })

    print(f"  Search proxy: found {len(all_jobs)} jobs from blocked/unlisted sites")
    return all_jobs
