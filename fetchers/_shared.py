"""Shared fetch helpers for CareerOps fetchers."""
import re
import html
from typing import Optional


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_salary(text: str) -> Optional[str]:
    """Extract salary information from text."""
    if not text:
        return None
    patterns = [
        r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*/\s*(?:hr|hour|year|annum|month|mo))?',
        r'€[\d,]+(?:\s*-\s*€[\d,]+)?(?:\s*/\s*(?:hr|hour|year|annum|month|mo))?',
        r'£[\d,]+(?:\s*-\s*£[\d,]+)?(?:\s*/\s*(?:hr|hour|year|annum|month|mo))?',
        r'[\d,]+(?:\s*-\s*[\d,]+)?\s*(?:USD|EUR|GBP|CAD|AUD)\s*/\s*(?:yr|year|hr|hour)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def extract_location(text: str) -> Optional[str]:
    """Extract location from text, returning None for remote/worldwide."""
    if not text:
        return None
    remote_indicators = ['remote', 'worldwide', 'anywhere', 'global', 'distributed', 'work from home']
    text_lower = text.lower()
    for indicator in remote_indicators:
        if indicator in text_lower:
            return "Remote"
    # Try to extract specific location
    location_match = re.search(r'(?:in|at|located in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
    if location_match:
        return location_match.group(1)
    return None


def normalize_job(raw: dict, source: str) -> dict:
    """Normalize a raw job record into the canonical job dict."""
    title = str(raw.get("title") or raw.get("name") or "").strip()
    description = str(raw.get("description") or raw.get("snippet") or "").strip()
    url = str(raw.get("url") or raw.get("link") or raw.get("apply_url") or "").strip()
    company = str(raw.get("company") or raw.get("organization") or "").strip()
    location = str(raw.get("location") or raw.get("remote_location") or "").strip()
    
    return {
        "id": raw.get("id") or f"{source}:{hash(url)}",
        "title": title,
        "description": description[:2000],
        "url": url,
        "company": company,
        "location": location,
        "source": source,
        "posted_at": raw.get("posted_at") or raw.get("created_at") or raw.get("date") or "",
        "salary": extract_salary(f"{title} {description}"),
        "tags": raw.get("tags") or [],
        "is_remote": raw.get("is_remote") or "remote" in location.lower() if location else False,
    }
