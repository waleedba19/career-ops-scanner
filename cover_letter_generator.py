"""
Cover Letter Generator for CareerOps
Generates personalized PDF cover letters based on job descriptions.
Each letter is unique, filled with CV details and company info.
Uses Ollama for AI-powered customization when available.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fpdf import FPDF

OUTPUT_DIR = Path(__file__).parent / "output" / "cover_letters"
CV_PROFILE_PATH = Path(__file__).parent / "cv_profile.json"

# Libya live time (Africa/Tripoli, UTC+2 — no DST since 2013).
# Letter date lines and file names follow the user's local day, not UTC.
LIBYA_TZ = timezone(timedelta(hours=2))  # Africa/Tripoli


def now_libya() -> datetime:
    """Current time in Libya (Africa/Tripoli, UTC+2)."""
    return datetime.now(LIBYA_TZ)


def load_cv_profile() -> dict:
    """Load CV profile from JSON file."""
    try:
        if CV_PROFILE_PATH.exists():
            return json.loads(CV_PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading CV profile: {e}")
    return {}


async def generate_ai_cover_letter_content(job: dict, profile: dict) -> dict:
    """
    Use Ollama to generate personalized cover letter content.
    Returns dict with custom paragraphs for each section.
    """
    try:
        import httpx
        
        title = job.get("title", "Position")
        company = job.get("company", "Your Company")
        description = job.get("description", "")[:1000]  # Limit description length
        
        # Build profile summary for AI
        personal = profile.get("personal", {})
        experience = profile.get("experience", [])
        skills = profile.get("skills", {})
        education = profile.get("education", [])
        awards = profile.get("awards", [])
        
        exp_summary = "; ".join([
            f"{e.get('title', '')} at {e.get('company', '')}" 
            for e in experience[:3]
        ])
        
        skills_summary = ", ".join([
            s for sublist in skills.values() for s in sublist[:3]
        ])
        
        edu_summary = "; ".join([
            f"{e.get('degree', '')} from {e.get('institution', '')}" 
            for e in education[:2]
        ])
        
        prompt = f"""Generate a professional cover letter for this job application.

JOB DETAILS:
- Position: {title}
- Company: {company}
- Requirements: {description[:500]}

CANDIDATE PROFILE:
- Name: {personal.get('full_name', 'Waleed Ballag')}
- Education: {edu_summary}
- Experience: {exp_summary}
- Skills: {skills_summary}
- Awards: {awards[0] if awards else 'None'}
- Languages: Native Arabic, C1 Advanced English

Generate exactly 4 paragraphs:
1. OPENING: Express enthusiasm for {title} at {company}, mention 1-2 key requirements from the job
2. EXPERIENCE: Highlight most relevant experience (2-3 sentences)
3. SKILLS: Match candidate skills to job requirements (2-3 sentences)
4. CLOSING: Express availability, enthusiasm, and request interview

Keep each paragraph 2-3 sentences. Be specific to this job. No generic statements.
Output as JSON with keys: opening, experience, skills, closing"""

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:1.5b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                }
            )
            
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "")
                
                # Try to parse JSON from response
                try:
                    # Find JSON in response
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    if start >= 0 and end > start:
                        ai_content = json.loads(response_text[start:end])
                        return ai_content
                except json.JSONDecodeError:
                    pass
                    
    except Exception as e:
        print(f"AI cover letter generation failed: {e}")
    
    return None


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
    pdf.cell(0, 6, now_libya().strftime("%B %d, %Y"), ln=True)
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
        degree = latest_edu.get("degree", "Master's degree")
        institution = latest_edu.get("institution", "a reputable university")
        edu_text = f"I hold a {degree} from {institution}"
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
    pdf.cell(0, 6, now_libya().strftime("%B %d, %Y"), ln=True)
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
    pdf.cell(0, 6, now_libya().strftime("%B %d, %Y"), ln=True)
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
        degree = latest_edu.get("degree", "Master's degree")
        institution = latest_edu.get("institution", "University of Zawia")
        edu_text = f"I hold a {degree} from {institution}, "
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
    pdf.cell(0, 6, now_libya().strftime("%B %d, %Y"), ln=True)
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
        degree = latest_edu.get("degree", "Master's degree")
        institution = latest_edu.get("institution", "University of Zawia")
        edu_text = f"I hold a {degree} from {institution}. "
    
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

    # Strip characters that are invalid in filenames (Windows and Unix)
    def _safe(s: str) -> str:
        return re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", s).strip()

    title = _safe(job.get("title", "unknown"))[:50]
    company = _safe(job.get("company", job.get("source", "unknown")))[:30]
    date_str = now_libya().strftime("%Y%m%d")

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

    # Check for AI-generated content
    ai_content = job.get("ai_cover_letter_content")
    
    if ai_content:
        # Use AI-generated content
        _generate_ai_enhanced_letter(pdf, job, profile, ai_content)
    else:
        # Use template-based generation
        generator = GENERATORS.get(job_type, _generate_general_letter)
        generator(pdf, job, profile)

    # Save PDF
    pdf.output(str(filepath))

    return str(filepath)


def _generate_ai_enhanced_letter(pdf: FPDF, job: dict, profile: dict, ai_content: dict) -> None:
    """Generate cover letter using AI-enhanced content."""
    company = job.get("company", "Your Company")
    title = job.get("title", "Position")
    personal = profile.get("personal", {})
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
    pdf.cell(0, 6, now_libya().strftime("%B %d, %Y"), ln=True)
    pdf.ln(5)

    # Recipient
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Hiring Manager", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, company, ln=True)
    pdf.ln(10)

    # Subject
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Re: {title} Position", ln=True)
    pdf.ln(5)

    # Body - AI-generated content
    pdf.set_font("Helvetica", "", 10)
    
    # Opening paragraph
    opening = ai_content.get("opening", f"Dear Hiring Manager,\n\nI am writing to express my interest in the {title} position at {company}.")
    pdf.multi_cell(0, 5, opening)
    pdf.ln(5)

    # Experience paragraph
    experience = ai_content.get("experience", "I have relevant experience in this field.")
    pdf.multi_cell(0, 5, experience)
    pdf.ln(5)

    # Skills paragraph
    skills = ai_content.get("skills", "I possess the required skills for this role.")
    pdf.multi_cell(0, 5, skills)
    pdf.ln(5)

    # Closing
    closing = ai_content.get("closing", "I am available for an interview at your convenience.")
    
    # Add education and awards
    edu_text = ""
    if education:
        latest_edu = education[0]
        degree = latest_edu.get("degree", "Master's degree")
        institution = latest_edu.get("institution", "University of Zawia")
        edu_text = f"\n\nI hold a {degree} from {institution}."
    
    award_text = ""
    if awards:
        award_text = f" {awards[0]}."
    
    full_closing = f"{closing}{edu_text}{award_text}\n\nBest regards,\n{personal.get('full_name', personal.get('name', 'Your Name'))}"
    pdf.multi_cell(0, 5, full_closing)


async def generate_all_cover_letters(jobs: list[dict]) -> list[dict]:
    """Generate PDF cover letters for a list of jobs with AI enhancement."""
    import asyncio
    
    results = []
    for job in jobs:
        try:
            # Try to generate AI content for the cover letter
            profile = load_cv_profile()
            ai_content = await generate_ai_cover_letter_content(job, profile)
            
            if ai_content:
                job["ai_cover_letter_content"] = ai_content
            
            path = generate_cover_letter_pdf(job)
            job["cover_letter_path"] = path
            job["cover_letter_type"] = _detect_job_type(
                job.get("title", ""), job.get("description", "")
            )
            job["cover_letter_ai"] = ai_content is not None
        except Exception as e:
            print(f"Cover letter failed for {job.get('title', 'unknown')}: {e}")
            job["cover_letter_path"] = ""
            job["cover_letter_type"] = "error"
            job["cover_letter_ai"] = False
        results.append(job)
    return results
