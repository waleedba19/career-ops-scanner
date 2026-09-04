"""
Company Research Module for CareerOps
Gathers company information before scoring to improve match accuracy.
Checks if company is legitimate, remote-friendly, and matches user preferences.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

CACHE_DIR = Path(__file__).parent / "output" / "company_cache"
CACHE_FILE = CACHE_DIR / "company_data.json"


def load_company_cache() -> dict:
    """Load company cache from file."""
    try:
        if CACHE_FILE.exists():
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_company_cache(cache: dict):
    """Save company cache to file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, default=str), encoding="utf-8")


def extract_company_from_url(url: str) -> str:
    """Extract company name from job URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. and common TLDs
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'\.(com|org|net|io|co|ai|dev)$', '', domain)
        
        # Handle specific job boards
        if "greenhouse.io" in domain:
            # Extract company from greenhouse URL
            parts = parsed.path.strip('/').split('/')
            if parts:
                return parts[0]
        
        if "lever.co" in domain:
            parts = parsed.path.strip('/').split('/')
            if parts:
                return parts[0]
        
        return domain
    except Exception:
        return "unknown"


def get_company_research(company: str, url: str = "") -> dict:
    """
    Research a company using cached data and basic heuristics.
    Returns company profile with legitimacy score.
    """
    cache = load_company_cache()
    
    # Check cache first
    if company in cache:
        return cache[company]
    
    # Basic heuristics
    research = {
        "name": company,
        "legitimacy_score": 50,  # Default neutral
        "remote_friendly": True,  # Assume yes for remote jobs
        "size_estimate": "unknown",
        "industry": "unknown",
        "red_flags": [],
        "positive_signals": [],
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    
    # Check URL for signals
    if url:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Positive signals from domain
        if any(x in domain for x in ["greenhouse.io", "lever.co", "ashbyhq.com"]):
            research["legitimacy_score"] += 20
            research["positive_signals"].append("Uses professional ATS")
        
        # Known job boards
        if any(x in domain for x in ["linkedin.com", "indeed.com", "glassdoor.com"]):
            research["legitimacy_score"] += 10
            research["positive_signals"].append("Listed on major job board")
        
        # Red flags
        if any(x in domain for x in ["freelancer.com", "upwork.com", "fiverr.com"]):
            research["legitimacy_score"] -= 10
            research["red_flags"].append("Freelance platform (may not be full-time)")
    
    # Check company name for signals
    company_lower = company.lower()
    
    # Positive name signals
    if any(x in company_lower for x in ["inc", "llc", "ltd", "corp", "group", "services"]):
        research["legitimacy_score"] += 5
        research["positive_signals"].append("Appears to be registered business")
    
    # Red flag names
    if any(x in company_lower for x in ["urgent", "immediate", "fast money", "no experience"]):
        research["legitimacy_score"] -= 20
        research["red_flags"].append("Suspicious name keywords")
    
    # Cap score
    research["legitimacy_score"] = max(0, min(100, research["legitimacy_score"]))
    
    # Cache the result
    cache[company] = research
    save_company_cache(cache)
    
    return research


def should_boost_score(research: dict) -> float:
    """
    Returns score adjustment based on company research.
    Positive = boost, negative = reduce.
    """
    adjustment = 0
    
    # Legitimacy score
    leg_score = research.get("legitimacy_score", 50)
    if leg_score >= 70:
        adjustment += 5  # Boost for legitimate companies
    elif leg_score <= 30:
        adjustment -= 10  # Reduce for suspicious companies
    
    # Red flags
    red_flags = research.get("red_flags", [])
    adjustment -= len(red_flags) * 3
    
    # Positive signals
    positive = research.get("positive_signals", [])
    adjustment += len(positive) * 2
    
    return adjustment


def get_company_summary(company: str, research: dict) -> str:
    """Get a one-line summary of company research."""
    if not research:
        return ""
    
    leg_score = research.get("legitimacy_score", 50)
    red_flags = len(research.get("red_flags", []))
    positive = len(research.get("positive_signals", []))
    
    parts = []
    if leg_score >= 70:
        parts.append("Verified company")
    elif leg_score <= 30:
        parts.append("Caution advised")
    
    if red_flags > 0:
        parts.append(f"{red_flags} red flags")
    
    if positive > 0:
        parts.append(f"{positive} positive signals")
    
    return " • ".join(parts) if parts else ""


def research_companies_batch(jobs: list[dict]) -> list[dict]:
    """
    Research companies for a batch of jobs.
    Enriches each job with company research data.
    """
    for job in jobs:
        company = job.get("company", "unknown")
        url = job.get("url", "")
        
        research = get_company_research(company, url)
        job["company_research"] = research
        job["company_legitimacy"] = research.get("legitimacy_score", 50)
        job["company_summary"] = get_company_summary(company, research)
        
        # Apply score adjustment
        adjustment = should_boost_score(research)
        if adjustment != 0:
            current_score = job.get("score", 0)
            job["score"] = max(0, min(100, current_score + adjustment))
            job["score_adjustment"] = adjustment
    
    return jobs


def cleanup_old_cache(max_age_days: int = 30):
    """Remove old cache entries."""
    cache = load_company_cache()
    cutoff = datetime.now(timezone.utc).timestamp() - (max_age_days * 86400)
    
    cleaned = {}
    for company, data in cache.items():
        try:
            updated = datetime.fromisoformat(data.get("last_updated", "")).timestamp()
            if updated > cutoff:
                cleaned[company] = data
        except Exception:
            cleaned[company] = data
    
    save_company_cache(cleaned)
    return len(cache) - len(cleaned)
