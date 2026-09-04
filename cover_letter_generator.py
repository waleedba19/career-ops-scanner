"""
Cover Letter Generator for CareerOps
Generates personalized cover letters based on job descriptions.
Saves as .txt files in output/cover_letters/
"""

from pathlib import Path
from datetime import datetime, timezone
import re

# User profile
USER_PROFILE = {
    "name": "Waleed",
    "title": "Bilingual Content Creator & Translation Specialist",
    "email": "waleedzydeco19@gmail.com",
    "skills": [
        "Arabic-English translation",
        "ESL teaching",
        "content writing",
        "copywriting",
        "data entry",
        "virtual assistance",
        "proofreading",
        "localization",
        "multilingual communication",
    ],
    "experience": "5+ years in translation, content creation, and virtual assistance",
    "strengths": [
        "native Arabic speaker with near-native English",
        "fast turnaround on translations",
        "detail-oriented proofreading",
        "experience with remote teams",
        "flexible schedule across time zones",
    ],
}

OUTPUT_DIR = Path(__file__).parent / "output" / "cover_letters"


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


def _generate_translation_letter(company: str, title: str, description: str) -> str:
    return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {title} position at {company}. As a native Arabic speaker with near-native English proficiency and over 5 years of experience in translation and localization, I believe I am an excellent fit for this role.

In my previous work, I have delivered high-quality Arabic-English translations across legal, medical, and technical domains. I understand the nuances of both languages and ensure that every translation captures the original meaning while reading naturally in the target language.

What I bring to {company}:
- Native Arabic with near-native English — no awkward phrasing
- Fast turnaround without sacrificing quality
- Experience with CAT tools and translation workflows
- Detail-oriented proofreading as a final step

I am available for a trial task at any time and can start immediately. I work across time zones and am comfortable with flexible schedules.

Thank you for your consideration. I look forward to discussing how I can contribute to your team.

Best regards,
{USER_PROFILE["name"]}
{USER_PROFILE["email"]}"""


def _generate_teaching_letter(company: str, title: str, description: str) -> str:
    return f"""Dear Hiring Manager,

I am excited to apply for the {title} position at {company}. With extensive experience teaching English as a second language to students of all ages, I am confident in my ability to create engaging and effective learning experiences.

My teaching approach combines structured curriculum with interactive activities. I have experience with:
- Teaching adults and children in online settings
- Developing lesson plans tailored to individual learning styles
- Using technology to enhance language acquisition
- Providing constructive feedback that motivates students

As a bilingual speaker (Arabic/English), I bring a unique perspective to language education. I understand the challenges learners face and can relate to their experience.

I am available to start immediately and can adapt to your scheduling needs across time zones.

Best regards,
{USER_PROFILE["name"]}
{USER_PROFILE["email"]}"""


def _generate_writing_letter(company: str, title: str, description: str) -> str:
    return f"""Dear Hiring Manager,

I am writing to apply for the {title} position at {company}. As a bilingual content creator with a passion for compelling storytelling, I am excited about the opportunity to contribute to your content team.

My writing experience includes:
- Blog posts, articles, and website copy
- Social media content and marketing materials
- Product descriptions and SEO-optimized content
- Creative writing and brand storytelling

I understand the power of words to engage audiences and drive results. I am detail-oriented, meet deadlines consistently, and adapt my writing style to match brand voices.

I am available for a writing test and can start immediately. I work across time zones and am comfortable with remote collaboration.

Best regards,
{USER_PROFILE["name"]}
{USER_PROFILE["email"]}"""


def _generate_data_entry_letter(company: str, title: str, description: str) -> str:
    return f"""Dear Hiring Manager,

I am interested in the {title} position at {company}. With strong attention to detail and extensive experience in data entry and administrative support, I am confident in my ability to deliver accurate and timely work.

My data entry skills include:
- High typing speed with excellent accuracy
- Experience with spreadsheets, databases, and CRM systems
- Attention to detail that ensures zero errors
- Ability to work with large volumes of data efficiently

I am organized, reliable, and comfortable working independently in remote settings. I can start immediately and adapt to your scheduling needs.

Best regards,
{USER_PROFILE["name"]}
{USER_PROFILE["email"]}"""


def _generate_va_letter(company: str, title: str, description: str) -> str:
    return f"""Dear Hiring Manager,

I am applying for the {title} position at {company}. As an experienced virtual assistant, I have supported executives and teams with administrative tasks, scheduling, and communication across multiple time zones.

My VA experience includes:
- Calendar management and appointment scheduling
- Email management and correspondence
- Travel arrangements and coordination
- Document preparation and organization
- Research and data gathering

I am tech-savvy, detail-oriented, and proactive in solving problems before they become issues. I work well independently and communicate clearly with remote teams.

I am available to start immediately and can adapt to your workflow.

Best regards,
{USER_PROFILE["name"]}
{USER_PROFILE["email"]}"""


def _generate_general_letter(company: str, title: str, description: str) -> str:
    return f"""Dear Hiring Manager,

I am writing to express my interest in the {title} position at {company}. With a diverse skill set spanning translation, content creation, and administrative support, I am confident I can contribute meaningfully to your team.

My key strengths include:
- Bilingual communication (Arabic/English)
- Strong attention to detail
- Experience working remotely across time zones
- Fast learner who adapts quickly to new tools and processes

I am available for an interview at your convenience and can start immediately.

Best regards,
{USER_PROFILE["name"]}
{USER_PROFILE["email"]}"""


GENERATORS = {
    "translation": _generate_translation_letter,
    "teaching": _generate_teaching_letter,
    "writing": _generate_writing_letter,
    "data_entry": _generate_data_entry_letter,
    "virtual_assistant": _generate_va_letter,
    "proofreading": _generate_translation_letter,  # Similar to translation
    "marketing": _generate_writing_letter,  # Similar to writing
    "general": _generate_general_letter,
}


def generate_cover_letter(job: dict) -> str:
    """Generate a personalized cover letter for a job."""
    title = job.get("title", "Position")
    company = job.get("company", job.get("source", "Your Company"))
    description = job.get("description", "")

    job_type = _detect_job_type(title, description)
    generator = GENERATORS.get(job_type, _generate_general_letter)

    letter = generator(company, title, description)
    return letter


def save_cover_letter(job: dict, letter: str) -> Path:
    """Save cover letter to file. Returns the file path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    title = job.get("title", "unknown").replace("/", "-")[:50]
    company = job.get("company", job.get("source", "unknown")).replace("/", "-")[:30]
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")

    filename = f"{company}_{title}_{date_str}.txt"
    filepath = OUTPUT_DIR / filename

    filepath.write_text(letter, encoding="utf-8")
    return filepath


def generate_all_cover_letters(jobs: list[dict]) -> list[dict]:
    """Generate cover letters for a list of jobs. Returns list with cover_letter_path added."""
    results = []
    for job in jobs:
        letter = generate_cover_letter(job)
        path = save_cover_letter(job, letter)
        job["cover_letter"] = letter
        job["cover_letter_path"] = str(path)
        results.append(job)
    return results
