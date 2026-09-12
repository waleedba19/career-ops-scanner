"""Greenhouse job boards."""
import re
from .base import BaseFetcher, FetchResult

GREENHOUSE_BOARDS = [
    ("Invisible", "agency"),
    ("Labelbox", "labelbox"),
    ("Turing", "turing"),
    ("Prolific", "prolific"),
    ("Deel", "deel"),
    ("Handshake", "joinhandshake"),
    ("Toloka", "toloka"),
    ("TELUS International", "telusinternational"),
    ("Welocalize", "welocalize"),
    ("RWS", "rws"),
    ("Keywords Studios", "KeywordsStudios"),
    ("TransPerfect", "TransPerfect"),
    ("Lionbridge", "lionbridge"),
    ("Appen", "appen"),
    ("Centific", "centific"),
    ("Surge AI", "surgeai"),
    ("Micro1", "micro1"),
]


async def fetch_greenhouse_board(session, company: str, slug: str) -> list[dict]:
    """Fetch from a single Greenhouse board."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for job in data.get("jobs", []):
                jobs.append({
                    "title": job.get("title", ""),
                    "company": company,
                    "url": job.get("absolute_url", ""),
                    "location": job.get("location", {}).get("name", ""),
                    "posted": job.get("updated_at", ""),
                    "description": job.get("content", "")[:500] if job.get("content") else "",
                    "salary": "",
                    "source": "greenhouse",
                })
            return jobs
    except Exception:
        return []
