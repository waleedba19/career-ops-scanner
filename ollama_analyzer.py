"""
Ollama AI Job Analyzer
Connects to local Ollama API (localhost:11434) to generate personalized
"why this fits" explanations for matched jobs.
Falls back gracefully if Ollama is unavailable.
"""

import json
import os
import re

import aiohttp

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

USER_BACKGROUND = (
    "Arabic/English translator, ESL teacher, editor, data entry specialist, "
    "virtual assistant, bilingual content creator"
)

PROMPT_TEMPLATE = """You are a career advisor. Given this job listing and the user's background, explain in 1-2 sentences why this job might be a good fit.

User background: {background}

Job title: {title}
Company: {company}
Category: {category}
Score: {score}%
Match reasons: {why}
Job description (first 500 chars): {description}

Keep the explanation concise, specific, and focused on the user's actual skills. Do not fabricate skills the user doesn't have. If the job is a weak fit, say so honestly."""


def _build_prompt(job: dict) -> str:
    desc = job.get("description", "")[:500]
    return PROMPT_TEMPLATE.format(
        background=USER_BACKGROUND,
        title=job.get("title", ""),
        company=job.get("company", ""),
        category=job.get("category", ""),
        score=job.get("score", 0),
        why=", ".join(job.get("why", [])),
        description=desc,
    )


async def _call_ollama(session: aiohttp.ClientSession, prompt: str) -> str | None:
    """Call Ollama API and return the response text, or None on failure."""
    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 200,
            },
        }
        timeout = aiohttp.ClientTimeout(total=30)
        async with session.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=timeout,
        ) as resp:
            if resp.status != 200:
                print(f"  Ollama HTTP {resp.status}")
                return None
            data = await resp.json(content_type=None)
            return data.get("response", "").strip()
    except Exception as e:
        print(f"  Ollama call failed: {e}")
        return None


async def _check_ollama_available(session: aiohttp.ClientSession) -> bool:
    """Quick health check — does Ollama respond at all?"""
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with session.get(f"{OLLAMA_URL}/api/tags", timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


async def analyze_jobs_with_ollama(jobs: list[dict]) -> list[dict]:
    """
    Enrich each matched job with an AI-generated 'why this fits' explanation.
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
            prompt = _build_prompt(job)
            ai_text = await _call_ollama(session, prompt)
            if ai_text:
                # Add AI insight to the job's why list
                if "ai_insight" not in job:
                    job["ai_insight"] = ai_text
                print(f"  [{i+1}/{len(jobs)}] Analyzed: {job.get('title', '')[:50]}")
            else:
                print(f"  [{i+1}/{len(jobs)}] Skipped (no response): {job.get('title', '')[:50]}")

    return jobs
