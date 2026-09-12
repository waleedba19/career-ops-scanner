"""SmartRecruiters job boards."""
from .base import BaseFetcher, FetchResult

SMARTRECRUITERS_BOARDS = [
    ("Keywords Studios", "KeywordsStudios"),
    ("TransPerfect", "TransPerfect"),
    ("Lionbridge", "lionbridge"),
    ("RWS", "rws"),
    ("Appen", "appen"),
    ("TELUS International", "telusinternational"),
    ("Concentrix", "concentrix"),
    ("Teleperformance", "teleperformance"),
    ("Alorica", "alorica"),
    ("Sitel", "sitel"),
]


async def fetch_smartrecruiters_board(session, company: str, slug: str) -> list[dict]:
    """Fetch from a single SmartRecruiters board."""
    url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for job in data.get("content", []):
                jobs.append({
                    "title": job.get("name", ""),
                    "company": company,
                    "url": job.get("ref", ""),
                    "location": job.get("location", {}).get("city", ""),
                    "posted": job.get("releasedDate", ""),
                    "description": job.get("jobAd", {}).get("sections", {}).get("jobDescription", {}).get("text", "")[:500] if job.get("jobAd") else "",
                    "salary": "",
                    "source": "smartrecruiters",
                })
            return jobs
    except Exception:
        return []
