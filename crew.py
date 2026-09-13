"""CareerOps Crew — Multi-agent job search and application system."""
import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Load environment
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_researcher_agent():
    """Create the Job Researcher agent."""
    try:
        from crewai import Agent
        from tools import DuckDuckGoSearchTool, RSSFeedTool, CompanyCareerScraper
        
        return Agent(
            role="Job Researcher",
            goal="Find Arabic translator and ESL teaching remote jobs across the web",
            backstory="""You are an expert job researcher specializing in finding remote Arabic
            translation and ESL teaching positions. You search DuckDuckGo, RSS feeds,
            and company career pages to discover new opportunities daily. You know that
            companies like TransPerfect, Lionbridge, RWS, Appen, and Telus International
            often hire Arabic translators.""",
            tools=[DuckDuckGoSearchTool(), RSSFeedTool(), CompanyCareerScraper()],
            verbose=True,
            allow_delegation=False,
        )
    except ImportError:
        print("Warning: CrewAI not installed. Using fallback researcher.")
        return None


def create_scraper_agent():
    """Create the Job Scraper agent."""
    try:
        from crewai import Agent
        from tools import PlaywrightScraperTool
        
        return Agent(
            role="Job Scraper",
            goal="Extract detailed job information from career pages and ATS systems",
            backstory="""You are a web scraping expert who can extract job details from any website.
            You use Playwright for JavaScript-heavy sites and simple HTTP for static pages.
            You extract title, company, location, salary, requirements, and apply URLs.""",
            tools=[PlaywrightScraperTool()],
            verbose=True,
            allow_delegation=False,
        )
    except ImportError:
        print("Warning: CrewAI not installed. Using fallback scraper.")
        return None


def create_scorer_agent():
    """Create the Job Scorer agent."""
    try:
        from crewai import Agent
        from tools import OllamaScoringTool, KeywordMatchTool, CompanyReputationTool
        
        return Agent(
            role="Job Scorer",
            goal="Score and rank jobs based on match with Arabic translator profile",
            backstory="""You are an expert job matcher who evaluates how well a job matches
            Waleed's profile: Arabic-English translator, ESL teacher, 5+ years
            experience, remote work, worldwide. You score jobs 0-100.""",
            tools=[OllamaScoringTool(), KeywordMatchTool(), CompanyReputationTool()],
            verbose=True,
            allow_delegation=False,
        )
    except ImportError:
        print("Warning: CrewAI not installed. Using fallback scorer.")
        return None


def create_applicant_agent():
    """Create the Application Filler agent."""
    try:
        from crewai import Agent
        from tools import PlaywrightFormFiller, GreenhouseFormTool
        
        return Agent(
            role="Application Filler",
            goal="Fill job application forms automatically using Playwright",
            backstory="""You are an automation expert who fills job application forms across
            Greenhouse, Lever, Ashby, and other ATS platforms. You upload CVs
            and cover letters, fill personal details, and prepare for human review.""",
            tools=[PlaywrightFormFiller(), GreenhouseFormTool()],
            verbose=True,
            allow_delegation=False,
        )
    except ImportError:
        print("Warning: CrewAI not installed. Using fallback applicant.")
        return None


def create_document_agent():
    """Create the Document Generator agent."""
    try:
        from crewai import Agent
        from tools import OllamaWritingTool
        
        return Agent(
            role="Document Generator",
            goal="Generate tailored CV and cover letter for each job application",
            backstory="""You are a professional document writer who creates tailored CVs and
            cover letters for each job application. You highlight Arabic translation
            experience, legal translation, ESL teaching, and academic supervision.""",
            tools=[OllamaWritingTool()],
            verbose=True,
            allow_delegation=False,
        )
    except ImportError:
        print("Warning: CrewAI not installed. Using fallback document writer.")
        return None


def run_crew_search(top_n: int = 10):
    """Run the full crew search pipeline."""
    print(f"\n{'='*60}")
    print(f"CAREEROPS 2.0 — AI-Powered Job Search")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")
    
    # Search queries for Arabic translator jobs
    search_queries = [
        "Arabic translator remote jobs 2026",
        "Arabic English translation work from home",
        "Arabic linguist remote position",
        "ESL teacher Arabic speaker remote",
        "Localization specialist Arabic remote",
        "Bilingual Arabic translator jobs",
        "Legal translator Arabic remote",
        "Academic translator Arabic remote",
    ]
    
    # RSS feeds for translation jobs
    rss_feeds = [
        "https://www.proz.com/jobs/feed",
        "https://www.eslcafe.com/jobs/feed",
    ]
    
    # Company career pages
    career_pages = [
        ("TransPerfect", "https://www.transperfect.com/careers"),
        ("Lionbridge", "https://www.lionbridge.com/careers"),
        ("RWS", "https://www.rws.com/careers"),
        ("Appen", "https://www.appen.com/careers"),
        ("Telus International", "https://www.telusinternational.com/careers"),
        ("Welocalize", "https://www.welocalize.com/careers"),
        ("OneForma", "https://www.oneforma.com/careers"),
    ]
    
    # Collect all jobs
    all_jobs = []
    
    # 1. DuckDuckGo Search
    print("[1/5] Searching DuckDuckGo...")
    try:
        from tools import DuckDuckGoSearchTool
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
        from tools import RSSFeedTool
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
        from tools import CompanyCareerScraper
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
        from tools import KeywordMatchTool
        keyword_tool = KeywordMatchTool()
        
        for job in all_jobs[:50]:  # Limit to 50 jobs
            result = keyword_tool._run(f"{job.get('title', '')} {job.get('url', '')}")
            try:
                score_data = json.loads(result)
                job["score"] = score_data.get("score", 0)
                job["category"] = score_data.get("category", "Other")
                job["reasons"] = score_data.get("reasons", [])
                scored_jobs.append(job)
            except:
                job["score"] = 0
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
            f.write(f"   URL: {job.get('url', '')}\n")
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
    # Run search
    results = run_crew_search(top_n=10)
    
    # Print summary
    print("\nTop 10 Jobs Found:")
    for i, job in enumerate(results, 1):
        print(f"{i}. [{job.get('score', 0)}] {job.get('title', 'Unknown')}")
        print(f"   {job.get('url', '')}")
