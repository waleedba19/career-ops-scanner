"""Workable job boards."""
from .base import BaseFetcher, FetchResult

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
    """Fetch from a single Workable board."""
    url = f"https://{slug}.workable.com/jobs"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            import re
            text = await resp.text()
            jobs = []
            cards = re.findall(r'<div[^>]+class="[^"]*job[^"]*"[^>]*>([\s\S]*?)</div>', text)
            for card in cards[:30]:
                title_match = re.search(r'<h2[^>]*>([\s\S]*?)</h2>', card)
                link_match = re.search(r'href="([^"]+)"', card)
                if title_match and link_match:
                    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                    link = link_match.group(1)
                    if not link.startswith("http"):
                        link = f"https://{slug}.workable.com{link}"
                    jobs.append({
                        "title": title[:160],
                        "company": company,
                        "url": link,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "workable",
                    })
            return jobs
    except Exception:
        return []
