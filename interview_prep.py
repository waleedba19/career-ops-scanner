"""
Interview Preparation Module for CareerOps
Generates interview questions and answers for top job matches.
Helps candidates prepare for interviews with personalized prep materials.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

OUTPUT_DIR = Path(__file__).parent / "output" / "interview_prep"
CV_PROFILE_PATH = Path(__file__).parent / "cv_profile.json"


def load_cv_profile() -> dict:
    """Load CV profile from JSON file."""
    try:
        if CV_PROFILE_PATH.exists():
            return json.loads(CV_PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading CV profile: {e}")
    return {}


def detect_job_type(title: str, description: str) -> str:
    """Detect the job type from title and description."""
    text = f"{title} {description}".lower()

    if any(w in text for w in ["translator", "translation", "localization", "interpreter"]):
        return "translation"
    if any(w in text for w in ["esl", "english teacher", "language teacher", "teach"]):
        return "teaching"
    if any(w in text for w in ["copywriter", "content writer", "content creator", "writing"]):
        return "writing"
    if any(w in text for w in ["data entry", "data input", "admin"]):
        return "data_entry"
    if any(w in text for w in ["virtual assistant", "va", "executive assistant"]):
        return "virtual_assistant"
    if any(w in text for w in ["proofreader", "editor", "qa", "quality"]):
        return "proofreading"
    if any(w in text for w in ["social media", "marketing", "brand"]):
        return "marketing"
    return "general"


def generate_interview_questions(job: dict, profile: dict) -> dict:
    """
    Generate interview questions and suggested answers based on job and profile.
    Returns dict with categories of questions.
    """
    title = job.get("title", "Position")
    company = job.get("company", "Company")
    description = job.get("description", "")
    job_type = detect_job_type(title, description)
    
    personal = profile.get("personal", {})
    experience = profile.get("experience", [])
    skills = profile.get("skills", {})
    education = profile.get("education", [])
    awards = profile.get("awards", [])
    
    questions = {
        "opening": [],
        "experience": [],
        "skills": [],
        "behavioral": [],
        "company_specific": [],
        "closing": [],
    }
    
    # Opening questions
    questions["opening"] = [
        {
            "question": f"Tell me about yourself and why you're interested in the {title} position at {company}.",
            "suggested_answer": f"I'm {personal.get('full_name', 'Waleed Ballag')}, a language professional with a Master's degree in Applied Linguistics from University of Zawia. I have extensive experience in {job_type}, including work as an ESL Instructor and Legal Translator. I'm excited about this position because it aligns perfectly with my skills in {', '.join(skills.get('translation', skills.get('academic', ['language services']))[:3])}.",
            "tips": "Keep it under 2 minutes. Focus on relevant experience."
        },
        {
            "question": "What are your greatest strengths?",
            "suggested_answer": f"My greatest strengths are my bilingual proficiency in Arabic and English (C1 Advanced), my attention to detail in translation work, and my ability to work across time zones. I've supervised {profile.get('supervision', {}).get('total_studies', 15)} graduate-level research studies, which demonstrates my analytical and mentoring abilities.",
            "tips": "Choose strengths relevant to the job. Give specific examples."
        }
    ]
    
    # Experience questions
    if experience:
        exp = experience[0]
        questions["experience"] = [
            {
                "question": f"Describe your experience as {exp.get('title', 'a professional')} at {exp.get('company', 'your previous company')}.",
                "suggested_answer": f"In my role as {exp.get('title', 'ESL Instructor')} at {exp.get('company', 'educational institutions')}, I {exp.get('bullets', ['developed and delivered curriculum'])[0].lower()} This experience taught me the importance of clear communication and adapting to diverse learner needs.",
                "tips": "Use the STAR method: Situation, Task, Action, Result."
            },
            {
                "question": "Tell me about a challenging project you've completed.",
                "suggested_answer": "I supervised 15 graduate-level research studies, each requiring meticulous attention to academic integrity and methodology. One particularly challenging project involved helping a student develop a corpus linguistics analysis, which required me to learn new software and methodology while maintaining strict academic standards.",
                "tips": "Focus on challenges overcome and lessons learned."
            }
        ]
    
    # Skills questions
    questions["skills"] = [
        {
            "question": "How do you ensure accuracy in your translation work?",
            "suggested_answer": "I use a multi-step verification process: initial translation, self-review against source text, terminology verification using specialized dictionaries, and final proofreading. I also maintain glossaries for consistent terminology across projects.",
            "tips": "Demonstrate your process and attention to detail."
        },
        {
            "question": "How do you handle working across different time zones?",
            "suggested_answer": "I have extensive experience working remotely across time zones. I use calendar tools to schedule overlapping hours for real-time collaboration, and I'm comfortable with asynchronous communication. I'm based in Libya (GMT+2) and have worked with teams in Europe, Middle East, and North America.",
            "tips": "Show flexibility and technical comfort."
        }
    ]
    
    # Behavioral questions
    questions["behavioral"] = [
        {
            "question": "Tell me about a time you had to meet a tight deadline.",
            "suggested_answer": "In my translation work, I frequently handle urgent legal documents with tight turnaround times. I prioritize tasks, break them into manageable segments, and use translation memory tools to maintain consistency while working efficiently. I've never missed a deadline.",
            "tips": "Show you can handle pressure while maintaining quality."
        },
        {
            "question": "How do you handle feedback or criticism of your work?",
            "suggested_answer": "I welcome feedback as an opportunity to improve. In my academic supervision role, I received feedback from professors and students alike, which helped me refine my approach. I believe constructive criticism is essential for professional growth.",
            "tips": "Show you're coachable and growth-minded."
        }
    ]
    
    # Company-specific questions
    # Ensure description is a string
    desc_str = str(description) if description else ""
    
    questions["company_specific"] = [
        {
            "question": f"What do you know about {company}?",
            "suggested_answer": f"I understand that {company} operates in the {job.get('category', 'language services')} space and values quality and professionalism. I'm particularly drawn to your commitment to remote work and global collaboration.",
            "tips": "Research the company beforehand. Mention specific values or projects."
        },
        {
            "question": "Why should we hire you over other candidates?",
            "suggested_answer": f"I bring a unique combination of native Arabic fluency, C1 Advanced English proficiency, and practical experience in both {job_type} and academic supervision. My Master's degree in Applied Linguistics gives me theoretical depth, while my 8 years of professional experience provide practical expertise. I'm also {awards[0].lower() if awards else 'recognized for my teaching excellence'}.",
            "tips": "Focus on unique value proposition. Be specific about what sets you apart."
        }
    ]
    
    # Closing questions
    questions["closing"] = [
        {
            "question": "Do you have any questions for us?",
            "suggested_answer": "Yes, I have a few questions: What does a typical day look like in this role? How do you measure success? What are the opportunities for professional development? What's the team structure and how would I collaborate with colleagues?",
            "tips": "Always have questions ready. Show genuine interest in the role and company."
        },
        {
            "question": "When can you start?",
            "suggested_answer": "I can start immediately or within a timeframe that works for your team. I'm flexible with scheduling and can accommodate any onboarding process you have in place.",
            "tips": "Be flexible but confident."
        }
    ]
    
    return questions


def save_interview_prep(job: dict, questions: dict) -> str:
    """Save interview preparation materials to a file. Returns file path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    title = job.get("title", "unknown").replace("/", "-")[:50]
    company = job.get("company", "unknown").replace("/", "-")[:30]
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    
    filename = f"{company}_{title}_{date_str}.json"
    filepath = OUTPUT_DIR / filename
    
    prep_data = {
        "job": {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "url": job.get("url", ""),
            "score": job.get("score", 0),
        },
        "questions": questions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    filepath.write_text(json.dumps(prep_data, indent=2, default=str), encoding="utf-8")
    return str(filepath)


def generate_interview_prep_for_top_matches(jobs: list[dict], min_score: int = 85) -> list[dict]:
    """
    Generate interview preparation for jobs with score >= min_score.
    Returns enriched jobs with interview prep data.
    """
    profile = load_cv_profile()
    
    for job in jobs:
        if job.get("score", 0) >= min_score:
            try:
                questions = generate_interview_questions(job, profile)
                prep_path = save_interview_prep(job, questions)
                
                job["interview_prep_path"] = prep_path
                job["interview_prep_generated"] = True
                job["interview_question_count"] = sum(len(q) for q in questions.values())
                
                print(f"Generated interview prep for {job.get('title', 'Unknown')} ({job.get('score', 0)}%)")
            except Exception as e:
                print(f"Interview prep failed for {job.get('title', 'Unknown')}: {e}")
                job["interview_prep_generated"] = False
        else:
            job["interview_prep_generated"] = False
    
    return jobs


def get_interview_prep_summary(jobs: list[dict]) -> str:
    """Get a summary of interview prep materials generated."""
    prepped = [j for j in jobs if j.get("interview_prep_generated")]
    
    if not prepped:
        return "No interview prep materials generated (score < 85%)."
    
    lines = [f"Interview prep generated for {len(prepped)} top matches:"]
    for j in prepped[:5]:
        lines.append(f"• {j.get('title', 'Unknown')} ({j.get('score', 0)}%) - {j.get('interview_question_count', 0)} questions")
    
    return "\n".join(lines)
