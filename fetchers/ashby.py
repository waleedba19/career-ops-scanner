"""Ashby job boards."""
from .base import BaseFetcher, FetchResult

# Probe-verified working boards (2026-09-18); non-working slugs dropped.
ASHBY_BOARDS = [
    ("Mercor", "mercor"),
    ("Deel", "deel"),
    ("Oyster", "oyster"),
]


async def fetch_ashby_board(session, company: str, slug: str) -> list[dict]:
    """Fetch from a single Ashby board."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for job in data.get("jobPostings", []):
                jobs.append({
                    "title": job.get("title", ""),
                    "company": company,
                    "url": f"https://jobs.ashbyhq.com/{slug}/{job.get('id', '')}",
                    "location": job.get("locationName", ""),
                    "posted": job.get("createdAt", ""),
                    "description": job.get("descriptionPlain", "")[:500] if job.get("descriptionPlain") else "",
                    "salary": "",
                    "source": "ashby",
                })
            return jobs
    except Exception:
        return []
