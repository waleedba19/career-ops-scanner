"""
Auto Source Discovery — discovers and manages job sources automatically.
Tests known translation RSS feeds, tracks active sources, removes stale ones.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

STATE_DIR = Path(__file__).parent / "state"
AUTO_SOURCES_FILE = STATE_DIR / "auto_sources.json"

KNOWN_TRANSLATION_FEEDS = [
    {"name": "ProZ", "url": "https://www.proz.com/jobs/feed", "type": "rss"},
    {"name": "Smartcat", "url": "https://www.smartcat.com/marketplace/rss", "type": "rss"},
    {"name": "GoTranscript", "url": "https://www.gotranscript.com/rss", "type": "rss"},
    {"name": "RemoteOK Translation", "url": "https://remoteok.com/remote-translation-jobs.json", "type": "json"},
]


def _load_sources() -> dict:
    try:
        if AUTO_SOURCES_FILE.exists():
            data = json.loads(AUTO_SOURCES_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return {"sources": data}
            return data
    except Exception:
        pass
    return {"sources": []}


def _save_sources(data: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    AUTO_SOURCES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def add_source(name: str, url: str, source_type: str = "rss"):
    """Add a new source to the auto-discovery list."""
    data = _load_sources()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Deduplicate by URL
    for s in data["sources"]:
        if s.get("url") == url:
            s["last_active"] = today
            s["name"] = name
            _save_sources(data)
            return
    data["sources"].append({
        "name": name,
        "url": url,
        "type": source_type,
        "added": today,
        "last_active": today,
        "jobs_found": 0,
        "consecutive_empty": 0,
    })
    _save_sources(data)


def get_active_sources() -> list[dict]:
    """Return sources that returned jobs in the last 7 days."""
    data = _load_sources()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    active = []
    for s in data["sources"]:
        last = s.get("last_active", "")
        if last and last >= cutoff and s.get("consecutive_empty", 0) < 14:
            active.append(s)
    return active


def record_source_result(url: str, jobs_found: int):
    """Update a source's stats after a fetch attempt."""
    data = _load_sources()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for s in data["sources"]:
        if s.get("url") == url:
            s["last_active"] = today
            s["jobs_found"] = s.get("jobs_found", 0) + jobs_found
            if jobs_found > 0:
                s["consecutive_empty"] = 0
            else:
                s["consecutive_empty"] = s.get("consecutive_empty", 0) + 1
            _save_sources(data)
            return


def remove_stale_sources():
    """Remove sources with 0 jobs for 14+ days."""
    data = _load_sources()
    today = datetime.now(timezone.utc).date()
    before = len(data["sources"])
    kept = []
    for s in data["sources"]:
        last = s.get("last_active", "")
        empty = s.get("consecutive_empty", 0)
        if empty >= 14:
            continue
        if last:
            try:
                last_date = datetime.strptime(last, "%Y-%m-%d").date()
                if (today - last_date).days > 30 and empty > 0:
                    continue
            except Exception:
                pass
        kept.append(s)
    data["sources"] = kept
    _save_sources(data)
    return before - len(kept)


def discover_translation_feeds():
    """Test known translation RSS feeds and add active ones."""
    import aiohttp
    discovered = []

    async def _test_feeds():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            for feed in KNOWN_TRANSLATION_FEEDS:
                try:
                    async with session.get(
                        feed["url"],
                        timeout=aiohttp.ClientTimeout(total=10),
                        headers={"User-Agent": "Mozilla/5.0 (compatible; CareerOps/1.0)"},
                    ) as resp:
                        if resp.status == 200:
                            add_source(feed["name"], feed["url"], feed["type"])
                            discovered.append(feed["name"])
                            record_source_result(feed["url"], 1)
                            print(f"  Auto-source discovered: {feed['name']} ({feed['url']})")
                        else:
                            print(f"  Auto-source skip: {feed['name']} (HTTP {resp.status})")
                except Exception as e:
                    print(f"  Auto-source error: {feed['name']} ({e})")
    try:
        loop = __import__('asyncio').get_event_loop()
        if loop.is_running():
            # Already inside an async context — schedule as a task
            import asyncio
            asyncio.ensure_future(_test_feeds())
        else:
            loop.run_until_complete(_test_feeds())
    except RuntimeError:
        import asyncio
        asyncio.run(_test_feeds())
    return discovered


def fetch_generic_rss(session, url: str, name: str):
    """Generic RSS/JSON fetcher for auto-discovered sources."""
    import re
    import aiohttp

    async def _fetch():
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"User-Agent": "Mozilla/5.0 (compatible; CareerOps/1.0)"},
            ) as resp:
                if resp.status != 200:
                    record_source_result(url, 0)
                    return []
                if url.endswith(".json") or "json" in resp.content_type:
                    data = await resp.json(content_type=None)
                    items = data if isinstance(data, list) else data.get("jobs") or data.get("items") or []
                    jobs = []
                    for j in items[:100]:
                        jobs.append({
                            "title": j.get("title") or j.get("name") or j.get("position", ""),
                            "company": j.get("company") or j.get("company_name") or name,
                            "url": j.get("url") or j.get("apply_url") or j.get("link", ""),
                            "location": j.get("location", "Remote"),
                            "posted": j.get("date") or j.get("published_at") or j.get("created_at", ""),
                            "description": j.get("description", ""),
                            "salary": j.get("salary", ""),
                            "source": name.lower().replace(" ", "_"),
                        })
                    record_source_result(url, len(jobs))
                    return [j for j in jobs if j.get("url")]
                else:
                    xml = await resp.text()
                    items = re.findall(r"<item>[\s\S]*?</item>", xml)
                    jobs = []
                    for item in items[:100]:
                        def get(tag):
                            m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                            return m.group(1) if m else ""
                        title = get("title").replace("&amp;", "&").strip()
                        if not title:
                            continue
                        link = get("link").strip()
                        desc = re.sub(r"<[^>]+>", " ", get("description")).strip()
                        jobs.append({
                            "title": title,
                            "company": name,
                            "url": link,
                            "location": "Remote",
                            "posted": get("pubDate") or "",
                            "description": desc,
                            "salary": "",
                            "source": name.lower().replace(" ", "_"),
                        })
                    record_source_result(url, len(jobs))
                    return [j for j in jobs if j.get("url")]
        except Exception as e:
            print(f"  Auto-source fetch error ({name}): {e}")
            record_source_result(url, 0)
            return []
    return _fetch()
