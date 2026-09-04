"""
Full test of enhanced scanner with Ollama AI analysis
"""

import asyncio
import json
import os

# Import scanner functions
from scanner import (
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
    GREENHOUSE_COMPANIES,
    fetch_greenhouse,
)

from ollama_analyzer import analyze_jobs_with_ollama

async def test_full():
    """Full test with multiple sources and AI analysis."""
    import aiohttp
    
    print("CAREEROPS ENHANCED SCANNER TEST")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Fetch from multiple sources
        print("\nFetching jobs from multiple sources...")
        
        all_jobs = []
        
        # Greenhouse companies (first 5 for testing)
        print("  Fetching Greenhouse companies...")
        for name, slug in GREENHOUSE_COMPANIES[:5]:
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
        
        print(f"\nTotal jobs fetched: {len(all_jobs)}")
        
        # Score and filter
        print("\nScoring jobs with 5-dimension evaluation...")
        scored_jobs = []
        
        for job in all_jobs:
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
                    if score >= 60:  # Lower threshold for testing
                        scored_jobs.append({
                            **job,
                            "score": score,
                            "category": category,
                            "why": why,
                        })
        
        # Sort by score
        scored_jobs.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"Found {len(scored_jobs)} jobs with 60%+ match")
        
        # Show top 10
        print("\n" + "=" * 60)
        print("TOP 10 MATCHING JOBS")
        print("=" * 60)
        
        for i, job in enumerate(scored_jobs[:10]):
            print(f"\n{i+1}. {job.get('title', 'Unknown')}")
            print(f"   Company: {job.get('company', 'Unknown')}")
            print(f"   Score: {job.get('score', 0)}% | Category: {job.get('category', '')}")
            print(f"   Why: {', '.join(job.get('why', [])[:3])}")
            print(f"   Location: {job.get('location', 'Remote')}")
            print(f"   Source: {job.get('source', 'unknown')}")
        
        # Test Ollama AI analysis on top 3 jobs
        print("\n" + "=" * 60)
        print("TESTING OLLAMA AI ANALYSIS")
        print("=" * 60)
        
        top_jobs = scored_jobs[:3]
        if top_jobs:
            print(f"\nAnalyzing top {len(top_jobs)} jobs with AI...")
            analyzed_jobs = await analyze_jobs_with_ollama(top_jobs)
            
            for job in analyzed_jobs:
                print(f"\n{job.get('title', 'Unknown')}")
                print(f"  AI Verdict: {job.get('ai_verdict', 'N/A')}")
                print(f"  AI Score: {job.get('ai_overall_score', 'N/A')}/100")
                ai_summary = job.get('ai_insight', 'N/A')
                if ai_summary:
                    print(f"  AI Summary: {ai_summary[:150]}...")
                if job.get('ai_strengths'):
                    print(f"  Strengths: {', '.join(job['ai_strengths'][:3])}")
                if job.get('ai_gaps'):
                    print(f"  Gaps: {', '.join(job['ai_gaps'][:3])}")
        
        # Test Telegram message format
        print("\n" + "=" * 60)
        print("TESTING TELEGRAM MESSAGE FORMAT")
        print("=" * 60)
        
        from notifier import build_telegram, format_job_card
        
        scan_info = {
            "elapsed": "0.0",
            "all_count": len(all_jobs),
            "source_count": 8,
            "fresh_count": len(all_jobs),
            "near_misses": scored_jobs[5:10] if len(scored_jobs) > 5 else [],
        }
        
        stats = {
            "total_scans": 1,
            "total_matches": len(scored_jobs),
            "last_scan_date": "2026-09-04",
        }
        
        telegram_msg = build_telegram(scored_jobs[:5], scan_info, stats)
        
        print("\nSample Telegram message saved to telegram_preview.txt")
        print("-" * 40)
        # Save to file to avoid encoding issues
        with open("telegram_preview.txt", "w", encoding="utf-8") as f:
            f.write(telegram_msg)
        print("Message preview (first 1500 chars):")
        preview = telegram_msg[:1500]
        # Replace problematic characters
        preview = preview.replace("\u2600\ufe0f", "[SUN]")
        preview = preview.replace("\U0001f4cb", "[MEMO]")
        preview = preview.replace("\U0001f319", "[MOON]")
        preview = preview.replace("\U0001f4bc", "[BRIEFCASE]")
        preview = preview.replace("\U0001f3e2", "[OFFICE]")
        preview = preview.replace("\U0001f4cd", "[PIN]")
        preview = preview.replace("\U0001f4b0", "[MONEY]")
        preview = preview.replace("\u23f1", "[CLOCK]")
        preview = preview.replace("\U0001f3af", "[TARGET]")
        preview = preview.replace("\U0001f4c2", "[FILE]")
        preview = preview.replace("\U0001f4ac", "[SPEECH]")
        preview = preview.replace("\U0001f517", "[LINK]")
        preview = preview.replace("\U0001f525", "[FIRE]")
        preview = preview.replace("\u2705", "[CHECK]")
        preview = preview.replace("\U0001f4a1", "[BULB]")
        preview = preview.replace("\u26a0\ufe0f", "[WARNING]")
        preview = preview.replace("\u2b50", "[STAR]")
        preview = preview.replace("\u2500", "-")
        preview = preview.replace("\u2014", "--")
        preview = preview.replace("\u2022", "*")
        preview = preview.replace("\xB7", ".")
        print(preview)
        print("-" * 40)
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_full())
