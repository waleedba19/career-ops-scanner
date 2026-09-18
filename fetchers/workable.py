"""Workable job boards."""
from .base import BaseFetcher, FetchResult

# Verified slugs (apply.workable.com/<slug>). The legacy <slug>.workable.com/jobs
# URL pattern was dead; the widget API below is the live one.
WORKABLE_BOARDS = [
    ("Tamatem Games", "tamatem"),
    ("Abwaab", "abwaab"),
    ("Nagwa", "nagwa"),
    ("Noon Academy", "noonacademy"),
    ("Edraak", "edraak"),
    ("Almentor", "almentor"),
    ("Baims", "baims"),
    ("Careem", "careem"),
    ("Tarjama", "tarjama"),
    ("Saudisoft", "saudisoft"),
]


async def fetch_workable_board(session, company: str, slug: str) -> list[dict]:
    """Fetch a single Workable board via the public widget API (JSON)."""
    url = f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for job in data.get("jobs", []):
                loc = ", ".join(
                    x for x in [job.get("city"), job.get("country")] if x
                )
                if job.get("telecommuting") and not loc:
                    loc = "Remote"
                jobs.append({
                    "title": job.get("title", ""),
                    "company": company,
                    "url": job.get("url") or job.get("shortlink", ""),
                    "location": loc or "Remote",
                    "posted": job.get("published_on") or job.get("created_at") or "",
                    "description": job.get("description", "")[:500],
                    "salary": "",
                    "source": "workable",
                })
            return jobs
    except Exception:
        return []
