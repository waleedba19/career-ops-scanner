"""
Search Orchestrator — 100% FREE FOREVER
No SerpAPI, no Bing API. Uses DuckDuckGo HTML (no key) + Sitemap polling.

Queries DuckDuckGo HTML for 4 high-intent queries, parses result hrefs,
deduplicates, and returns as synthetic job-like dicts to feed fetcher.
Also polls Greenhouse + Lever sitemaps for fresh URLs (free).

Graceful: if DuckDuckGo blocks or no internet, returns [].
Never raises. Designed to run before main fetch, 10s max.
"""
import re
import asyncio
import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

QUERIES = [
    "arabic translator remote site:greenhouse.io",
    "arabic linguist remote site:lever.co",
    "esl teacher remote worldwide",
    "translation localization remote worldwide",
]

DDG_URL = "https://html.duckduckgo.com/html/"

def _extract_links(html: str) -> list[str]:
    # DuckDuckGo HTML result links are in <a class="result__url" href="...">
    # fallback: any href containing greenhouse/lever/workable
    links = re.findall(r'href="([^"]+)"[^>]*class="[^"]*result__url', html, re.I)
    if not links:
        links = re.findall(r'href="([^"]+)"', html, re.I)
    # udd param is duckduckgo redirect: /l/?uddg=https%3A... -> decode
    out=[]
    for l in links:
        if "duckduckgo.com/l/?uddg=" in l:
            import urllib.parse
            try:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(l).query).get("uddg",[""])[0]
                l = urllib.parse.unquote(q)
            except: pass
        # keep only job-like
        if any(x in l for x in ["greenhouse.io","lever.co","workable.com","ashbyhq.com","smartrecruiters.com","teamtailor.com","bamboohr.com","workday.com"]):
            out.append(l)
    # dedup
    seen=set()
    uniq=[]
    for u in out:
        if u not in seen and u.startswith("http"):
            seen.add(u)
            uniq.append(u)
    return uniq[:20]

async def _fetch_ddg(session: aiohttp.ClientSession, query: str) -> list[str]:
    try:
        data = {"q": query}
        async with session.post(DDG_URL, data=data, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=8), ssl=False) as r:
            if r.status != 200:
                return []
            html = await r.text()
            return _extract_links(html)
    except:
        return []

async def _poll_sitemap(session: aiohttp.ClientSession, url: str) -> list[str]:
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=6), ssl=False) as r:
            if r.status != 200:
                return []
            xml = await r.text()
            urls = re.findall(r"<loc>([^<]+)</loc>", xml)
            # keep job-like
            job_urls = [u for u in urls if any(x in u for x in ["/jobs","/careers","/job/","/opening"])]
            return job_urls[:20]
    except:
        return []

async def discover_via_search(session: aiohttp.ClientSession) -> list[dict]:
    """
    Returns synthetic job dicts discovered via free search + sitemaps.
    Each dict has title=Search Discovered, url=found url, source=search_discovered.
    Scanner's normal fetch pipeline will later fetch details if needed, but even
    just the URL is valuable to surface new boards.
    """
    # Bound total time 12s
    try:
        # sitemaps (free, reliable)
        sitemaps = [
            "https://boards.greenhouse.io/sitemap.xml",
            "https://jobs.lever.co/sitemap.xml",
        ]
        sitemap_tasks = [_poll_sitemap(session, u) for u in sitemaps]
        # duckduckgo queries
        ddg_tasks = [_fetch_ddg(session, q) for q in QUERIES]
        results = await asyncio.gather(*(sitemap_tasks + ddg_tasks), return_exceptions=True)
        urls=[]
        for r in results:
            if isinstance(r, list):
                urls.extend(r)
        # dedup
        seen=set()
        uniq=[]
        for u in urls:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        # turn into job stubs
        jobs=[]
        for u in uniq[:40]:
            # infer title from slug
            slug = u.rstrip("/").split("/")[-1].replace("-"," ").title()[:80]
            jobs.append({
                "title": slug or "Search Discovered Opportunity",
                "company": "Search Discovered",
                "url": u,
                "location": "Remote",
                "posted": "",
                "description": "Discovered via free DuckDuckGo + sitemap search. Verify posting before applying.",
                "salary": "",
                "source": "search_discovered",
                "discovered_via": "duckduckgo+sitemap",
            })
        return jobs
    except:
        return []
