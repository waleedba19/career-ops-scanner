"""
Ollama AI Job Analyzer — Enhanced with 5-Dimension Fit Evaluation
Adapted from MadsLorentzen/ai-job-search framework.
Connects to local Ollama API (localhost:11434) to generate personalized
"why this fits" explanations AND detailed 5-dimension scoring for matched jobs.
Falls back gracefully if Ollama is unavailable.
"""

import json
import os
import re

import aiohttp

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

# ---------------------------------------------------------------------------
# User Profile — adapted from MadsLorentzen framework
# ---------------------------------------------------------------------------

USER_PROFILE = {
    "name": "Waleed",
    "background": (
        "Arabic/English translator, ESL teacher, editor, data entry specialist, "
        "virtual assistant, bilingual content creator"
    ),
    "primary_skills": [
        "Arabic translation",
        "English-Arabic localization",
        "ESL/EFL teaching",
        "Content editing/proofreading",
        "Data entry",
        "Virtual assistance",
        "Bilingual communication",
    ],
    "secondary_skills": [
        "Customer service",
        "Administrative support",
        "Social media management",
        "Basic HTML/WordPress",
        "Microsoft Office proficiency",
    ],
    "experience_domains": [
        "Translation & localization",
        "Education & tutoring",
        "Content creation",
        "Administrative support",
    ],
    "career_goals": [
        "Secure stable remote work with flexible hours",
        "Build long-term client relationships",
        "Grow into senior translator or content lead role",
    ],
    "languages": {
        "Arabic": "Native",
        "English": "Professional (B2/C1)",
    },
    "location": "Remote (worldwide)",
    "dealbreakers": [
        "Requires on-site presence",
        "US/EU citizenship required",
        "Visa sponsorship needed",
        "Engineering/developer roles",
    ],
}

# ---------------------------------------------------------------------------
# 5-Dimension Scoring Prompt (adapted from MadsLorentzen framework)
# ---------------------------------------------------------------------------

SCORING_PROMPT = """You are a professional job fit evaluator. Score this job against the candidate's profile on 5 dimensions.

CANDIDATE PROFILE:
- Background: {background}
- Primary skills: {primary_skills}
- Secondary skills: {secondary_skills}
- Experience domains: {experience_domains}
- Career goals: {career_goals}
- Languages: {languages}
- Location preference: {location}
- Dealbreakers: {dealbreakers}

JOB LISTING:
- Title: {title}
- Company: {company}
- Location: {location_job}
- Description: {description}

SCORE EACH DIMENSION (0-100):

1. TECHNICAL SKILLS MATCH (weight: 30%)
   - 80-100: Core requirements are primary skills
   - 60-79: Most requirements match, 1-2 learnable gaps
   - 40-59: Partial match, significant upskilling needed
   - 0-39: Fundamental mismatch

2. EXPERIENCE MATCH (weight: 25%)
   - 80-100: Direct experience in same domain/role type
   - 60-79: Related experience, transferable skills clear
   - 40-59: Adjacent experience, would need to make the case
   - 0-39: Unrelated experience

3. BEHAVIORAL/CULTURE FIT (weight: 15%)
   - 80-100: Culture strongly matches preferences
   - 60-79: Mixed signals but mostly compatible
   - 40-59: Some friction areas
   - 0-39: Significant mismatch

4. LOCATION & LOGISTICS (Pass/Fail + Notes)
   - PASS: Remote, worldwide, or compatible location
   - FAIL: Requires on-site, specific country restriction
   - FLAG: Hybrid or occasional travel

5. CAREER ALIGNMENT (weight: 30%)
   - 80-100: Strongly aligned with career direction
   - 60-79: Good role but partially aligned
   - 40-59: Decent job but doesn't build toward goals
   - 0-39: Dead end or backwards step

RESPOND IN EXACTLY THIS JSON FORMAT (no markdown, no extra text):
{{
  "technical_skills": {{"score": XX, "reason": "brief reason"}},
  "experience_match": {{"score": XX, "reason": "brief reason"}},
  "behavioral_fit": {{"score": XX, "reason": "brief reason"}},
  "location_logistics": {{"verdict": "PASS/FAIL/FLAG", "reason": "brief reason"}},
  "career_alignment": {{"score": XX, "reason": "brief reason"}},
  "overall_score": XX,
  "verdict": "Strong Fit/Good Fit/Moderate Fit/Weak Fit/Poor Fit",
  "strengths": ["strength1", "strength2"],
  "gaps": ["gap1", "gap2"],
  "recommendation": "1-2 sentence recommendation",
  "one_line_summary": "Ultra-brief 1-sentence summary of why this fits or doesn't"
}}

RULES:
- Be honest — if it's a weak fit, say so
- Focus on actual skills the candidate has
- Don't fabricate experience
- Keep reasons concise (under 15 words each)
- The one_line_summary should be suitable for a professional Telegram message"""


def _build_scoring_prompt(job: dict) -> str:
    desc = job.get("description", "")[:800]
    return SCORING_PROMPT.format(
        background=USER_PROFILE["background"],
        primary_skills=", ".join(USER_PROFILE["primary_skills"]),
        secondary_skills=", ".join(USER_PROFILE["secondary_skills"]),
        experience_domains=", ".join(USER_PROFILE["experience_domains"]),
        career_goals=", ".join(USER_PROFILE["career_goals"]),
        languages=", ".join(f"{k}: {v}" for k, v in USER_PROFILE["languages"].items()),
        location=USER_PROFILE["location"],
        dealbreakers=", ".join(USER_PROFILE["dealbreakers"]),
        title=job.get("title", ""),
        company=job.get("company", ""),
        location_job=job.get("location", "Remote"),
        description=desc,
    )


# ---------------------------------------------------------------------------
# Simple Prompt (fallback for quick analysis)
# ---------------------------------------------------------------------------

SIMPLE_PROMPT = """You are a career advisor. Given this job listing and the user's background, explain in 1-2 sentences why this job might be a good fit.

User background: {background}

Job title: {title}
Company: {company}
Category: {category}
Score: {score}%
Match reasons: {why}
Job description (first 500 chars): {description}

Keep the explanation concise, specific, and focused on the user's actual skills. Do not fabricate skills the user doesn't have. If the job is a weak fit, say so honestly."""


def _build_simple_prompt(job: dict) -> str:
    desc = job.get("description", "")[:500]
    return SIMPLE_PROMPT.format(
        background=USER_PROFILE["background"],
        title=job.get("title", ""),
        company=job.get("company", ""),
        category=job.get("category", ""),
        score=job.get("score", 0),
        why=", ".join(job.get("why", [])),
        description=desc,
    )


# ---------------------------------------------------------------------------
# API Calls
# ---------------------------------------------------------------------------


async def _call_ollama(session: aiohttp.ClientSession, prompt: str, max_retries: int = 2) -> str | None:
    """Call Ollama API and return the response text, or None on failure."""
    for attempt in range(max_retries + 1):
        try:
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 400,
                },
            }
            timeout = aiohttp.ClientTimeout(total=45)
            async with session.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=timeout,
            ) as resp:
                if resp.status != 200:
                    print(f"  Ollama HTTP {resp.status}")
                    if attempt < max_retries:
                        continue
                    return None
                data = await resp.json(content_type=None)
                return data.get("response", "").strip()
        except Exception as e:
            print(f"  Ollama call attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                continue
            return None
    return None


async def _check_ollama_available(session: aiohttp.ClientSession) -> bool:
    """Quick health check — does Ollama respond at all?"""
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with session.get(f"{OLLAMA_URL}/api/tags", timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def _parse_scoring_response(response: str) -> dict | None:
    """Parse the JSON scoring response from Ollama."""
    try:
        # Try to extract JSON from the response
        # Sometimes Ollama wraps it in markdown code blocks
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
            # Validate required fields
            required = ["overall_score", "verdict", "one_line_summary"]
            if all(k in data for k in required):
                return data
    except json.JSONDecodeError:
        pass
    return None


# ---------------------------------------------------------------------------
# Main Analysis Functions
# ---------------------------------------------------------------------------


async def analyze_jobs_with_ollama(jobs: list[dict]) -> list[dict]:
    """
    Enrich each matched job with AI-generated analysis.
    Uses 5-dimension scoring for detailed evaluation.
    Falls back gracefully if Ollama is unavailable — returns jobs unchanged.
    """
    if not jobs:
        return jobs

    async with aiohttp.ClientSession() as session:
        available = await _check_ollama_available(session)
        if not available:
            print("Ollama not available — skipping AI analysis")
            return jobs

        print(f"Ollama available — analyzing {len(jobs)} jobs with {MODEL}")

        for i, job in enumerate(jobs):
            # Try 5-dimension scoring first
            prompt = _build_scoring_prompt(job)
            ai_text = await _call_ollama(session, prompt)

            if ai_text:
                scoring = _parse_scoring_response(ai_text)
                if scoring:
                    # Success — store structured scoring
                    job["ai_scoring"] = scoring
                    job["ai_insight"] = scoring.get("one_line_summary", ai_text[:200])
                    job["ai_overall_score"] = scoring.get("overall_score", 0)
                    job["ai_verdict"] = scoring.get("verdict", "")
                    job["ai_strengths"] = scoring.get("strengths", [])
                    job["ai_gaps"] = scoring.get("gaps", [])
                    job["ai_recommendation"] = scoring.get("recommendation", "")
                    # Store dimension scores
                    job["ai_technical_skills"] = scoring.get("technical_skills", {}).get("score", 0)
                    job["ai_experience_match"] = scoring.get("experience_match", {}).get("score", 0)
                    job["ai_behavioral_fit"] = scoring.get("behavioral_fit", {}).get("score", 0)
                    job["ai_location_verdict"] = scoring.get("location_logistics", {}).get("verdict", "")
                    job["ai_career_alignment"] = scoring.get("career_alignment", {}).get("score", 0)
                    print(f"  [{i+1}/{len(jobs)}] 5D Scored: {job.get('title', '')[:50]} → {scoring.get('overall_score', 0)}/100 ({scoring.get('verdict', '')})")
                else:
                    # JSON parsing failed, use as simple insight
                    job["ai_insight"] = ai_text[:300]
                    print(f"  [{i+1}/{len(jobs)}] Simple insight: {job.get('title', '')[:50]}")
            else:
                print(f"  [{i+1}/{len(jobs)}] Skipped (no response): {job.get('title', '')[:50]}")

    return jobs


async def quick_analyze_job(session: aiohttp.ClientSession, job: dict) -> dict:
    """Quick analysis for a single job — used for real-time checks."""
    prompt = _build_simple_prompt(job)
    ai_text = await _call_ollama(session, prompt)
    if ai_text:
        job["ai_insight"] = ai_text[:300]
    return job
