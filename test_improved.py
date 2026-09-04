"""
Test improved scanner with 6-day window, paid platform filter, and Arabic focus
"""

import asyncio
import json
import os

# Import scanner functions
from scanner import (
    fetch_remotive,
    fetch_himalayas_api,
    fetch_jobicy_api,
    fetch_mostaql,
    fetch_for9a,
    normalize_date,
    age_hours,
    get_match_score,
    matches_positive,
    matches_negative,
    is_open_worldwide,
    is_paid_platform,
    get_freshness,
    strip_html,
    GREENHOUSE_COMPANIES,
    fetch_greenhouse,
)

async def test_improved():
    """Test improved scanner features."""
    import aiohttp
    
    print("CAREEROPS IMPROVED SCANNER TEST")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test paid platform filter
        print("\n1. Testing paid platform filter...")
        test_platforms = ["flexjobs", "tophire", "wellfound", "ziprecruiter", "remotive", "himalayas"]
        for platform in test_platforms:
            is_paid = is_paid_platform(platform)
            print(f"  {platform}: {'PAID (filtered)' if is_paid else 'FREE (included)'}")
        
        # Fetch from multiple sources including Arabic platforms
        print("\n2. Fetching jobs from multiple sources...")
        
        all_jobs = []
        
        # Greenhouse companies (first 3 for testing)
        print("  Fetching Greenhouse companies...")
        for name, slug in GREENHOUSE_COMPANIES[:3]:
            jobs = await fetch_greenhouse(session, name, slug)
            all_jobs.extend(jobs)
            print(f"    {name}: {len(jobs)} jobs")
        
        # Other sources
        print("  Fetching other sources...")
        remotive = await fetch_remotive(session)
        all_jobs.extend(remotive)
        print(f"    Remotive: {len(remotive)} jobs")
        
        himalayas = await fetch_himalayas_api(session)
        all_jobs.extend(himalayas)
        print(f"    Himalayas: {len(himalayas)} jobs")
        
        jobicy = await fetch_jobicy_api(session)
        all_jobs.extend(jobicy)
        print(f"    Jobicy: {len(jobicy)} jobs")
        
        # Arabic platforms
        print("  Fetching Arabic platforms...")
        mostaql = await fetch_mostaql(session)
        all_jobs.extend(mostaql)
        print(f"    Mostaql: {len(mostaql)} jobs")
        
        for9a = await fetch_for9a(session)
        all_jobs.extend(for9a)
        print(f"    For9a: {len(for9a)} jobs")
        
        print(f"\nTotal jobs fetched: {len(all_jobs)}")
        
        # Test time window filtering
        print("\n3. Testing 6-day time window...")
        within_window = 0
        outside_window = 0
        for job in all_jobs:
            posted = normalize_date(job.get("posted"))
            if posted:
                age = age_hours(posted)
                if age <= 144:  # 6 days
                    within_window += 1
                else:
                    outside_window += 1
        print(f"  Within 6-day window: {within_window}")
        print(f"  Outside window (too old): {outside_window}")
        
        # Score and filter
        print("\n4. Scoring jobs with Arabic focus...")
        scored_jobs = []
        
        for job in all_jobs:
            title = job.get("title", "")
            desc = job.get("description", "")
            
            # Skip paid platforms
            if is_paid_platform(job.get("source", "")):
                continue
            
            # Check if it matches positive keywords
            if matches_positive(title, desc):
                # Get match score
                score_result = get_match_score(title, desc)
                score = score_result["score"]
                category = score_result["category"]
                why = score_result["why"]
                
                # Check if it passes other filters
                if not matches_negative(title, desc) and is_open_worldwide(job.get("location", ""), desc):
                    if score >= 60:  # Lower threshold for testing
                        posted = normalize_date(job.get("posted"))
                        age = age_hours(posted) if posted else float("inf")
                        
                        # Check freshness
                        freshness = get_freshness(job.get("posted"))
                        
                        scored_jobs.append({
                            **job,
                            "score": score,
                            "category": category,
                            "why": why,
                            "age_hours": age,
                            "freshness": freshness,
                        })
        
        # Sort by score (highest first), then by age (newest first)
        scored_jobs.sort(key=lambda x: (-x["score"], x.get("age_hours", 0)))
        
        print(f"Found {len(scored_jobs)} jobs with 60%+ match")
        
        # Show top 15 with Arabic focus
        print("\n" + "=" * 60)
        print("TOP 15 MATCHING JOBS (Arabic focus prioritized)")
        print("=" * 60)
        
        arabic_jobs = [j for j in scored_jobs if "arabic" in j.get("title", "").lower() or "arabic" in j.get("description", "").lower()]
        other_jobs = [j for j in scored_jobs if j not in arabic_jobs]
        
        print(f"\nArabic-specific jobs found: {len(arabic_jobs)}")
        
        for i, job in enumerate(scored_jobs[:15]):
            freshness = job.get("freshness", {})
            is_arabic = "arabic" in job.get("title", "").lower() or "arabic" in job.get("description", "").lower()
            arabic_marker = " [ARABIC]" if is_arabic else ""
            
            print(f"\n{i+1}. {job.get('title', 'Unknown')}{arabic_marker}")
            print(f"   Company: {job.get('company', 'Unknown')}")
            print(f"   Score: {job.get('score', 0)}% | Category: {job.get('category', '')}")
            print(f"   Why: {', '.join(job.get('why', [])[:3])}")
            print(f"   Location: {job.get('location', 'Remote')}")
            print(f"   Source: {job.get('source', 'unknown')}")
            print(f"   Posted: {freshness.get('label', 'unknown')}")
            print(f"   Age: {job.get('age_hours', 0):.1f} hours")
        
        # Test freshness labels
        print("\n" + "=" * 60)
        print("TESTING FRESHNESS LABELS")
        print("=" * 60)
        
        test_times = [0.5, 1, 5, 24, 48, 72, 120, 168]
        for hours in test_times:
            from datetime import datetime, timezone, timedelta
            test_date = datetime.now(timezone.utc) - timedelta(hours=hours)
            freshness = get_freshness(test_date.isoformat())
            print(f"  {hours} hours ago: {freshness['label']} (is_fresh: {freshness['is_fresh']}, is_old: {freshness['is_old']})")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_improved())
