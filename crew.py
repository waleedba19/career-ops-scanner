"""CareerOps Crew — Multi-agent job search and application system."""
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone

# Load environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_email_from_text(text: str) -> str:
    """Extract email address from text."""
    if not text:
        return ""
    # Common email patterns
    email_patterns = [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'apply[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ]
    for pattern in email_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            email = match.group(1) if match.lastindex else match.group(0)
            # Filter out common non-personal emails
            skip_domains = ['example.com', 'sentry.io', 'wixpress.com', 'github.com', 'sentry-next.wixpress.com']
            if not any(domain in email.lower() for domain in skip_domains):
                return email
    return ""


def get_company_website(company_name: str) -> str:
    """Get company website from name."""
    # Known company websites
    company_websites = {
        "transperfect": "https://www.transperfect.com",
        "lionbridge": "https://www.lionbridge.com",
        "rws": "https://www.rws.com",
        "keywords studios": "https://www.keywordsstudios.com",
        "welocalize": "https://www.welocalize.com",
        "appen": "https://www.appen.com",
        "telus international": "https://www.telusinternational.com",
        "centific": "https://www.centific.com",
        "scale ai": "https://scale.com",
        "surge ai": "https://surgeai.com",
        "oneforma": "https://www.oneforma.com",
        "proz": "https://www.proz.com",
        "tarjama": "https://www.tarjama.com",
        "careem": "https://www.careem.com",
        "languagebird": "https://www.languagebird.com",
        "vipkid": "https://www.vipkid.com",
        "cambly": "https://www.cambly.com",
        "preply": "https://preply.com",
        "italki": "https://www.italki.com",
        "remote.com": "https://remote.com",
        "deel": "https://www.deel.com",
        "oyster": "https://www.oysterhr.com",
        "google": "https://careers.google.com",
        "microsoft": "https://careers.microsoft.com",
        "amazon": "https://www.amazon.jobs",
        "apple": "https://www.apple.com/careers",
        "meta": "https://www.metacareers.com",
    }
    
    company_lower = company_name.lower().strip()
    for key, website in company_websites.items():
        if key in company_lower or company_lower in key:
            return website
    
    # Try to construct website from company name
    if company_name:
        name = company_name.lower().strip()
        for suffix in [' inc', ' llc', ' ltd', ' corp', ' corporation', ' company', ' co']:
            name = name.replace(suffix, '')
        return f"https://www.{name.replace(' ', '')}.com"
    
    return ""


def run_crew_search(top_n: int = 10):
    """Run the full crew search pipeline with email and company website extraction."""
    print(f"\n{'='*60}")
    print(f"CAREEROPS 2.0 — AI-Powered Job Search")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")
    
    # Search queries for Arabic translator jobs (25 queries)
    search_queries = [
        "Arabic translator remote jobs 2026",
        "Arabic English translation work from home",
        "Arabic linguist remote position",
        "Arabic translator freelance online",
        "Arabic document translation remote",
        "Legal translator Arabic remote jobs",
        "Academic translator Arabic remote",
        "Medical translator Arabic remote",
        "ESL teacher Arabic speaker remote",
        "English teacher Arabic online",
        "Online tutoring Arabic native speaker",
        "ESL instructor remote Middle East",
        "Localization specialist Arabic remote",
        "Arabic localization jobs work from home",
        "Software localization Arabic translator",
        "Arabic content writer remote",
        "Arabic copywriter work from home",
        "Bilingual content creator Arabic",
        "Arabic data annotation remote",
        "Arabic AI trainer jobs",
        "Arabic language expert remote",
        "Arabic legal translation services",
        "Arabic medical translation jobs",
        "Arabic financial translation remote",
        "Arabic speaker remote jobs worldwide",
    ]
    
    # RSS feeds for translation jobs
    rss_feeds = [
        "https://www.proz.com/jobs/feed",
        "https://www.eslcafe.com/jobs/feed",
    ]
    
    # Company career pages (35 companies)
    career_pages = [
        ("TransPerfect", "https://www.transperfect.com/careers"),
        ("Lionbridge", "https://www.lionbridge.com/careers"),
        ("RWS", "https://www.rws.com/careers"),
        ("Keywords Studios", "https://www.keywordsstudios.com/careers"),
        ("Welocalize", "https://www.welocalize.com/careers"),
        ("OneForma", "https://www.oneforma.com/careers"),
        ("CETRA", "https://www.cetra.com/careers"),
        ("Propio LS", "https://www.propio.com/careers"),
        ("Appen", "https://www.appen.com/careers"),
        ("Telus International", "https://www.telusinternational.com/careers"),
        ("Centific", "https://www.centific.com/careers"),
        ("Scale AI", "https://scale.com/careers"),
        ("Surge AI", "https://surgeai.com/careers"),
        ("AuraOne", "https://www.auraone.com/careers"),
        ("LanguageBird", "https://www.languagebird.com/teach"),
        ("VIPKid", "https://www.vipkid.com/careers"),
        ("Cambly", "https://www.cambly.com/careers"),
        ("Preply", "https://preply.com/careers"),
        ("italki", "https://www.italki.com/careers"),
        ("Lingoda", "https://www.lingoda.com/careers"),
        ("Tarjama", "https://www.tarjama.com/careers"),
        ("Tamatem Games", "https://www.tamatemgames.com/careers"),
        ("Careem", "https://www.careem.com/careers"),
        ("Noon Academy", "https://www.noonacademy.com/careers"),
        ("AsiaLocalize", "https://www.asialocalize.com/careers"),
        ("Google", "https://careers.google.com/"),
        ("Microsoft", "https://careers.microsoft.com/"),
        ("Amazon", "https://www.amazon.jobs/"),
        ("Apple", "https://www.apple.com/careers/"),
        ("Meta", "https://www.metacareers.com/"),
        ("Remote.com", "https://remote.com/careers"),
        ("Deel", "https://www.deel.com/careers"),
        ("Oyster", "https://www.oysterhr.com/careers"),
        ("ProZ", "https://www.proz.com/translation-jobs"),
        ("TranslatorsCafe", "https://www.translatorscafe.com/jobs/"),
    ]
    
    # Collect all jobs
    all_jobs = []
    
    # 1. DuckDuckGo Search
    print("[1/5] Searching DuckDuckGo...")
    try:
        from tools.search_tools import DuckDuckGoSearchTool
        search_tool = DuckDuckGoSearchTool()
        
        for query in search_queries:
            result = search_tool._run(query, max_results=5)
            # Parse results
            for line in result.split("\n"):
                if line.strip().startswith("URL:"):
                    url = line.replace("URL:", "").strip()
                    if url.startswith("http"):
                        all_jobs.append({
                            "title": f"Job from search: {query[:30]}",
                            "url": url,
                            "source": "duckduckgo",
                            "query": query,
                        })
    except Exception as e:
        print(f"  Search error: {e}")
    
    print(f"  Found {len(all_jobs)} jobs from search")
    
    # 2. RSS Feeds
    print("[2/5] Parsing RSS feeds...")
    try:
        from tools.search_tools import RSSFeedTool
        rss_tool = RSSFeedTool()
        
        for feed_url in rss_feeds:
            result = rss_tool._run(feed_url, max_items=10)
            # Parse results
            for line in result.split("\n"):
                if line.strip().startswith("URL:"):
                    url = line.replace("URL:", "").strip()
                    if url.startswith("http"):
                        all_jobs.append({
                            "title": f"Job from RSS",
                            "url": url,
                            "source": "rss",
                            "feed": feed_url,
                        })
    except Exception as e:
        print(f"  RSS error: {e}")
    
    print(f"  Total jobs now: {len(all_jobs)}")
    
    # 3. Company Career Pages
    print("[3/5] Checking company career pages...")
    try:
        from tools.search_tools import CompanyCareerScraper
        career_tool = CompanyCareerScraper()
        
        for company_name, career_url in career_pages:
            result = career_tool._run(company_name, career_url)
            # Parse results
            for line in result.split("\n"):
                if line.strip().startswith("URL:"):
                    url = line.replace("URL:", "").strip()
                    if url.startswith("http"):
                        all_jobs.append({
                            "title": f"Job at {company_name}",
                            "url": url,
                            "source": "career_page",
                            "company": company_name,
                        })
    except Exception as e:
        print(f"  Career page error: {e}")
    
    print(f"  Total jobs now: {len(all_jobs)}")
    
    # 4. Score jobs
    print("[4/5] Scoring jobs...")
    scored_jobs = []
    
    try:
        from tools.ollama_tools import KeywordMatchTool
        keyword_tool = KeywordMatchTool()
        
        for job in all_jobs[:50]:  # Limit to 50 jobs
            result = keyword_tool._run(f"{job.get('title', '')} {job.get('url', '')} {job.get('description', '')}")
            try:
                score_data = json.loads(result)
                job["score"] = score_data.get("score", 0)
                job["category"] = score_data.get("category", "Other")
                job["reasons"] = score_data.get("reasons", [])
            except:
                job["score"] = 0
            
            # Extract email from job description
            job["email"] = extract_email_from_text(job.get("description", ""))
            
            # Get company website
            job["company_website"] = get_company_website(job.get("company", ""))
            
            scored_jobs.append(job)
    except Exception as e:
        print(f"  Scoring error: {e}")
    
    # Sort by score
    scored_jobs.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    print(f"  Scored {len(scored_jobs)} jobs")
    if scored_jobs:
        print(f"  Top score: {scored_jobs[0].get('score', 0)}")
    
    # 5. Save results
    print("[5/5] Saving results...")

    # Write a normalized file the main scanner merges into all_jobs (source="crewai")
    crewai_out = []
    for job in scored_jobs[:50]:
        crewai_out.append({
            "title": (job.get("title") or "Opportunity").strip(),
            "url": job.get("url", ""),
            "company": job.get("company", ""),
            "description": job.get("description", ""),
            "source": "crewai",
            "posted": "",
            "company_website": job.get("company_website", ""),
            "email": job.get("email", ""),
            "score": job.get("score", 0),
            "category": job.get("category", "Other"),
        })
    crewai_file = OUTPUT_DIR / "crewai_jobs.json"
    with open(crewai_file, "w", encoding="utf-8") as f:
        json.dump(crewai_out, f, indent=2, ensure_ascii=False)
    print(f"  CrewAI jobs for scanner: {len(crewai_out)} -> output/crewai_jobs.json")

    # Save to JSON
    output_file = OUTPUT_DIR / f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(scored_jobs[:top_n], f, indent=2, ensure_ascii=False)
    
    # Save top jobs to text file
    top_file = OUTPUT_DIR / "top_jobs.txt"
    with open(top_file, "w", encoding="utf-8") as f:
        f.write(f"CareerOps Search Results — {datetime.now().isoformat()}\n")
        f.write(f"{'='*60}\n\n")
        for i, job in enumerate(scored_jobs[:top_n], 1):
            f.write(f"{i}. [{job.get('score', 0)}] {job.get('title', 'Unknown')}\n")
            f.write(f"   Company: {job.get('company', 'Unknown')}\n")
            f.write(f"   URL: {job.get('url', '')}\n")
            f.write(f"   Company Website: {job.get('company_website', '')}\n")
            f.write(f"   Email: {job.get('email', 'Not found')}\n")
            f.write(f"   Source: {job.get('source', 'unknown')}\n")
            if job.get('reasons'):
                f.write(f"   Reasons: {', '.join(job['reasons'][:3])}\n")
            f.write("\n")
    
    print(f"\n{'='*60}")
    print(f"Search complete!")
    print(f"Total jobs found: {len(all_jobs)}")
    print(f"Jobs scored: {len(scored_jobs)}")
    print(f"Top {top_n} saved to: {top_file}")
    print(f"Full results: {output_file}")
    print(f"{'='*60}\n")
    
    return scored_jobs[:top_n]


if __name__ == "__main__":
    # Run search (top 50 for scanner merge + display top 10)
    results = run_crew_search(top_n=50)
    
    # Print summary
    print("\nTop 10 Jobs Found:")
    for i, job in enumerate(results, 1):
        print(f"{i}. [{job.get('score', 0)}] {job.get('title', 'Unknown')}")
        print(f"   Company: {job.get('company', 'Unknown')}")
        print(f"   URL: {job.get('url', '')}")
        print(f"   Email: {job.get('email', 'Not found')}")
        print(f"   Website: {job.get('company_website', '')}")
