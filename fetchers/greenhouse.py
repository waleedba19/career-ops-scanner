"""Greenhouse job boards."""
import re
from .base import BaseFetcher, FetchResult

# Probe-verified working boards (state/working_greenhouse_slugs.json, 2026-09-18).
# The classic LSP boards (TransPerfect/Lionbridge/RWS/Appen/Welocalize...) no
# longer publish on Greenhouse — they moved to other ATS — so they were dropped
# to stop burning requests on 404s.
GREENHOUSE_BOARDS = [
    ("WPP Media", "wppmedia"),
    ("Invisible", "agency"),
    ("Anthropic", "anthropic"),
    ("Cloudflare", "cloudflare"),
    ("OKX", "okx"),
    ("xAI", "xai"),
    ("GitLab", "gitlab"),
    ("Scale AI", "scaleai"),
    ("Figma", "figma"),
    ("Riot Games", "riotgames"),
    ("Duolingo", "duolingo"),
    ("Mozilla", "mozilla"),
    ("Snorkel AI", "snorkelai"),
    ("Prolific", "prolific"),
    ("Coursera", "coursera"),
    ("Careem", "careem"),
    ("Turing", "turing"),
    ("Toloka", "toloka"),
    ("Khan Academy", "khanacademy"),
    ("Udemy", "udemy"),
    ("Blend", "blend"),
    ("Labelbox", "labelbox"),
    ("Smartling", "smartling"),
    ("Masterclass", "masterclass"),
    ("Contentful", "contentful"),
    ("Lokalise", "lokalise"),
    ("Outschool", "outschool"),
    ("Remote.com", "remote"),
    ("KAYAK", "kayak"),
    ("Calm", "calm"),
]

# Additional translation/AI/EdTech boards to probe on the next probe run.
GREENHOUSE_PROSPECTS = [
    ("Akorbi", "akorbi"),
    ("Trusted Translations", "trustedtranslations"),
    ("Multilingual", "multilingual"),
    ("Bureau Works", "bureauworks"),
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
