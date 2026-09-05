"""
CareerOps Learning Module
Tracks application feedback and learns from user preferences.
Improves scoring over time based on what jobs you apply to, reject, or get interviews for.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

LEARNING_FILE = Path(__file__).parent / "output" / "learning_data.json"


def load_learning_data() -> dict:
    """Load learning data from file."""
    try:
        if LEARNING_FILE.exists():
            return json.loads(LEARNING_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {
        "applied_jobs": [],
        "rejected_jobs": [],
        "interviewed_jobs": [],
        "hired_jobs": [],
        "skill_preferences": {},
        "company_preferences": {},
        "location_preferences": {},
        "salary_preferences": {},
        "total_scans": 0,
        "total_matches": 0,
        "acceptance_rate": 0,
    }


def save_learning_data(data: dict):
    """Save learning data to file."""
    LEARNING_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEARNING_FILE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def record_application(job_url: str, job_data: dict, status: str = "applied"):
    """
    Record an application or feedback.
    Status: applied, rejected, interviewed, hired, declined
    """
    data = load_learning_data()
    
    record = {
        "url": job_url,
        "title": job_data.get("title", ""),
        "company": job_data.get("company", ""),
        "score": job_data.get("score", 0),
        "category": job_data.get("category", ""),
        "source": job_data.get("source", ""),
        "ai_score": job_data.get("ai_overall_score", 0),
        "ai_verdict": job_data.get("ai_verdict", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
    }
    
    if status == "applied":
        data["applied_jobs"].append(record)
        # Update skill preferences
        category = job_data.get("category", "Other")
        data["skill_preferences"][category] = data["skill_preferences"].get(category, 0) + 1
        # Update company preferences
        company = job_data.get("company", "Unknown")
        data["company_preferences"][company] = data["company_preferences"].get(company, 0) + 1
    elif status == "rejected":
        data["rejected_jobs"].append(record)
    elif status == "interviewed":
        data["interviewed_jobs"].append(record)
    elif status == "hired":
        data["hired_jobs"].append(record)
    elif status == "declined":
        data["rejected_jobs"].append(record)
    
    # Calculate acceptance rate
    total_applied = len(data["applied_jobs"])
    total_interviewed = len(data["interviewed_jobs"])
    if total_applied > 0:
        data["acceptance_rate"] = round((total_interviewed / total_applied) * 100, 1)
    
    save_learning_data(data)
    return data


def get_learning_insights() -> dict:
    """Get insights from learning data to improve scoring."""
    data = load_learning_data()
    
    insights = {
        "top_skills": sorted(data["skill_preferences"].items(), key=lambda x: -x[1])[:5],
        "top_companies": sorted(data["company_preferences"].items(), key=lambda x: -x[1])[:5],
        "acceptance_rate": data["acceptance_rate"],
        "total_applied": len(data["applied_jobs"]),
        "total_interviewed": len(data["interviewed_jobs"]),
        "total_hired": len(data["hired_jobs"]),
    }
    
    return insights


def adjust_scoring_based_on_learning(job: dict) -> float:
    """
    Adjust AI score based on learning data.
    Returns adjusted score (0-100).
    """
    data = load_learning_data()
    
    if not data["applied_jobs"]:
        return job.get("ai_overall_score", job.get("score", 0))
    
    base_score = job.get("ai_overall_score", job.get("score", 0))
    adjustment = 0
    
    # Get category and company
    category = job.get("category", "Other")
    company = job.get("company", "Unknown")
    title = (job.get("title") or "").lower()
    
    # ---- CATEGORY LEARNING ----
    # Boost score significantly if category matches frequently applied jobs
    if category in data["skill_preferences"]:
        times_applied = data["skill_preferences"][category]
        if times_applied >= 5:
            adjustment += 8  # Strong boost for favorite categories
        elif times_applied >= 3:
            adjustment += 5  # Moderate boost
        elif times_applied >= 1:
            adjustment += 3  # Small boost
    
    # ---- COMPANY LEARNING ----
    # Boost score for companies you've applied to before
    if company in data["company_preferences"]:
        times_applied = data["company_preferences"][company]
        if times_applied >= 3:
            adjustment += 6  # Strong boost for favorite companies
        elif times_applied >= 1:
            adjustment += 3  # Moderate boost
    
    # ---- REJECTION LEARNING ----
    # Reduce score if category matches rejected jobs
    rejected_categories = set()
    for rejected in data.get("rejected_jobs", []):
        rejected_categories.add(rejected.get("category", ""))
    
    if category in rejected_categories:
        adjustment -= 5  # Penalty for rejected categories
    
    # ---- INTERVIEW LEARNING ----
    # Boost score if category matches jobs that got interviews
    interview_categories = set()
    for interviewed in data.get("interviewed_jobs", []):
        interview_categories.add(interviewed.get("category", ""))
    
    if category in interview_categories:
        adjustment += 10  # Strong boost for interview-winning categories
    
    # ---- TITLE KEYWORD LEARNING ----
    # Learn from title patterns in applied jobs
    applied_titles = [j.get("title", "").lower() for j in data["applied_jobs"]]
    for applied_title in applied_titles:
        # Check for common keywords
        keywords = ["translator", "esl", "teacher", "tutor", "writer", "editor", "proofreader", "academic"]
        for kw in keywords:
            if kw in applied_title and kw in title:
                adjustment += 2  # Small boost for matching title keywords
                break
    
    # ---- SOURCE LEARNING ----
    # Learn which sources produce jobs you apply to
    source_preferences = {}
    for applied in data["applied_jobs"]:
        src = applied.get("source", "unknown")
        source_preferences[src] = source_preferences.get(src, 0) + 1
    
    job_source = job.get("source", "unknown")
    if job_source in source_preferences:
        times_from_source = source_preferences[job_source]
        if times_from_source >= 3:
            adjustment += 3  # Boost for productive sources
    
    # Apply adjustment
    adjusted_score = max(0, min(100, base_score + adjustment))
    
    return adjusted_score


def get_daily_recommendation() -> str:
    """Generate daily recommendation based on learning data."""
    data = load_learning_data()
    insights = get_learning_insights()
    
    if not data["applied_jobs"]:
        return "Start applying to jobs to build your preference profile!"
    
    lines = []
    lines.append(f"You've applied to {insights['total_applied']} jobs")
    lines.append(f"Interview rate: {insights['acceptance_rate']}%")
    
    if insights["top_skills"]:
        top_skill = insights["top_skills"][0][0]
        lines.append(f"Your strongest category: {top_skill}")
    
    if insights["top_companies"]:
        top_company = insights["top_companies"][0][0]
        lines.append(f"Most applied company: {top_company}")
    
    return "\n".join(lines)
