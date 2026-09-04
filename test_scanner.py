"""
Quick test of the enhanced scanner with longer time window
"""

import asyncio
import json
import os
import sys

# Set test environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""
os.environ["BREVO_API_KEY"] = ""
os.environ["TO_EMAIL"] = ""

# Import scanner functions
from scanner import (
    run_scan,
    fetch_remotive,
    fetch_remoteok,
    fetch_wwr,
    fetch_jobicy,
    fetch_himalayas_api,
    fetch_jobicy_api,
    fetch_workbeam,
    normalize_date,
    age_hours,
    get_match_score,
    matches_positive,
    matches_negative,
    is_open_worldwide,
    strip_html,
)

async def test_quick():
    """Quick test to see scoring in action."""
    import aiohttp
    
    print("Testing enhanced scanner with 5-dimension scoring...")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test a few sources
        print("\nFetching from Remotive...")
        remotive_jobs = await fetch_remotive(session)
        print(f"  Remotive: {len(remotive_jobs)} jobs")
        
        print("\nFetching from Himalayas API...")
        himalayas_jobs = await fetch_himalayas_api(session)
        print(f"  Himalayas: {len(himalayas_jobs)} jobs")
        
        print("\nFetching from Jobicy API...")
        jobicy_jobs = await fetch_jobicy_api(session)
        print(f"  Jobicy: {len(jobicy_jobs)} jobs")
        
        print("\nFetching from Workbeam...")
        workbeam_jobs = await fetch_workbeam(session)
        print(f"  Workbeam: {len(workbeam_jobs)} jobs")
        
        # Combine all jobs
        all_jobs = remotive_jobs + himalayas_jobs + jobicy_jobs + workbeam_jobs
        print(f"\nTotal jobs fetched: {len(all_jobs)}")
        
        # Test scoring on first 10 jobs
        print("\n" + "=" * 60)
        print("Testing 5-dimension scoring on 10 jobs...")
        print("=" * 60)
        
        scored_count = 0
        for i, job in enumerate(all_jobs[:10]):
            title = job.get("title", "")
            desc = job.get("description", "")
            
            # Check if it matches positive keywords
            if matches_positive(title, desc):
                # Get match score
                score_result = get_match_score(title, desc)
                score = score_result["score"]
                category = score_result["category"]
                why = score_result["why"]
                
                # Check if it passes other filters
                if not matches_negative(title, desc) and is_open_worldwide(job.get("location", ""), desc):
                    if score >= 50:  # Lower threshold for testing
                        scored_count += 1
                        print(f"\n{scored_count}. {title}")
                        print(f"   Company: {job.get('company', 'Unknown')}")
                        print(f"   Score: {score}% | Category: {category}")
                        print(f"   Why: {', '.join(why[:3])}")
                        print(f"   Location: {job.get('location', 'Remote')}")
        
        print(f"\n{'=' * 60}")
        print(f"Found {scored_count} jobs with 50%+ match")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_quick())
