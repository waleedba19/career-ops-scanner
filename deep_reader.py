"""
Deep Page Reader - extracts detailed information from job pages.
Reads individual job pages to get eligibility, requirements, and contact info.
"""
import re
import asyncio
from typing import Optional
from bs4 import BeautifulSoup

try:
    import aiohttp
except ImportError:
    aiohttp = None


class DeepPageReader:
    """
    Reads individual job pages and extracts structured data.
    """

    def __init__(self):
        self.session = None

    async def read_page(self, url: str) -> dict:
        """
        Read a job page and extract structured data.
        
        Returns:
            dict with keys: title, description, eligibility, requirements,
                           contact, deadline, salary, location, is_remote
        """
        if not aiohttp:
            return {"error": "aiohttp not installed"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        return {"error": f"HTTP {resp.status}"}
                    html = await resp.text()
                    return self._parse_page(html, url)
        except Exception as e:
            return {"error": str(e)}

    def _parse_page(self, html: str, url: str) -> dict:
        """Parse HTML and extract job information."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        
        return {
            "url": url,
            "title": self._extract_title(soup),
            "description": self._extract_description(soup, text),
            "eligibility": self._extract_eligibility(text),
            "requirements": self._extract_requirements(text),
            "contact": self._extract_contact(text),
            "deadline": self._extract_deadline(text),
            "salary": self._extract_salary(text),
            "location": self._extract_location(text),
            "is_remote": self._check_remote(text),
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title."""
        # Try common title patterns
        title_selectors = [
            'h1.job-title', 'h1.posting-headline', 'h1[data-ui="job-title"]',
            'h1[class*="title"]', 'h1[class*="job"]', 'h1', 'title'
        ]
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)[:200]
        return ""

    def _extract_description(self, soup: BeautifulSoup, text: str) -> str:
        """Extract job description."""
        # Try common description patterns
        desc_selectors = [
            '.job-description', '.posting-content', '.description',
            '[data-ui="job-description"]', 'article', 'main'
        ]
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(separator=' ', strip=True)
                if len(desc) > 100:  # Likely the main content
                    return desc[:3000]
        
        # Fallback to main text
        return text[:3000]

    def _extract_eligibility(self, text: str) -> list:
        """Extract eligibility requirements."""
        eligibility = []
        
        # Common eligibility patterns
        patterns = [
            r'(?:must|should|need to|required to)\s+(.{50,200}?)(?:\.|$)',
            r'(?:eligible|qualification|requirement)[:\s]+(.{50,200}?)(?:\.|$)',
            r'(?:who can apply|eligibility|requirements)[:\s]+(.{50,200}?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean = match.strip()
                if 20 < len(clean) < 300:
                    eligibility.append(clean)
        
        return eligibility[:5]  # Limit to 5 items

    def _extract_requirements(self, text: str) -> list:
        """Extract job requirements."""
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'(?:requirements|qualifications|what you need)[:\s]+(.{100,500}?)(?:what you|about|benefits|salary)',
            r'(?:experience|skills required)[:\s]+(.{50,200}?)(?:\.|$)',
            r'(?:\d+\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience\s+(?:in|with)\s+)(.{20,100}?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean = match.strip()
                if 10 < len(clean) < 500:
                    # Split by newlines or bullet points
                    items = re.split(r'[\n•\-\*]+', clean)
                    for item in items:
                        item = item.strip()
                        if 5 < len(item) < 200:
                            requirements.append(item)
        
        return requirements[:10]  # Limit to 10 items

    def _extract_contact(self, text: str) -> dict:
        """Extract contact information."""
        contact = {}
        
        # Email pattern
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact["email"] = email_match.group(0)
        
        # Phone pattern (international)
        phone_match = re.search(r'(?:\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text)
        if phone_match:
            contact["phone"] = phone_match.group(0)
        
        # Application link
        apply_match = re.search(r'(?:apply|application|submit)[:\s]+(https?://\S+)', text, re.IGNORECASE)
        if apply_match:
            contact["apply_url"] = apply_match.group(1)
        
        return contact

    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract application deadline."""
        patterns = [
            r'(?:deadline|closing date|apply by|applications? close)[:\s]+(.{10,50}?)(?:\.|$)',
            r'(?:deadline|closing date)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:deadline|closing date)[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:50]
        
        return None

    def _extract_salary(self, text: str) -> Optional[str]:
        """Extract salary information."""
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

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location."""
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

    def _check_remote(self, text: str) -> bool:
        """Check if job is remote."""
        remote_indicators = ['remote', 'work from home', 'wfh', 'anywhere', 'worldwide', 'distributed']
        text_lower = text.lower()
        
        for indicator in remote_indicators:
            if indicator in text_lower:
                return True
        
        return False


def enrich_jobs_with_deep_read(jobs: list[dict], max_deep_reads: int = 20) -> list[dict]:
    """
    Enrich top candidates with deep page reading.
    
    Args:
        jobs: List of job dicts with 'url' and 'final_score'
        max_deep_reads: Maximum number of pages to read
        
    Returns:
        Enriched job list
    """
    if not jobs:
        return jobs
    
    # Sort by score to read the best candidates first
    sorted_jobs = sorted(jobs, key=lambda x: x.get("final_score", 0), reverse=True)
    
    # Limit to top candidates
    jobs_to_read = sorted_jobs[:max_deep_reads]
    
    reader = DeepPageReader()
    
    async def _read_all():
        tasks = []
        for job in jobs_to_read:
            url = job.get("url", "")
            if url and url.startswith("http"):
                tasks.append(reader.read_page(url))
            else:
                tasks.append(asyncio.sleep(0))  # Placeholder for jobs without URLs
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for job, result in zip(jobs_to_read, results):
            if isinstance(result, dict) and not result.get("error"):
                job["deep_read"] = result
                # Update fields if deep read found better data
                if result.get("eligibility"):
                    job["eligibility"] = result["eligibility"]
                if result.get("requirements"):
                    job["requirements"] = result["requirements"]
                if result.get("contact"):
                    job["contact"] = result["contact"]
                    ce = (result["contact"] or {}).get("email")
                    if ce and not job.get("hiring_email"):
                        job["hiring_email"] = ce
                    cu = (result["contact"] or {}).get("apply_url")
                    if cu and not job.get("apply_url"):
                        job["apply_url"] = cu
                if result.get("deadline"):
                    job["deadline"] = result["deadline"]
                if result.get("salary"):
                    job["salary"] = result["salary"]
        
        return jobs
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, _read_all()).result()
        else:
            return loop.run_until_complete(_read_all())
    except RuntimeError:
        return asyncio.run(_read_all())
