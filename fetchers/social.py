
"""Reddit social-signal fetcher — job & gig posts from communities in the
candidate's niche (ESL teaching, Arabic-English translation, academic editing).

Design notes:
- Uses Reddit's public JSON search endpoints (no API key, no CLI chain).
  Same plain-HTTP approach as the rest of the fleet; degrades gracefully
  (returns []) when Reddit rate-limits or blocks the runner IP.
- t=week + sort=new: only posts from the last 7 days, newest first.
- Everything downstream (dedup, scoring, gates, delivery) is the standard
  pipeline — reddit_social jobs are just another source.
"""

import asyncio
from datetime import datetime, timezone

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (careerops-scan)"
}
TIMEOUT = aiohttp.ClientTimeout(total=10)

# (subreddit, search query) — the candidate's three niches where people
# actually post openings and gigs.
REDDIT_TARGETS = [
    ("forhire", "ESL teacher remote"),
    ("forhire", "Arabic translator"),
    ("RemoteJobs", "ESL"),
    ("RemoteJobs", "Arabic translator"),
    ("esl", "remote teacher hire"),
    ("Translation", "Arabic English remote"),
    ("languagelearning", "ESL remote"),
]
PER_TARGET_LIMIT = 15


def parse_reddit_listing(payload) -> list[dict]:
    """Pure parser for a /search.json payload (unit-testable offline)."""
    out: list[dict] = []
    if not isinstance(payload, dict):
        return out
    children = (payload.get("data") or {}).get("children") or []
    for c in children:
        p = (c or {}).get("data") or {}
        title = (p.get("title") or "").strip()
        permalink = p.get("permalink") or ""
        if not title or not permalink:
            continue
        posted = ""
        created = p.get("created_utc")
        if isinstance(created, (int, float)):
            try:
                posted = datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
            except Exception:
                posted = ""
        url = permalink if permalink.startswith("http") else "https://www.reddit.com" + permalink
        sub = p.get("subreddit") or ""
        out.append({
            "title": title[:160],
            "company": f"r/{sub}" if sub else "Reddit",
            "url": url,
            "location": "Remote",
            "posted": posted,
            "description": (p.get("selftext") or "").strip()[:2000],
            "salary": "",
            "source": "reddit_social",
        })
    return out


async def _reddit_search(session: aiohttp.ClientSession, sub: str, query: str, limit: int) -> dict:
    q = query.replace(" ", "+")
    url = (f"https://www.reddit.com/r/{sub}/search.json"
           f"?q={q}&restrict_sr=1&sort=new&t=week&limit={limit}")
    async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
        if resp.status == 200:
            return await resp.json(content_type=None)
        # Fallback mirror before giving up (datacenter IPs often get 403)
        if resp.status in (403, 429):
            alt = url.replace("https://www.reddit.com", "https://old.reddit.com")
            async with session.get(alt, headers=HEADERS, timeout=TIMEOUT) as resp2:
                if resp2.status == 200:
                    return await resp2.json(content_type=None)
    return {}


async def fetch_reddit_social(session: aiohttp.ClientSession) -> list[dict]:
    """Search the niche communities and return job-shaped dicts."""
    jobs: list[dict] = []
    seen: set[str] = set()
    for sub, query in REDDIT_TARGETS:
        try:
            payload = await _reddit_search(session, sub, query, PER_TARGET_LIMIT)
            for j in parse_reddit_listing(payload):
                if j["url"] in seen:
                    continue
                seen.add(j["url"])
                jobs.append(j)
        except Exception as e:
            print(f"  Reddit r/{sub}: {e}")
    print(f"  Reddit social: {len(jobs)} posts from {len(REDDIT_TARGETS)} communities")
    return jobs
