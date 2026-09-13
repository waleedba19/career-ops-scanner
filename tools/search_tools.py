"""DuckDuckGo Search Tool — Free web search, no API key required."""
import re
from typing import Type
from pydantic import BaseModel, Field

try:
    from crewai_tools import BaseTool
except ImportError:
    # Fallback if crewai_tools not installed
    class BaseTool:
        name: str = ""
        description: str = ""
        def _run(self, *args, **kwargs):
            raise NotImplementedError


class DuckDuckGoSearchInput(BaseModel):
    """Input for DuckDuckGo search."""
    query: str = Field(..., description="Search query for finding jobs")
    max_results: int = Field(default=10, description="Maximum number of results")


class DuckDuckGoSearchTool(BaseTool):
    """Search the web using DuckDuckGo — free, no API key required."""
    name: str = "duckduckgo_search"
    description: str = "Search the web for job listings using DuckDuckGo"
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str, max_results: int = 10) -> str:
        """Execute DuckDuckGo search."""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", r.get("link", "")),
                        "body": r.get("body", r.get("snippet", "")),
                    })
            
            if not results:
                return "No results found"
            
            output = []
            for i, r in enumerate(results, 1):
                output.append(f"{i}. {r['title']}")
                output.append(f"   URL: {r['url']}")
                output.append(f"   {r['body'][:200]}")
                output.append("")
            
            return "\n".join(output)
        except ImportError:
            return "Error: duckduckgo-search not installed"
        except Exception as e:
            return f"Search error: {str(e)}"


class RSSFeedInput(BaseModel):
    """Input for RSS feed parsing."""
    url: str = Field(..., description="RSS feed URL to parse")
    max_items: int = Field(default=20, description="Maximum items to return")


class RSSFeedTool(BaseTool):
    """Parse RSS feeds for job listings."""
    name: str = "rss_feed_parser"
    description: str = "Parse RSS feeds to extract job listings"
    args_schema: Type[BaseModel] = RSSFeedInput

    def _run(self, url: str, max_items: int = 20) -> str:
        """Parse RSS feed and extract job items."""
        try:
            import urllib.request
            import xml.etree.ElementTree as ET
            
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (CareerOps/2.0)"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read().decode("utf-8", "replace")
            
            # Parse XML
            root = ET.fromstring(xml_data)
            items = []
            
            # Handle RSS and Atom formats
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            # Try RSS format
            for item in root.findall(".//item")[:max_items]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                if title and link:
                    items.append(f"- {title}\n  URL: {link}\n  {desc[:150]}")
            
            # Try Atom format if no RSS items
            if not items:
                for entry in root.findall(".//atom:entry", ns)[:max_items]:
                    title = entry.findtext("atom:title", "", ns)
                    link_el = entry.find("atom:link", ns)
                    link = link_el.get("href", "") if link_el is not None else ""
                    summary = entry.findtext("atom:summary", "", ns)
                    if title and link:
                        items.append(f"- {title}\n  URL: {link}\n  {summary[:150]}")
            
            if not items:
                return "No items found in feed"
            
            return f"Found {len(items)} items:\n" + "\n\n".join(items)
        except Exception as e:
            return f"RSS parse error: {str(e)}"


class CompanyCareerInput(BaseModel):
    """Input for company career page scraping."""
    company_name: str = Field(..., description="Company name")
    career_url: str = Field(..., description="Career page URL")


class CompanyCareerScraper(BaseTool):
    """Scrape company career pages for job listings."""
    name: str = "company_career_scraper"
    description: str = "Scrape a company's career page for job listings"
    args_schema: Type[BaseModel] = CompanyCareerInput

    def _run(self, company_name: str, career_url: str) -> str:
        """Scrape company career page."""
        try:
            import urllib.request
            from bs4 import BeautifulSoup
            
            req = urllib.request.Request(career_url, headers={
                "User-Agent": "Mozilla/5.0 (CareerOps/2.0)"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", "replace")
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Look for job listings
            jobs = []
            
            # Common job listing patterns
            job_patterns = [
                r'href="([^"]*(?:job|position|role|career)[^"]*)"',
                r'<a[^>]*href="([^"]*)"[^>]*>([^<]*(?:translator|translation|linguist|esl|language)[^<]*)</a>',
            ]
            
            # Find links containing job-related keywords
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text(strip=True).lower()
                
                if any(kw in text for kw in ["translator", "translation", "linguist", "esl", "language", "arabic"]):
                    if not href.startswith("http"):
                        href = career_url.rstrip("/") + "/" + href.lstrip("/")
                    jobs.append(f"- {link.get_text(strip=True)}\n  URL: {href}")
            
            if not jobs:
                # Try to find any job-related links
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "")
                    text = link.get_text(strip=True).lower()
                    if "job" in text or "career" in text or "position" in text:
                        if not href.startswith("http"):
                            href = career_url.rstrip("/") + "/" + href.lstrip("/")
                        jobs.append(f"- {link.get_text(strip=True)}\n  URL: {href}")
            
            if not jobs:
                return f"No specific jobs found on {company_name} career page"
            
            return f"Found {len(jobs)} potential jobs at {company_name}:\n" + "\n".join(jobs[:10])
        except Exception as e:
            return f"Scraping error for {company_name}: {str(e)}"
