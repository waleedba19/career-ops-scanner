"""
CareerOps Auto-Discovery System
Automatically discovers new job sites, APIs, and ATS systems.
Runs weekly or on-demand to keep the scanner's source list fresh.
"""
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.5",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.6",
}
TIMEOUT = aiohttp.ClientTimeout(total=20)

# Profile search terms for discovery
PROFILE_QUERIES = [
    "arabic translator",
    "arabic linguist",
    "esl teacher",
    "english teacher online",
    "proofreader editor",
    "localization",
    "translation",
    "data annotation arabic",
]

# Known ATS patterns
ATS_PATTERNS = {
    "greenhouse": "boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
    "lever": "api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "api.ashbyhq.com/posting-api/job-board/{slug}",
    "workable": "apply.workable.com/api/v1/widget/accounts/{slug}?details=true",
    "smartrecruiters": "api.smartrecruiters.com/v1/companies/{slug}/postings",
    "recruitee": "{slug}.recruitee.com/api/offers/",
    "teamtailor": "{slug}.teamtailor.com/jobs.rss",
}

# Discovery sources
DISCOVERY_SOURCES = {
    "github_trending": "https://api.github.com/search/repositories?q=job+board+remote&sort=stars&order=desc&per_page=20",
    "wellknown_boards": [
        "https://remoteok.com/api",
        "https://remotive.com/api/remote-jobs?limit=20",
        "https://jobicy.com/api/v2/remote-jobs?count=20",
        "https://www.arbeitnow.com/api/job-board-api",
        "https://himalayas.app/jobs/api?limit=20",
    ],
    "ats_discovery": [
        "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
    ],
}

# Company slugs to try for ATS discovery
COMPANY_SLUGS_TO_TRY = [
    # AI / Data
    "scaleai", "outlier", "appen", "telusinternational", "toloka",
    "prolific", "deel", "mercor", "micro1", "surgeai", "centific",
    # Language
    "smartling", "lokalise", "unbabel", "lilt", "acclaro", "andovar",
    "straker", "rws", "lionbridge", "transperfect", "keywordsstudios",
    # EdTech
    "duolingo", "outschool", "khanacademy", "coursera", "preply",
    "babbel", "busuu", "lingoda", "engoo", "novakid", "openenglish",
    # MENA
    "anghami", "tamatem", "mawdoo3", "sarwa", "nagwa", "abwaab",
    # Academic
    "scribbr", "scribendi", "enago", "wordvice", "papertrue",
    # Remote-first
    "gitlab", "cloudflare", "mozilla", "kayak",
]


async def _get(session: aiohttp.ClientSession, url: str, **kw) -> tuple[int, str]:
    """GET → (status, body). Never raises."""
    try:
        async with session.get(url, headers=kw.pop("headers", HEADERS),
                               timeout=kw.pop("timeout", TIMEOUT), **kw) as r:
            return r.status, await r.text(errors="ignore")
    except Exception:
        return 0, ""


async def _get_json(session: aiohttp.ClientSession, url: str, **kw):
    """GET → (status, json). Never raises."""
    try:
        async with session.get(url, headers=kw.pop("headers", HEADERS),
                               timeout=kw.pop("timeout", TIMEOUT), **kw) as r:
            if r.status != 200:
                return r.status, None
            return 200, await r.json(content_type=None)
    except Exception:
        return 0, None


async def discover_github_repos(session: aiohttp.ClientSession) -> list[dict]:
    """Discover job boards from GitHub trending repos."""
    print("[Discovery] Checking GitHub for new job boards...")
    status, data = await _get_json(session, DISCOVERY_SOURCES["github_trending"])
    if status != 200:
        return []

    candidates = []
    for repo in (data or {}).get("items") or []:
        name = repo.get("name") or ""
        desc = repo.get("description") or ""
        url = repo.get("html_url") or ""
        if not name or not url:
            continue
        # Look for job board related repos
        keywords = ["job", "board", "career", "hiring", "recruitment", "ats", "remote"]
        if any(kw in name.lower() or kw in desc.lower() for kw in keywords):
            candidates.append({
                "type": "github_repo",
                "name": name,
                "url": url,
                "description": desc[:200],
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            })
    print(f"  Found {len(candidates)} potential job board repos")
    return candidates


async def discover_ats_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Discover new ATS boards by testing company slugs."""
    print("[Discovery] Probing ATS boards for new companies...")
    candidates = []
    seen = set()

    for slug in COMPANY_SLUGS_TO_TRY:
        if slug in seen:
            continue
        seen.add(slug)

        # Test each ATS pattern
        for ats_name, pattern in ATS_PATTERNS.items():
            try:
                url = pattern.format(slug=slug)
                if not url.startswith("http"):
                    url = f"https://{url}"
                status, data = await _get_json(session, url) if "json" in pattern else _get(session, url)
                if status == 200 and data:
                    # Check if it has jobs
                    has_jobs = False
                    if isinstance(data, dict):
                        has_jobs = bool(data.get("jobs") or data.get("content") or data.get("offers"))
                    elif isinstance(data, list):
                        has_jobs = bool(data)

                    if has_jobs:
                        candidates.append({
                            "type": "ats_board",
                            "ats": ats_name,
                            "slug": slug,
                            "url": url,
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        })
                        print(f"  ✓ {ats_name}:{slug} - found jobs")
                        break  # Found on this ATS, no need to try others
            except Exception:
                continue

        # Rate limiting
        await asyncio.sleep(0.5)

    print(f"  Found {len(candidates)} new ATS boards")
    return candidates


async def discover_rss_feeds(session: aiohttp.ClientSession) -> list[dict]:
    """Discover RSS feeds from known job boards."""
    print("[Discovery] Looking for RSS feeds...")
    candidates = []

    # Common RSS feed patterns
    rss_patterns = [
        "{base}/feed",
        "{base}/rss",
        "{base}/jobs/feed",
        "{base}/careers/feed",
        "{base}/feed/jobs",
    ]

    # Known bases to check
    bases = [
        "https://remoteok.com",
        "https://remotive.com",
        "https://weworkremotely.com",
        "https://www.workingnomads.com",
        "https://jobicy.com",
    ]

    for base in bases:
        for pattern in rss_patterns:
            url = pattern.format(base=base)
            status, body = await _get(session, url)
            if status == 200 and "<rss" in body.lower() or "<feed" in body.lower():
                candidates.append({
                    "type": "rss_feed",
                    "url": url,
                    "base": base,
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                })
                print(f"  ✓ RSS: {url}")
                break  # Found one for this base

    print(f"  Found {len(candidates)} RSS feeds")
    return candidates


async def discover_remote_boards(session: aiohttp.ClientSession) -> list[dict]:
    """Discover remote job boards by searching."""
    print("[Discovery] Searching for remote job boards...")
    candidates = []

    # Search for remote job boards
    search_queries = [
        "remote job board api",
        "remote work job listings",
        "freelance translation jobs",
        "esl teaching jobs online",
        "arabic translator jobs",
    ]

    for query in search_queries:
        # Use DuckDuckGo lite (no API needed)
        url = f"https://lite.duckduckgo.com/lite/?q={query.replace(' ', '+')}"
        status, body = await _get(session, url)
        if status != 200:
            continue

        # Extract URLs from results
        urls = re.findall(r'href="(https?://[^"]+)"', body)
        for url in urls:
            # Skip known sites
            if any(known in url for known in ["linkedin.com", "indeed.com", "glassdoor.com"]):
                continue
            # Check if it's a job board
            if any(kw in url.lower() for kw in ["job", "career", "remote", "work"]):
                candidates.append({
                    "type": "remote_board",
                    "url": url,
                    "query": query,
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                })

    # Deduplicate
    seen = set()
    unique = []
    for c in candidates:
        if c["url"] not in seen:
            seen.add(c["url"])
            unique.append(c)

    print(f"  Found {len(unique)} potential remote boards")
    return unique[:50]  # Limit to 50


async def test_candidate(session: aiohttp.ClientSession, candidate: dict) -> dict:
    """Test if a candidate source actually has jobs."""
    url = candidate.get("url", "")
    if not url:
        return {**candidate, "status": "no_url"}

    try:
        status, body = await _get(session, url)
        if status != 200:
            return {**candidate, "status": "error", "http_status": status}

        # Check for job content
        body_lower = body.lower()
        has_jobs = any(kw in body_lower for kw in [
            "job", "position", "opening", "vacancy", "hiring",
            "apply", "application", "career",
        ])

        if has_jobs:
            return {**candidate, "status": "ok", "tested_at": datetime.now(timezone.utc).isoformat()}
        else:
            return {**candidate, "status": "no_jobs", "tested_at": datetime.now(timezone.utc).isoformat()}

    except Exception as e:
        return {**candidate, "status": "error", "error": str(e)}


async def run_discovery(max_candidates: int = 100) -> dict:
    """Run the full discovery pipeline."""
    print("=" * 60)
    print("CareerOps Auto-Discovery System")
    print("=" * 60)

    results = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "discovered": [],
        "tested": [],
        "stats": {},
    }

    async with aiohttp.ClientSession() as session:
        # Run all discovery methods in parallel
        github_repos, ats_boards, rss_feeds, remote_boards = await asyncio.gather(
            discover_github_repos(session),
            discover_ats_boards(session),
            discover_rss_feeds(session),
            discover_remote_boards(session),
        )

        # Combine all candidates
        all_candidates = github_repos + ats_boards + rss_feeds + remote_boards
        results["discovered"] = all_candidates[:max_candidates]

        print(f"\n[Discovery] Total candidates: {len(all_candidates)}")

        # Test a sample of candidates
        test_sample = all_candidates[:20]  # Test first 20
        print(f"\n[Testing] Testing {len(test_sample)} candidates...")

        tested = []
        for candidate in test_sample:
            result = await test_candidate(session, candidate)
            tested.append(result)
            status_icon = "✓" if result["status"] == "ok" else "✗"
            print(f"  {status_icon} {candidate.get('url', 'unknown')}: {result['status']}")

        results["tested"] = tested

        # Calculate stats
        ok_count = sum(1 for t in tested if t["status"] == "ok")
        results["stats"] = {
            "total_discovered": len(all_candidates),
            "tested": len(tested),
            "successful": ok_count,
            "success_rate": f"{(ok_count / len(tested) * 100):.1f}%" if tested else "0%",
        }

    print("\n" + "=" * 60)
    print("Discovery Complete")
    print(f"  Discovered: {results['stats']['total_discovered']}")
    print(f"  Tested: {results['stats']['tested']}")
    print(f"  Successful: {results['stats']['successful']}")
    print(f"  Success Rate: {results['stats']['success_rate']}")
    print("=" * 60)

    return results


def save_results(results: dict, output_dir: Path = None):
    """Save discovery results to file."""
    if output_dir is None:
        output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save full results
    output_file = output_dir / "discovery_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {output_file}")

    # Save successful candidates to source_candidates.json
    successful = [t for t in results.get("tested", []) if t["status"] == "ok"]
    if successful:
        candidates_file = Path(__file__).parent / "discovered_sources.json"
        existing = []
        if candidates_file.exists():
            with open(candidates_file, "r", encoding="utf-8") as f:
                existing = json.load(f)

        # Merge new discoveries
        existing_urls = {c.get("url") for c in existing}
        new_discoveries = [s for s in successful if s.get("url") not in existing_urls]

        if new_discoveries:
            existing.extend(new_discoveries)
            with open(candidates_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            print(f"New discoveries saved to: {candidates_file}")
            print(f"  Added {len(new_discoveries)} new sources")


async def main():
    """Main entry point."""
    results = await run_discovery()
    save_results(results)
    return results


if __name__ == "__main__":
    asyncio.run(main())