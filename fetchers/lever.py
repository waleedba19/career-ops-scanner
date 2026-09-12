"""Lever job boards."""
from .base import BaseFetcher, FetchResult

LEVER_BOARDS = [
    ("Appen", "appen"),
    ("Unbabel", "unbabel"),
    ("Lilt", "lilt"),
    ("Anghami", "anghami"),
    ("Noon Academy", "noonacademy"),
    ("Vice Media", "vice"),
    ("Figma", "figma"),
    ("Notion", "notion"),
    ("Coinbase", "coinbase"),
    ("Square", "square"),
    ("DoorDash", "doordash"),
    ("Flexport", "flexport"),
    ("GitLab", "gitlab"),
    ("Postmates", "postmates"),
    ("WeWork", "wework"),
    ("N26", "n26"),
    ("Revolut", "revolut"),
    ("Monzo", "monzo"),
    ("Nubank", "nubank"),
    ("Klarna", "klarna"),
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
