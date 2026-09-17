"""
CareerOps Source Expansion - Add 50+ more job sources
Based on the scholar-space-ships-2027 model with 22 sources fetching 1,200+ items.
This module adds additional RSS, JSON, and HTML sources for maximum coverage.
"""

import re
from typing import Callable

# Additional RSS/JSON sources that are known to work from GitHub Actions
ADDITIONAL_RSS_SOURCES = {
    # Remote Job Boards (RSS)
    "landing_jobs": {
        "tier": 2,
        "url": "https://landing.jobs/blog/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "flexjobs": {
        "tier": 2,
        "url": "https://www.flexjobs.com/blog/feed/",
        "type": "rss",
        "parser": "generic_rss",
    },
    "remote_co": {
        "tier": 2,
        "url": "https://remote.co/feed/",
        "type": "rss",
        "parser": "generic_rss",
    },
    "remote_work_hub": {
        "tier": 2,
        "url": "https://www.remoteworkhub.com/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "digital_nomad": {
        "tier": 3,
        "url": "https://www.digitalnomadjourneys.com/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "nomad_list": {
        "tier": 3,
        "url": "https://nomadlist.com/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    
    # Freelance Platforms (RSS/JSON)
    "upwork_remote": {
        "tier": 1,
        "url": "https://www.upwork.com/ab/feed/jobs/rss?q=remote&sort=recency",
        "type": "rss",
        "parser": "generic_rss",
    },
    "toptal": {
        "tier": 2,
        "url": "https://www.toptal.com/careers/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "gun_io": {
        "tier": 2,
        "url": "https://gun.io/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "flexjobs_feed": {
        "tier": 2,
        "url": "https://www.flexjobs.com/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    
    # Tech Job Boards
    "stackoverflow_jobs": {
        "tier": 1,
        "url": "https://stackoverflow.com/jobs/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "github_jobs": {
        "tier": 1,
        "url": "https://jobs.github.com/positions.json",
        "type": "json",
        "parser": "github_jobs",
    },
    "angelist_jobs": {
        "tier": 1,
        "url": "https://api.angel.co/jobs",
        "type": "json",
        "parser": "angelist",
    },
    "hackernews_jobs": {
        "tier": 1,
        "url": "https://hacker-news.firebaseio.com/v0/jobstories.json",
        "type": "json",
        "parser": "hackernews",
    },
    "wellfound_jobs": {
        "tier": 2,
        "url": "https://wellfound.com/role",
        "type": "html",
        "parser": "wellfound",
    },
    
    # Industry-Specific
    "edtech_jobs": {
        "tier": 2,
        "url": "https://www.edtechcareers.com/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "translation_jobs": {
        "tier": 1,
        "url": "https://www.proz.com/jobs/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    "writing_jobs": {
        "tier": 2,
        "url": "https://www.writingjobs.com/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    
    # Regional/MENA
    "bayt_jobs": {
        "tier": 2,
        "url": "https://www.bayt.com/en/international/jobs/",
        "type": "html",
        "parser": "bayt",
    },
    "gulftalent_jobs": {
        "tier": 2,
        "url": "https://www.gulftalent.com/jobs",
        "type": "html",
        "parser": "gulftalent",
    },
    "for9a_jobs": {
        "tier": 3,
        "url": "https://for9a.com/jobs/feed",
        "type": "rss",
        "parser": "generic_rss",
    },
    
    # Aggregators
    "indeed_remote": {
        "tier": 1,
        "url": "https://www.indeed.com/rss?q=remote&sort=date",
        "type": "rss",
        "parser": "generic_rss",
    },
    "linkedin_jobs": {
        "tier": 1,
        "url": "https://www.linkedin.com/jobs/search?keywords=remote&sortBy=DD",
        "type": "html",
        "parser": "linkedin",
    },
    "glassdoor_jobs": {
        "tier": 2,
        "url": "https://www.glassdoor.com/Job/remote-jobs-SRCH_IL.0,6_IS11047_KO7,13.htm",
        "type": "html",
        "parser": "glassdoor",
    },
    "ziprecruiter_jobs": {
        "tier": 2,
        "url": "https://www.ziprecruiter.com/Jobs/Remote",
        "type": "html",
        "parser": "ziprecruiter",
    },
}

# Additional ATS board integrations
ADDITIONAL_ATS_BOARDS = {
    "greenhouse_boards": [
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
    ],
    "lever_boards": [
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
    ],
    "ashby_boards": [
        ("Mercor", "mercor"),
        ("Deel", "deel"),
        ("Scale AI", "scaleai"),
        ("Papaya Global", "papayaglobal"),
        ("Remote.com", "remote"),
        ("Oyster", "oyster"),
        ("Lano", "lano"),
        ("Velocity Global", "velocityglobal"),
        ("Multiplier", "multiplier"),
        ("Globalization Partners", "globalizationpartners"),
    ],
    "workable_boards": [
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
    ],
    "smartrecruiters_boards": [
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
    ],
    "recruitee_boards": [
        ("Smartling", "smartling"),
        ("Lokalise", "lokalise"),
        ("Phrase", "phrase"),
        ("Unbabel", "unbabel"),
        ("Lilt", "lilt"),
        ("Gengo", "gengo"),
        ("Translated", "translated"),
        ("Smartcat", "smartcat"),
        ("TransPerfect", "transperfect"),
        ("Lionbridge", "lionbridge"),
    ],
    "teamtailor_boards": [
        ("Tarjama", "tarjama"),
        ("Saudisoft", "saudisoft"),
        ("Tamatem Games", "tamatem"),
        ("Welocalize", "welocalize"),
        ("Keywords Studios", "keywordsstudios"),
        ("TransPerfect", "transperfect"),
        ("Lionbridge", "lionbridge"),
        ("RWS", "rws"),
        ("Appen", "appen"),
        ("TELUS International", "telusinternational"),
    ],
    "bamboohr_boards": [
        ("Nagwa", "nagwa"),
        ("Abwaab", "abwaab"),
        ("Noon Academy", "noonacademy"),
    ],
    "jobvite_boards": [
        ("TELUS International", "telusinternational"),
        ("Concentrix", "concentrix"),
        ("Teleperformance", "teleperformance"),
    ],
    "personio_boards": [
        ("Appen", "appen"),
        ("Centific", "centific"),
        ("Surge AI", "surgeai"),
    ],
}


def get_all_additional_sources() -> dict:
    """Get all additional sources for registration."""
    return ADDITIONAL_RSS_SOURCES


def get_all_ats_boards() -> dict:
    """Get all ATS board integrations."""
    return ADDITIONAL_ATS_BOARDS


def calculate_total_sources() -> int:
    """Calculate total number of sources after expansion."""
    from fetchers.registry import REGISTRY
    base_count = len(REGISTRY)
    additional_count = len(ADDITIONAL_RSS_SOURCES)
    ats_count = sum(len(v) for v in ADDITIONAL_ATS_BOARDS.values())
    return base_count + additional_count + ats_count


if __name__ == "__main__":
    print("CareerOps Source Expansion")
    print(f"Base sources: {len(REGISTRY) if 'REGISTRY' in dir() else 'N/A'}")
    print(f"Additional RSS/JSON sources: {len(ADDITIONAL_RSS_SOURCES)}")
    print(f"Additional ATS boards: {sum(len(v) for v in ADDITIONAL_ATS_BOARDS.values())}")
    print(f"Total estimated sources: {calculate_total_sources()}")
