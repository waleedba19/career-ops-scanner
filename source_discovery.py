"""
CareerOps Source Auto-Discovery System
Automatically finds and validates new job sources.
Runs before each scan to expand coverage.
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

REGISTRY_FILE = Path(__file__).parent / "output" / "source_registry.json"
DISCOVERY_LOG = Path(__file__).parent / "output" / "discovery_log.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = aiohttp.ClientTimeout(total=10)

# Known job board patterns to discover
DISCOVERY_SEEDS = [
    # RSS feeds to check
    "https://remotive.com/remote-jobs/feed",
    "https://weworkremotely.com/remote-jobs.rss",
    "https://jobicy.com/jobs/feed",
    "https://www.yayremote.com/api/remote-jobs/feeds/jobs.xml",
    "https://www.realworkfromanywhere.com/remote-jobs.rss",
    "https://workingnomads.com/feed",
    "https://jobspresso.co/feed/",
    "https://himalayas.app/jobs/rss",
    "https://remoteok.com/remote-jobs.rss",
    "https://landing.jobs/blog/feed",
    "https://www.flexjobs.com/blog/feed/",
    "https://remote.co/feed/",
    "https://justremote.co/feed/",
    "https://www.upwork.com/ab/feed/jobs/rss?q=remote&sort=recency",
    "https://www.indeed.com/rss?q=remote&sort=date",
    "https://www.linkedin.com/jobs/search?keywords=remote&sortBy=DD",
    # Arabic/MENA feeds
    "https://www.mostaql.com/jobs/feed",
    "https://for9a.com/jobs/feed",
    "https://wuzzuf.net/jobs/feed",
    "https://www.bayt.com/en/international/jobs/",
    "https://www.gulftalent.com/jobs",
    # Major platforms
    "https://www.glassdoor.com/Job/remote-jobs-SRCH_IL.0,6_IS11047_KO7,13.htm",
    "https://www.ziprecruiter.com/Jobs/Remote",
    "https://wellfound.com/role",
]

# Job board search patterns
JOB_BOARD_PATTERNS = [
    r"https?://[^\s\"']+remote[^\s\"']*\.xml",
    r"https?://[^\s\"']+jobs[^\s\"']*/feed",
    r"https?://[^\s\"']+rss[^\s\"']*jobs",
    r"https?://api\.[^\s\"']+/jobs",
    r"https?://[^\s\"']+\.json.*jobs",
]


def load_registry() -> dict:
    """Load the source registry."""
    try:
        if REGISTRY_FILE.exists():
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"sources": [], "last_discovery": "", "total_discoveries": 0}


def save_registry(registry: dict):
    """Save the source registry."""
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def log_discovery(source_url: str, status: str, details: str = ""):
    """Log a discovery attempt."""
    try:
        logs = []
        if DISCOVERY_LOG.exists():
            logs = json.loads(DISCOVERY_LOG.read_text(encoding="utf-8"))
        logs.append({
            "url": source_url,
            "status": status,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        # Keep last 500 entries
        DISCOVERY_LOG.write_text(json.dumps(logs[-500:], indent=2), encoding="utf-8")
    except Exception:
        pass


async def test_source(session: aiohttp.ClientSession, url: str) -> dict:
    """Test if a URL is a valid job source."""
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return {"valid": False, "reason": f"HTTP {resp.status}"}
            
            content_type = resp.headers.get("content-type", "")
            text = await resp.text()
            
            # Check for RSS/XML
            if "xml" in content_type or text.strip().startswith("<?xml") or "<rss" in text[:500]:
                items = re.findall(r"<item>[\s\S]*?</item>", text)
                if len(items) > 0:
                    return {"valid": True, "type": "rss", "items": len(items)}
            
            # Check for JSON API
            if "json" in content_type:
                try:
                    data = json.loads(text)
                    if isinstance(data, list) and len(data) > 0:
                        return {"valid": True, "type": "json", "items": len(data)}
                    if isinstance(data, dict):
                        for key in ["jobs", "results", "data", "postings"]:
                            if key in data and isinstance(data[key], list):
                                return {"valid": True, "type": "json", "items": len(data[key])}
                except json.JSONDecodeError:
                    pass
            
            # Check for HTML job listings
            if "html" in content_type:
                job_links = re.findall(r'href="([^"]*(?:job|position|role|career)[^"]*)"', text, re.I)
                if len(job_links) >= 3:
                    return {"valid": True, "type": "html", "items": len(job_links)}
            
            return {"valid": False, "reason": "No job content detected"}
    except Exception as e:
        return {"valid": False, "reason": str(e)[:100]}


def _derive_source_name(url: str) -> str:
    """Derive a readable source name from a URL."""
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc.lower()
        domain = re.sub(r"^www\.", "", domain)
        domain = re.sub(r"\.(com|org|net|io|co|ai|dev|jobs)$", "", domain)
        return re.sub(r"[^a-z0-9]+", "_", domain).strip("_") or "discovered"
    except Exception:
        return "discovered"


async def _crawl_seed(session: aiohttp.ClientSession, seed_url: str) -> list[str]:
    """Scan a seed page's HTML for links to feeds/APIs/job boards."""
    try:
        async with session.get(seed_url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            text = await resp.text()
        found: list[str] = []
        for pattern in JOB_BOARD_PATTERNS:
            for match in re.findall(pattern, text, re.I)[:8]:
                url = match.strip().strip('"\'')
                if url.startswith("//"):
                    url = "https:" + url
                elif url.startswith("/"):
                    url = "https://" + urlparse(seed_url).netloc + url
                elif not url.startswith("http"):
                    continue
                if url not in found:
                    found.append(url)
        return found[:10]
    except Exception:
        return []


async def discover_new_sources(registry: dict) -> list[dict]:
    """Discover new job sources from seeds and patterns."""
    from urllib.parse import urlparse

    new_sources = []
    existing_urls = {s["url"] for s in registry.get("sources", [])}
    
    async with aiohttp.ClientSession() as session:
        # Round 1: test the known seed URLs directly
        for url in DISCOVERY_SEEDS:
            if url in existing_urls:
                continue
            
            result = await test_source(session, url)
            if result["valid"]:
                source = {
                    "url": url,
                    "source_name": _derive_source_name(url),
                    "type": result["type"],
                    "items": result.get("items", 0),
                    "added": datetime.now(timezone.utc).isoformat(),
                    "auto_discovered": True,
                }
                new_sources.append(source)
                existing_urls.add(url)
                log_discovery(url, "discovered", f"{result['type']} ({result.get('items', 0)} items)")
                print(f"  ✓ Discovered: {url} ({result['type']}, {result.get('items', 0)} items)")
            else:
                log_discovery(url, "rejected", result.get("reason", ""))
        
        # Round 2: crawl seed pages for new feed/API links nobody has found yet
        candidates = []
        for url in DISCOVERY_SEEDS[:8]:
            for found in await _crawl_seed(session, url):
                if found not in existing_urls and found not in candidates:
                    candidates.append(found)
        
        tested = 0
        for url in candidates:
            if tested >= 15:
                break
            tested += 1
            result = await test_source(session, url)
            if result["valid"]:
                source = {
                    "url": url,
                    "source_name": _derive_source_name(url),
                    "type": result["type"],
                    "items": result.get("items", 0),
                    "added": datetime.now(timezone.utc).isoformat(),
                    "auto_discovered": True,
                }
                new_sources.append(source)
                existing_urls.add(url)
                log_discovery(url, "discovered", f"crawled: {result['type']} ({result.get('items', 0)} items)")
                print(f"  ✓ Crawled & discovered: {url} ({result['type']}, {result.get('items', 0)} items)")
            else:
                log_discovery(url, "rejected", result.get("reason", ""))
    
    return new_sources


async def run_discovery():
    """Main discovery routine."""
    print("CareerOps Source Auto-Discovery running...")
    
    registry = load_registry()
    print(f"  Known sources: {len(registry.get('sources', []))}")
    
    new_sources = await discover_new_sources(registry)
    
    if new_sources:
        registry["sources"].extend(new_sources)
        registry["last_discovery"] = datetime.now(timezone.utc).isoformat()
        registry["total_discoveries"] = registry.get("total_discoveries", 0) + len(new_sources)
        # Keep the registry bounded so it doesn't grow forever
        registry["sources"] = registry.get("sources", [])[:60]
        save_registry(registry)
        print(f"  ✓ Added {len(new_sources)} new sources")
    else:
        print("  No new sources discovered this run")
    
    print(f"  Total sources now: {len(registry.get('sources', []))}")
    return registry


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_discovery())
