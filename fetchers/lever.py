"""Lever job boards."""
from .base import BaseFetcher, FetchResult

# Probe-verified working boards (state/working_lever_slugs.json, 2026-09-18).
LEVER_BOARDS = [
    ("Appen", "appen"),
]


async def fetch_lever_board(session, company: str, slug: str) -> list[dict]:
    """Fetch from a single Lever board."""
    url = f"https://api.lever.co/v0/postings/{slug}"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for job in data if isinstance(data, list) else []:
                jobs.append({
                    "title": job.get("text", ""),
                    "company": company,
                    "url": job.get("hostedUrl", ""),
                    "location": job.get("categories", {}).get("location", ""),
                    "posted": job.get("createdAt", ""),
                    "description": job.get("descriptionPlain", "")[:500] if job.get("descriptionPlain") else "",
                    "salary": "",
                    "source": "lever",
                })
            return jobs
    except Exception:
        return []
