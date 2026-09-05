"""
Ollama AI Job Analyzer — Enhanced with 5-Dimension Fit Evaluation
Connects to local Ollama API (localhost:11434) to generate personalized
"why this fits" explanations AND detailed 5-dimension scoring for matched jobs.
Falls back gracefully if Ollama is unavailable.
"""

import json
import os
import re
from pathlib import Path

import aiohttp

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

# Load real CV profile
CV_PROFILE_PATH = Path(__file__).parent / "cv_profile.json"

def _load_cv_profile() -> dict:
    """Load the real CV profile."""
    try:
        if CV_PROFILE_PATH.exists():
            return json.loads(CV_PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

# ---------------------------------------------------------------------------
# User Profile — Real CV details from Waleed Ballag
# ---------------------------------------------------------------------------

CV = _load_cv_profile()

USER_PROFILE = {
    "name": "Waleed Ballag",
    "background": (
        "ESL Instructor and Academic Secondary Supervisor with MA in Applied Linguistics. "
        "Supervised 15 graduate-level research studies. Experienced in Arabic-English translation "
        "(legal, academic, technical). Awarded English Language Trainer of the Year (2024). "
        "Native Arabic speaker with C1 Advanced English proficiency."
    ),
    "primary_skills": [
        "ESL/EFL Instruction (secondary & university levels)",
        "Academic Supervision & Research Guidance (15 graduate studies)",
        "Arabic-English Bidirectional Translation",
        "Academic Editing & Thesis Review (APA/MLA/Harvard)",
        "Data Analysis (SPSS, thematic coding)",
        "Curriculum Development",
        "Legal Translation",
    ],
    "secondary_skills": [
        "Academic Writing & Proposal Development",
        "Survey & Instrument Design",
        "Plagiarism Checking & Originality",
        "Viva Preparation & Defense Coaching",
        "Microsoft Office Suite (Expert)",
        "Adobe Photoshop",
        "AI Tools & Advanced Programs",
    ],
    "experience_domains": [
        "ESL Teaching (2023-Present)",
        "Academic Supervision (2024-Present)",
        "Legal Translation (2019-2022)",
        "Procurement & Logistics (2017-2019)",
        "Banking Operations (2020)",
    ],
    "career_goals": [
        "Secure stable remote work in translation or ESL teaching",
        "Build long-term client relationships in academic services",
        "Grow into senior translator or academic coordinator role",
        "Contribute to graduate-level research supervision",
    ],
    "education": [
        "MA in Applied Linguistics - University of Zawia (2025)",
        "BA in English Language - University of Sabratha (2014, GPA: 87%)",
    ],
    "certifications": [
        "English Language Trainer - Muhtarifon Al-Awael Center (2024)",
        "English Language Specialist & Translator - Afaq Office (2021)",
        "ICDL - Al-Shimaa Centre (2013)",
    ],
    "awards": [
        "The Laureate of Linguistic Excellence: English Language Trainer of the Year (2024)",
    ],
    "languages": {
        "Arabic": "Native",
        "English": "C1 Advanced",
    },
    "location": "Remote (worldwide)",
    "dealbreakers": [
        "Requires on-site presence in specific city",
        "US/EU citizenship required",
        "Visa sponsorship needed",
        "Engineering/developer roles",
        "Sales quotas or commission-only",
        "Senior leadership requiring 10+ years",
    ],
}

# ---------------------------------------------------------------------------
# Enhanced 5-Dimension Scoring Prompt
# ---------------------------------------------------------------------------

SCORING_PROMPT = """You are a senior career advisor evaluating job fit for a specific candidate. Be precise and honest.

CANDIDATE PROFILE:
Name: {name}
Background: {background}
Education: {education}
Certifications: {certifications}
Awards: {awards}
Primary Skills: {primary_skills}
Secondary Skills: {secondary_skills}
Experience: {experience_domains}
Career Goals: {career_goals}
Languages: {languages}
Location: {location}
Dealbreakers: {dealbreakers}

JOB LISTING:
Title: {title}
Company: {company}
Location: {location_job}
Description: {description}

CRITICAL EVALUATION RULES:
1. If the job title contains "Engineer", "Developer", "Programmer", "DevOps", "Data Scientist", "ML/AI" → score MUST be below 40
2. If the job requires specific programming languages (Python, Java, JavaScript, etc.) → score MUST be below 40
3. If the job is clearly NOT translation/teaching/writing/academic → score MUST be below 40
4. If the job requires US/EU citizenship or specific visa → location_logistics MUST be FAIL
5. If the job mentions "commission only", "quota", or "sales target" → score MUST be below 50
6. If the job title contains "Head of", "Director", "VP", "C-Suite" → score MUST be below 50

SCORE EACH DIMENSION (0-100):

1. TECHNICAL SKILLS MATCH (weight: 30%)
   - 90-100: Job requires exactly Arabic-English translation, ESL teaching, or academic supervision
   - 70-89: Requires language skills, writing, or academic work
   - 50-69: Partial match, some transferable skills
   - 0-49: Requires engineering, development, or unrelated technical skills

2. EXPERIENCE MATCH (weight: 25%)
   - 90-100: Direct experience in translation, ESL teaching, or academic supervision
   - 70-89: Related experience in language services or education
   - 50-69: Adjacent experience
   - 0-49: Unrelated experience

3. BEHAVIORAL/CULTURE FIT (weight: 15%)
   - 90-100: Remote, flexible, academic environment
   - 70-89: Mostly compatible
   - 50-69: Some friction
   - 0-49: Significant mismatch

4. LOCATION & LOGISTICS (Pass/Fail + Notes)
   - PASS: Remote, worldwide, or compatible
   - FAIL: Requires on-site, specific country, or visa sponsorship
   - FLAG: Hybrid or occasional travel

5. CAREER ALIGNMENT (weight: 30%)
   - 90-100: Builds toward translation/teaching/academic career
   - 70-89: Good role, mostly aligned
   - 50-69: Decent but doesn't build toward goals
   - 0-49: Dead end or backwards step

RESPOND IN EXACTLY THIS JSON FORMAT:
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
  "interview_prep": "Top 3 likely interview questions with suggested answers",
  "one_line_summary": "Ultra-brief summary for Telegram"
}}

RULES:
- Be honest — if it's a weak fit, say so
- Focus on actual skills from the CV
- Don't fabricate experience
- Keep reasons concise (under 15 words each)
- Calculate overall_score as weighted average: (technical*0.30 + experience*0.25 + behavioral*0.15 + career*0.30)
- If location is FAIL, overall_score must be below 50
- If job is NOT translation/teaching/writing/academic, overall_score MUST be below 40"""


def _build_scoring_prompt(job: dict) -> str:
    desc = job.get("description", "")[:1000]
    return SCORING_PROMPT.format(
        name=USER_PROFILE["name"],
        background=USER_PROFILE["background"],
        education="; ".join(USER_PROFILE["education"]),
        certifications="; ".join(USER_PROFILE["certifications"]),
        awards="; ".join(USER_PROFILE["awards"]),
        primary_skills=", ".join(USER_PROFILE["primary_skills"]),
        secondary_skills=", ".join(USER_PROFILE["secondary_skills"]),
        experience_domains="; ".join(USER_PROFILE["experience_domains"]),
        career_goals="; ".join(USER_PROFILE["career_goals"]),
        languages=", ".join(f"{k}: {v}" for k, v in USER_PROFILE["languages"].items()),
        location=USER_PROFILE["location"],
        dealbreakers=", ".join(USER_PROFILE["dealbreakers"]),
        title=job.get("title", ""),
        company=job.get("company", ""),
        location_job=job.get("location", "Remote"),
        description=desc,
    )


# ---------------------------------------------------------------------------
# Enhanced Simple Prompt (fallback)
# ---------------------------------------------------------------------------

SIMPLE_PROMPT = """You are a career advisor for Waleed Ballag, an ESL Instructor and Academic Supervisor with MA in Applied Linguistics.

Given this job listing, explain in 1-2 sentences why this job might be a good fit for Waleed specifically.

Job title: {title}
Company: {company}
Category: {category}
Score: {score}%
Match reasons: {why}
Job description: {description}

Focus on:
1. How Waleed's ESL teaching experience applies
2. How Waleed's translation skills apply
3. How Waleed's academic supervision experience applies

Be specific about Waleed's actual qualifications. Do not fabricate skills."""


def _build_simple_prompt(job: dict) -> str:
    desc = job.get("description", "")[:500]
    return SIMPLE_PROMPT.format(
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
                    "num_predict": 500,
                },
            }
            timeout = aiohttp.ClientTimeout(total=60)
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
                    job["ai_interview_prep"] = scoring.get("interview_prep", "")
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
