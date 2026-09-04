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
    education = profile.get("education", [])
    awards = profile.get("awards", [])

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, f"{personal.get('phone', '')} ({personal.get('country_code', '')})", ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.cell(0, 6, personal.get("linkedin", ""), ln=True)
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
        f"As a native Arabic speaker with C1 Advanced English proficiency and extensive experience "
        f"in translation, ESL instruction, and academic supervision, I believe I am an excellent fit."
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    # Experience paragraph - pull from CV
    exp_text = ""
    if experience:
        # Find translation-related experience
        for exp in experience:
            if any(w in exp.get("title", "").lower() for w in ["translator", "translation", "legal"]):
                exp_text = (
                    f"In my role as {exp.get('title', 'Translator')} at {exp.get('company', 'various organizations')}, "
                    f"I {exp.get('bullets', ['delivered accurate translations'])[0].lower()} "
                    f"This experience has prepared me to deliver exceptional results for {company}."
                )
                break
        if not exp_text:
            latest = experience[0]
            exp_text = (
                f"In my recent role as {latest.get('title', 'ESL Instructor')} at {latest.get('company', 'educational institutions')}, "
                f"I {latest.get('bullets', ['developed language skills using innovative approaches'])[0].lower()} "
                f"This experience has prepared me to deliver exceptional results for {company}."
            )
    else:
        exp_text = (
            "In my previous work, I have delivered high-quality Arabic-English translations "
            "across legal, academic, and technical domains."
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
    academic_skills = skills.get("academic", [])
    all_skills = trans_skills + academic_skills
    skills_text = ", ".join(all_skills[:5]) if all_skills else "Arabic-English translation, academic editing, and thesis review"

    skills_para = (
        f"My expertise includes {skills_text}. "
        f"I am detail-oriented, meet deadlines consistently, and am comfortable working "
        f"remotely across time zones."
    )
    pdf.multi_cell(0, 5, skills_para)
    pdf.ln(5)

    # Education and awards
    edu_text = ""
    if education:
        latest_edu = education[0]
        edu_text = f"I hold a {latest_edu.get('degree', 'Master's degree')} from {latest_edu.get('institution', 'a reputable university')}"
        if latest_edu.get("gpa"):
            edu_text += f" with a GPA of {latest_edu['gpa']}"
        edu_text += ". "
    
    award_text = ""
    if awards:
        award_text = f" {awards[0]}."

    education_para = f"{edu_text}{award_text}"
    pdf.multi_cell(0, 5, education_para)
    pdf.ln(5)

    # Closing
    closing = (
        f"I am available for a trial task at any time and can start immediately. "
        f"I would welcome the opportunity to discuss how I can contribute to {company}'s success.\n\n"
        f"Thank you for your consideration.\n\n"
        f"Best regards,\n"
        f"{personal.get('full_name', personal.get('name', 'Your Name'))}"
    )
    pdf.multi_cell(0, 5, closing)


def _generate_teaching_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate teaching-specific cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})
    experience = profile.get("experience", [])
    education = profile.get("education", [])
    awards = profile.get("awards", [])
    supervision = profile.get("supervision", {})

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, f"{personal.get('phone', '')} ({personal.get('country_code', '')})", ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.cell(0, 6, personal.get("linkedin", ""), ln=True)
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
        f"As a dedicated ESL Instructor with extensive experience teaching English to students "
        f"of all levels and supervising graduate-level research, I am confident in my ability "
        f"to create engaging and effective learning experiences."
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    teaching_para = (
        f"My teaching experience includes:\n"
        f"- ESL instruction at secondary and university levels (2023-Present)\n"
        f"- Training professionals at National Oil Corporation\n"
        f"- Online and in-person instruction across diverse learner backgrounds\n"
        f"- Curriculum development and innovative pedagogical approaches\n"
        f"- Supervising {supervision.get('total_studies', 15)} graduate-level research studies"
    )
    pdf.multi_cell(0, 5, teaching_para)
    pdf.ln(5)

    bilingual_para = (
        f"As a native Arabic speaker with C1 Advanced English proficiency, I bring a unique "
        f"perspective to language education. I understand the challenges learners face and can "
        f"relate to their experience. My MA in Applied Linguistics from University of Zawia "
        f"has deepened my expertise in corpus linguistics and discourse analysis."
    )
    pdf.multi_cell(0, 5, bilingual_para)
    pdf.ln(5)

    award_text = ""
    if awards:
        award_text = f"\n\nI am honored to have received {awards[0]}, recognizing my commitment to excellence in teaching."

    closing = (
        f"I am available to start immediately and can adapt to your scheduling needs across time zones.{award_text}\n\n"
        f"Best regards,\n"
        f"{personal.get('full_name', personal.get('name', 'Your Name'))}"
    )
    pdf.multi_cell(0, 5, closing)


def _generate_writing_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate writing/content-specific cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})
    experience = profile.get("experience", [])
    skills = profile.get("skills", {})
    education = profile.get("education", [])

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, f"{personal.get('phone', '')} ({personal.get('country_code', '')})", ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.cell(0, 6, personal.get("linkedin", ""), ln=True)
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
        f"As a bilingual content creator with extensive experience in academic writing, "
        f"thesis editing, and Arabic-English translation, I am excited about the opportunity "
        f"to contribute to your content team."
    )
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    writing_para = (
        f"My writing and content experience includes:\n"
        f"- Academic thesis writing and editing (15+ graduate-level studies)\n"
        f"- Arabic-English bidirectional translation of research papers\n"
        f"- Blog content creation and website copy\n"
        f"- APA/MLA/Harvard formatting and academic tone enhancement\n"
        f"- Data analysis reporting and statistical write-ups"
    )
    pdf.multi_cell(0, 5, writing_para)
    pdf.ln(5)

    # Education
    edu_text = ""
    if education:
        latest_edu = education[0]
        edu_text = f"I hold a {latest_edu.get('degree', 'Master's degree')} from {latest_edu.get('institution', 'University of Zawia')}, "
        edu_text += f"with expertise in corpus linguistics and discourse analysis. "

    closing = (
        f"{edu_text}I understand the power of words to engage audiences and drive results. "
        f"I am detail-oriented, meet deadlines consistently, and adapt my writing style "
        f"to match brand voices.\n\n"
        f"I am available for a writing test and can start immediately.\n\n"
        f"Best regards,\n"
        f"{personal.get('full_name', personal.get('name', 'Your Name'))}"
    )
    pdf.multi_cell(0, 5, closing)


def _generate_general_letter(pdf: FPDF, job: dict, profile: dict) -> None:
    """Generate general cover letter."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})
    summary = profile.get("summary", "")
    education = profile.get("education", [])
    awards = profile.get("awards", [])

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, personal.get("full_name", personal.get("name", "Your Name")), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, personal.get("email", ""), ln=True)
    pdf.cell(0, 6, f"{personal.get('phone', '')} ({personal.get('country_code', '')})", ln=True)
    pdf.cell(0, 6, personal.get("location", ""), ln=True)
    pdf.cell(0, 6, personal.get("linkedin", ""), ln=True)
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
        f"- Native Arabic speaker with C1 Advanced English proficiency\n"
        f"- Extensive experience in ESL instruction and academic supervision\n"
        f"- Professional Arabic-English translation (legal, academic, technical)\n"
        f"- Strong attention to detail and academic integrity compliance\n"
        f"- Experience working remotely across time zones"
    )
    pdf.multi_cell(0, 5, skills_para)
    pdf.ln(5)

    # Education
    edu_text = ""
    if education:
        latest_edu = education[0]
        edu_text = f"I hold a {latest_edu.get('degree', 'Master's degree')} from {latest_edu.get('institution', 'University of Zawia')}. "
    
    award_text = ""
    if awards:
        award_text = f" {awards[0]}."

    closing = (
        f"{edu_text}I am available for an interview at your convenience and can start immediately.{award_text}\n\n"
        f"Best regards,\n"
        f"{personal.get('full_name', personal.get('name', 'Your Name'))}"
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
