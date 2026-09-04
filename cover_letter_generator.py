"""
Cover Letter Generator for CareerOps
Generates personalized PDF cover letters based on job descriptions.
Each letter is unique, filled with CV details and company info.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from fpdf import FPDF

OUTPUT_DIR = Path(__file__).parent / "output" / "cover_letters"
CV_PROFILE_PATH = Path(__file__).parent / "cv_profile.json"


def load_cv_profile() -> dict:
    """Load CV profile from JSON file."""
    try:
        if CV_PROFILE_PATH.exists():
            return json.loads(CV_PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading CV profile: {e}")
    return {}


def _detect_job_type(title: str, description: str) -> str:
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


def _extract_key_requirements(description: str) -> list[str]:
    """Extract key requirements from job description."""
    requirements = []
    text = description.lower()

    # Common requirements to look for
    req_keywords = [
        "experience", "proficiency", "knowledge", "skills",
        "bilingual", "multilingual", "fluent", "native",
        "remote", "flexible", "full-time", "part-time", "contract",
        "deadline", "fast turnaround", "attention to detail",
        "team", "independent", "self-motivated",
    ]

    for keyword in req_keywords:
        if keyword in text:
            requirements.append(keyword)

    return requirements[:5]  # Return top 5


def _generate_translation_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate translation-specific cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    requirements = _extract_key_requirements(job.get("description", ""))

    personal = profile.get("personal", {})
    experience = profile.get("experience", [])
    skills = profile.get("skills", {})

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, personal.get("phone", ""), ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.ln(10)

    # Date
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, datetime.now().strftime("%B %d, %Y"), ln=True)
    pdf.ln(5)

    # Recipient
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Hiring Manager", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, company, ln=True)
    pdf.ln(10)

    # Subject
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Re: {title} Position", ln=True)
    pdf.ln(5)

    # Body
    pdf.set_font("Helvetica", "", 10)

    # Opening paragraph - mention specific requirements
    req_text = ""
    if requirements:
        req_text = f" I noticed this role requires {', '.join(requirements[:3])}, which aligns perfectly with my background."

    opening = (
        f"Dear Hiring Manager,{req_text}\n\n"
        f"I am writing to express my strong interest in the {title} position at {company}. "
        f"As a native Arabic speaker with near-native English proficiency and over 5 years of "
        f"experience in translation and localization, I believe I am an excellent fit for this role."
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    # Experience paragraph - pull from CV
    exp_text = ""
    if experience:
        latest = experience[0]
        exp_text = (
            f"In my recent role as {latest.get('title', 'a translator')} at {latest.get('company', 'various clients')}, "
            f"I {latest.get('bullets', ['delivered high-quality translations'])[0].lower()}. "
            f"This experience has prepared me to deliver exceptional results for {company}."
        )
    else:
        exp_text = (
            "In my previous work, I have delivered high-quality Arabic-English translations "
            "across legal, medical, and technical domains."
        )

    experience_para = (
        f"{exp_text}\n\n"
        f"I understand the nuances of both languages and ensure that every translation "
        f"captures the original meaning while reading naturally in the target language."
    )
    pdf.multi_cell(0, 5, experience_para)
    pdf.ln(5)

    # Skills paragraph - highlight relevant skills
    trans_skills = skills.get("translation", [])
    skills_text = ", ".join(trans_skills[:4]) if trans_skills else "legal, medical, and technical translation"

    skills_para = (
        f"My expertise includes {skills_text}. "
        f"I am detail-oriented, meet deadlines consistently, and am comfortable working "
        f"remotely across time zones."
    )
    pdf.multi_cell(0, 5, skills_para)
    pdf.ln(5)

    # Closing
    closing = (
        f"I am available for a trial task at any time and can start immediately. "
        f"I would welcome the opportunity to discuss how I can contribute to {company}'s success.\n\n"
        f"Thank you for your consideration.\n\n"
        f"Best regards,\n"
        f"{personal.get('name', 'Your Name')}"
    )
    pdf.multi_cell(0, 5, closing)


def _generate_teaching_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate teaching-specific cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})
    experience = profile.get("experience", [])

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, personal.get("phone", ""), ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, datetime.now().strftime("%B %d, %Y"), ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Hiring Manager", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, company, ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Re: {title} Position", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)

    opening = (
        f"Dear Hiring Manager,\n\n"
        f"I am excited to apply for the {title} position at {company}. "
        f"With extensive experience teaching English as a second language to students of all ages, "
        f"I am confident in my ability to create engaging and effective learning experiences."
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    teaching_para = (
        f"My teaching approach combines structured curriculum with interactive activities. "
        f"I have experience with:\n"
        f"- Teaching adults and children in online settings\n"
        f"- Developing lesson plans tailored to individual learning styles\n"
        f"- Using technology to enhance language acquisition\n"
        f"- Providing constructive feedback that motivates students"
    )
    pdf.multi_cell(0, 5, teaching_para)
    pdf.ln(5)

    bilingual_para = (
        f"As a bilingual speaker (Arabic/English), I bring a unique perspective to language education. "
        f"I understand the challenges learners face and can relate to their experience."
    )
    pdf.multi_cell(0, 5, bilingual_para)
    pdf.ln(5)

    closing = (
        f"I am available to start immediately and can adapt to your scheduling needs across time zones.\n\n"
        f"Best regards,\n"
        f"{personal.get('name', 'Your Name')}"
    )
    pdf.multi_cell(0, 5, closing)


def _generate_writing_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate writing/content-specific cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, personal.get("phone", ""), ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, datetime.now().strftime("%B %d, %Y"), ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Hiring Manager", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, company, ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Re: {title} Position", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)

    opening = (
        f"Dear Hiring Manager,\n\n"
        f"I am writing to apply for the {title} position at {company}. "
        f"As a bilingual content creator with a passion for compelling storytelling, "
        f"I am excited about the opportunity to contribute to your content team."
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    writing_para = (
        f"My writing experience includes:\n"
        f"- Blog posts, articles, and website copy\n"
        f"- Social media content and marketing materials\n"
        f"- Product descriptions and SEO-optimized content\n"
        f"- Creative writing and brand storytelling"
    )
    pdf.multi_cell(0, 5, writing_para)
    pdf.ln(5)

    closing = (
        f"I understand the power of words to engage audiences and drive results. "
        f"I am detail-oriented, meet deadlines consistently, and adapt my writing style "
        f"to match brand voices.\n\n"
        f"I am available for a writing test and can start immediately.\n\n"
        f"Best regards,\n"
        f"{personal.get('name', 'Your Name')}"
    )
    pdf.multi_cell(0, 5, closing)


def _generate_general_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate general cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})
    summary = profile.get("summary", "")

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, personal.get("phone", ""), ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, datetime.now().strftime("%B %d, %Y"), ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Hiring Manager", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, company, ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Re: {title} Position", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)

    opening = (
        f"Dear Hiring Manager,\n\n"
        f"I am writing to express my interest in the {title} position at {company}. "
        f"{summary}"
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    skills_para = (
        f"My key strengths include:\n"
        f"- Bilingual communication (Arabic/English)\n"
        f"- Strong attention to detail\n"
        f"- Experience working remotely across time zones\n"
        f"- Fast learner who adapts quickly to new tools and processes"
    )
    pdf.multi_cell(0, 5, skills_para)
    pdf.ln(5)

    closing = (
        f"I am available for an interview at your convenience and can start immediately.\n\n"
        f"Best regards,\n"
        f"{personal.get('name', 'Your Name')}"
    )
    pdf.multi_cell(0, 5, closing)


GENERATORS = {
    "translation": _generate_translation_letter,
    "teaching": _generate_teaching_letter,
    "writing": _generate_writing_letter,
    "data_entry": _generate_general_letter,
    "virtual_assistant": _generate_general_letter,
    "proofreading": _generate_translation_letter,
    "marketing": _generate_writing_letter,
    "general": _generate_general_letter,
}


def generate_cover_letter_pdf(job: dict) -> str:
    """Generate a personalized PDF cover letter. Returns file path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    title = job.get("title", "unknown").replace("/", "-")[:50]
    company = job.get("company", job.get("source", "unknown")).replace("/", "-")[:30]
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")

    filename = f"{company}_{title}_{date_str}.pdf"
    filepath = OUTPUT_DIR / filename

    # Load CV profile
    profile = load_cv_profile()

    # Detect job type
    job_type = _detect_job_type(title, job.get("description", ""))

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Set font (Helvetica is built-in, no need for external fonts)
    pdf.set_font("Helvetica", size=10)

    # Generate letter based on job type
    generator = GENERATORS.get(job_type, _generate_general_letter)
    generator(pdf, job, profile)

    # Save PDF
    pdf.output(str(filepath))

    return str(filepath)


def generate_all_cover_letters(jobs: list[dict]) -> list[dict]:
    """Generate PDF cover letters for a list of jobs."""
    results = []
    for job in jobs:
        try:
            path = generate_cover_letter_pdf(job)
            job["cover_letter_path"] = path
            job["cover_letter_type"] = _detect_job_type(
                job.get("title", ""), job.get("description", "")
            )
        except Exception as e:
            print(f"Cover letter failed for {job.get('title', 'unknown')}: {e}")
            job["cover_letter_path"] = ""
            job["cover_letter_type"] = "error"
        results.append(job)
    return results
