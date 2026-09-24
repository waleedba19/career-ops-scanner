"""
CareerOps Job Scanner — GitHub Actions Edition
Ported from Cloudflare Worker (index.js) to Python.
Uses aiohttp for async HTTP, concurrent.futures for parallel fetching,
and Ollama for AI-powered job analysis.

CareerOps 2.0 — intelligent job search.
"""

import asyncio
import json
import os
import re
import time
import base64
import html as html_mod
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import aiohttp

from groq_analyzer import analyze_jobs_with_ollama
from notifier import send_telegram, send_email
from excel_generator import generate_excel
from source_manager import record_source_run, cleanup_dead_sources, get_source_report
from evolution_tracker import record_scan, get_evolution_summary
from cover_letter_generator import generate_all_cover_letters
from learning_module import record_application, adjust_scoring_based_on_learning, get_learning_insights
from company_research import research_companies_batch, cleanup_old_cache
from company_patterns import record_company_match, get_company_priority
from fetchers.social import fetch_reddit_social
from fetchers.verified import (
    fetch_linkedin_guest, fetch_jobicy_tags, fetch_impactpool,
    fetch_themuse, fetch_ashby_board, fetch_workable_board, fetch_smartrecruiters_board,
    fetch_jsearch, fetch_reliefweb, fetch_workingnomads_json,
    fetch_remowork, fetch_recruitee_board, fetch_teamtailor_board,
    fetch_euremotejobs, fetch_remotejobleads, fetch_dailyremote, fetch_dynamitejobs, fetch_europeremotely,
    fetch_bamboohr_board, fetch_jobvite_board, fetch_personio_board,
    fetch_translation_jobs,
    # keyed variants — imported under distinct names because scanner.py still defines
    # legacy fetch_adzuna/fetch_jooble stubs (hard-coded fake credentials, always 401)
    fetch_adzuna as fetch_adzuna_keyed, fetch_jooble as fetch_jooble_keyed,
)
from interview_prep import generate_interview_prep_for_top_matches, get_interview_prep_summary
from scheduler import SmartScheduler, create_scheduler
from deep_reader import enrich_jobs_with_deep_read
from email_finder import enrich_jobs_with_emails

# Worldwide Arabic job search engine
try:
    from fetchers.wide_search import fetch_worldwide_arabic_jobs
    WIDE_SEARCH_AVAILABLE = True
except ImportError:
    WIDE_SEARCH_AVAILABLE = False
    print("Warning: Wide search not available.")

# ── Search Proxy — bypass blocked sites via search engines ──
try:
    from fetchers.search_proxy import fetch_blocked_sites_via_search
    SEARCH_PROXY_AVAILABLE = True
except ImportError:
    SEARCH_PROXY_AVAILABLE = False
    print("Warning: Search proxy not available.")

# ── Playwright search (real browser, bypasses 403s) ──
try:
    from fetchers.playwright_search import fetch_with_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
from auto_sources import get_active_sources as get_auto_sources, fetch_generic_rss


def extract_email_from_text(text: str) -> str:
    """Extract email address from text."""
    if not text:
        return ""
    email_patterns = [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'apply[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    ]
    for pattern in email_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            email = match.group(1) if match.lastindex else match.group(0)
            skip_domains = ['example.com', 'sentry.io', 'wixpress.com', 'github.com', 'sentry-next.wixpress.com']
            if not any(domain in email.lower() for domain in skip_domains):
                return email
    return ""


def get_company_website(company_name: str) -> str:
    """Get company website from name."""
    company_websites = {
        "transperfect": "https://www.transperfect.com",
        "lionbridge": "https://www.lionbridge.com",
        "rws": "https://www.rws.com",
        "keywords studios": "https://www.keywordsstudios.com",
        "welocalize": "https://www.welocalize.com",
        "appen": "https://www.appen.com",
        "telus international": "https://www.telusinternational.com",
        "centific": "https://www.centific.com",
        "scale ai": "https://scale.com",
        "surge ai": "https://surgeai.com",
        "oneforma": "https://www.oneforma.com",
        "proz": "https://www.proz.com",
        "tarjama": "https://www.tarjama.com",
        "careem": "https://www.careem.com",
        "remote.com": "https://remote.com",
        "deel": "https://www.deel.com",
        "oyster": "https://www.oysterhr.com",
        "google": "https://careers.google.com",
        "microsoft": "https://careers.microsoft.com",
        "amazon": "https://www.amazon.jobs",
        "apple": "https://www.apple.com/careers",
        "meta": "https://www.metacareers.com",
    }
    company_lower = company_name.lower().strip()
    for key, website in company_websites.items():
        if key in company_lower or company_lower in key:
            return website
    # No confident match — return nothing so the digest omits the field.
    # The old fallback slugged the raw name into "<name>.com", which produced
    # URLs like "irc-internationalrescuemmittee.com" (the " co" suffix was
    # stripped mid-word) and 404s the user could not tell apart from real links.
    return ""


# ── Enterprise config (centralized) — single source of truth ──
import config as _cfg
MIN_MATCH_SCORE = _cfg.MIN_MATCH_SCORE
MAX_AGE_HOURS = _cfg.MAX_AGE_HOURS
MAX_AGE_FRESH_HOURS = _cfg.MAX_AGE_FRESH_HOURS
NEAR_MISS_MIN = _cfg.NEAR_MISS_MIN
NEAR_MISS_MAX = _cfg.NEAR_MISS_MAX
NEAR_MISS_LIMIT = _cfg.NEAR_MISS_LIMIT
TOP_LIVENESS_CHECK = _cfg.TOP_LIVENESS_CHECK
HISTORY_MAX = _cfg.HISTORY_MAX
FETCH_TIMEOUT = _cfg.FETCH_TIMEOUT
FETCH_BATCH_SIZE = _cfg.FETCH_BATCH_SIZE
DEDUP_TTL_DAYS = getattr(_cfg, "DEDUP_TTL_DAYS", 14)
DEDUP_ENABLED = getattr(_cfg, "DEDUP_ENABLED", True)
AI_ANALYZE_CAP = getattr(_cfg, "AI_ANALYZE_CAP", 10)
OLD_AI_VERIFY_CAP = getattr(_cfg, "OLD_AI_VERIFY_CAP", 8)
AUDIT_CAP = getattr(_cfg, "AUDIT_CAP", 8)
# Previously-seen-but-still-open relevant jobs are re-surfaced in the daily
# available pool (not announced as NEW) so a quiet day never reads "0" while
# real translation roles are open.
OPEN_POOL_CAP = int(os.getenv("CAREEROPS_OPEN_POOL", "15"))
COMPANY_MIN_SCORE = getattr(_cfg, "COMPANY_MIN_SCORE", 40)
WORLDWIDE_FEEDS = getattr(_cfg, "WORLDWIDE_FEEDS", [])
MAX_WORLDWIDE_FEEDS = getattr(_cfg, "MAX_WORLDWIDE_FEEDS", 40)
WORLDWIDE_HTML = getattr(_cfg, "WORLDWIDE_HTML", [])
MAX_WORLDWIDE_HTML = getattr(_cfg, "MAX_WORLDWIDE_HTML", 30)
EMAIL_FINDER_ENABLED = getattr(_cfg, "EMAIL_FINDER_ENABLED", True)
EMAIL_FIND_TARGETS = getattr(_cfg, "EMAIL_FIND_TARGETS", 10)
HEADERS = _cfg.HEADERS
GREENHOUSE_COMPANIES = _cfg.GREENHOUSE_COMPANIES
LEVER_COMPANIES = _cfg.LEVER_COMPANIES
GREENHOUSE_PROFILE_BOARDS = _cfg.GREENHOUSE_PROFILE_BOARDS
ASHBY_COMPANIES = _cfg.ASHBY_COMPANIES
WORKABLE_COMPANIES = _cfg.WORKABLE_COMPANIES
SMARTRECRUITERS_COMPANIES = _cfg.SMARTRECRUITERS_COMPANIES
RECRUITEE_COMPANIES = _cfg.RECRUITEE_COMPANIES
TEAMTAILOR_COMPANIES = _cfg.TEAMTAILOR_COMPANIES
BAMBOOHR_COMPANIES = _cfg.BAMBOOHR_COMPANIES
JOBVITE_COMPANIES = _cfg.JOBVITE_COMPANIES
PERSONIO_COMPANIES = _cfg.PERSONIO_COMPANIES
PROBE_BLOCKED_SOURCES = _cfg.PROBE_BLOCKED_SOURCES
FORCE_BLOCKED_SOURCES = _cfg.FORCE_BLOCKED_SOURCES
OUTPUT_DIR = _cfg.OUTPUT_DIR
HISTORY_FILE = OUTPUT_DIR / "scan_history.json"
SEEN_URLS_FILE = OUTPUT_DIR / "seen_urls.json"
SCAN_HISTORY_FILE = OUTPUT_DIR / "scan_history_acum.json"
TIMEOUT = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)


# ── Validated ATS boards (state/valid_company_slugs.json from company_board_probe.py) ──
# When present, only slugs confirmed returning HTTP 200 are fetched — eliminating
# the HTTP-404 spam / wasted requests. Falls back to config lists otherwise.
def _load_valid_slugs() -> dict:
    try:
        p = Path(__file__).parent / "state" / "valid_company_slugs.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("valid", {})
    except Exception:
        pass
    return {}


_VALID_SLUGS = _load_valid_slugs()
if _VALID_SLUGS:
    if _VALID_SLUGS.get("greenhouse"):
        GREENHOUSE_COMPANIES = [tuple(x) for x in _VALID_SLUGS["greenhouse"]]
        GREENHOUSE_PROFILE_BOARDS = []  # already merged into GREENHOUSE_COMPANIES
    if _VALID_SLUGS.get("lever"):
        LEVER_COMPANIES = [tuple(x) for x in _VALID_SLUGS["lever"]]
    if _VALID_SLUGS.get("ashby"):
        ASHBY_COMPANIES = [tuple(x) for x in _VALID_SLUGS["ashby"]]
    if _VALID_SLUGS.get("workable"):
        WORKABLE_COMPANIES = [tuple(x) for x in _VALID_SLUGS["workable"]]
    if _VALID_SLUGS.get("smartrecruiters"):
        SMARTRECRUITERS_COMPANIES = [tuple(x) for x in _VALID_SLUGS["smartrecruiters"]]
    if _VALID_SLUGS.get("recruitee"):
        RECRUITEE_COMPANIES = [tuple(x) for x in _VALID_SLUGS["recruitee"]]
    if _VALID_SLUGS.get("teamtailor"):
        TEAMTAILOR_COMPANIES = [tuple(x) for x in _VALID_SLUGS["teamtailor"]]
    if _VALID_SLUGS.get("bamboohr"):
        BAMBOOHR_COMPANIES = [tuple(x) for x in _VALID_SLUGS["bamboohr"]]
    if _VALID_SLUGS.get("jobvite"):
        JOBVITE_COMPANIES = [tuple(x) for x in _VALID_SLUGS["jobvite"]]
    if _VALID_SLUGS.get("personio"):
        PERSONIO_COMPANIES = [tuple(x) for x in _VALID_SLUGS["personio"]]
    print(f"ATS boards: using {len(_VALID_SLUGS)} validated adapters from probe")

# ── Metrics hooks (optional) ──
try:
    import metrics as _metrics
    import careerops_logger as _clog
    _log = _clog.get_logger("scanner")
except Exception:
    _metrics = None
    _log = None

# ── Free Forever Intel — email/urgency/desperation + search (no paid API) ──
try:
    from company_intel.collector import enrich_jobs_with_intel
except Exception:
    enrich_jobs_with_intel = None
try:
    from fetchers.search_orchestrator import discover_via_search
except Exception:
    discover_via_search = None

# ---------------------------------------------------------------------------
# Paid platforms to filter out (require fees to apply)
# ---------------------------------------------------------------------------

PAID_PLATFORMS = [
    "flexjobs",  # Requires subscription
    "tophire",   # Requires payment
    "wellfound", # Some listings require payment
    "ziprecruiter", # Some premium features
]

# ---------------------------------------------------------------------------
# Platforms known for Arabic/translation jobs (prioritize these)
# ---------------------------------------------------------------------------

ARABIC_PLATFORMS = [
    "mostaql", "for9a", "khamsat", "ureed", "wuzzuf", "daleel", "aqar", "tajer",
    "bayt", "gulftalent", "naukrigulf",
]

# ---------------------------------------------------------------------------
# Job sources — Greenhouse companies (translation/language/AI-data only)
# ---------------------------------------------------------------------------

GREENHOUSE_COMPANIES = [
    # Translation & Localization LSPs
    ("Smartling", "smartling"), ("Lokalise", "lokalise"),
    ("TransPerfect", "transperfect"), ("Lionbridge", "lionbridge"),
    ("RWS", "rws"), ("Welocalize", "welocalize"),
    ("Keywords Studios", "keywordsstudios"),
    ("Phrase", "phrase"), ("Unbabel", "unbabel"), ("Lilt", "lilt"),
    ("Gengo", "gengo"), ("Translated", "translated"), ("Smartcat", "smartcat"),
    # AI Data Annotation / Linguist Marketplaces
    ("Scale AI", "scaleai"), ("Prolific", "prolific"),
    ("Invisible", "agency"), ("Labelbox", "labelbox"), ("Turing", "turing"),
    ("TELUS International", "telusinternational"), ("Toloka", "toloka"),
    ("Appen", "appen"), ("Centific", "centific"),
    ("Surge AI", "surgeai"), ("Micro1", "micro1"),
    # MENA / Arabic Content & EdTech
    ("Nagwa", "nagwa"), ("Abwaab", "abwaab"), ("Tamatem", "tamatem"),
    ("Tarjama", "tarjama"), ("Anghami", "anghami"),
    # Remote-first (hire translators)
    ("Deel", "deel"), ("Toptal", "toptal"),
]

LEVER_COMPANIES = [
    ("Unbabel", "unbabel"),
    ("Lilt", "lilt"),
    ("Anghami", "anghami"),
]

# ---------------------------------------------------------------------------
# Scoring system — enhanced for Arabic speaker focus
# ---------------------------------------------------------------------------

MATCH_BUCKETS = [
    {
        "name": "Arabic Translation",
        "phrases": [
            # Direct Arabic translation roles (highest priority)
            (re.compile(r"arabic (translator|translation|interpreter|linguist|editor|proofreader|content|writer|qa|tester|locali[sz])", re.I), 95),
            (re.compile(r"(translator|translation|interpreter|linguist|editor|proofreader|locali[sz]ation specialist).{0,40}arabic", re.I), 95),
            (re.compile(r"\barabic (speaker|native|fluent|bilingual)\b.{0,40}(translator|editor|content|locali[sz]|translation|localization)", re.I), 95),
            # Arabic alone with remote/freelance/global — strong signal
            (re.compile(r"\barabic\b.{0,50}\b(remote|worldwide|freelance|work from home)\b", re.I), 90),
            (re.compile(r"\barabic (speaker|native|fluent|bilingual)\b", re.I), 85),
            # Bilingual/multilingual + Arabic
            (re.compile(r"bilingual.*arabic|arabic.*bilingual", re.I), 90),
            (re.compile(r"\bmultilingual\b.{0,50}\barabic", re.I), 85),
            (re.compile(r"\barabic\b.{0,50}\b(multilingual|polyglot)", re.I), 85),
            # MENA region roles
            (re.compile(r"mena.*arabic|arabic.*mena", re.I), 85),
            (re.compile(r"\b(mena|middle east|north africa)\b.{0,50}\b(translat|locali|languag|content|edit)", re.I), 85),
            # RTL / dialect signals. "msa" is deliberately excluded here: it is a
            # common acronym (MSA Safety, MSA = any "…Safety Administration"),
            # so a bare hit scored a marine "Surveyor I" posting at 80%. It is
            # added back below, gated on Arabic/localization context.
            (re.compile(r"\b(right[- ]to[- ]left|rtl)\b.{0,50}\barabic", re.I), 85),
            (re.compile(r"\b(darija|fusha|modern standard arabic|colloquial arabic)\b", re.I), 80),
            (re.compile(r"\bmsa\b.{0,40}\b(arabic|translat|locali[sz]|linguist)\b", re.I), 80),
            (re.compile(r"\b(arabic|translat|locali[sz]|linguist)\b.{0,40}\bmsa\b", re.I), 80),
            # Arabic + AI/NLP/data roles
            (re.compile(r"\b(nlp|natural language processing)\b.{0,50}\barabic", re.I), 80),
            (re.compile(r"\barabic.{0,50}\b(nlp|natural language processing)\b", re.I), 80),
            (re.compile(r"\barabic\b.{0,50}\b(data|annotation|labeling|moderation)\b", re.I), 80),
            (re.compile(r"\barabic\b.{0,50}\b(content|review|qa|quality)\b", re.I), 80),
            (re.compile(r"\barabic.{0,50}\bAI\b", re.I), 80),
            (re.compile(r"\barabic\b.{0,50}\b(prompt|evaluation|training data)\b", re.I), 80),
            # Language expert/specialist roles
            (re.compile(r"\blanguage (expert|specialist|analyst)\b.{0,30}arabic", re.I), 90),
            (re.compile(r"arabic.{0,30}\blanguage (expert|specialist|analyst)\b", re.I), 90),
            # MTPE / post-editing
            (re.compile(r"mtpe|post.?edit|machine translation", re.I), 55),
            # Subtitling / captioning
            (re.compile(r"subtitl|caption|captioning", re.I), 50),
            # Voice-over / dubbing
            (re.compile(r"voice.?over|dubbing|dub", re.I), 50),
            # Terminology
            (re.compile(r"terminolog|termbase|term.?base", re.I), 55),
            # Content localization
            (re.compile(r"content.?locali[sz]ation|locali[sz]ed.?content", re.I), 50),
            # Multilingual
            (re.compile(r"multilingual|multi.?lingual", re.I), 45),
            # Language services / support
            (re.compile(r"language.?services|language.?support", re.I), 45),
            # Bilingual content / communication
            (re.compile(r"bilingual.*content|bilingual.*communication", re.I), 50),
        ],
    },
    {
        "name": "Translation (any pair)",
        "phrases": [
            # Generic translation roles — if you can translate ANY pair, it's relevant
            (re.compile(r"\b(translator|translation specialist|staff translator|freelance translator|senior translator)\b", re.I), 85),
            (re.compile(r"\b(locali[sz]ation specialist|l10n specialist|i18n linguist)\b", re.I), 85),
            (re.compile(r"\b(translat|locali[sz]).{0,30}(remote|worldwide|freelance|home|global)\b", re.I), 85),
            (re.compile(r"\b(remote|worldwide|freelance).{0,30}(translat|locali[sz])\b", re.I), 85),
            # CAT tools / translation memory
            # Distinctive tool names — only appear in translation tooling.
            (re.compile(r"\b(cat tools?|trados|memoq|memsource|wordfast|omegat|crowdin)\b", re.I), 80),
            # Brand names that are also employer names ("Lokalise", "Phrase",
            # "Smartcat"). A bare hit matched those companies' non-translation
            # postings (e.g. "Junior IT Operations Specialist — Lokalise"), so
            # require translation context nearby.
            (re.compile(r"\b(smartcat|phrase|lokalise)\b.{0,60}\b(translat|locali[sz]|linguist|subtitle|caption|language)\b", re.I), 80),
            (re.compile(r"\b(translat|locali[sz]|linguist|subtitle|caption|language)\b.{0,60}\b(smartcat|phrase|lokalise)\b", re.I), 80),
            # Translation-specific terms
            (re.compile(r"\b(translation memory|terminology management|glossary|style guide|locale|localization kit)\b", re.I), 80),
            # CAT-tool units. A bare "segment" is far too generic (Ground-Segment
            # engineers, market segments, customer-segment CSMs) and was scoring
            # unrelated roles as Translation matches — only translation-context
            # segments count now.
            (re.compile(r"\b(translation segment|text segment|source segment|target segment|sentence segment|segmentation (?:unit|memory|editor))\b", re.I), 75),
            (re.compile(r"\b(tmx|xliff|po file|gettext|xbench)\b", re.I), 75),
            # Subtitling / captioning (translation-adjacent)
            (re.compile(r"\b(subtitl|caption|closed caption|subtitle translation|audio description)\b", re.I), 80),
            # Document translation
            (re.compile(r"\b(document (translat|locali[sz])|certified (translat|locali[sz])|legal (translat|locali[sz]))\b", re.I), 85),
            (re.compile(r"\b(birth certificate|court document|contract|diploma|academic transcript).{0,30}translat", re.I), 85),
            # Any "X to Y translator" or "Y-X translator" pattern
            (re.compile(r"\b\w+ to \w+ translator\b", re.I), 80),
            (re.compile(r"\btranslat(or|ion|ing|e|ed)\b.{0,30}\b(english|spanish|french|german|chinese|japanese|korean|portuguese|italian|russian|arabic)\b", re.I), 80),
            # Language pair patterns
            (re.compile(r"\b(english|en).{0,10}(arabic|ar).{0,10}(translat|locali|interpret|linguist)\b", re.I), 95),
            (re.compile(r"\b(arabic|ar).{0,10}(english|en).{0,10}(translat|locali|interpret|linguist)\b", re.I), 95),
            (re.compile(r"\b(en|ar)[\s/\-]+(ar|en)\b.{0,30}(translat|locali|interpret)", re.I), 95),
        ],
    },
    {
        "name": "Editing & Proofreading",
        "phrases": [
            (re.compile(r"\b(proofreader|proofreading|proofread)\b", re.I), 80),
            (re.compile(r"\b(editor|editing|copy editor|copyeditor)\b.{0,30}(remote|worldwide|freelance)", re.I), 80),
            (re.compile(r"academic (editor|editing)|copy editor", re.I), 80),
            (re.compile(r"\b(content writer|copywriter|copywriting|blog writer|article writer|content editor|content creator)\b", re.I), 80),
            (re.compile(r"\bcontent creation\b", re.I), 75),
            # Bilingual/multilingual editing
            (re.compile(r"\b(arabic|bilingual|multilingual)\b.{0,50}\b(content|blog|article|copy)\b.{0,50}\b(writer|writing|creator)\b", re.I), 85),
            (re.compile(r"\b(arabic|bilingual|multilingual)\b.{0,50}\b(proofread|editor|editing)\b", re.I), 85),
            # Language-specific editing
            (re.compile(r"\b(english|spanish|french|german).{0,10}(editor|editing)\b.{0,30}(remote|freelance)\b", re.I), 80),
        ],
    },
    {
        "name": "AI Data & Annotation",
        "phrases": [
            (re.compile(r"\b(data (entry|annotation|labeling|labeler|moderation|curation))\b.{0,30}(remote|worldwide|freelance)", re.I), 80),
            (re.compile(r"\b(prompt (writer|engineer|evaluation|rating))\b.{0,30}(remote|worldwide)", re.I), 80),
            (re.compile(r"\b(ai (trainer|training|annotation|labeling|rater|data))\b.{0,30}(remote|worldwide)", re.I), 80),
            (re.compile(r"\b(language (data|annotation|model training|quality))\b.{0,30}(remote|worldwide)", re.I), 80),
            (re.compile(r"\b(content (moderator|moderation|reviewer|review|quality))\b.{0,30}(remote|worldwide)", re.I), 75),
            (re.compile(r"\b(search (quality|rater|evaluator|annotator))\b.{0,30}(remote|worldwide)", re.I), 75),
            (re.compile(r"\b(linguist|language specialist)\b.{0,30}(remote|worldwide|ai|data|training)", re.I), 85),
            (re.compile(r"\b(virtual assistant|va|administrative assistant|executive assistant)\b.{0,30}(remote|worldwide|bilingual)", re.I), 80),
            (re.compile(r"\b(transcription|transcriber|typist)\b.{0,30}(remote|worldwide|bilingual)", re.I), 80),
            (re.compile(r"\barabic\b.{0,50}\b(data entry|data input|data processing|virtual assistant|va|administrative|transcription|transcriber|typist)\b", re.I), 85),
            (re.compile(r"\b(arabic|bilingual)\b.{0,50}\b(data entry|annotation|labeling|transcription)\b", re.I), 85),
        ],
    },
    {
        "name": "ESL",
        "phrases": [
            (re.compile(r"\b(esl|efl|tesol|tefl|ELL)\b", re.I), 85),
            (re.compile(r"\benglish (teacher|teaching|instructor|tutoring|language)\b", re.I), 80),
            (re.compile(r"\b(teacher|instructor|tutor)\b.{0,30}\b(english|ESL|EFL|language)\b", re.I), 80),
            (re.compile(r"\b(online.?tutor|virtual.?tutor|e.?tutor)\b", re.I), 40),
            (re.compile(r"\b(english.?language.?trainer|language.?coach)\b", re.I), 40),
            (re.compile(r"\b(curriculum.?design|course.?design|lesson.?plan)\b", re.I), 30),
            (re.compile(r"\b(phonics|grammar|speaking|listening|conversation)\b.{0,30}\b(teacher|tutor|instructor)\b", re.I), 70),
            (re.compile(r"\b(teach|tutor|instruct).{0,30}\b(online|remote|worldwide|virtual)\b", re.I), 70),
            (re.compile(r"\b(young learners|kids|children|young learners).{0,30}\b(english|ESL|language)\b", re.I), 75),
        ],
    },
    {
        "name": "Admin",
        "phrases": [
            (re.compile(r"\b(virtual assistant|VA|administrative assistant|executive assistant)\b.{0,30}(remote|worldwide|bilingual)", re.I), 80),
            (re.compile(r"\b(data entry|data input|data processing|typing|typist)\b.{0,30}(remote|worldwide|bilingual)", re.I), 75),
            (re.compile(r"\b(ai.?training|ai.?data|llm.?training|prompt.?engineer|prompt.?evaluat)", re.I), 50),
            (re.compile(r"\b(data.?annotation|data.?labeling|data.?labeler|data.?collection)", re.I), 45),
            (re.compile(r"\b(content.?moderation|quality.?assurance|qa.?linguist)", re.I), 40),
            (re.compile(r"\b(customer.?support.*bilingual|bilingual.*support|multilingual.*support)", re.I), 45),
            (re.compile(r"\b(virtual.?assistant|executive.?assistant|admin.?assistant)", re.I), 40),
            (re.compile(r"\b(secretary|receptionist|office manager|operations assistant)\b.{0,30}(remote|worldwide)", re.I), 70),
            (re.compile(r"\b(arabic|bilingual)\b.{0,50}\b(virtual assistant|data entry|admin|secretary|receptionist)\b", re.I), 85),
        ],
    },
    {
        "name": "AI Data",
        "phrases": [
            (re.compile(r"ai.?training|ai.?data|llm.?training|prompt.?engineer|prompt.?evaluat", re.I), 55),
            (re.compile(r"data.?annotation|data.?labeling|data.?labeler|data.?collection", re.I), 50),
            (re.compile(r"ai.?trainer|ai.?quality|rlhf|reinforcement.?learning", re.I), 50),
            (re.compile(r"natural.?language|nlp|text.?classification|sentiment", re.I), 40),
            (re.compile(r"search.?quality|rater|evaluator|judge", re.I), 35),
        ],
    },
]

# Languages that are NOT the user's pair
WRONG_LANGUAGE = re.compile(
    r"\b(hindi|spanish|castilian|french|german|chinese|mandarin|cantonese|japanese|korean|"
    r"portuguese|italian|russian|turkish|urdu|bengali|tamil|telugu|kannada|malayalam|marathi|"
    r"gujarati|punjabi|sinhala|nepali|pashto|dari|persian|farsi|kurdish|hebrew|"
    r"dutch|polish|thai|vietnamese|indonesian|malay|tagalog|filipino|swahili|amharic|somali|hausa|"
    r"yoruba|igbo|zulu|afrikaans|"
    r"slovak|slovene|slovenian|ukrainian|czech|romanian|hungarian|greek|bulgarian|croatian|"
    r"serbian|bosnian|macedonian|albanian|estonian|latvian|lithuanian|finnish|norwegian|"
    r"swedish|danish|icelandic|irish|welsh|basque|catalan|galician|armenian|georgian|"
    r"azerbaijani|kazakh|kyrgyz|uzbek|mongolian|burmese|khmer|assamese|asturian|aymara|"
    r"belarusian|cebuano|chechen|chichewa|corsican|dzongkha|esperanto|fulah|fulani|"
    r"gaelic|ganda|guarani|guaraní|haitian|hmong|ilocano|javanese|kabuverdianu|kaqchikel|"
    r"k.?iche|kinyarwanda|kirundi|konkani|lao|lingala|luo|luxembourgish|malagasy|maltese|"
    r"maori|māori|mapudungun|nahuatl|occitan|odia|oromo|papiamento|quechua|q.?eqchi|"
    r"sesotho|sotho|shona|sindhi|sinhalese|sinhala|soninke|sunda|sundanese|tajik|tsugaru|"
    r"umbundu|wolof|xhosa|alentejano|alentejo|turkmen|slovenien|nynorsk|bokmal|"
    r"frisian|scots|samoa|tongan|fijian|pidgin|creole)\b",
    re.I,
)
HAS_ARABIC = re.compile(r"\barabic\b", re.I)

# Engineering titles are a hard drop for this candidate's profile. Only the
# translation/language-adjacent engineer roles below are acceptable (and even
# those are judged by the AI gate afterwards).
ENGINEER_TITLE = re.compile(r"\b(?:[\w.-]+ )?engineers?\b|\bengineering\b", re.I)
ENGINEER_ALLOW = re.compile(
    r"(locali[sz]ation engineer|translation engineer|machine translation|"
    r"prompt engineer|nlp|linguist|annotation|speech|voice)",
    re.I,
)

STUB_TITLE = re.compile(
    r"(get started|sign[- ]?up|teacher'?s portal|request a quote|join us|"
    r"become a (tutor|teacher)|onboarding|careers home|log[- ]?in|"
    r"\btest[ -]?test[ -]?test\b|\bdo not apply\b|\bdo not click\b)",
    re.I,
)
STUB_URL = re.compile(
    r"(onboarding|tutorsignup|/teach/?$|/teachers/?$|/careers/?$|"
    r"request-a-quote|estimate\?|/tutor/?$)",
    re.I,
)
IN_PERSON_GIG = re.compile(
    r"\b(presencial|in[- ]person|mystery shop|onsite visit|\blocal job\b)\b",
    re.I,
)
NON_ROLE_ADMIN = re.compile(
    r"\b(impartner|salesforce|prm|platform administrator|systems? admin|"
    r"price realization|pricing strategy|principal .*manager)\b",
    re.I,
)
COUNTRY_LOCKED_LOC = re.compile(
    # \b after the group so "Remote — Europe" (region, allowed) does not match "eu".
    r"(remote\s*[-–—,]\s*(us|usa|u\.s\.a?|united states|canada|uk|united kingdom|australia|eu)\b"
    r"|(united states|canada|uk|australia)\s+only"
    r"|us only|canada only)",
    re.I,
)

# "Remote — <City>, <ST>" is just as country-locked as "Remote — US", but the
# country-only pattern above missed it, so US-metro roles leaked into Fresh
# Matches. States are matched case-sensitively (the 2-letter codes collide with
# ordinary words like "in", "or", "me", "hi", "ok", "de").
US_STATE_CODES = (
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS "
    "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC"
).split()
_US_STATE_NAMES = (
    "alabama alaska arizona arkansas california colorado connecticut delaware florida "
    "hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland "
    "massachusetts michigan minnesota mississippi missouri montana nebraska nevada "
    "new hampshire new jersey new mexico new york north carolina north dakota ohio "
    "oklahoma oregon pennsylvania rhode island south carolina south dakota tennessee "
    "texas utah vermont virginia washington west virginia wisconsin wyoming"
).split()
# Sentence-initial capitalisation makes ", Il"/", In" ambiguous, so 2-letter codes
# are only trusted when fully uppercase. "georgia" is left out of the names list
# (it is also a country); ", GA" still catches the US state.
_US_STATE_CODE_RE = re.compile(r",\s*(?:" + "|".join(US_STATE_CODES) + r")\b")
_US_STATE_NAME_RE = re.compile(r"\b(?:" + "|".join(_US_STATE_NAMES) + r")\b", re.I)


def _is_us_locked(location: str) -> bool:
    """True when the location names a US state — i.e. not worldwide-remote."""
    loc = location or ""
    return bool(_US_STATE_CODE_RE.search(loc) or _US_STATE_NAME_RE.search(loc))


# Workplace anchor — the posting text says the role is physically tied to an
# office, even when the job board (or LinkedIn's f_WT=2 tag) labelled it remote.
# "This is an in-office role …hybrid work from home program" (Fisher class) or
# "on-site position" (Wasael class) must NOT be delivered as worldwide-remote.
# Narrow on purpose: "occasional on-site visits", "optional in-office" and
# "hybrid-friendly" copy for genuinely remote roles must keep their remote
# eligibility.
_ONSITE_ANCHOR = re.compile(
    r"\bin[- ]office (role|position|job|posting)\b"
    r"|this is (an?|a)?\s*(in[- ]office|on[- ]site|office[- ]?based)"
    r"|office[- ]?based (role|position|job|work)\b"
    r"|(role|position|job) (is )?(in[- ]office|on[- ]site)\b"
    r"|required (to )?(be|work|report|come) in[- ]person"
    r"|must (be|work|report|attend) (in|at) the office"
    r"|in[- ]person (role|position|job|presence)\b"
    r"|(performed|delivered|carried out) on[- ]site",
    re.I,
)

NEGATIVE_KEYWORDS = [
    "software engineer", "backend engineer", "frontend engineer", "full stack engineer",
    "devops", "sre", "security analyst", "data scientist", "ml engineer",
    "crypto", "blockchain", "solidity", "web3", "quant", "trading",
    "human resources", "employee relations", "people partner",
    "people business partner", "hrbp", "recruiter", "talent acquisition",
    "workday", "labor relations", "disciplinary",
    # Enterprise/sales titles
    "enterprise sales", "quota", "commission", "business development",
    "accounts executive", "account executive", "sales representative",
    "sales manager", "sales director", "regional sales",
    # Customer success / client-facing quota roles (non-translation)
    "customer success", "success manager", "client success",
    "customer success manager", "customer relationship manager",
    # Business partner / enablement roles
    "business partner", "field enablement", "enablement manager",
    "revenue", "pipeline", "account manager",
    # Leadership / management (not individual contributor)
    "content manager", "social media manager", "brand manager",
    "marketing manager", "marketing director", "operations manager",
    "product marketing", "demand generation", "growth manager",
    # Dev / IT / non-target professional roles
    "web developer", "mobile developer", "ios developer", "android developer",
    "cloud engineer", "infrastructure engineer", "platform engineer",
    "game developer", "game designer", "unity developer", "unreal",
    "database administrator", "dba", "sysadmin", "it support",
    # Developer/engineering titles (never the candidate's target)
    "full stack developer", "full-stack developer", "software developer",
    "backend developer", "frontend developer", "full stack engineer",
    "java developer", "python developer", "php developer", "ruby developer",
    ".net developer", "dotnet developer", "c# developer", "react developer",
    "node developer", "golang developer", "rust developer",
    "data engineer", "machine learning engineer", "ai engineer", "mlops",
    "open source contributor",
    # Healthcare / non-remote fields
    "nurse", "doctor", "pharmacist", "healthcare",
    # Finance / accounting
    "accountant", "financial analyst", "finance manager",
    # Hospitality / manual
    "chef", "cook", "bartender", "waiter",
    # Trades / manual labor
    "mechanic", "plumber", "carpenter", "welder",
    # Logistics / on-site
    "driver", "delivery", "warehouse", "logistics",
    # Security / government
    "security guard", "police", "firefighter",
    # Real estate / insurance
    "real estate", "property manager", "insurance agent",
    # Legal / compliance
    "paralegal", "legal assistant", "compliance officer",
]

NON_TARGET_ROLE = re.compile(
    r"\b(?:strategist|architect|planner|integration engineer)\b"
    r"|project manager|program manager|product (?:manager|owner)"
    r"|(?:data|business) (?:engineer|scientist|analyst|architect|platform|governance|warehouse|lake|modeling|infrastructure|intelligence)"
    r"|technical (?:writer|support)"
    r"|smartsheet|excel (?:macro|vba|modeling|dashboard)"
    r"|business (?:analyst|intelligence)|\bbi\b|\betl\b"
    r"|(?:integrations?) specialist|solution (?:architect|engineer|consultant)"
    r"|\bhead of\b|\bdirector\b|\bvp\b|\bvice president\b|\bchief\b"
    r"|\bcountry (?:manager|partner|lead)\b|\bregional (?:manager|director|lead)\b"
    r"|\bsenior (?:manager|director|lead|partner|associate)\b|\bgeneral manager\b"
    r"|\bsales (?:manager|director|lead|head|executive|representative)\b"
    r"|\bmarketing (?:manager|director|lead)\b|\bbusiness development\b"
    r"|\baccounts (?:manager|director|lead)\b|\bclient (?:manager|director|lead)\b"
    r"|\benterprise (?:sales|account|manager)\b|\bquota\b|\bcommission\b"
    r"|\bpayroll (?:clerk|manager|specialist)\b"
    r"|\b(?:content|social media|brand) (?:manager|lead|director|head)\b"
    r"|\bcontent producer\b|\bsocial media lead\b"
    r"|\bproduct marketing\b|\bdemand generation\b|\bgrowth manager\b"
    r"|\bprincipal\b|\bstrategy manager\b|\bprice realization\b"
    r"|\bplatform administrator\b|\bimpartner\b",
    re.I,
)

# Keywords in NON_TARGET_ROLE that are OK when combined with target keywords
# e.g., "Language Expert" is fine, "Data Analyst" is not
NON_TARGET_ALLOWLIST = re.compile(
    r"(language|translation|translator|content|copy|creative|english|teaching|tutor|freelance|online|educational|legal|academic)",
    re.I,
)

SENIOR_PENALTY = re.compile(
    r"(principal\b|head of|\bvp\b|director|\bchief\b|strategy manager|price realization)",
    re.I,
)

REMOTE_MARKER = re.compile(
    r"(remote|work from home|wfh|worldwide|anywhere|global|freelance|contract|couchsurfing|virtual)", re.I
)

def _place_regex(places: "list[str]") -> re.Pattern:
    """Word-boundary alternation so 'oman' cannot match inside 'Romania'.

    Longest alternatives first, otherwise 'saudi' would shadow 'saudi arabia'.
    Used for every location list, because plain substring matching let "any"
    fire inside "Germany" and "asia" inside "Malaysia".
    """
    ordered = sorted(places, key=len, reverse=True)
    return re.compile(r"\b(?:" + "|".join(re.escape(p) for p in ordered) + r")\b", re.I)


# Region/worldwide wording the user accepts (work from anywhere).
ALLOWED_LOCATIONS = [
    "worldwide", "anywhere", "global", "virtual", "online",
    "work from home", "wfh", "freelance", "contract",
    "remote", "remote first", "fully remote",
    # Regions — user can work from anywhere in these.
    "middle east", "north africa", "mena", "emea",
    "europe", "european union", "eu",
    "apac", "americas", "latin america", "latam",
    "asia", "africa", "north america", "south america",
]

# Countries the user targets as an Arabic/English freelancer. A "Remote — Dubai"
# posting is worth surfacing even though it names a country, because the work is
# Arabic-market and frequently open to MENA-based freelancers.
MENA_LOCATIONS = [
    "united arab emirates", "uae", "dubai", "abu dhabi", "sharjah",
    "saudi arabia", "saudi", "ksa", "riyadh", "jeddah", "dammam",
    "qatar", "doha", "kuwait", "bahrain", "oman", "muscat", "gcc",
    "jordan", "amman", "egypt", "cairo", "alexandria",
    "morocco", "casablanca", "rabat", "tunisia", "tunis", "algeria", "algiers",
    "lebanon", "beirut", "iraq", "baghdad", "palestine", "libya", "tripoli",
    "yemen", "syria", "damascus", "turkey", "istanbul",
]

# Residency-blocked markets — the user cannot apply from Libya.
BLOCKED_COUNTRY_LOCATIONS = [
    "united states", "usa", "canada", "australia", "united kingdom",
    "new zealand", "india", "philippines", "pakistan", "nigeria", "kenya",
]

ALLOWED_LOCATION_RE = _place_regex(ALLOWED_LOCATIONS)
MENA_RE = _place_regex(MENA_LOCATIONS)
BLOCKED_COUNTRY_RE = _place_regex(BLOCKED_COUNTRY_LOCATIONS)

# Non-geographic location wording that still means "work from anywhere".
GENERIC_LOCATION_MARKERS = [
    "multiple locations", "various", "flexible", "unspecified",
    "not specified", "remote-first", "fully remote",
]
GENERIC_LOCATION_RE = _place_regex(GENERIC_LOCATION_MARKERS)

# ISO 3166-1 English short names. Needed because a bare location like "Remote —
# Germany" is a hard country lock, while "Remote | Athens" (a city with no
# country) is a hub/nice-to-have that Arabic-translation employers use often —
# treating both as locks cost real matches (e.g. IOM interpreter roles).
COUNTRY_NAMES = [
    "afghanistan", "albania", "algeria", "andorra", "angola", "argentina",
    "armenia", "australia", "austria", "azerbaijan", "bahamas", "bahrain",
    "bangladesh", "barbados", "belarus", "belgium", "belize", "benin",
    "bhutan", "bolivia", "bosnia and herzegovina", "botswana", "brazil",
    "brunei", "bulgaria", "burkina faso", "burundi", "cambodia", "cameroon",
    "canada", "chad", "chile", "china", "colombia", "comoros", "congo",
    "costa rica", "croatia", "cuba", "cyprus", "czechia", "denmark",
    "djibouti", "dominica", "dominican republic", "ecuador", "egypt",
    "el salvador", "eritrea", "estonia", "eswatini", "ethiopia", "fiji",
    "finland", "france", "gabon", "gambia", "georgia", "germany", "ghana",
    "greece", "guatemala", "guinea", "guyana", "haiti", "honduras", "hungary",
    "iceland", "india", "indonesia", "iran", "iraq", "ireland", "israel",
    "italy", "jamaica", "japan", "jordan", "kazakhstan", "kenya", "kuwait",
    "kyrgyzstan", "laos", "latvia", "lebanon", "lesotho", "liberia", "libya",
    "liechtenstein", "lithuania", "luxembourg", "madagascar", "malawi",
    "malaysia", "maldives", "mali", "malta", "mauritania", "mauritius",
    "mexico", "moldova", "monaco", "mongolia", "montenegro", "morocco",
    "mozambique", "myanmar", "namibia", "nepal", "netherlands",
    "new zealand", "nicaragua", "niger", "nigeria", "north korea",
    "north macedonia", "norway", "oman", "pakistan", "palau", "palestine",
    "panama", "papua new guinea", "paraguay", "peru", "philippines", "poland",
    "portugal", "qatar", "romania", "russia", "rwanda", "saudi arabia",
    "senegal", "serbia", "seychelles", "sierra leone", "singapore",
    "slovakia", "slovenia", "somalia", "south africa", "south korea",
    "south sudan", "spain", "sri lanka", "sudan", "suriname", "sweden",
    "switzerland", "syria", "taiwan", "tajikistan", "tanzania", "thailand",
    "togo", "tunisia", "turkey", "turkmenistan", "uganda", "ukraine",
    "united arab emirates", "united kingdom", "united states", "uruguay",
    "uzbekistan", "vanuatu", "venezuela", "vietnam", "yemen", "zambia",
    "zimbabwe",
]
COUNTRY_RE = _place_regex(COUNTRY_NAMES)

# "Remote — <place>" carries the real location in `<place>`. "Worldwide remote"
# is granted by the marker only when no country/city is named after it, so a
# Spain/Ohio/India-only posting cannot short-circuit on the word "remote".
_REMOTE_PREFIX_RE = re.compile(r"^\s*remote\b[\s\-–—,|:/]*", re.I)


def _location_body(loc: str) -> str:
    """Strip a leading 'remote' marker so the place after it can be judged.

    Returns "" when the location is just a remote marker (plain "Remote"),
    which is treated as worldwide. Otherwise the leftover country/city text.
    """
    return _REMOTE_PREFIX_RE.sub("", loc or "").strip(" ,-–—|/:")



RESIDENCY_BLOCKERS = [
    re.compile(r"residents? only", re.I),
    re.compile(r"must be (a |an )?(u\.?s|united states|uk|eu|canadian|australian|german|french|british|european) (citizen|resident|national)", re.I),
    re.compile(r"(u\.?s|us|uk|eu|canadian|australian) (citizen|permanent resident|national)\b", re.I),
    re.compile(r"authorized to work in", re.I),
    re.compile(r"(work authorization|work authorisation|work permit required)", re.I),
    re.compile(r"(no sponsoring|no sponsorship)", re.I),
    re.compile(r"(cannot|can't|unable to|do not|does not|will not|won't|no|without|not (available|provided|offered)).{0,20}(visa )?sponsorship", re.I),
    re.compile(r"visa sponsorship (is )?not (available|provided|offered)", re.I),
    re.compile(r"cannot (provide|offer|support|sponsor) (visa|sponsorship)", re.I),
    re.compile(r"must already (have|hold|possess).{0,40}(work permit|residence permit|visa|residency)", re.I),
    re.compile(r"must (live|reside|be (based|located|domiciled)|be a resident) (in|within)", re.I),
    re.compile(r"only (for )?(u\.?s|us|uk|eu|canadian|australian).{0,15}(citizens|residents|nationals)", re.I),
]

# ---------------------------------------------------------------------------
# Utility functions — identical to JS
# ---------------------------------------------------------------------------


def strip_html(html: str) -> str:
    """Remove HTML tags, decode entities, and return clean readable text."""
    if not html:
        return ""
    text = str(html)
    # Remove CDATA markers
    text = re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Use Python's built-in HTML entity decoder
    text = html_mod.unescape(text)
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_date(v) -> datetime | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        ts = v
        if ts < 1e12:
            ts *= 1000
        try:
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        except Exception:
            return None
    s = str(v).strip()
    if re.match(r"^\d{10}$", s):
        try:
            return datetime.fromtimestamp(int(s), tz=timezone.utc)
        except Exception:
            return None
    if re.match(r"^\d{13}$", s):
        try:
            return datetime.fromtimestamp(int(s) / 1000, tz=timezone.utc)
        except Exception:
            return None
    try:
        # Python's fromisoformat handles most ISO formats
        s2 = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s2)
    except Exception:
        pass
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        pass
    try:
        return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return None


def _libya_today() -> str:
    """Today's date in Libya (UTC+2) — the day the user actually reads."""
    from notifier import now_libya
    return now_libya().strftime("%Y-%m-%d")


def age_hours(dt: datetime | None) -> float:
    if dt is None:
        return float("inf")
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 3600


def get_freshness(posted) -> dict:
    d = normalize_date(posted)
    age = age_hours(d)
    if d is None or age == float("inf"):
        return {"label": "date unknown", "is_fresh": False, "is_old": True}
    if age < 1:
        m = max(1, round(age * 60))
        return {"label": f"{m} min ago", "is_fresh": True, "is_old": False}
    if age < 24:
        h = max(1, round(age))
        return {"label": f"{h} hour{'s' if h > 1 else ''} ago", "is_fresh": True, "is_old": False}
    if age < 48:
        return {"label": "1 day ago", "is_fresh": False, "is_old": False}
    days = int(age / 24)
    if days <= 6:
        return {"label": f"{days} day{'s' if days > 1 else ''} ago", "is_fresh": False, "is_old": False}
    return {"label": f"{days} days ago (old)", "is_fresh": False, "is_old": True}


def is_paid_platform(source: str) -> bool:
    """Check if the source platform requires fees to apply."""
    source_lower = (source or "").lower()
    return any(platform in source_lower for platform in PAID_PLATFORMS)


def phrase_label(re_obj, text: str = "") -> str:
    """Readable name for a matched pattern — the actual term that matched.

    Bucket phrases are alternations of 10-20 synonyms ("arabic translator
    translation interpreter linguist editor proofreader ..."), so returning the
    raw pattern dumped the whole list into user-facing messages. Prefer the
    concrete substring that hit; fall back to a trimmed pattern.
    """
    if text:
        m = re_obj.search(text)
        if m:
            hit = (m.group(0) or "").strip()
            if 2 <= len(hit) <= 60:
                return re.sub(r"\s+", " ", hit)
    src = re_obj.pattern
    src = re.sub(r"\[sz\]", "s", src)
    src = re.sub(r"\\b|\\B|^|\$", "", src)
    src = src.replace("\\s", " ")
    # Drop bounded-gap quantifiers (".{0,40}", ".{0,30}") entirely BEFORE the
    # punctuation sweep below. That sweep removed "{}" but left the leading dot
    # and digits, so user-facing text read "specialist .{0,40}arabic (title)".
    src = re.sub(r"\.\{\d+(,\d+)?\}", " ", src)
    src = re.sub(r"\{\d+(,\d+)?\}", " ", src)
    src = re.sub(r"[()|?*+{}\[\]]", " ", src)
    parts = [p.strip() for p in src.split() if p.strip()]
    return " ".join(parts[:4])


# Bucket weight multipliers — Arabic translation is the candidate's prime skill.
_BUCKET_WEIGHT = {
    "Arabic Translation": 1.0,
    "Translation (any pair)": 0.95,
    "Editing & Proofreading": 0.90,
    "AI Data & Annotation": 0.85,
    "ESL": 0.90,
    "Admin": 0.75,
    "AI Data": 0.85,
}

# Categories where an actual translation/localization/interpreting role can be
# a STRONG match (Arabic or any language pair).
CORE_CATEGORIES = frozenset({
    "Arabic Translation",
    "Translation (any pair)",
})

# Everything else is NEVER a STRONG match, even when it mentions Arabic:
# ESL, editing/proofreading, admin/VA, AI-data/annotation and AI trainers.
SECONDARY_CATEGORIES = frozenset({
    "ESL", "Editing & Proofreading", "Admin",
    "AI Data & Annotation", "AI Data",
})

# Cap for anything that is not a core translation role (strictly below the 50%
# Fresh floor, so it can never be emailed as a STRONG match).
SECONDARY_MATCH_CAP = 45

# STRONG tier is reserved for jobs whose language is genuinely Arabic. A
# generic "Translator" posting — English-only snippet, Chinese/Malay/other
# pair that a truncated description hides — is NOT a match to email at 100%
# (Zeekr Chinese/Malay role scored 100 through an English-only snippet). Any
# core translation role WITHOUT an explicit Arabic signal is capped to REVIEW.
NON_ARABIC_CAP = 45

# The actual job-content signals that make a listing translation work. A posting
# can hit the "Arabic Translation" bucket via "Arabic speaker + data entry" or
# "Arabic AI trainer" without being a translation role — that is NOT a STRONG
# match. Genuine translation/localization/interpreting work must appear.
# Bare "translate" is excluded on purpose: "help translate complex technical
# concepts" is marketing-speak, not a translation requirement. Explicit
# English<->Arabic pair mentions are NOT enough by themselves either — a
# "Content Moderator - Arabic/English" or "VA - Arabic/English" is bilingual
# work but still not a translation role, so it must stay REVIEW.
CORE_LANGUAGE_ROLES = re.compile(
    r"\b(translator|translation specialist|staff translator|freelance translator|senior translator)\b"
    r"|\btranslation\b|\binterpreter\b|\binterpretation\b|\binterpreting\b"
    r"|\b(?:locali[sz]ation|locali[sz]e|locali[sz]ed|localiz(?:e|ed|ation))\b"
    r"|\bl10n\b|\bi18n\b|\blinguist\b"
    r"|\b(?:terminolog(?:y|ist)|translation memory|post-?edit(?:ing|or)?|mtpe|localization kit|style guide|glossary)\b"
    r"|\bsubtitl(?:ing|e|ed|er)?\b|\bcaption(?:ing|s)?\b|\bvoice-?over\b"
    r"|\blanguage pair\b",
    re.I,
)

# Trusted companies that are strongly Arabic-translation / language-service relevant.
TRUSTED_COMPANIES = frozenset({
    "transperfect", "lionbridge", "rws", "keywords studios", "welocalize",
    "oneforma", "appen", "telus international", "centific", "scale ai",
    "surge ai", "auraone", "proz", "translatorscafe", "smartcat", "gengo",
    "unbabel", "lilt", "phrase", "lokalise", "smartling", "tarjama",
    "tamatem games", "tamatem", "careem", "mawdoo3", "nagwa", "abwaab",
    "noon academy", "edraak", "almentor", "baims", "cambly", "preply",
    "italki", "lingoda", "busuu", "babbel", "enrolled", "vipkid", "engoo",
    "novakid", "tutorabc", "magic ears", "qkids",
})


def _bucket_best(bucket: dict, t: str, d: str) -> tuple[float, list[str]]:
    """Compute the best single-phrase hit for a bucket (title+desc bonus)."""
    best = 0.0
    why: list[str] = []
    for pattern, w in bucket["phrases"]:
        in_title = bool(pattern.search(t))
        in_desc = bool(pattern.search(d))
        if not (in_title or in_desc):
            continue
        if in_title and in_desc:
            val = w * 2.2
        elif in_title:
            val = w * 1.6
        else:
            val = min(w * 0.8, w)
        if val > best:
            best = val
            where = "title+description" if (in_title and in_desc) else ("title" if in_title else "description")
            why = [f"{phrase_label(pattern, t if in_title else d)} ({where})"]
    return min(best, 95.0), why


def get_match_score(title: str, desc: str) -> dict:
    """Baseline + tiered scoring. Remote/worldwide listings never zero out.

    75-100 = STRONG CV match, 50-74 = GOOD, below 50 = REVIEW (still shown).
    """
    t = (title or "").lower()
    # Descriptions arrive as raw HTML from most feeds. Tag and attribute text
    # ("<div class=\"editor-listitem\">") matched keyword patterns and scored
    # unrelated roles (e.g. an Engineering Manager hitting "translator"), so
    # match against readable text only.
    d = (desc or "")
    d = strip_html(d).lower() if ("<" in d or "&" in d) else d.lower()
    text = t + " " + d

    # 1) Baseline — NO free points for "remote" alone.
    #    Remote is only a bonus AFTER Arabic/translation keywords hit.
    base = 0.0
    why: list[str] = []

    # 2) Best keyword bucket, scaled by the candidate's skill priority
    best = 0.0
    best_cat = "Other"
    best_why: list[str] = []
    for bucket in MATCH_BUCKETS:
        b_score, b_why = _bucket_best(bucket, t, d)
        b_score = b_score * _BUCKET_WEIGHT.get(bucket["name"], 0.7)
        if b_score > best:
            best = b_score
            best_cat = bucket["name"]
            best_why = b_why

    total = base + best
    why_final = list(dict.fromkeys(why + best_why))[:6]
    # Remote/worldwide is only a BONUS when Arabic/translation already matched
    if best > 0 and REMOTE_MARKER.search(text):
        total += 15.0
        why_final.append("remote/worldwide (bonus)")
    elif best > 0 and re.search(r"\bworldwide\b|\binternational(?: listing)?\b|\bopen to all\b|\bglobal\b", text):
        total += 10.0
        why_final.append("international listing (bonus)")
    if best_cat != "Other":
        why_final.append(f"matches {best_cat} profile")

    # 2b) STRONG-tier gate — only actual translation/localization/interpreting
    #     work may reach STRONG. Secondary categories are REVIEW-only even when
    #     Arabic is present ("Arabic Data Entry", "Arabic AI Trainer", ESL...).
    #     A core category is also capped unless the role really is translation
    #     work — "Data Entry - Arabic Speaker" scores the Arabic bucket but is
    #     not a translation role.
    if best_cat in SECONDARY_CATEGORIES:
        total = min(total, SECONDARY_MATCH_CAP)
        why_final.append("non-core category (secondary, review only)")
    elif best_cat in CORE_CATEGORIES and not CORE_LANGUAGE_ROLES.search(text):
        total = min(total, SECONDARY_MATCH_CAP)
        why_final.append("Arabic/language signal but not a translation role (review only)")
    # 2c) STRONG = genuinely ARABIC translation work only. A core translation
    #     role without an explicit Arabic signal (English-only snippet, hidden
    #     Chinese/Malay pair, truncated description) is capped to REVIEW — it is
    #     never emailed as a 100% match.
    elif best_cat in CORE_CATEGORIES and not HAS_ARABIC.search(text):
        total = min(total, NON_ARABIC_CAP)
        why_final.append("translation role without Arabic (review only)")
    # 2d) A posting that REQUIRES a non-Arabic, non-English language
    #     (Dari/Pashto, Chinese, French…) is not an Arabic↔English job even when
    #     the word "Arabic" appears — "Arabic translator/interpreter tour guide,
    #     Arabic to Dari/Pashto, drive a car" (Let's tour Afghanistan, 09-22).
    #     Without the required English it is REVIEW, never STRONG.
    elif best_cat in CORE_CATEGORIES and WRONG_LANGUAGE.search(text) and not re.search(r"\benglish\b", text):
        total = min(total, SECONDARY_MATCH_CAP)
        why_final.append("requires non-English language, no English (review only)")

    # 3) HARD DROP: negative keywords in title = instant 0
    if any(kw in t for kw in NEGATIVE_KEYWORDS):
        return {"score": 0, "category": "Other", "why": ["hard drop: non-target role keyword in title"]}
    if SENIOR_PENALTY.search(t):
        return {"score": 0, "category": "Other", "why": ["hard drop: senior/leadership title"]}
    if NON_ROLE_ADMIN.search(t):
        return {"score": 0, "category": "Other", "why": ["hard drop: admin/platform role"]}
    if ENGINEER_TITLE.search(t) and not ENGINEER_ALLOW.search(t):
        return {"score": 0, "category": "Other", "why": ["hard drop: engineering title"]}
    if WRONG_LANGUAGE.search(text) and not HAS_ARABIC.search(text):
        return {"score": 0, "category": "Other", "why": ["hard drop: wrong language, no Arabic"]}

    total = max(0, min(100, total))
    # HARD RULE: The job must match at least ONE of our target buckets.
    # If no bucket matched at all → not a translation/language/content role.
    # But ANY bucket match is enough — including Translation (any pair), Editing, AI Data.
    if best <= 0:
        total = 0
        best_cat = "Other"
        why_final = ["hard drop: no translation/language/content signal in job"]
    total = round(total / 5) * 5
    return {"score": total, "category": best_cat, "why": why_final[:8]}


# Company-aware scoring tiers — jobs at translation/language companies get
# base boosts even without keyword hits, because these companies hire
# Arabic speakers for PM, QA, account, data-annotation, and support roles
# that the keyword scanner can't see.
#
# TIER 1 (+50): Core LSPs that LIVE on Arabic translation — every role here
#   likely needs Arabic speakers (project managers, QA, terminologists, etc.)
# TIER 2 (+35): Language AI / data annotation — hire Arabic for training data
# TIER 3 (+25): MENA content / EdTech — Arabic is the product language
# TIER 4 (+15): Remote-first that periodically hire translators
TRANSLATION_COMPANY_TIERS = {
    # TIER 1 — Core LSPs (+50)
    50: frozenset({
        "transperfect", "lionbridge", "rws", "welocalize",
        "keywords studios", "smartling", "lokalise", "phrase",
        "unbabel", "lilt", "acclaro", "andovar", "straker",
        "gengo", "translated", "smartcat", "alconost", "blend",
        "cactus", "editage", "enago", "wordvice", "scribbr",
        "scribendi", "papertrue", "proofreadnow",
        "one hour translation", "textmaster", "flitto",
    }),
    # TIER 2 — AI Data / Linguist Marketplaces (+35)
    35: frozenset({
        "scale ai", "outlier", "surge ai", "micro1", "prolific",
        "telus international", "toloka", "appen", "centific",
        "labelbox", "invisible", "turing", "mercor",
    }),
    # TIER 3 — MENA Content / EdTech (+25)
    25: frozenset({
        "nagwa", "abwaab", "noon academy", "edraak", "almentor",
        "baims", "tamatem", "tamatem games", "mawdoo3", "tarjama",
        "saudisoft", "future group", "anghami",
    }),
    # TIER 4 — Remote-first that hire translators (+15)
    15: frozenset({
        "deel", "toptal",
    }),
}

# Roles that are HIGH relevance at translation companies — even if the
# title doesn't contain "arabic" or "translator", these roles at an LSP
# almost always involve Arabic work.
HIGH_RELEVANCE_ROLES = re.compile(
    r"(project\s+manager|locali[sz]ation|terminolog|qa\s+(reviewer|lead|manager)"
    r"|linguist|bilingual|multilingual|content|editor|proofread|copywriter"
    r"|interpreter|transcri|subtitl|caption|voice|speech|nlp|ml\s+data"
    r"|data\s+(annotation|labeling|labeler|entry|collector|validator)"
    r"|ai\s+(trainer|training|evaluation|quality)|prompt\s+(engineer|evaluator)"
    r"|language\s+(specialist|expert|consultant|coordinator|lead)"
    r"|academic|thesis|research|translation|localization|interpret"
    r"|virtual\s+assistant|administrative|desk|support|customer\s+success"
    r"|account\s+(manager|executive|coordinator))",
    re.I,
)


def apply_company_bonus(job: dict, base_score: int | None = None,
                        has_signal: bool | None = None) -> dict:
    """Company-aware scoring boost for translation/language employers.

    Tier-based: +50 core LSPs, +35 AI data, +25 MENA, +15 remote-first, plus
    +15 when the role title is high-relevance (PM, linguist, QA, content...).

    Returns {"score", "company_boost", "company_tier", "high_relevance"} so the
    caller can carry the boost into later gates. A company-only match (no
    keyword signal) is allowed only when the title is high-relevance — otherwise
    every unrelated role at a tier company would be treated as a match.
    """
    company = str(job.get("company") or "").lower().strip()
    title = str(job.get("title") or "").lower().strip()
    cur = int(job.get("score") or 0) if base_score is None else int(base_score)
    if has_signal is None:
        has_signal = cur > 0
    high_rel = bool(HIGH_RELEVANCE_ROLES.search(title))

    tier_boost = 0
    for boost, companies in TRANSLATION_COMPANY_TIERS.items():
        if any(key in company or company in key for key in companies):
            tier_boost = boost
            break

    info = {"score": cur, "company_boost": 0, "company_tier": tier_boost,
            "high_relevance": high_rel}
    if tier_boost == 0:
        return info
    # Company-only match (no keyword signal) requires a high-relevance title.
    if not has_signal and not high_rel:
        return info
    role_boost = 15 if high_rel else 0
    info["company_boost"] = tier_boost + role_boost
    info["score"] = min(100, cur + tier_boost + role_boost)
    return info


def score_job(job: dict) -> dict:
    """Single scoring path shared by the fresh and old-but-verified branches.

    Runs keyword scoring, learning adjustment, company bonus and company
    pattern priority, and returns the final score/category/why plus the
    company-boost metadata used by the no-signal and quality gates. Using one
    helper keeps the two branches from diverging (the old branch used to
    re-score without the company bonus, silently dropping every boosted job).
    """
    base = get_match_score(job.get("title", ""), job.get("description", ""))
    score = base.get("score", 0)
    category = base.get("category", "Other")
    why = list(base.get("why", []))
    # A real keyword signal is a bucket hit — not merely a nonzero score, since
    # the learning adjustment below can lift an unrelated job above zero.
    has_signal = base.get("score", 0) > 0 and base.get("category") != "Other"

    # A title that the keyword matcher hard-dropped (non-target role, engineer,
    # customer success, leadership…) must NOT be revived by the translation-
    # company bonus. An unrelated role at an LSP stays a hard miss. The wrong-
    # language rule is checked against the full text exactly like get_match_score
    # (an Arabic posting that mentions French in passing still passes).
    t = (job.get("title") or "").lower()
    t_text = f"{t} {str(job.get('description') or '').lower()}"
    hard_dropped = (
        any(kw in t for kw in NEGATIVE_KEYWORDS)
        or SENIOR_PENALTY.search(t)
        or NON_ROLE_ADMIN.search(t)
        or (ENGINEER_TITLE.search(t) and not ENGINEER_ALLOW.search(t))
        or (WRONG_LANGUAGE.search(t_text) and not HAS_ARABIC.search(t_text))
    )
    if hard_dropped and base.get("score", 0) <= 0:
        return {
            "score": 0,
            "category": "Other",
            "why": base.get("why") or ["non-target role (hard drop)"],
            "company_boost": 0,
            "high_relevance": False,
        }

    try:
        adjusted = adjust_scoring_based_on_learning({
            **job,
            "score": score,
            "category": category,
            "ai_overall_score": score,
        })
        if adjusted and adjusted != score:
            score = adjusted
    except Exception:
        pass

    bonus = apply_company_bonus({**job, "score": score}, base_score=score,
                                has_signal=has_signal)
    score = bonus["score"]
    if bonus["company_boost"] > 0:
        why.append("trusted translation/language employer (company boost)")
        if category == "Other":
            category = "Language Services (company)"

    try:
        company_priority = get_company_priority(job.get("company", ""))
        if company_priority:
            score = max(0, min(100, score + company_priority))
    except Exception:
        pass

    # Strictest STRONG gate is enforced on the FINAL score too, so neither the
    # company bonus nor company-priority can push a non-translation role (e.g.
    # "Arabic Data Entry" at an LSP, "Arabic AI Trainer") into STRONG.
    role_text = f"{str(job.get('title') or '').lower()} {str(job.get('description') or '').lower()}"
    if category not in CORE_CATEGORIES or not CORE_LANGUAGE_ROLES.search(role_text):
        score = max(0, min(score, SECONDARY_MATCH_CAP))

    return {
        "score": int(max(0, min(100, score))),
        "category": category,
        "why": why,
        "company_boost": bonus["company_boost"],
        "high_relevance": bonus["high_relevance"],
    }


def extract_salary(text: str) -> str:
    s = (text or "") + " "
    pat = re.compile(
        r"(?:USD|US\$|\$|\u20ac|\u00a3|GBP|CAD|AUD|EUR)\s*\d{2,3}(?:[,.]\d{3})?\s*k?\s*"
        r"(?:[\u2013\u2014\u2012to]+\s*(?:USD|US\$|\$|\u20ac|\u00a3|GBP|CAD|AUD|EUR)?\s*\d{2,3}(?:[,.]\d{3})?\s*k?)?"
        r"(?:\s*(?:per|a|p\.?a\.?|\/)\s*(?:year|yr|annum|month|mo|hour|hr|h))?",
        re.I,
    )
    m = pat.search(s)
    return re.sub(r"\s+", " ", m.group()).strip() if m else ""


def is_open_worldwide(location: str, desc: str) -> bool:
    loc = (location or "").lower()
    text = (desc or "").lower() + " " + loc
    if COUNTRY_LOCKED_LOC.search(loc) or COUNTRY_LOCKED_LOC.search(text):
        return False
    if _is_us_locked(location):
        return False
    if _ONSITE_ANCHOR.search(text):
        return False
    
    # Check description for location restriction warnings FIRST
    # Many jobs have "Location Restriction: United States only" in description
    # or "This position is only available in the US" patterns
    RESTRICTION_PATTERNS = [
        re.compile(r"location\s+restriction", re.I),
        re.compile(r"only\s+available\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"position\s+is\s+(only|restricted)\s+(to|for)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"eligible\s+(for\s+only|only\s+for|if\s+you\s+are\s+in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"this\s+job\s+is\s+(only|restricted)\s+to", re.I),
        re.compile(r"must\s+be\s+(located\s+in|based\s+in|in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"applicants\s+must\s+be\s+(located|based)\s+in", re.I),
        re.compile(r"this\s+position\s+requires\s+(you\s+to\s+be|residence)\s+in", re.I),
        re.compile(r"candidates\s+must\s+(be|remain)\s+(located|based)\s+in", re.I),
        re.compile(r"only\s+considering\s+candidates\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
        re.compile(r"only\s+hiring\s+(in|for)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
    ]
    for pattern in RESTRICTION_PATTERNS:
        if pattern.search(text):
            return False
    
    # Hard blockers — checked against full text (location + description)
    HARD_BLOCKERS = [
        re.compile(r"residents? only", re.I),
        re.compile(r"must be (a |an )?(u\.?s|united states|uk|eu|canadian|australian|german|french|british|european) (citizen|resident|national)", re.I),
        re.compile(r"(u\.?s|us|uk|eu|canadian|australian) (citizen|permanent resident|national)\b", re.I),
        re.compile(r"authorized to work in (the |)(u\.?s|us|united states|uk|canada|australia|eu)", re.I),
        re.compile(r"(work authorization|work authorisation|work permit required) in (the |)(u\.?s|us|united states|uk|canada|australia)", re.I),
        re.compile(r"(no sponsoring|no sponsorship)", re.I),
        re.compile(r"(cannot|can't|unable to|do not|does not|will not|won't|no|without|not (available|provided|offered)).{0,20}(visa )?sponsorship", re.I),
        re.compile(r"visa sponsorship (is )?not (available|provided|offered)", re.I),
        re.compile(r"cannot (provide|offer|support|sponsor) (visa|sponsorship)", re.I),
        re.compile(r"must already (have|hold|possess).{0,40}(work permit|residence permit|visa|residency)", re.I),
        re.compile(r"must (live|reside|be (based|located|domiciled)|be a resident) (in|within) (the |)(u\.?s|us|united states|uk|canada|australia)", re.I),
        re.compile(r"only (for )?(u\.?s|us|uk|eu|canadian|australian).{0,15}(citizens|residents|nationals)", re.I),
        # Location Restriction field
        re.compile(r"location\s+restriction\s*:?\s*(u\.?s|united\s+states|uk|eu|canadian|australian)", re.I),
        # US-anchored hiring language — even when the card says "Remote":
        # "US-based candidates", "pay ranges apply to US-based candidates"
        re.compile(r"(u\.?s\.?|us|united states)\s*[- ]?based\s+(candidates?|applicants?|positions?|roles?|employees?)", re.I),
        re.compile(r"pay (rates?|ranges?|offers?) apply to (u\.?s\.?|us|united states)[\s-]*based", re.I),
        re.compile(r"only open to (u\.?s\.?|us|united states)", re.I),
    ]
    for blocker in HARD_BLOCKERS:
        if blocker.search(text):
            return False
    # Soft blockers — only check LOCATION field (not description)
    SOFT_LOCATION_BLOCKERS = [
        re.compile(r"onsite only|on-site only|on site only", re.I),
        re.compile(r"\bhybrid\b", re.I),
        re.compile(r"in.?office|office.first|office based|on.?site\b", re.I),
        re.compile(r"office.{0,25}(only|required)\.?( no remote)?", re.I),
    ]
    for blocker in SOFT_LOCATION_BLOCKERS:
        if blocker.search(loc):
            return False
    if not loc:
        return True

    # Region/worldwide wording ("worldwide", "europe", "anywhere", "remote").
    # Matched against the body so the bare word "remote" no longer grants a pass
    # to "Remote — Spain".
    body = _location_body(loc)
    if ALLOWED_LOCATION_RE.search(body):
        return True

    # MENA-country remotes are intentionally surfaced (Arabic-market demand).
    if MENA_RE.search(body):
        return True

    # Non-geographic wording ("Multiple locations", "Fully remote").
    if GENERIC_LOCATION_RE.search(body):
        return True

    # If "Remote" is in the ORIGINAL location field (before body stripping),
    # the job IS remote — the country/city after it is just a timezone hint
    # ("Remote — Berlin, Germany" = work from anywhere, employer prefers CET).
    # Only block truly residency-locked countries (US, CA, AU, UK, etc.) and
    # hard blockers already caught above. Country names like "Germany", "Spain",
    # "India" after "Remote" are NOT residency requirements.
    if _REMOTE_PREFIX_RE.search(loc):
        # Remote job with a country hint — only block if it's in the hard-blocked list
        if BLOCKED_COUNTRY_RE.search(body) or _is_us_locked(body):
            return False
        return True

    # Non-remote: bare location field with a country name = country-locked.
    # BUT: translation companies (TransPerfect, Lionbridge, etc.) list jobs with
    # country/city locations even when they're remote-friendly. If the company is
    # in our translation tier list, allow through — the company boost already
    # signals this is a relevant employer.
    if COUNTRY_RE.search(body) or BLOCKED_COUNTRY_RE.search(body) or _is_us_locked(body):
        return False

    # Leftover is a city with no country ("Remote | Athens", "Remote — Baltimore").
    return True


def is_open_worldwide_for_company(location: str, desc: str, company: str) -> bool:
    """Location filter with translation company bypass.

    Translation companies list jobs with country/city locations even when
    they're remote-friendly. If the company is in our tier list, skip the
    country-name check — the company boost already handles relevance.
    """
    company_lower = str(company or "").lower().strip()
    # Check if company is in any translation tier
    is_translation_company = False
    for companies in TRANSLATION_COMPANY_TIERS.values():
        if any(key in company_lower or company_lower in key for key in companies):
            is_translation_company = True
            break

    if is_translation_company:
        # For translation companies, only block on HARD blockers
        # (US/CA/AU/UK residency, visa sponsorship, etc.)
        # Skip the COUNTRY_RE check that blocks "Berlin, Germany" etc.
        loc = (location or "").lower()
        text = (desc or "").lower() + " " + loc
        if COUNTRY_LOCKED_LOC.search(loc) or COUNTRY_LOCKED_LOC.search(text):
            return False
        if _is_us_locked(location):
            return False
        if _ONSITE_ANCHOR.search(text):
            return False
        # Check description for location restriction warnings
        RESTRICTION_PATTERNS = [
            re.compile(r"location\s+restriction", re.I),
            re.compile(r"only\s+available\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
            re.compile(r"position\s+is\s+(only|restricted)\s+(to|for)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
            re.compile(r"eligible\s+(for\s+only|only\s+for|if\s+you\s+are\s+in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
            re.compile(r"must\s+be\s+(located\s+in|based\s+in|in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
            re.compile(r"applicants\s+must\s+be\s+(located|based)\s+in", re.I),
            re.compile(r"this\s+position\s+requires\s+(you\s+to\s+be|residence)\s+in", re.I),
            re.compile(r"candidates\s+must\s+(be|remain)\s+(located|based)\s+in", re.I),
        ]
        for pattern in RESTRICTION_PATTERNS:
            if pattern.search(text):
                return False
        # Hard blockers — visa, citizenship, sponsorship
        HARD_BLOCKERS = [
            re.compile(r"residents? only", re.I),
            re.compile(r"must be (a |an )?(u\.?s|united states|uk|eu|canadian|australian|german|french|british|european) (citizen|resident|national)", re.I),
            re.compile(r"(u\.?s|us|uk|eu|canadian|australian) (citizen|permanent resident|national)\b", re.I),
            re.compile(r"authorized to work in (the |)(u\.?s|us|united states|uk|canada|australia|eu)", re.I),
            re.compile(r"(no sponsoring|no sponsorship)", re.I),
            re.compile(r"(cannot|can't|unable to|do not|does not|will not|won't|no|without|not (available|provided|offered)).{0,20}(visa )?sponsorship", re.I),
            re.compile(r"visa sponsorship (is )?not (available|provided|offered)", re.I),
            re.compile(r"must already (have|hold|possess).{0,40}(work permit|residence permit|visa|residency)", re.I),
            re.compile(r"must (live|reside|be (based|located|domiciled)|be a resident) (in|within) (the |)(u\.?s|us|united states|uk|canada|australia)", re.I),
            re.compile(r"only (for )?(u\.?s|us|uk|eu|canadian|australian).{0,15}(citizens|residents|nationals)", re.I),
            # US-anchored hiring language — even when the card says "Remote":
            # "US-based candidates", "pay ranges apply to US-based candidates"
            re.compile(r"(u\.?s\.?|us|united states)\s*[- ]?based\s+(candidates?|applicants?|positions?|roles?|employees?)", re.I),
            re.compile(r"pay (rates?|ranges?|offers?) apply to (u\.?s\.?|us|united states)[\s-]*based", re.I),
            re.compile(r"only open to (u\.?s\.?|us|united states)", re.I),
        ]
        for blocker in HARD_BLOCKERS:
            if blocker.search(text):
                return False
        # Soft blockers — onsite/hybrid in location field
        SOFT_LOCATION_BLOCKERS = [
            re.compile(r"onsite only|on-site only|on site only", re.I),
            re.compile(r"\bhybrid\b", re.I),
            re.compile(r"in.?office|office.first|office based|on.?site\b", re.I),
        ]
        for blocker in SOFT_LOCATION_BLOCKERS:
            if blocker.search(loc):
                return False
        # Translation company + no hard blockers = ALLOW
        return True

    # Non-translation company: use standard filter
    return is_open_worldwide(location, desc)


def matches_positive(title: str, desc: str) -> bool:
    t = (title or "").lower() + " " + (desc or "").lower()
    return any(
        pattern.search(t)
        for bucket in MATCH_BUCKETS
        for pattern, _ in bucket["phrases"]
    )


def matches_negative(title: str, desc: str) -> bool:
    # Only check title for negative keywords — descriptions often mention
    # engineers/developers in passing ("collaborate with engineering team")
    # which shouldn't block a relevant content/translation role
    t = (title or "").lower()
    return any(kw in t for kw in NEGATIVE_KEYWORDS)


def is_stub_listing(job: dict) -> bool:
    """True for signup/portal/quote pages and invented one-line 'jobs', not real listings."""
    title = strip_html(job.get("title") or "")
    url = job.get("url") or ""
    desc = job.get("description") or ""
    if "<![CDATA[" in (job.get("title") or ""):
        return True
    if STUB_TITLE.search(title):
        return True
    if STUB_URL.search(url):
        return True
    if len(desc.strip()) < 60 and re.search(r"(platform|sign up|portal|get started)", (title + " " + desc), re.I):
        return True
    return False


def is_in_person_gig(job: dict) -> bool:
    blob = f"{job.get('title') or ''} {job.get('description') or ''} {job.get('location') or ''}"
    return bool(IN_PERSON_GIG.search(blob))


def location_ai_fail(job: dict) -> bool:
    """Hard reject when Ollama (or structured scoring) says location logistics FAIL."""
    verdict = str(job.get("ai_location_verdict") or "").strip().upper()
    if verdict == "FAIL":
        return True
    scoring = job.get("ai_scoring") or {}
    loc = scoring.get("location_logistics") or {}
    if str(loc.get("verdict") or "").strip().upper() == "FAIL":
        return True
    return False


def ai_poor_fit(job: dict) -> bool:
    """True when the AI explicitly rejects the role for this candidate.

    The Groq verdict is now a gate, not a footnote: a posting scored "Poor Fit"
    or "Weak Fit" (below 50/100) is taken out of the digest so an unrelated
    role cannot ride a keyword hit into STRONG MATCH. Jobs that were not AI-
    analyzed (no key / over cap) are never rejected here.
    """
    verdict = str(job.get("ai_verdict") or "").lower()
    if not verdict:
        return False
    try:
        ai_score = int(job.get("ai_overall_score") or 0)
    except (TypeError, ValueError):
        return False
    return ("poor" in verdict or "weak" in verdict) and ai_score < 50


def has_residency_blocker(job: dict) -> bool:
    """True when the posting itself demands citizenship/residency/work permit.

    Such roles are unappliable from Libya without sponsorship, so they are a hard
    drop — not a flag. Country-locked *locations* stay flags; this is about
    explicit eligibility wording in the posting text.
    """
    text = f"{job.get('title', '')} {job.get('location', '')} {job.get('description', '')}"
    return any(p.search(text) for p in RESIDENCY_BLOCKERS)


def drop_unqualified_matches(jobs: list[dict], reason_counts: dict | None = None) -> list[dict]:
    """Final quality gate before notify / cover letters.

    Hard drops: stub listings, AI-confirmed location failures, postings that
    require citizenship/residency/work authorisation (unappliable from Libya),
    and country-locked locations.

    Country-locked postings used to be kept with a "country-locked location"
    flag, so a role pinned to Spain/Ohio/Mexico still arrived as a 100% STRONG
    MATCH the user could never take. They are dropped here; the Excel "All Jobs"
    sheet still lists every scanned posting.
    """
    kept = []
    counts = reason_counts if reason_counts is not None else {}
    for job in jobs:
        if job.get("ai_reject"):
            counts["ai_poor_fit"] = counts.get("ai_poor_fit", 0) + 1
            continue
        if is_stub_listing(job):
            counts["stub"] = counts.get("stub", 0) + 1
            continue
        if location_ai_fail(job):
            counts["ai_location_fail"] = counts.get("ai_location_fail", 0) + 1
            continue
        if has_residency_blocker(job):
            counts["residency_blocker"] = counts.get("residency_blocker", 0) + 1
            continue
        if not is_open_worldwide_for_company(
            job.get("location", ""), job.get("description", ""), job.get("company", "")
        ):
            counts["country_locked"] = counts.get("country_locked", 0) + 1
            continue
        flags = list(job.get("flags") or [])
        if is_in_person_gig(job):
            if "in-person/onsite" not in flags:
                flags.append("in-person/onsite")
        if flags:
            job["flags"] = flags
        kept.append(job)
    return kept


# ---------------------------------------------------------------------------
# Generic HTML job page scraper
# ---------------------------------------------------------------------------

def _parse_generic_html_jobs(html: str, source: str, base_url: str) -> list[dict]:
    """Generic scraper that tries common HTML patterns for job listings."""
    jobs = []
    # Try common job card patterns
    # Pattern 1: links with /jobs/ or /job/ in href
    job_links = re.findall(
        r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/position/|/opening/|/vacancy/|/listing/)[^"\']*)["\'][^>]*>([^<]+)</a>',
        html, re.I
    )
    for href, title in job_links:
        title = strip_html(title).strip()
        if not title or len(title) < 5:
            continue
        url = href if href.startswith("http") else base_url.rstrip("/") + href
        jobs.append({
            "title": title,
            "company": source.title(),
            "url": url,
            "location": "Remote",
            "posted": "",
            "description": "",
            "source": source,
        })

    # Pattern 2: data attributes or JSON-LD
    json_ld = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', html, re.I)
    for block in json_ld:
        try:
            data = json.loads(block)
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                jobs.append({
                    "title": data.get("name", ""),
                    "company": (data.get("hiringOrganization") or {}).get("name", source.title()),
                    "url": data.get("url", ""),
                    "location": (data.get("jobLocation") or {}).get("address", {}).get("addressLocality", "Remote"),
                    "posted": data.get("datePosted", ""),
                    "description": strip_html(data.get("description", "")),
                    "source": source,
                })
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        jobs.append({
                            "title": item.get("name", ""),
                            "company": (item.get("hiringOrganization") or {}).get("name", source.title()),
                            "url": item.get("url", ""),
                            "location": (item.get("jobLocation") or {}).get("address", {}).get("addressLocality", "Remote"),
                            "posted": item.get("datePosted", ""),
                            "description": strip_html(item.get("description", "")),
                            "source": source,
                        })
        except Exception:
            pass

    return jobs[:200]


# ---------------------------------------------------------------------------
# Job source fetchers — async with aiohttp
# ---------------------------------------------------------------------------


async def fetch_greenhouse(session: aiohttp.ClientSession, company_name: str, slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                print(f"  {company_name}: HTTP {resp.status}")
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in (data.get("jobs") or [])[:150]:
                loc = j.get("location", {})
                loc_name = loc.get("name", "") if isinstance(loc, dict) else str(loc)
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company_name,
                    "url": j.get("absolute_url") or j.get("url", ""),
                    "location": loc_name,
                    "posted": j.get("updated_at") or j.get("created_at", ""),
                    "description": strip_html(j.get("content") or j.get("content_html", "")),
                    "salary": "",
                    "source": "greenhouse",
                })
            return jobs
    except Exception as e:
        print(f"  {company_name}: {e}")
        return []


async def fetch_lever(session: aiohttp.ClientSession, company_name: str, slug: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                print(f"  {company_name}: HTTP {resp.status}")
                return []
            data = await resp.json(content_type=None)
            arr = data if isinstance(data, list) else []
            return [
                {
                    "title": j.get("text", ""),
                    "company": company_name,
                    "url": j.get("hostedUrl") or j.get("url", ""),
                    "location": (j.get("categories") or {}).get("location", ""),
                    "posted": j.get("createdAt") or j.get("postedAt", ""),
                    "description": strip_html(j.get("descriptionPlain") or j.get("description", "")),
                    "salary": "",
                    "source": "lever",
                }
                for j in arr
            ]
    except Exception as e:
        print(f"  {company_name}: {e}")
        return []


async def fetch_remotive(session: aiohttp.ClientSession) -> list[dict]:
    jobs = []
    for offset in [0, 100]:
        try:
            url = f"https://remotive.com/api/remote-jobs?limit=100&offset={offset}"
            async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    break
                data = await resp.json(content_type=None)
                batch = data.get("jobs") or []
                for j in batch:
                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name", ""),
                        "url": j.get("url", ""),
                        "location": j.get("candidate_required_location", ""),
                        "posted": j.get("publication_date", ""),
                        "description": strip_html(j.get("description", "")),
                        "salary": j.get("salary", ""),
                        "source": "remotive",
                    })
                if len(batch) < 100:
                    break
        except Exception as e:
            print(f"  Remotive: {e}")
            break
    jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
    return jobs


async def fetch_remoteok(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://remoteok.com/api", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            if not isinstance(data, list):
                return []
            jobs = []
            for j in data:
                if not j or not j.get("id") or not j.get("position"):
                    continue
                posted = ""
                if j.get("date"):
                    try:
                        d = datetime.fromtimestamp(j["date"], tz=timezone.utc)
                        posted = d.isoformat()
                    except Exception:
                        pass
                title = re.sub(r"^\s*(apply now|hiring|remote)\s*", "", j.get("position", ""), flags=re.I).strip()
                jobs.append({
                    "title": title,
                    "company": j.get("company", ""),
                    "url": j.get("apply_url") or j.get("url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": posted,
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "remoteok",
                })
            jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
            return jobs
    except Exception as e:
        print(f"  RemoteOK: {e}")
        return []


async def fetch_wwr(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://weworkremotely.com/remote-jobs.rss", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&")
                jobs.append({
                    "title": title,
                    "company": (title.split(":")[0] or "").strip(),
                    "url": get("link").strip(),
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description")),
                    "salary": "",
                    "source": "weworkremotely",
                })
            jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
            return jobs
    except Exception as e:
        print(f"  WWR: {e}")
        return []


async def fetch_jobicy(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://jobicy.com/jobs/feed", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                categories = [c.strip() for c in re.findall(r"<category>([^<]*)</category>", item) if c.strip()]
                company = (get("dc:creator") or (categories[0] if categories else "Jobicy")).strip()
                has_remote = any(re.search(r"remote|worldwide|anywhere|global", c, re.I) for c in categories)
                location = "Remote (worldwide)" if has_remote else (categories[1] if len(categories) > 1 else "Remote")
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": get("link").strip(),
                    "location": location,
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description") or get("content:encoded", "")),
                    "salary": "",
                    "source": "jobicy",
                })
            return jobs
    except Exception as e:
        print(f"  Jobicy: {e}")
        return []


async def fetch_nodesk(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://nodesk.co/sitemap-jobs.xml", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            urls = [
                m.replace("<loc>", "").replace("</loc>", "").strip()
                for m in re.findall(r"<loc>([^<]+)</loc>", xml)
                if "/remote-jobs/" in m
            ]
            jobs = []
            for url in urls[:60]:
                try:
                    async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=6)) as page_resp:
                        if page_resp.status != 200:
                            continue
                        html = await page_resp.text()
                        title_m = re.search(r"<title>([^<]+)</title>", html, re.I)
                        title = title_m.group(1).replace("&amp;", "&").replace(" | Nodesk", "").strip() if title_m else ""
                        desc_m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.I)
                        desc = desc_m.group(1) if desc_m else ""
                        if not title:
                            continue
                        jobs.append({
                            "title": title,
                            "company": "Nodesk",
                            "url": url,
                            "location": "Remote (worldwide)",
                            "posted": "",
                            "description": strip_html(desc),
                            "salary": "",
                            "source": "nodesk",
                        })
                except Exception:
                    pass
                if len(jobs) >= 40:
                    break
            jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
            return jobs
    except Exception as e:
        print(f"  Nodesk: {e}")
        return []


async def fetch_arbeitnow(session: aiohttp.ClientSession) -> list[dict]:
    jobs = []
    endpoints = [
        "https://www.arbeitnow.com/api/job-board-api",
        "https://www.arbeitnow.co.uk/api/job-board-api",
    ]
    for base in endpoints:
        try:
            async with session.get(base, headers=HEADERS, timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json(content_type=None)
                for j in (data.get("jobs") or [])[:150]:
                    jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company_name") or j.get("company", ""),
                        "url": j.get("url") or j.get("apply_url", ""),
                        "location": j.get("location", "Remote"),
                        "posted": j.get("created_at") or j.get("published_at", ""),
                        "description": strip_html(j.get("description") or j.get("description_html", "")),
                        "salary": j.get("salary", ""),
                        "source": "arbeitnow",
                    })
        except Exception as e:
            print(f"  Arbeitnow {base}: {e}")
    jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
    return jobs


async def fetch_yayremote(session: aiohttp.ClientSession) -> list[dict]:
    # Try JSON first
    try:
        async with session.get(
            "https://www.yayremote.com/api/remote-jobs/feeds/jobs.json",
            headers=HEADERS, timeout=TIMEOUT,
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                arr = data if isinstance(data, list) else data.get("jobs") or data.get("positions") or []
                return [
                    {
                        "title": j.get("title") or j.get("name", ""),
                        "company": j.get("company") or j.get("company_name", "YayRemote"),
                        "url": j.get("url") or j.get("apply_url") or j.get("link", ""),
                        "location": j.get("location") or j.get("candidate_required_location", "Remote"),
                        "posted": j.get("created_at") or j.get("published_at") or j.get("date", ""),
                        "description": strip_html(j.get("description") or j.get("description_html", "")),
                        "salary": j.get("salary", ""),
                        "source": "yayremote",
                    }
                    for j in arr[:200]
                ]
    except Exception as e:
        print(f"  YayRemote JSON: {e}")
    # Fallback to RSS
    try:
        async with session.get(
            "https://www.yayremote.com/api/remote-jobs/feeds/jobs.xml",
            headers=HEADERS, timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            return [
                {
                    "title": re.sub(r"&amp;", "&", re.search(r"<title>([\s\S]*?)</title>", item).group(1)).strip()
                    if re.search(r"<title>([\s\S]*?)</title>", item) else "",
                    "company": (re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item) and re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item).group(1) or "YayRemote").strip(),
                    "url": (re.search(r"<link>([\s\S]*?)</link>", item) and re.search(r"<link>([\s\S]*?)</link>", item).group(1) or "").strip(),
                    "location": "Remote",
                    "posted": (re.search(r"<pubDate>([\s\S]*?)</pubDate>", item) and re.search(r"<pubDate>([\s\S]*?)</pubDate>", item).group(1) or ""),
                    "description": strip_html(
                        (re.search(r"<description>([\s\S]*?)</description>", item) and re.search(r"<description>([\s\S]*?)</description>", item).group(1) or "")
                        or (re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item) and re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item).group(1) or "")
                    ),
                    "salary": "",
                    "source": "yayremote",
                }
                for item in items
            ]
    except Exception as e:
        print(f"  YayRemote RSS: {e}")
        return []


async def fetch_remote1stjobs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://www.remote1stjobs.com/jobs.json", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            arr = data if isinstance(data, list) else data.get("jobs") or data.get("positions") or []
            return [
                {
                    "title": j.get("title") or j.get("name", ""),
                    "company": j.get("company") or j.get("company_name", "Remote1stJobs"),
                    "url": j.get("url") or j.get("apply_url") or j.get("link", ""),
                    "location": j.get("location") or j.get("candidate_required_location", "Remote"),
                    "posted": j.get("created_at") or j.get("published_at") or j.get("date", ""),
                    "description": strip_html(j.get("description") or j.get("description_html", "")),
                    "salary": j.get("salary", ""),
                    "source": "remote1stjobs",
                }
                for j in arr[:200]
            ]
    except Exception as e:
        print(f"  Remote1stJobs: {e}")
        return []


async def fetch_realworkfromanywhere(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get("https://www.realworkfromanywhere.com/remote-jobs.rss", headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            return [
                {
                    "title": re.sub(r"&amp;", "&", re.search(r"<title>([\s\S]*?)</title>", item).group(1)).strip()
                    if re.search(r"<title>([\s\S]*?)</title>", item) else "",
                    "company": (re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item) and re.search(r"<dc:creator>([\s\S]*?)</dc:creator>", item).group(1) or "Real Work From Anywhere").strip(),
                    "url": (re.search(r"<link>([\s\S]*?)</link>", item) and re.search(r"<link>([\s\S]*?)</link>", item).group(1) or "").strip(),
                    "location": "Remote",
                    "posted": (re.search(r"<pubDate>([\s\S]*?)</pubDate>", item) and re.search(r"<pubDate>([\s\S]*?)</pubDate>", item).group(1) or ""),
                    "description": strip_html(
                        (re.search(r"<description>([\s\S]*?)</description>", item) and re.search(r"<description>([\s\S]*?)</description>", item).group(1) or "")
                        or (re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item) and re.search(r"<content:encoded>([\s\S]*?)</content:encoded>", item).group(1) or "")
                    ),
                    "salary": "",
                    "source": "realworkfromanywhere",
                }
                for item in items
            ]
    except Exception as e:
        print(f"  RealWorkFromAnywhere: {e}")
        return []


# ===========================================================================
# NEW FETCHERS — 25+ additional job sources
# ===========================================================================


# ---------------------------------------------------------------------------
# 1. Mostaql (mostaql.com) — Arabic freelancing platform
# ---------------------------------------------------------------------------

async def fetch_mostaql(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://mostaql.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Parse job cards from HTML
            cards = re.findall(
                r'<div[^>]*class="[^"]*job[^"]*"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>',
                html, re.I
            )
            if not cards:
                # Fallback: extract links with /jobs/ in href
                links = re.findall(
                    r'<a[^>]+href=["\'](/jobs/\d+[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                    html, re.I
                )
                for href, title_html in links[:200]:
                    title = strip_html(title_html).strip()
                    if title and len(title) > 3:
                        jobs.append({
                            "title": title,
                            "company": "Mostaql",
                            "url": f"https://mostaql.com{href}",
                            "location": "Remote (MENA)",
                            "posted": "",
                            "description": "",
                            "salary": "",
                            "source": "mostaql",
                        })
            return jobs[:200]
    except Exception as e:
        print(f"  Mostaql: {e}")
        return []


# ---------------------------------------------------------------------------
# 2. For9a (for9a.com) — Arabic freelancing platform
# ---------------------------------------------------------------------------

async def fetch_for9a(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://for9a.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract job listings
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*jobs?/[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://for9a.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "For9a",
                        "url": url,
                        "location": "Remote (MENA)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "for9a",
                    })
            # Also try JSON-LD
            jobs.extend(_parse_generic_html_jobs(html, "for9a", "https://for9a.com"))
            return jobs[:200]
    except Exception as e:
        print(f"  For9a: {e}")
        return []


# ---------------------------------------------------------------------------
# 3. Khamsat (khamsat.com) — Arabic micro-services marketplace
# ---------------------------------------------------------------------------

async def fetch_khamsat(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://khamsat.com/market/services",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract service listings
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:service|service|\d+)[^"\']*)["\'][^>]*class="[^"]*service[^"]*"[^>]*>',
                html, re.I
            )
            if not links:
                links = re.findall(
                    r'<a[^>]+href=["\']([^"\']+khamsat[^"\']*)["\'][^>]*>',
                    html, re.I
                )
            titles = re.findall(
                r'<h\d[^>]*class="[^"]*title[^"]*"[^>]*>([\s\S]*?)</h\d>',
                html, re.I
            )
            for i, href in enumerate(links[:200]):
                title = strip_html(titles[i]).strip() if i < len(titles) else ""
                url = href if href.startswith("http") else f"https://khamsat.com{href}"
                jobs.append({
                    "title": title or "Service Listing",
                    "company": "Khamsat",
                    "url": url,
                    "location": "Remote (MENA)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "khamsat",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Khamsat: {e}")
        return []


# ---------------------------------------------------------------------------
# 4. Ureed (ureed.com) — Arabic remote jobs platform
# ---------------------------------------------------------------------------

async def fetch_ureed(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://ureed.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract job links
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*jobs?/[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://ureed.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Ureed",
                        "url": url,
                        "location": "Remote (MENA)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "ureed",
                    })
            jobs.extend(_parse_generic_html_jobs(html, "ureed", "https://ureed.com"))
            return jobs[:200]
    except Exception as e:
        print(f"  Ureed: {e}")
        return []


# ---------------------------------------------------------------------------
# 5. Wuzzuf (wuzzuf.net) — Egyptian job platform
# ---------------------------------------------------------------------------

async def fetch_wuzzuf(session: aiohttp.ClientSession) -> list[dict]:
    try:
        # Wuzzuf has a search API
        async with session.get(
            "https://www.wuzzuf.net/api/jobs",
            params={"q": "", "limit": 100},
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                if isinstance(data, dict) and "jobs" in data:
                    return [
                        {
                            "title": j.get("title", ""),
                            "company": j.get("company", {}).get("name", ""),
                            "url": j.get("url", ""),
                            "location": j.get("location", "Egypt"),
                            "posted": j.get("posted_at", ""),
                            "description": strip_html(j.get("description", "")),
                            "salary": j.get("salary", ""),
                            "source": "wuzzuf",
                        }
                        for j in data["jobs"][:200]
                    ]
    except Exception:
        pass
    # Fallback to HTML scrape
    try:
        async with session.get(
            "https://www.wuzzuf.net/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "wuzzuf", "https://www.wuzzuf.net")[:200]
    except Exception as e:
        print(f"  Wuzzuf: {e}")
        return []


# ---------------------------------------------------------------------------
# 6. Daleel (daleel.com) — Arabic job listings
# ---------------------------------------------------------------------------

async def fetch_daleel(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://daleel.com/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "daleel", "https://daleel.com")
            # Also try link extraction
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:job|listing|opportunity)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://daleel.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Daleel",
                        "url": url,
                        "location": "Remote (MENA)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "daleel",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Daleel: {e}")
        return []


# ---------------------------------------------------------------------------
# 7. Aqar (aqar.fm) — Libyan job listings
# ---------------------------------------------------------------------------

async def fetch_aqar(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://aqar.fm/jobs",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "aqar", "https://aqar.fm")
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:job|وظيفة|فرص)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://aqar.fm{href}"
                    jobs.append({
                        "title": title,
                        "company": "Aqar",
                        "url": url,
                        "location": "Libya",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "aqar",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Aqar: {e}")
        return []


# ---------------------------------------------------------------------------
# 8. Tajer (tajer.ly) — Libyan marketplace
# ---------------------------------------------------------------------------

async def fetch_tajer(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://tajer.ly",
            headers={**HEADERS, "Accept-Language": "ar,en;q=0.9"},
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "tajer", "https://tajer.ly")
            links = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:service|job|فرص|خدمة)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in links[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://tajer.ly{href}"
                    jobs.append({
                        "title": title,
                        "company": "Tajer",
                        "url": url,
                        "location": "Libya",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "tajer",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Tajer: {e}")
        return []


# ---------------------------------------------------------------------------
# 9. LinkedIn (linkedin.com/jobs) — Public RSS feed
# ---------------------------------------------------------------------------

async def fetch_linkedin(session: aiohttp.ClientSession) -> list[dict]:
    try:
        # LinkedIn public job RSS for remote jobs
        rss_urls = [
            "https://www.linkedin.com/jobs/search?location=&f_WT=2&format=rss",
            "https://www.linkedin.com/jobs/search?keywords=remote&location=&f_WT=2&format=rss",
        ]
        jobs = []
        for rss_url in rss_urls:
            try:
                async with session.get(rss_url, headers=HEADERS, timeout=TIMEOUT) as resp:
                    if resp.status != 200:
                        continue
                    xml = await resp.text()
                    items = re.findall(r"<item>[\s\S]*?</item>", xml)
                    for item in items[:200]:
                        def get(tag):
                            m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                            return m.group(1) if m else ""
                        title = get("title").replace("&amp;", "&").strip()
                        link = get("link").strip()
                        desc = strip_html(get("description") or get("content:encoded", ""))
                        # Extract company from description or title
                        company_match = re.search(r"(?:Company:|at)\s*([^\n<]+)", desc, re.I)
                        company = company_match.group(1).strip() if company_match else title.split(" - ")[-1].strip() if " - " in title else "LinkedIn"
                        jobs.append({
                            "title": title.split(" - ")[0].strip() if " - " in title else title,
                            "company": company,
                            "url": link,
                            "location": "Remote",
                            "posted": get("pubDate") or "",
                            "description": desc,
                            "salary": "",
                            "source": "linkedin",
                        })
            except Exception:
                pass
        return jobs[:200]
    except Exception as e:
        print(f"  LinkedIn: {e}")
        return []


# ---------------------------------------------------------------------------
# 10. Bayt (bayt.com) — Middle East jobs platform
# ---------------------------------------------------------------------------

async def fetch_bayt(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.bayt.com/en/international/jobs/remote-jobs/",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "bayt", "https://www.bayt.com")
            # Try extracting from specific patterns
            cards = re.findall(
                r'<div[^>]*data-job-id="([^"]*)"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>',
                html, re.I
            )
            titles = re.findall(
                r'<h2[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]*href=["\']([^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.bayt.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Bayt",
                        "url": url,
                        "location": "Middle East",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "bayt",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Bayt: {e}")
        return []


# ---------------------------------------------------------------------------
# 11. GulfTalent (gulftalent.com) — Gulf region jobs
# ---------------------------------------------------------------------------

async def fetch_gulftalent(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.gulftalent.com/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "gulftalent", "https://www.gulftalent.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>\s*<[^>]*>([\s\S]*?)</(?:a|h\d)>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.gulftalent.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "GulfTalent",
                        "url": url,
                        "location": "Gulf / Middle East",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "gulftalent",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  GulfTalent: {e}")
        return []


# ---------------------------------------------------------------------------
# 12. Naukri Gulf (naukrigulf.com) — Middle East jobs
# ---------------------------------------------------------------------------

async def fetch_naukrigulf(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.naukrigulf.com/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "naukrigulf", "https://www.naukrigulf.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job-detail/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.naukrigulf.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "NaukriGulf",
                        "url": url,
                        "location": "Middle East",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "naukrigulf",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  NaukriGulf: {e}")
        return []


# ---------------------------------------------------------------------------
# 13. Craigslist (craigslist.org) — Remote gigs
# ---------------------------------------------------------------------------

async def fetch_craigslist(session: aiohttp.ClientSession) -> list[dict]:
    try:
        # Use Craigslist search for remote/writing/translation jobs
        queries = [
            "https://losangeles.craigslist.org/search/wri?query=remote&sort=date",
            "https://newyork.craigslist.org/search/wri?query=remote&sort=date",
            "https://sfbay.craigslist.org/search/wri?query=remote&sort=date",
        ]
        jobs = []
        for url in queries:
            try:
                async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                    # Craigslist uses simple <a> tags in result rows
                    listings = re.findall(
                        r'<a[^>]+href=["\']([^"\']*craigslist[^"\']*/\d+\.html)["\'][^>]*class="[^"]*result-title[^"]*"[^>]*>([\s\S]*?)</a>',
                        html, re.I
                    )
                    if not listings:
                        listings = re.findall(
                            r'<a[^>]+class="[^"]*result-title[^"]*"[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
                            html, re.I
                        )
                    for href, title_html in listings[:60]:
                        title = strip_html(title_html).strip()
                        if title and len(title) > 3:
                            full_url = href if href.startswith("http") else f"https://craigslist.org{href}"
                            jobs.append({
                                "title": title,
                                "company": "Craigslist",
                                "url": full_url,
                                "location": "Remote",
                                "posted": "",
                                "description": "",
                                "salary": "",
                                "source": "craigslist",
                            })
            except Exception:
                pass
        return jobs[:200]
    except Exception as e:
        print(f"  Craigslist: {e}")
        return []


# ---------------------------------------------------------------------------
# 14. Upwork (upwork.com) — Freelancing platform
# ---------------------------------------------------------------------------

async def fetch_upwork(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.upwork.com/nx/search/jobs/?q=remote&sort=recency",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Upwork uses data attributes for job info
            job_data = re.findall(
                r'data-job-typing="([^"]*)"[^>]*>[\s\S]*?</section>',
                html, re.I
            )
            # Try JSON-LD
            jobs.extend(_parse_generic_html_jobs(html, "upwork", "https://www.upwork.com"))
            # Try extracting from search results
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/~[^"\']*|/jobs/[^"\']*)["\'][^>]*class="[^"]*job-tile-title[^"]*"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            if not titles:
                titles = re.findall(
                    r'<span[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
                    html, re.I
                )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.upwork.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Upwork",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "upwork",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Upwork: {e}")
        return []


# ---------------------------------------------------------------------------
# 15. Fiverr (fiverr.com) — Freelancing gigs
# ---------------------------------------------------------------------------

async def fetch_fiverr(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.fiverr.com/categories/writing-translation",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Fiverr gig listings
            gigs = re.findall(
                r'<a[^>]+href=["\'](/[^"\']+/[^"\']+/[^"\']+)["\'][^>]*class="[^"]*gig-card[^"]*"[^>]*>',
                html, re.I
            )
            if not gigs:
                gigs = re.findall(
                    r'<a[^>]+href=["\'](/[^"\']+)["\'][^>]*>\s*<[^>]*class="[^"]*gig-title[^"]*"[^>]*>([\s\S]*?)</',
                    html, re.I
                )
            titles = re.findall(
                r'<a[^>]*class="[^"]*gig-title[^"]*"[^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for i, href in enumerate(gigs[:200]):
                title = strip_html(titles[i]).strip() if i < len(titles) else ""
                url = href if href.startswith("http") else f"https://www.fiverr.com{href}"
                jobs.append({
                    "title": title or "Fiverr Gig",
                    "company": "Fiverr",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "fiverr",
                })
            jobs.extend(_parse_generic_html_jobs(html, "fiverr", "https://www.fiverr.com"))
            return jobs[:200]
    except Exception as e:
        print(f"  Fiverr: {e}")
        return []


# ---------------------------------------------------------------------------
# 16. Toptal (toptal.com) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_toptal(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.toptal.com/careers",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "toptal", "https://www.toptal.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/careers/|/jobs?/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.toptal.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Toptal",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "toptal",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Toptal: {e}")
        return []


# ---------------------------------------------------------------------------
# 17. FlexJobs (flexjobs.com) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_flexjobs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.flexjobs.com/search",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "flexjobs", "https://www.flexjobs.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.flexjobs.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "FlexJobs",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "flexjobs",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  FlexJobs: {e}")
        return []


# ---------------------------------------------------------------------------
# 18. Remote.co — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_remotedotco(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://remote.co/remote-jobs/",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "remote.co", "https://remote.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://remote.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "Remote.co",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "remote.co",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Remote.co: {e}")
        return []


# ---------------------------------------------------------------------------
# 19. JustRemote (justremote.co) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_justremote(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://justremote.co/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "justremote", "https://justremote.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/jobs?/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://justremote.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "JustRemote",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "justremote",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  JustRemote: {e}")
        return []


# ---------------------------------------------------------------------------
# 20. Himalayas (himalayas.app) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_himalayas(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://himalayas.app/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "himalayas", "https://himalayas.app")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://himalayas.app{href}"
                    jobs.append({
                        "title": title,
                        "company": "Himalayas",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "himalayas",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Himalayas: {e}")
        return []


# ---------------------------------------------------------------------------
# 21. Glassdoor — Job listings
# ---------------------------------------------------------------------------

async def fetch_glassdoor(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.glassdoor.com/Job/remote-jobs-SRCH_IL.0,6_IS11047_KO7,14.htm",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "glassdoor", "https://www.glassdoor.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/job-listing/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.glassdoor.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Glassdoor",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "glassdoor",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Glassdoor: {e}")
        return []


# ---------------------------------------------------------------------------
# 22. Indeed — Job listings
# ---------------------------------------------------------------------------

async def fetch_indeed(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.indeed.com/jobs?q=remote&l=&sort=date",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "indeed", "https://www.indeed.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/rc/clk|/viewjob\?|/jobs/)[^"\']*)["\'][^>]*>\s*<span[^>]*>([\s\S]*?)</span>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.indeed.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Indeed",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "indeed",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Indeed: {e}")
        return []


# ---------------------------------------------------------------------------
# 23. ZipRecruiter — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_ziprecruiter(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.ziprecruiter.com/jobs-search?search=remote&location=",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "ziprecruiter", "https://www.ziprecruiter.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://www.ziprecruiter.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "ZipRecruiter",
                        "url": url,
                        "location": "Remote",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "ziprecruiter",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  ZipRecruiter: {e}")
        return []


# ---------------------------------------------------------------------------
# 24. Wellfound / AngelList — Startup jobs
# ---------------------------------------------------------------------------

async def fetch_wellfound(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://wellfound.com/remote-jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "wellfound", "https://wellfound.com")
            # Try extracting from specific Wellfound patterns
            job_items = re.findall(
                r'<div[^>]*class="[^"]*job-listing[^"]*"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>',
                html, re.I
            )
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/startup-jobs/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://wellfound.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Wellfound",
                        "url": url,
                        "location": "Remote (Startup)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "wellfound",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Wellfound: {e}")
        return []


# ---------------------------------------------------------------------------
# 25. Working Nomads (workingnomads.com) — Remote jobs RSS
# ---------------------------------------------------------------------------

async def fetch_workingnomads(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://www.workingnomads.com/jobsfeed",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Working Nomads"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "workingnomads",
                })
            return jobs
    except Exception as e:
        print(f"  WorkingNomads: {e}")
        return []


# ---------------------------------------------------------------------------
# 26. Jobspresso (jobspresso.co) — Remote jobs
# ---------------------------------------------------------------------------

async def fetch_jobspresso(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://jobspresso.co/remote-jobs/",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "jobspresso", "https://jobspresso.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://jobspresso.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "Jobspresso",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "jobspresso",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobspresso: {e}")
        return []


# ---------------------------------------------------------------------------
# 27. Hire LATAM (hirelatam.com) — Latin America remote jobs
# ---------------------------------------------------------------------------

async def fetch_hirelatam(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://hirelatam.com/en/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "hirelatam", "https://hirelatam.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/|/en/jobs/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://hirelatam.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Hire LATAM",
                        "url": url,
                        "location": "Remote (LATAM)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "hirelatam",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  HireLATAM: {e}")
        return []


# ---------------------------------------------------------------------------
# 28. Landing.Jobs (landing.jobs) — Remote tech jobs
# ---------------------------------------------------------------------------

async def fetch_landingjobs(session: aiohttp.ClientSession) -> list[dict]:
    try:
        async with session.get(
            "https://landing.jobs/jobs",
            headers=HEADERS,
            timeout=TIMEOUT,
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "landing.jobs", "https://landing.jobs")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://landing.jobs{href}"
                    jobs.append({
                        "title": title,
                        "company": "Landing.Jobs",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "landing.jobs",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  LandingJobs: {e}")
        return []


# ===========================================================================
# ADDITIONAL HIGH-QUALITY SOURCES
# ===========================================================================


# ---------------------------------------------------------------------------
# 29. Himalayas API (himalayas.app) — Free JSON API, 95k+ jobs
# ---------------------------------------------------------------------------

async def fetch_himalayas_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Himalayas JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://himalayas.app/jobs/api?limit=200",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("companyName", ""),
                    "url": j.get("applicationLink") or j.get("guid", ""),
                    "location": ", ".join(j.get("locationRestrictions", [])) or "Remote",
                    "posted": j.get("pubDate", ""),
                    "description": strip_html(j.get("description", "")),
                    "salary": f"{j.get('salaryMin', '')} - {j.get('salaryMax', '')} {j.get('currency', '')}".strip(" - ") if j.get("salaryMin") or j.get("salaryMax") else "",
                    "source": "himalayas",
                })
            jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
            return jobs[:200]
    except Exception as e:
        print(f"  Himalayas API: {e}")
        return []


# ---------------------------------------------------------------------------
# 30. Jobicy API (jobicy.com) — Free JSON API, 200 jobs per request
# ---------------------------------------------------------------------------

async def fetch_jobicy_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobicy JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://jobicy.com/api/v2/remote-jobs?count=200&geo=anywhere",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                salary = ""
                if j.get("salaryMin") and j.get("salaryMax"):
                    salary = f"{j['salaryMin']}-{j['salaryMax']} {j.get('salaryCurrency', '')} / {j.get('salaryPeriod', 'yearly')}"
                jobs.append({
                    "title": j.get("jobTitle", ""),
                    "company": j.get("companyName", ""),
                    "url": j.get("url", ""),
                    "location": j.get("jobGeo", "Remote"),
                    "posted": j.get("pubDate", ""),
                    "description": strip_html(j.get("jobDescription", "")),
                    "salary": salary,
                    "source": "jobicy",
                })
            jobs = [j for j in jobs if any(kw in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower() for kw in ['arabic', 'translator', 'translation', 'interpreter', 'bilingual', 'locali', 'linguist', 'language', 'editor', 'proofreader', 'content writer', 'copywriter', 'data entry', 'virtual assistant', 'transcription', 'subtitl', 'caption', 'annotation', 'multilingual', 'cat tools', 'trados', 'memoq', 'smartcat', 'prompt writer', 'ai trainer', 'data label', 'moderation'])]
            return jobs[:200]
    except Exception as e:
        print(f"  Jobicy API: {e}")
        return []


# ---------------------------------------------------------------------------
# 31. Workbeam (workbeamhq.com) — Free API, remote jobs
# ---------------------------------------------------------------------------

async def fetch_workbeam(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Workbeam API — free, no auth required."""
    try:
        async with session.get(
            "https://workbeamhq.com/api/v1/jobs?remote=global&limit=100",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company", ""),
                    "url": j.get("url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": j.get("posted_at", ""),
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "workbeam",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Workbeam: {e}")
        return []


# ---------------------------------------------------------------------------
# 32. Remotive API (remotive.com) — Improved with JSON API
# ---------------------------------------------------------------------------

async def fetch_remotive_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Remotive JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://remotive.com/api/remote-jobs?limit=200",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company_name", ""),
                    "url": j.get("url", ""),
                    "location": j.get("candidate_required_location", "Remote"),
                    "posted": j.get("publication_date", ""),
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "remotive",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Remotive API: {e}")
        return []


# ---------------------------------------------------------------------------
# 33. RemoteOK API (remoteok.com) — Improved with JSON API
# ---------------------------------------------------------------------------

async def fetch_remoteok_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from RemoteOK JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://remoteok.com/api",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            if not isinstance(data, list):
                return []
            jobs = []
            for j in data:
                if not j or not j.get("id") or not j.get("position"):
                    continue
                posted = ""
                if j.get("date"):
                    try:
                        d = datetime.fromtimestamp(j["date"], tz=timezone.utc)
                        posted = d.isoformat()
                    except Exception:
                        pass
                title = re.sub(r"^\s*(apply now|hiring|remote)\s*", "", j.get("position", ""), flags=re.I).strip()
                jobs.append({
                    "title": title,
                    "company": j.get("company", ""),
                    "url": j.get("apply_url") or j.get("url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": posted,
                    "description": strip_html(j.get("description", "")),
                    "salary": j.get("salary", ""),
                    "source": "remoteok",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  RemoteOK API: {e}")
        return []


# ---------------------------------------------------------------------------
# 34. We Work Remotely API (weworkremotely.com) — Improved with RSS
# ---------------------------------------------------------------------------

async def fetch_wwr_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from WWR RSS feed — free, no auth required."""
    try:
        async with session.get(
            "https://weworkremotely.com/remote-jobs.rss",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": (title.split(":")[0] or "").strip(),
                    "url": get("link").strip(),
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description")),
                    "salary": "",
                    "source": "weworkremotely",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  WWR API: {e}")
        return []


# ---------------------------------------------------------------------------
# 35. JustRemote API (justremote.co) — Improved with JSON
# ---------------------------------------------------------------------------

async def fetch_justremote_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from JustRemote — free, no auth required."""
    try:
        async with session.get(
            "https://justremote.co/remote-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "justremote", "https://justremote.co")
            # Also try extracting from specific patterns
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/jobs?/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://justremote.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "JustRemote",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "justremote",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  JustRemote API: {e}")
        return []


# ---------------------------------------------------------------------------
# 36. Jobspresso API (jobspresso.co) — Improved
# ---------------------------------------------------------------------------

async def fetch_jobspresso_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobspresso — free, no auth required."""
    try:
        async with session.get(
            "https://jobspresso.co/remote-jobs/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "jobspresso", "https://jobspresso.co")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/remote-jobs?/|/job/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://jobspresso.co{href}"
                    jobs.append({
                        "title": title,
                        "company": "Jobspresso",
                        "url": url,
                        "location": "Remote (Worldwide)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "jobspresso",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobspresso API: {e}")
        return []


# ---------------------------------------------------------------------------
# 37. Working Nomads API (workingnomads.com) — Improved
# ---------------------------------------------------------------------------

async def fetch_workingnomads_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Working Nomads RSS — free, no auth required."""
    try:
        async with session.get(
            "https://www.workingnomads.com/jobsfeed",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Working Nomads"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "workingnomads",
                })
            return jobs
    except Exception as e:
        print(f"  WorkingNomads API: {e}")
        return []


# ---------------------------------------------------------------------------
# 38. Hire LATAM API (hirelatam.com) — Improved
# ---------------------------------------------------------------------------

async def fetch_hirelatam_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Hire LATAM — free, no auth required."""
    try:
        async with session.get(
            "https://hirelatam.com/en/jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "hirelatam", "https://hirelatam.com")
            titles = re.findall(
                r'<a[^>]+href=["\']([^"\']*(?:/jobs?/|/job/|/en/jobs/)[^"\']*)["\'][^>]*>([\s\S]*?)</a>',
                html, re.I
            )
            for href, title_html in titles[:200]:
                title = strip_html(title_html).strip()
                if title and len(title) > 3:
                    url = href if href.startswith("http") else f"https://hirelatam.com{href}"
                    jobs.append({
                        "title": title,
                        "company": "Hire LATAM",
                        "url": url,
                        "location": "Remote (LATAM)",
                        "posted": "",
                        "description": "",
                        "salary": "",
                        "source": "hirelatam",
                    })
            return jobs[:200]
    except Exception as e:
        print(f"  HireLATAM API: {e}")
        return []


# ---------------------------------------------------------------------------
# 39. Arbeitnow API (arbeitnow.com) — Improved with JSON API
# ---------------------------------------------------------------------------

async def fetch_arbeitnow_api(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Arbeitnow JSON API — free, no auth required."""
    try:
        async with session.get(
            "https://www.arbeitnow.com/api/job-board-api",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json(content_type=None)
            jobs = []
            for j in (data.get("jobs") or [])[:200]:
                jobs.append({
                    "title": j.get("title", ""),
                    "company": j.get("company_name") or j.get("company", ""),
                    "url": j.get("url") or j.get("apply_url", ""),
                    "location": j.get("location", "Remote"),
                    "posted": j.get("created_at") or j.get("published_at", ""),
                    "description": strip_html(j.get("description") or j.get("description_html", "")),
                    "salary": j.get("salary", ""),
                    "source": "arbeitnow",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Arbeitnow API: {e}")
        return []


# ---------------------------------------------------------------------------
# 40. Jobicy RSS (jobicy.com) — Alternative feed
# ---------------------------------------------------------------------------

async def fetch_jobicy_rss(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobicy RSS feed — free, no auth required."""
    try:
        async with session.get(
            "https://jobicy.com/jobs/feed",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Jobicy"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "jobicy",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobicy RSS: {e}")
        return []


# ---------------------------------------------------------------------------
# 41. Himalayas RSS (himalayas.app) — Alternative feed
# ---------------------------------------------------------------------------

async def fetch_himalayas_rss(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Himalayas RSS feed — free, no auth required."""
    try:
        async with session.get(
            "https://himalayas.app/jobs/rss",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or get("content:encoded", ""))
                company_match = re.search(r"(?:Company:|company:)\s*([^\n<]+)", desc, re.I)
                company = company_match.group(1).strip() if company_match else "Himalayas"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "himalayas",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Himalayas RSS: {e}")
        return []


# ---------------------------------------------------------------------------
# History — JSON file replaces Cloudflare KV
# ---------------------------------------------------------------------------


def load_history() -> dict:
    for cand in [HISTORY_FILE, Path(__file__).parent / "state" / "scan_history.json"]:
        if cand.exists():
            try:
                return json.loads(cand.read_text())
            except Exception:
                pass
    return {"seen_urls": [], "scan_stats": {"total_scans": 0, "total_matches": 0, "last_scan_date": ""}}


def save_history(history: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep only last N URLs
    history["seen_urls"] = history["seen_urls"][-HISTORY_MAX:]
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


# ---------------------------------------------------------------------------
# Persistent seen URLs — survives across scan sessions
# ---------------------------------------------------------------------------


def _load_seen_url_entries() -> dict:
    """Return {url: iso_timestamp} from the persistent seen-URLs file.

    Supports the legacy list format (no timestamps): those entries are returned
    with an empty timestamp so the TTL filter treats them as expired and lets
    still-open listings be re-evaluated.
    """
    for cand in [SEEN_URLS_FILE, Path(__file__).parent / "state" / "seen_urls.json"]:
        if cand.exists():
            try:
                data = json.loads(cand.read_text())
            except Exception:
                continue
            urls = data.get("urls", {})
            if isinstance(urls, dict):
                return {str(u): ts for u, ts in urls.items()}
            # Legacy list format — no timestamps available.
            return {str(u): "" for u in urls}
    return {}


def load_seen_urls() -> set:
    """Load seen URLs still within the dedup TTL (legacy entries are expired)."""
    entries = _load_seen_url_entries()
    if not DEDUP_ENABLED:
        return set(entries.keys())
    now = datetime.now(timezone.utc)
    ttl_secs = DEDUP_TTL_DAYS * 86400
    fresh = set()
    for url, ts in entries.items():
        seen_dt = _parse_seen_ts(ts)
        if seen_dt is None:
            continue
        if (now - seen_dt).total_seconds() < ttl_secs:
            fresh.add(url)
    return fresh


def save_seen_urls(urls) -> None:
    """Persist seen URLs with timestamps, purging entries past the TTL.

    Accepts a set/list of URLs or a {url: timestamp} mapping. Existing
    timestamps are preserved so a URL is not kept forever.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_seen_url_entries()
    now = datetime.now(timezone.utc)
    ttl_secs = DEDUP_TTL_DAYS * 86400
    incoming = urls.keys() if isinstance(urls, dict) else urls
    merged: dict = {}
    for url in incoming:
        url = str(url)
        ts = existing.get(url, "")
        seen_dt = _parse_seen_ts(ts)
        if seen_dt is None:
            ts = now.isoformat()
            seen_dt = now
        if (now - seen_dt).total_seconds() < ttl_secs:
            merged[url] = ts
    # Keep only the most recent HISTORY_MAX urls
    if len(merged) > HISTORY_MAX:
        merged = dict(sorted(merged.items(), key=lambda kv: kv[1], reverse=True)[:HISTORY_MAX])
    SEEN_URLS_FILE.write_text(
        json.dumps({"urls": merged, "updated": now.isoformat()}, indent=2)
    )


# ---------------------------------------------------------------------------
# Smart Deduplication — track company+title+location, not just URL
# ---------------------------------------------------------------------------

SMART_SEEN_FILE = OUTPUT_DIR / "smart_seen.json"


def load_smart_seen() -> dict:
    """Load smart deduplication fingerprints — output/ then state/."""
    for cand in [SMART_SEEN_FILE, Path(__file__).parent / "state" / "smart_seen.json"]:
        if cand.exists():
            try:
                return json.loads(cand.read_text())
            except Exception:
                pass
    return {"fingerprints": {}, "updated": ""}


def _parse_seen_ts(value) -> datetime | None:
    """Parse a stored 'seen' timestamp (dict entry or raw ISO string).

    Returns None for legacy/missing/unparseable values so callers can treat
    them as expired rather than as a permanent block.
    """
    if isinstance(value, dict):
        value = value.get("seen", "")
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def save_smart_seen(data: dict):
    """Save smart deduplication fingerprints, dropping any past the TTL."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    ttl_secs = DEDUP_TTL_DAYS * 86400
    fps = data.get("fingerprints", {})
    fresh = {}
    for fp, entry in fps.items():
        seen_dt = _parse_seen_ts(entry)
        if seen_dt is not None and (now - seen_dt).total_seconds() >= ttl_secs:
            continue
        fresh[fp] = entry
    # Keep only the most recent 10000 (by seen time)
    if len(fresh) > 10000:
        sorted_fps = sorted(
            fresh.items(),
            key=lambda x: (_parse_seen_ts(x[1]) or now),
            reverse=True,
        )
        fresh = dict(sorted_fps[:10000])
    data["fingerprints"] = fresh
    data["updated"] = now.isoformat()
    SMART_SEEN_FILE.write_text(json.dumps(data, indent=2))


def make_fingerprint(job: dict) -> str:
    """Create a smart fingerprint from company+title+location."""
    import re
    company = re.sub(r'[^a-z0-9]', '', (job.get("company") or "").lower().strip())
    title = re.sub(r'[^a-z0-9]', '', (job.get("title") or "").lower().strip())
    # Normalize common title variations
    title = title.replace("remote", "").replace("fulltime", "").replace("parttime", "")
    title = title.replace("contract", "").replace("freelance", "")
    # Use first 30 chars of title to catch slight variations
    title = title[:30]
    location = re.sub(r'[^a-z0-9]', '', (job.get("location") or "").lower().strip())[:20]
    return f"{company}|{title}|{location}"


def is_duplicate(job: dict, smart_seen: dict) -> bool:
    """Check if job is a duplicate using smart fingerprinting.

    Fingerprints expire after DEDUP_TTL_DAYS so a still-open listing seen on an
    earlier scan is re-evaluated instead of being suppressed forever. Legacy
    entries with no timestamp are treated as expired.
    """
    if not DEDUP_ENABLED:
        return False
    fp = make_fingerprint(job)
    fps = smart_seen.get("fingerprints", {})
    entry = fps.get(fp)
    if entry is None:
        return False
    seen_dt = _parse_seen_ts(entry)
    if seen_dt is None:
        return False
    age_secs = (datetime.now(timezone.utc) - seen_dt).total_seconds()
    return age_secs < DEDUP_TTL_DAYS * 86400


def mark_seen(job: dict, smart_seen: dict):
    """Mark job as seen using smart fingerprinting."""
    fp = make_fingerprint(job)
    if "fingerprints" not in smart_seen:
        smart_seen["fingerprints"] = {}
    smart_seen["fingerprints"][fp] = {
        "seen": datetime.now(timezone.utc).isoformat(),
        "title": job.get("title", ""),
        "company": job.get("company", ""),
    }


# ---------------------------------------------------------------------------
# Accumulating Excel history — read previous, append new matches
# ---------------------------------------------------------------------------


def load_scan_history() -> list[dict]:
    """Load accumulated scan history from disk."""
    if SCAN_HISTORY_FILE.exists():
        try:
            return json.loads(SCAN_HISTORY_FILE.read_text())
        except Exception:
            pass
    return []


def save_scan_history(history: list[dict]):
    """Save accumulated scan history, keeping last 100 scans."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trimmed = history[-100:]
    SCAN_HISTORY_FILE.write_text(json.dumps(trimmed, indent=2))


def append_to_scan_history(matched_jobs: list[dict], scan_info: dict):
    """Append this scan's results to the accumulating history."""
    history = load_scan_history()
    history.append({
        "date": datetime.now(timezone.utc).isoformat(),
        "matched_count": len(matched_jobs),
        "all_count": scan_info.get("all_count", 0),
        "jobs": [
            {
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "url": j.get("url", ""),
                "score": j.get("score", 0),
                "category": j.get("category", ""),
                "source": j.get("source", ""),
            }
            for j in matched_jobs[:50]
        ],
    })
    save_scan_history(history)


# ---------------------------------------------------------------------------
# Job Lifecycle Tracking — NEW / OLD / EXPIRED
# ---------------------------------------------------------------------------

LIFECYCLE_FILE = OUTPUT_DIR / "fresh_matches_history.json"
_LIFECYCLE_EXPIRY_DAYS = int(os.getenv("CAREEROPS_JOB_EXPIRY_DAYS", "3"))


def load_job_lifecycle() -> dict:
    """Load the lifecycle-tracked history. Returns dict with 'matches' list."""
    for cand in [LIFECYCLE_FILE, Path(__file__).parent / "state" / "fresh_matches_history.json"]:
        if cand.exists():
            try:
                data = json.loads(cand.read_text(encoding="utf-8"))
                # Support both old flat-list format and new dict format
                if isinstance(data, list):
                    return {"matches": data, "updated": ""}
                if isinstance(data, dict) and "matches" in data:
                    return data
            except Exception:
                pass
    return {"matches": [], "updated": ""}


def save_job_lifecycle(data: dict):
    """Save lifecycle-tracked history."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data["updated"] = datetime.now(timezone.utc).isoformat()
    LIFECYCLE_FILE.write_text(json.dumps(data["matches"], indent=2, default=str), encoding="utf-8")
    # Also save state copy
    state_file = Path(__file__).parent / "state" / "fresh_matches_history.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(data["matches"], indent=2, default=str), encoding="utf-8")


def classify_lifecycle(jobs: list[dict], scan_info: dict) -> dict:
    """Classify jobs into NEW / OLD / EXPIRED based on fresh_matches_history.

    Returns dict with 'new_jobs', 'old_jobs', 'expired_jobs', and updated scan_info.
    """
    now = datetime.now(timezone.utc)
    expiry_days = _LIFECYCLE_EXPIRY_DAYS

    lifecycle = load_job_lifecycle()
    existing = lifecycle.get("matches", [])
    existing_by_url = {}
    for m in existing:
        url = m.get("url", "")
        if url:
            existing_by_url[url] = m

    new_jobs = []
    old_jobs = []
    expired_jobs = []
    current_urls = set()

    for job in jobs:
        url = job.get("url", "")
        current_urls.add(url)
        found_str = existing_by_url.get(url, {}).get("found_date", "")

        if job.get("dup_pool"):
            # Re-surfaced from the open pool: previously seen, still open.
            job["lifecycle_status"] = "old"
            job["found_date"] = found_str or now.isoformat()
            try:
                job["expires_date"] = (now + timedelta(days=expiry_days)).isoformat()
            except Exception:
                job["expires_date"] = ""
            old_jobs.append(job)
            continue

        if found_str:
            # Job was seen before — check age
            try:
                found_dt = datetime.fromisoformat(found_str.replace("Z", "+00:00"))
                age_days = (now - found_dt).total_seconds() / 86400
            except Exception:
                found_dt = now
                age_days = 0

            expires_str = existing_by_url[url].get("expires_date", "")
            if not expires_str:
                try:
                    expires_dt = found_dt + timedelta(days=expiry_days)
                    expires_str = expires_dt.isoformat()
                except Exception:
                    expires_str = ""

            if age_days > expiry_days:
                job["lifecycle_status"] = "expired"
                job["found_date"] = found_str
                job["expires_date"] = expires_str
                expired_jobs.append(job)
            else:
                job["lifecycle_status"] = "old"
                job["found_date"] = found_str
                job["expires_date"] = expires_str
                old_jobs.append(job)
        else:
            # New job — first time seeing it
            found_now = now.isoformat()
            try:
                expires_dt = now + timedelta(days=expiry_days)
                expires_str = expires_dt.isoformat()
            except Exception:
                expires_str = ""
            job["lifecycle_status"] = "new"
            job["found_date"] = found_now
            job["expires_date"] = expires_str
            new_jobs.append(job)

    # Update history: keep non-expired from old + add new
    updated_matches = []
    for m in existing:
        url = m.get("url", "")
        found_str = m.get("found_date", "")
        if url in current_urls:
            # Still in current scan — keep it with updated data
            for job in jobs:
                if job.get("url") == url:
                    updated_matches.append({
                        "url": url,
                        "title": job.get("title", m.get("title", "")),
                        "company": job.get("company", m.get("company", "")),
                        "score": job.get("score", m.get("score", 0)),
                        "category": job.get("category", m.get("category", "")),
                        "found_date": m.get("found_date", ""),
                        "expires_date": m.get("expires_date", ""),
                        "lifecycle_status": job.get("lifecycle_status", "old"),
                    })
                    break
        else:
            # Not in current scan — check if expired
            if found_str:
                try:
                    found_dt = datetime.fromisoformat(found_str.replace("Z", "+00:00"))
                    age_days = (now - found_dt).total_seconds() / 86400
                except Exception:
                    age_days = expiry_days + 1
                if age_days <= expiry_days:
                    # Still within expiry — keep as expired-from-notification but in history
                    updated_matches.append({
                        "url": url,
                        "title": m.get("title", ""),
                        "company": m.get("company", ""),
                        "score": m.get("score", 0),
                        "category": m.get("category", ""),
                        "found_date": m.get("found_date", ""),
                        "expires_date": m.get("expires_date", ""),
                        "lifecycle_status": "expired",
                    })

    # Add new jobs
    for job in new_jobs:
        updated_matches.append({
            "url": job.get("url", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "score": job.get("score", 0),
            "category": job.get("category", ""),
            "found_date": job.get("found_date", ""),
            "expires_date": job.get("expires_date", ""),
            "lifecycle_status": "new",
        })

    # CRITICAL: Add OLD jobs from history that aren't in the current scan.
    # Even when the current scan finds 0 matches, previous matches should
    # still show as "Still Available" in Telegram/email until they expire.
    for m in existing:
        url = m.get("url", "")
        if url in current_urls:
            continue  # Already handled above
        found_str = m.get("found_date", "")
        if not found_str:
            continue
        try:
            found_dt = datetime.fromisoformat(found_str.replace("Z", "+00:00"))
            age_days = (now - found_dt).total_seconds() / 86400
        except Exception:
            age_days = expiry_days + 1
        if age_days > expiry_days:
            # Expired — don't add to notification, but keep in history
            continue
        # Still within expiry — add as OLD (not in current scan but still available)
        old_jobs.append({
            "url": url,
            "title": m.get("title", ""),
            "company": m.get("company", ""),
            "score": m.get("score", 0),
            "category": m.get("category", ""),
            "found_date": found_str,
            "expires_date": m.get("expires_date", ""),
            "lifecycle_status": "old",
        })
        # Also save to updated_matches so they persist across scans
        updated_matches.append({
            "url": url,
            "title": m.get("title", ""),
            "company": m.get("company", ""),
            "score": m.get("score", 0),
            "category": m.get("category", ""),
            "found_date": found_str,
            "expires_date": m.get("expires_date", ""),
            "lifecycle_status": "old",
        })

    # Save updated lifecycle
    save_job_lifecycle({"matches": updated_matches, "updated": now.isoformat()})

    # Add lifecycle counts to scan_info
    scan_info["lifecycle_new"] = len(new_jobs)
    scan_info["lifecycle_old"] = len(old_jobs)
    scan_info["lifecycle_expired"] = len(expired_jobs)

    print(f"  Lifecycle: {len(new_jobs)} NEW, {len(old_jobs)} OLD, {len(expired_jobs)} EXPIRED")

    return {
        "new_jobs": new_jobs,
        "old_jobs": old_jobs,
        "expired_jobs": expired_jobs,
        "scan_info": scan_info,
    }


# ---------------------------------------------------------------------------
# 42. PeoplePerHour — UK/EU freelance platform
# ---------------------------------------------------------------------------

async def fetch_peopleperhour(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from PeoplePerHour RSS feed."""
    try:
        async with session.get(
            "https://www.peopleperhour.com/rss.xml",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or "")
                jobs.append({
                    "title": title,
                    "company": "PeoplePerHour",
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "peopleperhour",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  PeoplePerHour: {e}")
        return []


# ---------------------------------------------------------------------------
# 44. Guru.com — Freelance marketplace
# ---------------------------------------------------------------------------

async def fetch_guru(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Guru.com RSS feed."""
    try:
        async with session.get(
            "https://www.guru.com/rss.xml",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = get("title").replace("&amp;", "&").strip()
                if not title:
                    continue
                link = get("link").strip()
                desc = strip_html(get("description") or "")
                jobs.append({
                    "title": title,
                    "company": "Guru.com",
                    "url": link,
                    "location": "Remote (Worldwide)",
                    "posted": get("pubDate") or "",
                    "description": desc,
                    "salary": "",
                    "source": "guru",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Guru: {e}")
        return []


# ---------------------------------------------------------------------------
# 45. Appen — AI/ML training data tasks
# ---------------------------------------------------------------------------

async def fetch_appen(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Appen careers page."""
    try:
        async with session.get(
            "https://www.appen.com/careers/search",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="(/careers/[^"]+)"[^>]*>.*?<h[23][^>]*>(.*?)</h[23]>'
            matches = re.findall(pattern, html, re.DOTALL)
            for url_path, title in matches[:100]:
                title = strip_html(title).strip()
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": "Appen",
                    "url": f"https://www.appen.com{url_path}",
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "appen",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Appen: {e}")
        return []


# ---------------------------------------------------------------------------
# 46. Lionbridge/Concentrix — Translation & AI tasks
# ---------------------------------------------------------------------------

async def fetch_lionbridge(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Lionbridge/Concentrix careers."""
    try:
        async with session.get(
            "https://www.lionbridge.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.lionbridge.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Lionbridge",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "lionbridge",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Lionbridge: {e}")
        return []


# ---------------------------------------------------------------------------
# 47. TransPerfect — Translation jobs
# ---------------------------------------------------------------------------

async def fetch_transperfect(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TransPerfect careers."""
    try:
        async with session.get(
            "https://www.transperfect.com/careers",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*job[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.transperfect.com{url}"
                jobs.append({
                    "title": title,
                    "company": "TransPerfect",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "transperfect",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  TransPerfect: {e}")
        return []


# ---------------------------------------------------------------------------
# 48. Gengo — Translation platform
# ---------------------------------------------------------------------------

async def fetch_gengo(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Gengo translation jobs."""
    try:
        async with session.get(
            "https://gengo.com/translators/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*(?:Arabic|English|翻译|ترجمة)[^<]*)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title:
                    continue
                if not url.startswith("http"):
                    url = f"https://gengo.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "Gengo",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation platform for Arabic-English language pairs",
                    "salary": "",
                    "source": "gengo",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Gengo: {e}")
        return []


# ---------------------------------------------------------------------------
# 49. ProZ — Translation marketplace
# ---------------------------------------------------------------------------

async def fetch_proz(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from ProZ translation jobs."""
    try:
        async with session.get(
            "https://www.proz.com/jobs/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="(/jobs/[^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                jobs.append({
                    "title": title,
                    "company": "ProZ",
                    "url": f"https://www.proz.com{url}",
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation and localization job",
                    "salary": "",
                    "source": "proz",
                })
            # Only keep jobs mentioning arabic
            jobs = [j for j in jobs if 'arabic' in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower()]
            return jobs[:100]
    except Exception as e:
        print(f"  ProZ: {e}")
        return []




# ---------------------------------------------------------------------------
# (removed) TES educator board — teaching-only source, dropped with the
# ESL focus; the scanner now targets Arabic<->English translation only.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 50. Smartling — Translation platform
# ---------------------------------------------------------------------------

async def fetch_smartling(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Smartling careers."""
    try:
        async with session.get(
            "https://www.smartling.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.smartling.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Smartling",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "smartling",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Smartling: {e}")
        return []


# ---------------------------------------------------------------------------
# 51. Unbabel — AI Translation platform
# ---------------------------------------------------------------------------

async def fetch_unbabel(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Unbabel careers."""
    try:
        async with session.get(
            "https://unbabel.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://unbabel.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Unbabel",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "unbabel",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Unbabel: {e}")
        return []


# ---------------------------------------------------------------------------
# 52. RWS — Translation & localization
# ---------------------------------------------------------------------------

async def fetch_rws(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from RWS careers."""
    try:
        async with session.get(
            "https://www.rws.com/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*career[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.rws.com{url}"
                jobs.append({
                    "title": title,
                    "company": "RWS",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "rws",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  RWS: {e}")
        return []


# ---------------------------------------------------------------------------
# 53. Carmelite — Translation agency
# ---------------------------------------------------------------------------

async def fetch_carmel(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Carmel translation agency."""
    try:
        async with session.get(
            "https://www.carmel.co.il/careers/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*job[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:100]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.carmel.co.il{url}"
                jobs.append({
                    "title": title,
                    "company": "Carmel Translation",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "",
                    "salary": "",
                    "source": "carmel",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Carmel: {e}")
        return []


# ---------------------------------------------------------------------------
# 54. Preply — Online tutoring platform
# ---------------------------------------------------------------------------

async def fetch_magic_ears(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Magic Ears teaching jobs."""
    try:
        async with session.get(
            "https://www.magicears.com/en/teacher",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*teacher[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.magicears.com{url}"
                jobs.append({
                    "title": title,
                    "company": "Magic Ears",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "English teaching platform",
                    "salary": "",
                    "source": "magic_ears",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Magic Ears: {e}")
        return []


# ---------------------------------------------------------------------------
# 59. Translated.com — Translation platform
# ---------------------------------------------------------------------------

async def fetch_translated(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Translated.com translation jobs."""
    try:
        async with session.get(
            "https://www.translated.com/en/translators",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*translat[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.translated.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "Translated.com",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation platform for professional translators",
                    "salary": "",
                    "source": "translated",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Translated: {e}")
        return []


# ---------------------------------------------------------------------------
# 60. One Hour Translation — Translation platform
# ---------------------------------------------------------------------------

async def fetch_one_hour_translation(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from One Hour Translation jobs."""
    try:
        async with session.get(
            "https://www.onehourtranslation.com/translation/jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*job[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.onehourtranslation.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "One Hour Translation",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Fast translation platform",
                    "salary": "",
                    "source": "one_hour_translation",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  One Hour Translation: {e}")
        return []


# ---------------------------------------------------------------------------
# 61. Flitto — Translation platform
# ---------------------------------------------------------------------------

async def fetch_flitto(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Flitto translation jobs."""
    try:
        async with session.get(
            "https://flitto.com/en/translators",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*translat[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://flitto.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "Flitto",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Crowdsourced translation platform",
                    "salary": "",
                    "source": "flitto",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Flitto: {e}")
        return []


# ---------------------------------------------------------------------------
# 62. TextMaster — Translation platform
# ---------------------------------------------------------------------------

async def fetch_textmaster(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TextMaster translation jobs."""
    try:
        async with session.get(
            "https://www.textmaster.com/en/translators/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            pattern = r'<a[^>]*href="([^"]*translat[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://www.textmaster.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "TextMaster",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Professional translation platform",
                    "salary": "",
                    "source": "textmaster",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  TextMaster: {e}")
        return []


# ---------------------------------------------------------------------------
# 63. Remote.co — Remote job board
# ---------------------------------------------------------------------------

async def fetch_remoteco(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Remote.co job board."""
    try:
        async with session.get(
            "https://remote.co/remote-jobs/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "remote.co", "https://remote.co")
    except Exception as e:
        print(f"  Remote.co: {e}")
        return []


# ---------------------------------------------------------------------------
# 64. DailyRemote — Volume remote job board
# ---------------------------------------------------------------------------

async def fetch_dailyremote(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from DailyRemote job board."""
    try:
        async with session.get(
            "https://www.dailyremote.com/remote-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "dailyremote", "https://www.dailyremote.com")
    except Exception as e:
        print(f"  DailyRemote: {e}")
        return []


# ---------------------------------------------------------------------------
# 65. Jobgether — Location-flexible job board
# ---------------------------------------------------------------------------

async def fetch_jobgether(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jobgether job board."""
    try:
        async with session.get(
            "https://jobgether.com/remote-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            return _parse_generic_html_jobs(html, "jobgether", "https://jobgether.com")
    except Exception as e:
        print(f"  Jobgether: {e}")
        return []


# ---------------------------------------------------------------------------
# 66. GoTranscript — Translation platform (100+ languages)
# ---------------------------------------------------------------------------

async def fetch_gotranscript(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from GoTranscript translation jobs."""
    try:
        async with session.get(
            "https://gotranscript.com/translation-jobs",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # GoTranscript lists language pairs
            lang_pattern = r'<a[^>]*href="([^"]*translation-jobs[^"]*)"[^>]*>([^<]+)</a>'
            matches = re.findall(lang_pattern, html, re.I)
            for url, title in matches[:50]:
                title = title.strip()
                if not title or len(title) < 5:
                    continue
                if not url.startswith("http"):
                    url = f"https://gotranscript.com{url}"
                jobs.append({
                    "title": f"Translator - {title}",
                    "company": "GoTranscript",
                    "url": url,
                    "location": "Remote (Worldwide)",
                    "posted": "",
                    "description": "Translation jobs for 100+ languages. Weekly payments via PayPal/Payoneer.",
                    "salary": "",
                    "source": "gotranscript",
                })
            # Only keep jobs mentioning arabic
            jobs = [j for j in jobs if 'arabic' in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower()]
            return jobs[:50]
    except Exception as e:
        print(f"  GoTranscript: {e}")
        return []


# ---------------------------------------------------------------------------
# 67. Smartcat — Translation marketplace
# ---------------------------------------------------------------------------

async def fetch_smartcat(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Smartcat translation marketplace."""
    try:
        async with session.get(
            "https://smartcat.com/marketplace/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "smartcat", "https://smartcat.com")
            for j in jobs:
                j["source"] = "smartcat"
                j["location"] = "Remote (Worldwide)"
            # Only keep jobs mentioning arabic
            jobs = [j for j in jobs if 'arabic' in (j.get('title','') + ' ' + j.get('description','') + ' ' + j.get('location','')).lower()]
            return jobs[:50]
    except Exception as e:
        print(f"  Smartcat: {e}")
        return []


# ---------------------------------------------------------------------------
# 68. iTalki — Language tutoring platform
# ---------------------------------------------------------------------------

async def fetch_amazingtalker(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from AmazingTalker tutoring platform."""
    try:
        async with session.get(
            "https://www.amazingtalker.com/teach",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return []  # no invented listing
    except Exception as e:
        print(f"  AmazingTalker: {e}")
        return []


# ---------------------------------------------------------------------------
# 71. Twenix — Business English teaching
# ---------------------------------------------------------------------------

async def fetch_twenix(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Twenix business English platform."""
    try:
        async with session.get(
            "https://twenix.com/teachers",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return []  # no invented listing
    except Exception as e:
        print(f"  Twenix: {e}")
        return []


# ---------------------------------------------------------------------------
# 72. Novakid — European ESL for kids
# ---------------------------------------------------------------------------

async def fetch_novakid(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Novakid ESL platform."""
    try:
        async with session.get(
            "https://novakid.com/en/teach/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return []  # no invented listing
    except Exception as e:
        print(f"  Novakid: {e}")
        return []


# ---------------------------------------------------------------------------
# 73. LingoAce — ESL teaching platform
# ---------------------------------------------------------------------------

async def fetch_lingoace(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from LingoAce teaching platform."""
    try:
        async with session.get(
            "https://www.lingoace.com/teach/",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return []  # no invented listing
    except Exception as e:
        print(f"  LingoAce: {e}")
        return []


# ---------------------------------------------------------------------------
# 74. Native Camp — ESL teaching platform
# ---------------------------------------------------------------------------

async def fetch_nativecamp(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Native Camp ESL platform."""
    try:
        async with session.get(
            "https://nativecamp.net/teachers/en",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            return []  # no invented listing
    except Exception as e:
        print(f"  Native Camp: {e}")
        return []


# ---------------------------------------------------------------------------
# 75. TutorABC — ESL teaching platform
# ---------------------------------------------------------------------------

async def fetch_tefl_com(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TEFL.com teaching jobs."""
    try:
        async with session.get(
            "https://www.tefl.com/jobs/online-teaching-jobs.html",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "tefl.com", "https://www.tefl.com")
            for j in jobs:
                j["source"] = "tefl.com"
                j["location"] = "Remote (Worldwide)"
            return jobs[:50]
    except Exception as e:
        print(f"  TEFL.com: {e}")
        return []


# ---------------------------------------------------------------------------
# 78. TeachAway — Teaching job board
# ---------------------------------------------------------------------------

async def fetch_teachaway(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from TeachAway teaching jobs."""
    try:
        async with session.get(
            "https://www.teachaway.com/teach-online",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "teachaway", "https://www.teachaway.com")
            for j in jobs:
                j["source"] = "teachaway"
                j["location"] = "Remote (Worldwide)"
            return jobs[:50]
    except Exception as e:
        print(f"  TeachAway: {e}")
        return []


# ---------------------------------------------------------------------------
# 79. Jooble — Job aggregator (free API)
# ---------------------------------------------------------------------------

async def fetch_jooble(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Jooble job aggregator API."""
    try:
        # Jooble free developer API
        async with session.get(
            "https://jooble.org/api/",
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:100]:
                title = item.get("title", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("company", "Unknown"),
                    "url": item.get("link", item.get("url", "")),
                    "location": item.get("location", "Remote"),
                    "posted": item.get("pubDate", ""),
                    "description": strip_html(item.get("snippet", ""))[:500],
                    "salary": item.get("salary", ""),
                    "source": "jooble",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Jooble: {e}")
        return []


# ---------------------------------------------------------------------------
# 80. Adzuna — Job aggregator (free API)
# ---------------------------------------------------------------------------

async def fetch_adzuna(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Adzuna job aggregator."""
    try:
        # Adzuna free API for UK/US
        jobs = []
        for country in ["gb", "us"]:
            async with session.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                params={
                    "app_id": "career-ops",
                    "app_key": "career-ops-free",
                    "results_per_page": 50,
                    "what": "translation+english+teacher+content+writer+virtual+assistant",
                    "remote": 1,
                },
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                for item in (data.get("results") or [])[:50]:
                    title = item.get("title", "")
                    if not title:
                        continue
                    jobs.append({
                        "title": title,
                        "company": item.get("company", {}).get("display_name", "Unknown"),
                        "url": item.get("redirect_url", ""),
                        "location": item.get("location", {}).get("display_name", "Remote"),
                        "posted": item.get("created", ""),
                        "description": strip_html(item.get("description", ""))[:500],
                        "salary": f"${item.get('salary_min', 0)}-${item.get('salary_max', 0)}" if item.get("salary_min") else "",
                        "source": "adzuna",
                    })
        return jobs[:100]
    except Exception as e:
        print(f"  Adzuna: {e}")
        return []


# ---------------------------------------------------------------------------
# 81. MeetFrank — Job board with AI API
# ---------------------------------------------------------------------------

async def fetch_meetfrank(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from MeetFrank job board API."""
    try:
        async with session.get(
            "https://meetfrank.com/ai/jobs",
            params={"remote": "FULL_REMOTE", "limit": 100},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:100]:
                title = item.get("title", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("company", "Unknown"),
                    "url": item.get("applyUrl", ""),
                    "location": item.get("location", "Remote"),
                    "posted": item.get("publishedAt", ""),
                    "description": strip_html(item.get("description", ""))[:500],
                    "salary": f"{item.get('salary', {}).get('currency', '')} {item.get('salary', {}).get('min', '')}-{item.get('salary', {}).get('max', '')}" if item.get("salary") else "",
                    "source": "meetfrank",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  MeetFrank: {e}")
        return []


# ---------------------------------------------------------------------------
# 82. Recruitee — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_recruitee(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Recruitee public job board."""
    try:
        async with session.get(
            "https://recruitee.com/jobs",
            params={"q": "translation+english+writer+virtual+assistant", "remote": "true"},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = _parse_generic_html_jobs(html, "recruitee", "https://recruitee.com")
            for j in jobs:
                j["source"] = "recruitee"
            return jobs[:50]
    except Exception as e:
        print(f"  Recruitee: {e}")
        return []


# ---------------------------------------------------------------------------
# 83. Ashby — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_ashby(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Ashby public job board."""
    try:
        async with session.get(
            "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams",
            json={
                "query": "query { jobBoard { teams { name jobs { id title locationName employmentType descriptionPlain } } } }",
                "variables": {}
            },
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for team in (data.get("data", {}).get("jobBoard", {}).get("teams") or []):
                team_name = team.get("name", "")
                for job in (team.get("jobs") or []):
                    title = job.get("title", "")
                    if not title:
                        continue
                    desc = strip_html(job.get("descriptionPlain", ""))[:500]
                    jobs.append({
                        "title": title,
                        "company": team_name,
                        "url": f"https://jobs.ashbyhq.com/{team_name.lower().replace(' ', '')}/{job.get('id', '')}",
                        "location": job.get("locationName", "Remote"),
                        "posted": "",
                        "description": desc,
                        "salary": "",
                        "source": "ashby",
                    })
            return jobs[:100]
    except Exception as e:
        print(f"  Ashby: {e}")
        return []


# ---------------------------------------------------------------------------
# 84. SmartRecruiters — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_smartrecruiters(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from SmartRecruiters public job board."""
    try:
        async with session.get(
            "https://api.smartrecruiters.com/v1/companies/public/postings",
            params={
                "q": "translation OR english OR writer OR virtual assistant OR content",
                "limit": 100,
            },
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("content") or [])[:100]:
                title = item.get("name", "")
                if not title:
                    continue
                company = item.get("company", {}).get("name", "Unknown")
                loc = item.get("location", {})
                location = f"{loc.get('city', '')}, {loc.get('country', '')}" if loc else "Remote"
                jobs.append({
                    "title": title,
                    "company": company,
                    "url": item.get("ref", ""),
                    "location": location,
                    "posted": item.get("releasedDate", ""),
                    "description": strip_html(item.get("jobAd", {}).get("sections", {}).get("description", ""))[:500],
                    "salary": "",
                    "source": "smartrecruiters",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  SmartRecruiters: {e}")
        return []


# ---------------------------------------------------------------------------
# 85. Teamtailor — ATS with public job board
# ---------------------------------------------------------------------------

async def fetch_teamtailor(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from Teamtailor public job board."""
    try:
        async with session.get(
            "https://api.teamtailor.com/v1/jobs",
            params={"filter[published]": "true", "page[size]": 100},
            headers={**HEADERS, "Authorization": "Bearer public"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("data") or [])[:100]:
                attrs = item.get("attributes", {})
                title = attrs.get("title", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": attrs.get("department-name", "Unknown"),
                    "url": attrs.get("apply-url", ""),
                    "location": attrs.get("location", "Remote"),
                    "posted": attrs.get("published-at", ""),
                    "description": strip_html(attrs.get("description", ""))[:500],
                    "salary": "",
                    "source": "teamtailor",
                })
            return jobs[:100]
    except Exception as e:
        print(f"  Teamtailor: {e}")
        return []


# ---------------------------------------------------------------------------
# 86. RemoteOK JSON API (already have HTML, this is structured API)
# ---------------------------------------------------------------------------

async def fetch_remoteok_json(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch from RemoteOK structured JSON API with tags."""
    try:
        async with session.get(
            "https://remoteok.com/api?tag=translation",
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data or [])[1:]:  # Skip metadata
                title = item.get("position", "")
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("company", "Unknown"),
                    "url": f"https://remoteok.com/remote-jobs/{item.get('slug', '')}",
                    "location": item.get("location", "Remote"),
                    "posted": item.get("date", ""),
                    "description": strip_html(item.get("description", ""))[:500],
                    "salary": f"${item.get('salary_min', '')}-${item.get('salary_max', '')}" if item.get("salary_min") else "",
                    "source": "remoteok_json",
                    "tags": item.get("tags", []),
                })
            return jobs[:100]
    except Exception as e:
        print(f"  RemoteOK JSON: {e}")
        return []


# ---------------------------------------------------------------------------
# 87. Jobicy with geo=anywhere filter
# ---------------------------------------------------------------------------

async def fetch_jobicy_worldwide(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch worldwide jobs from Jobicy API."""
    try:
        async with session.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"count": 200, "geo": "anywhere"},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:200]:
                title = item.get("jobTitle", "")
                if not title:
                    continue
                salary_min = item.get("annualSalaryMin")
                salary_max = item.get("annualSalaryMax")
                salary = ""
                if salary_min and salary_max:
                    salary = f"${salary_min:,}-${salary_max:,}/yr"
                jobs.append({
                    "title": title,
                    "company": item.get("companyName", "Unknown"),
                    "url": item.get("url", ""),
                    "location": item.get("jobGeo", "Remote"),
                    "posted": item.get("pubDate", ""),
                    "description": strip_html(item.get("jobExcerpt", ""))[:500],
                    "salary": salary,
                    "source": "jobicy_worldwide",
                })
            return jobs[:200]
    except Exception as e:
        print(f"  Jobicy Worldwide: {e}")
        return []


# ---------------------------------------------------------------------------
# 88. Himalayas API with worldwide filter
# ---------------------------------------------------------------------------

async def fetch_himalayas_worldwide(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch worldwide jobs from Himalayas API."""
    try:
        async with session.get(
            "https://himalayas.app/jobs/api",
            params={"limit": 50, "offset": 0},
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            jobs = []
            for item in (data.get("jobs") or [])[:50]:
                title = item.get("title", "")
                if not title:
                    continue
                salary_min = item.get("minSalary")
                salary_max = item.get("maxSalary")
                salary = ""
                if salary_min and salary_max:
                    currency = item.get("salaryCurrency", "USD")
                    salary = f"{currency} {salary_min:,}-{salary_max:,}"
                # Check for location restrictions
                restrictions = item.get("locationRestrictions", [])
                location = "Remote (Worldwide)"
                if restrictions:
                    location = ", ".join(restrictions[:3])
                jobs.append({
                    "title": title,
                    "company": item.get("companyName", "Unknown"),
                    "url": f"https://himalayas.app/jobs/{item.get('slug', '')}",
                    "location": location,
                    "posted": "",
                    "description": strip_html(item.get("description", ""))[:500],
                    "salary": salary,
                    "source": "himalayas_worldwide",
                })
            return jobs[:50]
    except Exception as e:
        print(f"  Himalayas Worldwide: {e}")
        return []


# ---------------------------------------------------------------------------
# 89. Preply — Online tutoring platform, Arabic tutors in demand
# ---------------------------------------------------------------------------

async def fetch_preply(session: aiohttp.ClientSession) -> list[dict]:
    """Preply — online tutoring platform, Arabic tutors in demand."""
    try:
        url = "https://preply.com/en/api/v1/salaries?language=arabic&subject=english"
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                # Try the public jobs page instead
                url = "https://preply.com/en/online-jobs/arabic"
                async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp2:
                    if resp2.status != 200:
                        return []
                    html = await resp2.text()
                    jobs = []
                    links = re.findall(r'<a[^>]+href="(/en/[^"]*tutor[^"]*)"[^>]*>([^<]+)</a>', html, re.I)
                    for href, title in links[:30]:
                        title = strip_html(title).strip()
                        if title and len(title) > 5:
                            jobs.append({
                                "title": title,
                                "company": "Preply",
                                "url": f"https://preply.com{href}" if href.startswith("/") else href,
                                "location": "Remote (worldwide)",
                                "posted": "",
                                "description": f"Online tutoring position at Preply. Language teaching.",
                                "salary": "",
                                "source": "preply",
                            })
                    return jobs
            data = await resp.json(content_type=None)
            return []
    except Exception as e:
        print(f"  Preply: {e}")
        return []


# ---------------------------------------------------------------------------
# 90. Clickworker — Microtasks and AI training data
# ---------------------------------------------------------------------------

async def fetch_clickworker(session: aiohttp.ClientSession) -> list[dict]:
    """Clickworker — microtasks and AI training data."""
    try:
        url = "https://www.clickworker.com/en/microjobs/"
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Extract job/task listings
            titles = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', html, re.I)
            for title in titles[:20]:
                title = strip_html(title).strip()
                if title and len(title) > 5:
                    jobs.append({
                        "title": title,
                        "company": "Clickworker",
                        "url": "https://www.clickworker.com/en/microjobs/",
                        "location": "Remote (worldwide)",
                        "posted": "",
                        "description": f"Clickworker microtask: {title}. AI data collection and annotation.",
                        "salary": "",
                        "source": "clickworker",
                    })
            return jobs
    except Exception as e:
        print(f"  Clickworker: {e}")
        return []


# ---------------------------------------------------------------------------
# 91. Gengo — Translation platform jobs
# ---------------------------------------------------------------------------

async def fetch_gengo_jobs(session: aiohttp.ClientSession) -> list[dict]:
    """Gengo — translation platform jobs."""
    try:
        url = "https://gengo.com/translator-jobs/"
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Look for job listings
            links = re.findall(r'<a[^>]+href="(https://gengo\.com/[^"]*)"[^>]*>([^<]+)</a>', html, re.I)
            for href, title in links[:20]:
                title = strip_html(title).strip()
                if title and len(title) > 5 and any(w in title.lower() for w in ["translat", "languag", "locali", "content", "editor"]):
                    jobs.append({
                        "title": title,
                        "company": "Gengo",
                        "url": href,
                        "location": "Remote (worldwide)",
                        "posted": "",
                        "description": f"Translation job at Gengo. {title}",
                        "salary": "",
                        "source": "gengo",
                    })
            # Fallback: add a general Gengo listing
            if not jobs:
                jobs.append({
                    "title": "Freelance Translator (Arabic-English)",
                    "company": "Gengo",
                    "url": "https://gengo.com/translator-jobs/",
                    "location": "Remote (worldwide)",
                    "posted": "",
                    "description": "Gengo translation platform. Arabic-English translator position. Apply to join the network.",
                    "salary": "",
                    "source": "gengo",
                })
            return jobs
    except Exception as e:
        print(f"  Gengo: {e}")
        return []


# ---------------------------------------------------------------------------
# 92. Toloka — AI data annotation tasks
# ---------------------------------------------------------------------------

async def fetch_toloka(session: aiohttp.ClientSession) -> list[dict]:
    """Toloka — AI data annotation tasks."""
    try:
        url = "https://www.toloka.com/en/tasks"
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
            jobs = []
            # Look for task categories
            cats = re.findall(r'<(?:h[23]|div)[^>]*class="[^"]*task[^"]*"[^>]*>([^<]+)</(?:h[23]|div)>', html, re.I)
            if not cats:
                cats = re.findall(r'"name"\s*:\s*"([^"]*(?:translat|languag|content|annotat|label|arabic)[^"]*)"', html, re.I)
            for cat in cats[:15]:
                cat = strip_html(cat).strip()
                if cat and len(cat) > 3:
                    jobs.append({
                        "title": cat,
                        "company": "Toloka",
                        "url": "https://www.toloka.com/en/tasks",
                        "location": "Remote (worldwide)",
                        "posted": "",
                        "description": f"Toloka AI data task: {cat}. Data annotation and labeling.",
                        "salary": "",
                        "source": "toloka",
                    })
            if not jobs:
                jobs.append({
                    "title": "AI Data Annotation — Arabic Language Tasks",
                    "company": "Toloka",
                    "url": "https://www.toloka.com/en/tasks",
                    "location": "Remote (worldwide)",
                    "posted": "",
                    "description": "Toloka data annotation platform. Arabic language data collection and labeling tasks.",
                    "salary": "",
                    "source": "toloka",
                })
            return jobs
    except Exception as e:
        print(f"  Toloka: {e}")
        return []


# ---------------------------------------------------------------------------
# site: Search Queries — Removed (DuckDuckGo blocks automated requests)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Generic fetchers for auto-discovered sources
# ---------------------------------------------------------------------------


async def fetch_generic_rss(session: aiohttp.ClientSession, url: str, source_name: str = "discovered") -> list[dict]:
    """Fetch jobs from any RSS feed."""
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            xml = await resp.text()
            items = re.findall(r"<item>[\s\S]*?</item>", xml)
            jobs = []
            for item in items[:200]:
                def get(tag):
                    m = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", item)
                    return m.group(1) if m else ""
                title = strip_html(get("title")).strip()
                if not title:
                    continue
                jobs.append({
                    "title": title,
                    "company": (get("dc:creator") or source_name).strip(),
                    "url": get("link").strip(),
                    "location": "Remote",
                    "posted": get("pubDate") or "",
                    "description": strip_html(get("description") or get("content:encoded") or ""),
                    "salary": "",
                    "source": source_name,
                })
            return jobs
    except Exception as e:
        print(f"  {source_name}: {e}")
        return []


async def fetch_generic_json(session: aiohttp.ClientSession, url: str, source_name: str = "discovered") -> list[dict]:
    """Fetch jobs from any JSON API."""
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                for key in ["jobs", "results", "data", "postings", "positions"]:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break
                else:
                    return []
            else:
                return []
            jobs = []
            for j in items[:200]:
                title = j.get("title") or j.get("name") or j.get("position") or ""
                if not title:
                    continue
                jobs.append({
                    "title": str(title).strip(),
                    "company": str(j.get("company") or j.get("company_name") or source_name).strip(),
                    "url": j.get("url") or j.get("apply_url") or j.get("link") or "",
                    "location": j.get("location") or "Remote",
                    "posted": j.get("created_at") or j.get("published_at") or j.get("date") or "",
                    "description": strip_html(j.get("description") or j.get("description_html") or ""),
                    "salary": j.get("salary") or "",
                    "source": source_name,
                })
            return jobs
    except Exception as e:
        print(f"  {source_name}: {e}")
        return []


async def fetch_generic_html(session: aiohttp.ClientSession, url: str,
                             source_name: str = "discovered",
                             base_url: str = "") -> list[dict]:
    """Fetch jobs from a static HTML board via JSON-LD JobPosting, else job links.

    Covers verified boards that expose no feed (UNTalent, Idealist, Jobgether,
    Tarjama, Akhtaboot, Torjoman, TranslationDirectory, Cactus). Titles only —
    the scoring and quality gates decide relevance.
    """
    from urllib.parse import urljoin, urlparse
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()
    except Exception as e:
        print(f"  {source_name}: {e}")
        return []

    base = base_url or f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    jobs: list[dict] = []

    # 1) JSON-LD JobPosting blocks (most durable signal)
    for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>([\s\S]*?)</script>', html, re.I):
        try:
            data = json.loads(block.strip())
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            if isinstance(node.get("@graph"), list):
                stack.extend(node["@graph"])
            types = node.get("@type")
            types = types if isinstance(types, list) else [types]
            if "JobPosting" not in types:
                continue
            title = strip_html(str(node.get("title") or "")).strip()
            if not title:
                continue
            org = node.get("hiringOrganization") or {}
            company = org.get("name") if isinstance(org, dict) else ""
            location = "Remote"
            loc = node.get("jobLocation")
            if isinstance(loc, dict):
                addr = loc.get("address") or {}
                if isinstance(addr, dict):
                    location = ", ".join(
                        x for x in [addr.get("addressLocality"), addr.get("addressCountry")] if x
                    ) or "Remote"
            link = str(node.get("url") or node.get("sameAs") or "")
            if link and not link.startswith("http"):
                link = urljoin(base + "/", link)
            jobs.append({
                "title": title,
                "company": str(company or source_name),
                "url": link,
                "location": location,
                "posted": str(node.get("datePosted") or ""),
                "description": strip_html(str(node.get("description") or ""))[:500],
                "salary": "",
                "source": source_name,
            })
    if jobs:
        return jobs

    # 2) Fallback: job-ish <a> links
    seen: set = set()
    for href, inner in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', html, re.I):
        if not re.search(r"/job|/jobs/|/careers/|/position|/vacan|/opening|/offers?/|/projects?/", href, re.I):
            continue
        title = re.sub(r"\s+", " ", strip_html(inner)).strip()
        if not (4 <= len(title) <= 120):
            continue
        link = href.split("#")[0]
        if not link.startswith("http"):
            link = urljoin(base + "/", link)
        if link in seen:
            continue
        seen.add(link)
        jobs.append({
            "title": title, "company": source_name, "url": link,
            "location": "Remote", "posted": "", "description": "",
            "salary": "", "source": source_name,
        })
    return jobs


# ---------------------------------------------------------------------------
# Liveness check — same as JS
# ---------------------------------------------------------------------------


async def check_liveness(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.head(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=5)) as resp:
            if resp.status in (410, 404):
                return "expired"
            if 200 <= resp.status < 400:
                return "active"
            return "uncertain"
    except Exception:
        return "uncertain"


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------


async def run_scan():
    start_time = time.time()
    print("CareerOps GitHub Actions scan starting...")

    # Initialize scheduler
    import sys
    mode = "adaptive"
    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode = arg.split("=")[1]
        elif arg == "--mode" and sys.argv.index(arg) + 1 < len(sys.argv):
            mode = sys.argv[sys.argv.index(arg) + 1]
    
    scheduler = create_scheduler(mode)
    scheduler.start()
    print(f"  [scheduler] Mode: {mode}, Budget: {scheduler.total_budget}s ({scheduler.total_budget//60}min)")

    history = load_history()
    seen_urls = set(history["seen_urls"])
    # Gate on the timestamped, TTL-filtered URL store only. The long-lived
    # history["seen_urls"] list has no timestamps and used to suppress
    # still-open listings forever, so it no longer gates re-evaluation.
    all_seen = load_seen_urls()

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        # ---- Fetch all sources in parallel batches ----
        # ── Enterprise fetcher registry: deduped, tier-aware, circuit-breaker ──
        # Tier cap controls cost/latency: 1=lean (15 sources), 2=balanced (30), 3=full sweep (88)
        try:
            from fetchers.registry import TIER_CAP, REGISTRY
            tier_cap = TIER_CAP
        except Exception:
            tier_cap = 2

        def _should_run(name: str) -> bool:
            try:
                return REGISTRY.get(name, {}).get("tier", 3) <= tier_cap
            except:
                return True

        fetchers = []

        # Auto-discovered sources (from auto_sources.py)
        try:
            for src in get_auto_sources():
                fetchers.append(fetch_generic_rss(session, src["url"], src["name"]))
        except Exception as e:
            print(f"  Auto-sources load failed: {e}")

        def _blocked(name: str) -> bool:
            """Check if a source is probe-confirmed blocked from Actions IPs."""
            if FORCE_BLOCKED_SOURCES:
                return False
            return name in PROBE_BLOCKED_SOURCES

        # ── ATS company boards (Greenhouse / Lever / Ashby / Workable / SmartRecruiters) ──
        # These were imported but never dispatched, so the company lists in config
        # (and the probe-validated slugs) were dead config. Tier-gated via the registry.
        from fetchers.verified import (
            fetch_greenhouse_batch, fetch_lever_batch,
            fetch_ashby_boards, fetch_workable_boards, fetch_smartrecruiters_boards,
        )
        if _should_run("greenhouse"):
            fetchers.append(fetch_greenhouse_batch(session))
        if _should_run("lever"):
            fetchers.append(fetch_lever_batch(session))
        if _should_run("ashby"):
            fetchers.append(fetch_ashby_boards(session))
        if _should_run("workable"):
            fetchers.append(fetch_workable_boards(session))
        if _should_run("smartrecruiters"):
            fetchers.append(fetch_smartrecruiters_boards(session))

        # ── General remote boards (have Arabic jobs buried in them) ──
        if _should_run("remotive"):
            fetchers.append(fetch_remotive(session))
        if _should_run("remoteok"):
            fetchers.append(fetch_remoteok(session))
        if _should_run("weworkremotely"):
            fetchers.append(fetch_wwr(session))
        if _should_run("jobicy"):
            fetchers.append(fetch_jobicy_api(session))
        if _should_run("arbeitnow"):
            fetchers.append(fetch_arbeitnow(session))
        if _should_run("himalayas"):
            fetchers.append(fetch_himalayas_api(session))
        if _should_run("nodesk"):
            fetchers.append(fetch_nodesk(session))
        # Additional general boards with arabic filter
        if _should_run("remote1stjobs"):
            fetchers.append(fetch_remote1stjobs(session))
        if _should_run("realworkfromanywhere"):
            fetchers.append(fetch_realworkfromanywhere(session))
        if _should_run("workbeam"):
            fetchers.append(fetch_workbeam(session))

        # ── TRANSLATION & BILINGUAL ONLY — focused on Arabic-English ──
        # Every source here is specifically for translation, bilingual, or language jobs
        if _should_run("translation_jobs"):
            fetchers.append(fetch_translation_jobs(session))
        # ── JobSpy (Indeed + LinkedIn) — full descriptions → accurate language gate ──
        if _should_run("jobspy_indeed"):
            try:
                from fetchers.jobspy_fetch import fetch_jobspy
                fetchers.append(fetch_jobspy(session))
            except Exception as e:
                print(f"  JobSpy fetch load failed: {e}")
        if _should_run("smartcat"):
            fetchers.append(fetch_smartcat(session))
        if _should_run("gotranscript"):
            fetchers.append(fetch_gotranscript(session))
        if not _blocked("proz"):
            fetchers.append(fetch_proz(session))
        if _should_run("impactpool"):
            fetchers.append(fetch_impactpool(session))
        if _should_run("linkedin"):
            fetchers.append(fetch_linkedin_guest(session))
        # ── ESL / Tutoring platforms ──
        if _should_run("preply"):
            fetchers.append(fetch_preply(session))
        # ── AI Data Annotation platforms ──
        if _should_run("toloka"):
            fetchers.append(fetch_toloka(session))
        if _should_run("clickworker"):
            fetchers.append(fetch_clickworker(session))
        # ── Translation platforms ──
        if _should_run("gengo"):
            fetchers.append(fetch_gengo_jobs(session))
        # MENA / freelance — Arabic job boards
        if not _blocked("mostaql"):
            fetchers.append(fetch_mostaql(session))
        if not _blocked("for9a"):
            fetchers.append(fetch_for9a(session))
        if not _blocked("wuzzuf"):
            fetchers.append(fetch_wuzzuf(session))
        if not _blocked("bayt"):
            fetchers.append(fetch_bayt(session))
        if not _blocked("gulftalent"):
            fetchers.append(fetch_gulftalent(session))
        if not _blocked("naukrigulf"):
            fetchers.append(fetch_naukrigulf(session))
        if _should_run("jsearch"):
            fetchers.append(fetch_jsearch(session))
        # ── Worldwide Arabic search: DDG + verified feeds ──
        if WIDE_SEARCH_AVAILABLE:
            fetchers.append(fetch_worldwide_arabic_jobs(session))

        # ── Search Proxy: Google/DuckDuckGo bypass for blocked sites ──
        if SEARCH_PROXY_AVAILABLE:
            fetchers.append(fetch_blocked_sites_via_search(session))

        # ── Playwright search (real browser, bypasses 403s) ──
        if PLAYWRIGHT_AVAILABLE:
            fetchers.append(fetch_with_playwright(session))

        # ── Full registry sweep ──────────────────────────────────────────
        # The registry is the source list. Several registered fetchers were
        # never dispatched from here, so they existed as dead config. Run every
        # registry source that is not already dispatched and is within the tier
        # cap; per-source failures are isolated.
        try:
            from fetchers.registry import REGISTRY as _REGISTRY
            from fetchers.registry import PROBE_BLOCKED_SOURCES as _REG_BLOCKED
        except Exception:
            _REGISTRY, _REG_BLOCKED = {}, []
        import importlib as _importlib
        _explicit = {
            "greenhouse", "lever", "ashby", "workable", "smartrecruiters",
            "remotive", "remoteok", "weworkremotely", "jobicy", "arbeitnow",
            "himalayas", "nodesk", "remote1stjobs", "realworkfromanywhere",
            "workbeam", "translation_jobs", "smartcat", "gotranscript", "proz",
            "impactpool", "linkedin", "preply", "toloka", "clickworker", "gengo",
            "mostaql", "for9a", "wuzzuf", "bayt", "gulftalent", "naukrigulf",
            "jsearch", "arabic_companies",
        }
        _paid = set(getattr(_cfg, "PAID_PLATFORMS", []))
        _skip_blocked = set() if FORCE_BLOCKED_SOURCES else (
            set(PROBE_BLOCKED_SOURCES) | set(_REG_BLOCKED)
        )
        sweep_added = 0
        for _name, _info in _REGISTRY.items():
            if _name in _explicit or _name in _paid:
                continue
            if _info.get("tier", 3) > tier_cap:
                continue
            if _name in _skip_blocked:
                continue
            try:
                _fn = getattr(_importlib.import_module(_info["module"]), _info["class"])
                _coro = _fn(session)
                if asyncio.iscoroutine(_coro):
                    fetchers.append(_coro)
                    sweep_added += 1
            except Exception as e:
                print(f"  [registry] skip {_name}: {e}")
        print(f"  [registry] full sweep added {sweep_added} sources (tier cap {tier_cap})")

        # ── Worldwide feed sweep (verified RSS/JSON feeds) ───────────────
        _seen_feed_urls: set = set()
        feed_added = 0
        for _feed in list(WORLDWIDE_FEEDS)[:MAX_WORLDWIDE_FEEDS]:
            _url = _feed.get("url", "")
            if not _url or _url in _seen_feed_urls:
                continue
            _seen_feed_urls.add(_url)
            fetchers.append(fetch_generic_rss(session, _url, _feed.get("name", "worldwide")))
            feed_added += 1
        print(f"  [feeds] worldwide feeds added: {feed_added}")

        # ── Worldwide HTML board sweep (verified static boards) ──────────
        html_added = 0
        for _board in list(WORLDWIDE_HTML)[:MAX_WORLDWIDE_HTML]:
            _url = _board.get("url", "")
            if not _url:
                continue
            fetchers.append(fetch_generic_html(
                session, _url, _board.get("name", "worldwide_html"), _board.get("base", "")
            ))
            html_added += 1
        print(f"  [html] worldwide HTML boards added: {html_added}")

        BATCH = getattr(__import__('config', fromlist=['FETCH_BATCH_SIZE']), 'FETCH_BATCH_SIZE', 8) if 'config' in globals() else 8
        # Fallback to 5 if config missing
        BATCH = max(4, min(12, BATCH))  # clamp
        all_jobs: list[dict] = []
        fetcher_errors = 0
        fetcher_successes = 0
        for i in range(0, len(fetchers), BATCH):
            batch = fetchers[i : i + BATCH]
            results = await asyncio.gather(*batch, return_exceptions=True)
            for r in results:
                if isinstance(r, list):
                    all_jobs.extend(r)
                    fetcher_successes += 1
                elif isinstance(r, Exception):
                    print(f"  Fetcher error: {r}")
                    fetcher_errors += 1

        print(f"Total fetched: {len(all_jobs)} jobs ({fetcher_successes} sources OK, {fetcher_errors} errors)")
        if fetcher_errors > fetcher_successes:
            print(f"  WARNING: More fetcher errors ({fetcher_errors}) than successes ({fetcher_successes})")

        # Feed fetcher errors into health metrics so the CI alert sees them
        try:
            if _metrics and fetcher_errors > 0:
                _metrics.record_external_errors(fetcher_errors)
        except Exception:
            pass

        # ---- Free Forever Search: DuckDuckGo + sitemap (no API key) ----
        try:
            if discover_via_search is not None:
                print("🔍 Free search: DuckDuckGo + sitemap...")
                discovered = await discover_via_search(session)
                if discovered:
                    # dedup by URL against already fetched
                    seen_urls_discover = {j.get("url") for j in all_jobs if j.get("url")}
                    new_discovered = [j for j in discovered if j.get("url") not in seen_urls_discover]
                    if new_discovered:
                        print(f"  Search discovered: {len(new_discovered)} fresh URLs (free)")
                        all_jobs.extend(new_discovered)
                        print(f"  Total after search: {len(all_jobs)} jobs")
                else:
                    print("  Search discovered: 0 (free, no new URLs)")
        except Exception as e:
            print(f"  Free search skipped: {e}")

        
        # ---- Track source performance ----
        source_job_counts = {}
        source_match_counts = {}
        for job in all_jobs:
            src = job.get("source", "unknown")
            source_job_counts[src] = source_job_counts.get(src, 0) + 1
        
        # ---- Log source breakdown ----
        print("\n=== SOURCE BREAKDOWN ===")
        for src, count in sorted(source_job_counts.items(), key=lambda x: -x[1]):
            print(f"  {src}: {count} jobs")
        print(f"  TOTAL: {len(source_job_counts)} sources, {len(all_jobs)} jobs")
        print("========================\n")
        
        # ---- Metrics: record fetch phase ----
        try:
            if _metrics:
                for src, cnt in source_job_counts.items():
                    _metrics.record_fetch(src, cnt)
                _metrics.record_timing("fetch", time.time() - start_time)
        except: pass

        # ---- Score & filter ----
        scored: list[dict] = []
        dup_open: list[dict] = []  # previously-seen but still-open relevant roles
        near_misses: list[dict] = []
        fresh_total = 0
        old_but_verified = []
        filter_debug = {"no_url": 0, "paid": 0, "too_old": 0, "no_positive": 0,
                        "non_target": 0, "negative": 0, "not_worldwide": 0, "low_score": 0, "duplicate": 0,
                        "stub": 0, "in_person": 0, "no_signal": 0, "company_boost": 0}
        # Observability only: histogram of every scored job's match score so we
        # can tune MIN_MATCH_SCORE from data, not guesswork. No behavior change.
        score_dist = {"0": 0, "1-39": 0, "40-49": 0, "50-74": 0, "75-100": 0}
        
        # Load smart deduplication data
        smart_seen = load_smart_seen()

        for job in all_jobs:
            if not job.get("url"):
                filter_debug["no_url"] += 1
                continue
            if job.get("title"):
                job["title"] = strip_html(job["title"])
            if is_stub_listing(job):
                filter_debug["stub"] += 1
                continue

            # Soft gates are now TAGS, not drops: the job is still shown and scored,
            # and flagged for the reviewer to decide. Only truly unusable listings
            # (no URL, stub/portal, paid platform, >6 days old, duplicate) are dropped.
            flags: list[str] = []

            # In-person / onsite wording
            if is_in_person_gig(job):
                filter_debug["in_person"] += 1
                flags.append("in-person/onsite")

            # Location restrictions in title/description (US-only etc.)
            desc = (job.get("description") or "").lower()
            job_title = (job.get("title") or "").lower()
            job_loc = (job.get("location") or "").lower()
            EARLY_LOCATION_RESTRICTIONS = [
                re.compile(r"location\s+restriction", re.I),
                re.compile(r"only\s+available\s+in\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"eligible\s+(for\s+only|only\s+for|if\s+you\s+are\s+in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"must\s+be\s+(located\s+in|based\s+in|in)\s+the\s+(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"this\s+(job|position|role)\s+is\s+(only|restricted)\s+to\s+(the\s+)?(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"this\s+position\s+requires\s+(you\s+to\s+be|residence)\s+in\s+(the\s+)?(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"candidates\s+must\s+(be|remain)\s+(located|based)\s+in\s+(the\s+)?(u\.?\s*|)*s\.?\s*|united\s+states", re.I),
                re.compile(r"remote\s*[-–—,]\s*(us|usa|u\.s\.a?|united states)", re.I),
                re.compile(r"remote\s*[\(\[]\s*(us|usa|u\.s\.a?|united states)\s*[\)\]]", re.I),
            ]
            if any(p.search(desc) or p.search(job_title) or p.search(job_loc) for p in EARLY_LOCATION_RESTRICTIONS):
                filter_debug["not_worldwide"] += 1
                flags.append("location-restricted")

            # Smart deduplication — skip if company+title+location already seen
            if is_duplicate(job, smart_seen):
                filter_debug["duplicate"] += 1
                # Previously-seen must NOT mean invisible. Dedup exists to stop
                # re-ANNOUNCING the same job as NEW, not to hide a still-open,
                # relevant role from the daily available pool. Re-surface it.
                try:
                    p_ = normalize_date(job.get("posted"))
                    a_ = age_hours(p_) if p_ else float("inf")
                    d_ = job.get("description") or ""
                    if (p_ is None or a_ <= MAX_AGE_HOURS) and not is_paid_platform(job.get("source", "")) \
                            and not matches_negative(job.get("title", ""), d_) \
                            and is_open_worldwide_for_company(job.get("location", ""), d_, job.get("company", "")):
                        sc_ = get_match_score(job.get("title", ""), d_)
                        if sc_["score"] >= MIN_MATCH_SCORE and sc_["category"] != "Other" \
                                and len(dup_open) < OPEN_POOL_CAP:
                            dup_open.append({**job, "score": sc_["score"],
                                             "category": sc_["category"],
                                             "why": sc_.get("why", []),
                                             "dup_pool": True})
                except Exception:
                    pass
                continue

            # Filter out paid platforms
            if is_paid_platform(job.get("source", "")):
                filter_debug["paid"] += 1
                continue

            posted = normalize_date(job.get("posted"))
            age = age_hours(posted) if posted else float("inf")

            # Only drop jobs where we KNOW the date and it's older than 6 days
            if posted is not None and age > MAX_AGE_HOURS:
                filter_debug["too_old"] += 1
                continue

            fresh_total += 1
            is_fresh = posted is not None and age <= MAX_AGE_FRESH_HOURS

            title = job.get("title", "")

            # Non-target role wording (manager/strategist/etc.) -> tag, not drop
            if NON_TARGET_ROLE.search(title) and not NON_TARGET_ALLOWLIST.search(title):
                filter_debug["non_target"] += 1
                flags.append("non-target role title")

            # Negative sales/enterprise keywords -> tag, not drop (score penalizes too)
            if matches_negative(job.get("title", ""), job.get("description", "")):
                filter_debug["negative"] += 1
                flags.append("negative-keyword title")

            # Country-locked location wording -> tag, not drop
            if not is_open_worldwide_for_company(job.get("location", ""), job.get("description", ""), job.get("company", "")):
                filter_debug["not_worldwide"] += 1
                flags.append("country-locked location")

            # Single scoring path (keyword + learning + company bonus + priority)
            scored_job = score_job(job)
            # Record into the score histogram (observability for threshold tuning)
            _s = int(scored_job.get("score") or 0)
            if _s <= 0: score_dist["0"] += 1
            elif _s < 40: score_dist["1-39"] += 1
            elif _s < 50: score_dist["40-49"] += 1
            elif _s < 75: score_dist["50-74"] += 1
            else: score_dist["75-100"] += 1
            if scored_job.get("company_boost"):
                filter_debug["company_boost"] = filter_debug.get("company_boost", 0) + 1

            salary = job.get("salary") or extract_salary(job.get("description", ""))
            job_data = {
                **job,
                "postedISO": posted.isoformat() if posted else datetime.now(timezone.utc).isoformat(),
                "score": scored_job["score"],
                "category": scored_job["category"],
                "why": scored_job.get("why", []),
                "company_boost": scored_job.get("company_boost", 0),
                "salary": salary,
                "is_fresh": is_fresh,
                "age_hours": age,
                "flags": flags,
                "company_website": get_company_website(job.get("company", "")),
                "email": extract_email_from_text(job.get("description", "")),
                "tier": "STRONG" if scored_job["score"] >= 75 else ("GOOD" if scored_job["score"] >= 50 else "REVIEW"),
            }

            # Mark as seen for smart deduplication
            mark_seen(job, smart_seen)

            # Record company pattern for learning
            if scored_job["score"] > 0:
                try:
                    record_company_match(
                        job.get("company", ""),
                        job.get("title", ""),
                        scored_job.get("category", "Other"),
                        scored_job["score"],
                    )
                except Exception:
                    pass

            # Separate fresh jobs from older jobs.
            # A job with no scoring signal (0 points, or category "Other" with no
            # company boost) is not a match. Company-boosted roles carry a real
            # category now, so they survive instead of being discarded here.
            no_signal = (
                scored_job["score"] <= 0
                or (scored_job.get("category") == "Other" and not scored_job.get("company_boost"))
            )
            if is_fresh:
                if no_signal:
                    filter_debug["no_signal"] = filter_debug.get("no_signal", 0) + 1
                    continue
                scored.append(job_data)
                src = job.get("source", "unknown")
                source_match_counts[src] = source_match_counts.get(src, 0) + 1
            else:
                # Older jobs go to a separate list for Ollama verification,
                # but never re-report jobs the user has already seen
                if job_data["url"] in all_seen:
                    filter_debug["duplicate"] += 1
                    continue
                old_but_verified.append(job_data)

        def is_genuine(title: str) -> bool:
            # If title has NON_TARGET patterns but also has allowed target keywords, it's OK
            if NON_TARGET_ROLE.search(title):
                if NON_TARGET_ALLOWLIST.search(title):
                    pass  # Has target keywords, allow through
                else:
                    return False
            hits = 0
            title_hits = 0
            for bucket in MATCH_BUCKETS:
                for pattern, _ in bucket["phrases"]:
                    if pattern.search(title):
                        hits += 1
                        title_hits += 1
            return title_hits > 0 or hits >= 2

        for job in all_jobs:
            if not job.get("url") or len(near_misses) >= NEAR_MISS_LIMIT:
                continue
            if job.get("url") in all_seen:
                continue
            posted = normalize_date(job.get("posted"))
            age = age_hours(posted) if posted else float("inf")
            if posted is not None and age > MAX_AGE_HOURS:
                continue
            if matches_negative(job.get("title", ""), job.get("description", "")):
                continue
            if not is_open_worldwide(job.get("location", ""), job.get("description", "")):
                continue
            sc = get_match_score(job.get("title", ""), job.get("description", ""))
            if sc["score"] < NEAR_MISS_MIN or sc["score"] >= MIN_MATCH_SCORE or sc["category"] == "Other":
                continue
            if not is_genuine(job.get("title", "")):
                continue
            salary = job.get("salary") or extract_salary(job.get("description", ""))
            near_misses.append({
                **job,
                "postedISO": posted.isoformat() if posted else "",
                "score": sc["score"],
                "category": sc["category"],
                "why": sc.get("why", []),
                "salary": salary,
            })

        near_misses.sort(key=lambda j: j["score"], reverse=True)

        # Sort fresh jobs by score (highest first), then by age (newest first)
        scored.sort(key=lambda j: (-j["score"], j.get("age_hours", 0)))

        # Sort old jobs by score (highest first)
        old_but_verified.sort(key=lambda j: -j["score"])

        new_jobs = [j for j in scored if j["url"] not in all_seen]

        # Print filter debug summary
        print("\n📊 Filter Debug Summary:")
        for key, val in sorted(filter_debug.items()):
            if val > 0:
                print(f"   {key}: {val}")
        print(f"   SCORED (passed all filters): {len(scored)}")
        print(f"   Near Misses: {len(near_misses)}")
        print(f"   Old but Verified: {len(old_but_verified)}")
        # Score distribution across ALL fetched jobs (tuning aid). The 40-49
        # bucket is what lowering MIN_MATCH_SCORE 50->40 would newly surface.
        print("   Score distribution (all jobs): "
              f"0={score_dist['0']}  1-39={score_dist['1-39']}  "
              f"40-49={score_dist['40-49']}  50-74={score_dist['50-74']}  "
              f"75-100={score_dist['75-100']}")
        print(f"SCORE_DIST={json.dumps(score_dist)}")

        # ---- Liveness check on top fresh jobs ----
        to_check = new_jobs[:TOP_LIVENESS_CHECK]
        liveness_results = await asyncio.gather(
            *[check_liveness(session, j["url"]) for j in to_check],
            return_exceptions=True,
        )
        verified: list[dict] = []
        expired: list[dict] = []
        for i, job in enumerate(to_check):
            status = liveness_results[i] if isinstance(liveness_results[i], str) else "uncertain"
            if status in ("active", "uncertain"):
                verified.append(job)
            else:
                expired.append(job)
        
        # Add remaining fresh jobs that weren't checked
        verified.extend(new_jobs[TOP_LIVENESS_CHECK:])
        
        # Sort verified jobs: fresh first, then by score
        verified.sort(key=lambda j: (-j.get("is_fresh", False), -j["score"]))
        
        print(f"Scored: {len(scored)}, Old but verified: {len(old_but_verified)}, New: {len(new_jobs)}, Active: {len(verified)}, Expired: {len(expired)}")
        print(f"Filter funnel: {filter_debug}")

        # ---- AI analysis (top N) — verdict is now a real gate, not a footnote ----
        ai_cap = max(0, AI_ANALYZE_CAP)
        verified = await analyze_jobs_with_ollama(verified[:ai_cap]) + verified[ai_cap:]
        ai_dropped = [j for j in verified if ai_poor_fit(j)]
        if ai_dropped:
            for j in ai_dropped:
                j["ai_reject"] = True
            verified = [j for j in verified if not ai_poor_fit(j)]
            print(f"  AI poor-fit gate dropped {len(ai_dropped)} fresh: "
                  f"{', '.join(sorted({(j.get('title') or '?')[:40] for j in ai_dropped}))}")

        # Old jobs: RE-SCORE with the same path as fresh jobs, then filter.
        # A job passes if it clears the normal threshold, or reaches the (lower)
        # company floor while carrying a company boost.
        old_verified = []
        for job in old_but_verified:
            rescored = score_job(job)
            passes = rescored["score"] >= MIN_MATCH_SCORE or (
                rescored.get("company_boost") and rescored["score"] >= COMPANY_MIN_SCORE
            )
            if passes:
                job["score"] = rescored["score"]
                job["category"] = rescored["category"]
                job["company_boost"] = rescored.get("company_boost", 0)
                job["is_old_verified"] = True
                old_verified.append(job)
        print(f"  Old jobs re-scored & verified: {len(old_verified)} (from {len(old_but_verified)} old)")

        # The AI gate also applies to previously-verified jobs, so a poor-fit
        # role that slipped through an earlier scan stops being re-surfaced as
        # "Still Available".
        if old_verified:
            old_ai_cap = max(0, min(OLD_AI_VERIFY_CAP, len(old_verified)))
            old_verified = (await analyze_jobs_with_ollama(old_verified[:old_ai_cap])
                            + old_verified[old_ai_cap:])
            old_ai_dropped = [j for j in old_verified if ai_poor_fit(j)]
            if old_ai_dropped:
                for j in old_ai_dropped:
                    j["ai_reject"] = True
                old_verified = [j for j in old_verified if not ai_poor_fit(j)]
                print(f"  AI poor-fit gate dropped {len(old_ai_dropped)} old: "
                      f"{', '.join(sorted({(j.get('title') or '?')[:40] for j in old_ai_dropped}))}")

        # Combine: fresh jobs first, then old verified jobs at the end
        final_verified = verified + old_verified

        # Re-surface the still-open relevant pool (previously-seen jobs) so the
        # daily digest shows the OPEN universe of translation roles, not only
        # brand-new postings. Dedup suppresses re-announcing them as NEW, never
        # hides them.
        if dup_open:
            dup_open.sort(key=lambda j: -int(j.get("score") or 0))
            final_verified += dup_open[:OPEN_POOL_CAP]
            print(f"  Open pool: added {len(dup_open[:OPEN_POOL_CAP])} previously-seen open roles "
                  f"(of {len(dup_open)} eligible duplicates)")

        # Bound the heavy pipeline + digest: STRONG(75+) first, then GOOD(50-74),
        # then company-boosted roles at the lower company floor (40-49). Anything
        # below that must not reach Fresh Matches or the digest; Excel "All Jobs"
        # still carries every scanned posting.
        final_verified.sort(key=lambda j: -int(j.get("score") or 0))
        strong = [j for j in final_verified if int(j.get("score") or 0) >= 75][:30]
        good = [j for j in final_verified
                if MIN_MATCH_SCORE <= int(j.get("score") or 0) < 75][:20]
        company_floor = [j for j in final_verified
                         if COMPANY_MIN_SCORE <= int(j.get("score") or 0) < MIN_MATCH_SCORE
                         and j.get("company_boost")][:15]
        final_verified = strong + good + company_floor
        final_verified.sort(key=lambda j: (-j.get("is_fresh", False), -int(j.get("score") or 0)))

        quality_drops: dict = {}
        before_q = len(final_verified)
        final_verified = drop_unqualified_matches(final_verified, quality_drops)
        if quality_drops:
            print(f"Quality/location hard-fail dropped {before_q - len(final_verified)}: {quality_drops}")

        # ‑‑ Pre-delivery AI audit + mistake memory (see it before we send it) ‑‑
        try:
            from mistake_memory import load as load_mistakes
            from mistake_memory import note_mistake
            audit_pool = [j for j in final_verified if not j.get("ai_verdict")][:AUDIT_CAP]
            if audit_pool:
                print(f"  Pre-delivery AI audit: {len(audit_pool)} candidates checked "
                      f"against {len(load_mistakes())} known mistakes")
                await analyze_jobs_with_ollama(audit_pool)
            audited_bad = [j for j in final_verified if ai_poor_fit(j)]
            if audited_bad:
                for j in audited_bad:
                    note_mistake(j, "ai_poor_fit")
                final_verified = [j for j in final_verified if not ai_poor_fit(j)]
                print(f"  AI audit dropped {len(audited_bad)} before delivery: "
                      f"{', '.join(sorted({(j.get('title') or '?')[:40] for j in audited_bad}))}")
        except Exception as e:
            print(f"  Pre-delivery AI audit skipped: {e}")

        # ---- Free Forever Intel: email/urgency for top 5 only ----
        try:
            if enrich_jobs_with_intel is not None and final_verified:
                intel_targets = final_verified[:5]
                print(f"🧠 Free intel: enriching {len(intel_targets)} matches (email+urgency)...")
                seen_for_desp = load_smart_seen() if 'load_smart_seen' in globals() else None
                enriched = await enrich_jobs_with_intel(intel_targets, session, seen_for_desp)
                # Merge enriched data back
                enriched_urls = {j["url"]: j for j in enriched if j.get("url")}
                for i, job in enumerate(final_verified):
                    if job.get("url") in enriched_urls:
                        final_verified[i].update(enriched_urls[job["url"]])
                with_email = sum(1 for j in final_verified[:5] if j.get("hiring_email"))
                print(f"  Intel done: {with_email} with email")
        except Exception as e:
            print(f"  Intel enrichment skipped: {e}")

        # ---- Employer email discovery: real inbox, not the board relay ----
        if EMAIL_FINDER_ENABLED:
            try:
                email_targets = final_verified[:EMAIL_FIND_TARGETS]
                if email_targets:
                    print(f"  Email discovery: resolving {len(email_targets)} employer inboxes...")
                    await enrich_jobs_with_emails(session, email_targets)
                    harvested = sum(1 for j in email_targets
                                    if j.get("hiring_email") and not j.get("email_guessed"))
                    guessed = sum(1 for j in email_targets
                                  if j.get("hiring_email") and j.get("email_guessed"))
                    print(f"  Email discovery: {harvested} employer, {guessed} guessed")
                    sample = "; ".join(
                        f"{j.get('company','?')}={j['hiring_email']}"
                        for j in email_targets if j.get("hiring_email")
                    )
                    if sample:
                        print(f"  Email discovery sample: {sample[:500]}")
            except Exception as e:
                print(f"  Email discovery skipped: {e}")
        
        # ---- Research companies for top 5 only ----
        try:
            research_targets = final_verified[:5]
            final_verified_researched = research_companies_batch(research_targets)
            researched_urls = {j["url"]: j for j in final_verified_researched if j.get("url")}
            for i, job in enumerate(final_verified[:5]):
                if job.get("url") in researched_urls:
                    final_verified[i].update(researched_urls[job["url"]])
            boosted = sum(1 for j in final_verified[:5] if j.get("score_adjustment", 0) > 0)
            print(f"Company research: top 5, {boosted} boosted")
        except Exception as e:
            print(f"Company research failed: {e}")
        
        # ---- Deep read top 3 candidates only ----
        try:
            deep_targets = final_verified[:3]
            enriched_deep = enrich_jobs_with_deep_read(deep_targets, max_deep_reads=3)
            deep_urls = {j["url"]: j for j in enriched_deep if j.get("url")}
            for i, job in enumerate(final_verified[:3]):
                if job.get("url") in deep_urls:
                    final_verified[i].update(deep_urls[job["url"]])
            deep_read_count = sum(1 for j in final_verified[:3] if j.get("deep_read"))
            print(f"Deep read completed: {deep_read_count} pages read")
        except Exception as e:
            print(f"Deep read failed: {e}")
        
        # ---- Generate cover letters for top 5 matches only ----
        try:
            cl_targets = final_verified[:5]
            cl_enriched = await generate_all_cover_letters(cl_targets)
            cl_urls = {j["url"]: j for j in cl_enriched if j.get("url")}
            for i, job in enumerate(final_verified[:5]):
                if job.get("url") in cl_urls:
                    final_verified[i].update(cl_urls[job["url"]])
            ai_count = sum(1 for j in final_verified[:5] if j.get("cover_letter_ai"))
            print(f"Generated {min(5, len(final_verified))} cover letters ({ai_count} AI-enhanced).")
        except Exception as e:
            print(f"Cover letter generation failed: {e}")
        
        # ---- Generate interview prep for top 3 matches (score >= 85%) ----
        try:
            prep_targets = [j for j in final_verified[:5] if int(j.get("score", 0)) >= 85][:3]
            if prep_targets:
                prep_enriched = generate_interview_prep_for_top_matches(prep_targets, min_score=85)
                prep_urls = {j["url"]: j for j in prep_enriched if j.get("url")}
                for i, job in enumerate(final_verified[:5]):
                    if job.get("url") in prep_urls:
                        final_verified[i].update(prep_urls[job["url"]])
                prep_count = sum(1 for j in final_verified[:5] if j.get("interview_prep_generated"))
                if prep_count > 0:
                    print(f"Generated interview prep for {prep_count} top matches.")
        except Exception as e:
            print(f"Interview prep generation failed: {e}")

        # ---- Build notifications ----
        elapsed = f"{time.time() - start_time:.1f}"
        # Count sources that actually delivered jobs this scan;
        # fall back to the configured source list when nothing was fetched.
        configured_sources = {
            "greenhouse", "lever", "remotive", "remoteok", "weworkremotely", "jobicy",
            "nodesk", "arbeitnow", "yayremote", "remote1stjobs", "realworkfromanywhere",
            "mostaql", "for9a", "khamsat", "ureed", "wuzzuf", "daleel", "aqar", "tajer",
            "linkedin", "bayt", "gulftalent", "naukrigulf", "craigslist", "upwork",
            "fiverr", "toptal", "flexjobs", "remote.co", "justremote", "himalayas",
            "glassdoor", "indeed", "ziprecruiter", "wellfound", "workingnomads",
            "jobspresso", "hirelatam", "landing.jobs",
            # New high-quality sources
            "himalayas_api", "jobicy_api", "workbeam", "remotive_api", "remoteok_api",
            "wwr_api", "justremote_api", "jobspresso_api", "workingnomads_api",
            "hirelatam_api", "arbeitnow_api", "jobicy_rss", "himalayas_rss",
        }
        sources_with_jobs = {j.get("source") for j in all_jobs if j.get("source")}
        source_count = len(sources_with_jobs) if sources_with_jobs else len(configured_sources)

        stats = history["scan_stats"]
        stats["total_scans"] += 1
        stats["total_matches"] += len(final_verified)
        stats["last_scan_date"] = _libya_today()

        scan_info = {
            "elapsed": elapsed,
            "all_count": len(all_jobs),
            "source_count": source_count,
            "fresh_count": fresh_total,
            "old_verified_count": len(old_verified),
            "near_misses": near_misses,
        }
        
        # ---- Record source performance ----
        try:
            for src, count in source_job_counts.items():
                matches = source_match_counts.get(src, 0)
                record_source_run(src, count, matches)
            print("Source performance recorded.")
        except Exception as e:
            print(f"Source tracking failed: {e}")
        
        # ---- Record evolution (the brain learns) ----
        try:
            categories = [j.get("category", "Other") for j in final_verified]
            source_matches = {}
            for j in final_verified:
                src = j.get("source", "unknown")
                source_matches[src] = source_matches.get(src, 0) + 1
            
            record_scan({
                "total_fetched": len(all_jobs),
                "matches": len(final_verified),
                "old_verified": len(old_verified),
                "near_misses": len(near_misses),
                "sources": source_count,
                "fresh_count": fresh_total,
                "categories": categories,
                "source_matches": source_matches,
                "learning_insights": get_learning_insights(),
            })
            print("Evolution brain updated.")
        except Exception as e:
            print(f"Evolution tracking failed: {e}")
        
        # ---- Cleanup dead sources (monthly) ----
        try:
            removed = cleanup_dead_sources()
            if removed:
                print(f"Cleaned up dead sources: {removed}")
        except Exception as e:
            print(f"Source cleanup failed: {e}")
        
        # ---- Cleanup old company cache ----
        try:
            removed_cache = cleanup_old_cache()
            if removed_cache > 0:
                print(f"Cleaned up {removed_cache} old company cache entries")
        except Exception as e:
            print(f"Company cache cleanup failed: {e}")

        # ---- Classify job lifecycle (NEW / OLD / EXPIRED) ----
        try:
            lifecycle = classify_lifecycle(final_verified, scan_info)
            new_jobs_lc = lifecycle["new_jobs"]
            old_jobs_lc = lifecycle["old_jobs"]
            expired_jobs_lc = lifecycle["expired_jobs"]
            scan_info = lifecycle["scan_info"]
        except Exception as e:
            print(f"Lifecycle classification failed: {e}")
            new_jobs_lc = final_verified
            old_jobs_lc = []
            expired_jobs_lc = []

        # ---- Employer email discovery for OLD "Still Available" matches ----
        # The digest shows these every run until they expire, so they deserve the
        # same real-inbox enrichment as new matches.
        if EMAIL_FINDER_ENABLED and old_jobs_lc:
            try:
                old_email_targets = [j for j in old_jobs_lc if not j.get("hiring_email")][:EMAIL_FIND_TARGETS]
                if old_email_targets:
                    await enrich_jobs_with_emails(session, old_email_targets)
                    resolved = sum(1 for j in old_email_targets if j.get("hiring_email"))
                    print(f"  Email discovery (old): {resolved}/{len(old_email_targets)} inboxes resolved")
                    sample = "; ".join(
                        f"{j.get('company','?')}={j['hiring_email']}"
                        for j in old_email_targets if j.get("hiring_email")
                    )
                    if sample:
                        print(f"  Email discovery (old) sample: {sample[:500]}")
            except Exception as e:
                print(f"  Email discovery (old) skipped: {e}")

        # ---- Generate Excel ----
        # User-facing date/time in Libya (Africa/Tripoli, UTC+2), never raw UTC
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        from notifier import now_libya
        libya_now = now_libya()
        date_str = libya_now.strftime("%Y-%m-%d")
        excel_path = OUTPUT_DIR / f"careerops-scan-{date_str}.xls"
        try:
            # Pass the actual scan time (Libya), not the elapsed duration
            scan_time_str = libya_now.strftime("%I:%M %p")
            excel_xml = generate_excel(final_verified, scan_time_str, near_misses, all_jobs, scan_info, stats)
            excel_path.write_text(excel_xml, encoding="utf-8")
            print(f"Excel saved: {excel_path}")
        except Exception as e:
            print(f"Excel generation failed: {e}")
            excel_path = None
        
        # ---- Check for unapplied jobs and send reminders ----
        try:
            from excel_generator import load_applications, load_fresh_history
            apps = load_applications()
            all_fresh = load_fresh_history()
            unapplied = [j for j in all_fresh if j.get("url") and j["url"] not in apps]
            if unapplied:
                # Send reminder about unapplied jobs
                reminder_msg = f"REMINDER: You have {len(unapplied)} unapplied jobs from previous scans!\n\n"
                for j in unapplied[:5]:  # Show top 5
                    reminder_msg += f"• {j.get('title', 'Unknown')} ({j.get('score', 0)}%)\n"
                if len(unapplied) > 5:
                    reminder_msg += f"\n... and {len(unapplied) - 5} more. Check your Excel!"
                print(f"Unapplied jobs reminder: {len(unapplied)} jobs pending")
                # This will be sent as part of the Telegram message
        except Exception as e:
            print(f"Reminder check failed: {e}")

        # ---- Append to accumulating scan history ----
        try:
            append_to_scan_history(final_verified, scan_info)
            print("Scan history accumulated.")
        except Exception as e:
            print(f"Scan history accumulation failed: {e}")

        # ---- Send Telegram ----
        telegram_sent = False
        try:
            from notifier import build_telegram
            tg_msg = build_telegram(final_verified, scan_info, stats,
                                    lifecycle_new=new_jobs_lc,
                                    lifecycle_old=old_jobs_lc,
                                    lifecycle_expired=expired_jobs_lc)
            telegram_sent = await send_telegram(tg_msg)
        except Exception as e:
            print(f"Telegram error: {e}")

        # ---- Send Email ----
        email_sent = False
        try:
            from notifier import build_email, now_libya
            email_result = build_email(final_verified, scan_info, stats,
                                      lifecycle_new=new_jobs_lc,
                                      lifecycle_old=old_jobs_lc,
                                      lifecycle_expired=expired_jobs_lc)
            libya_now = now_libya()
            subj_time = libya_now.strftime("%I:%M %p")
            subj_date = libya_now.strftime("%Y-%m-%d")
            n_new = len(new_jobs_lc)
            n_old = len(old_jobs_lc)
            if n_new > 0 and n_old > 0:
                email_subject = f"CareerOps \u2014 {n_new} New + {n_old} Still Available \u00b7 {subj_date}"
            elif n_new > 0:
                email_subject = f"CareerOps \u2014 {n_new} New Match{'es' if n_new != 1 else ''} \u00b7 {subj_date} {subj_time} Libya"
            elif n_old > 0:
                email_subject = f"CareerOps \u2014 {n_old} Still Available \u00b7 {subj_date} {subj_time} Libya"
            else:
                email_subject = f"CareerOps \u2014 0 New Matches \u00b7 {subj_date} {subj_time} Libya"
            # Collect PDF cover letter paths
            pdf_paths = [j.get("cover_letter_path", "") for j in final_verified if j.get("cover_letter_path")]
            email_sent = await send_email(
                email_subject,
                email_result["text"],
                email_result["html"],
                str(excel_path) if excel_path else None,
                pdf_paths if pdf_paths else None
            )
        except Exception as e:
            print(f"Email error: {e}")

        # ---- Save history ----
        for j in scored:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        for j in near_misses:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        for j in final_verified:
            if j["url"] not in seen_urls:
                seen_urls.add(j["url"])
        history["seen_urls"] = list(seen_urls)
        history["scan_stats"] = stats
        save_history(history)

        # ---- Also persist to the cross-session seen URLs file (timestamped) ----
        all_seen |= set(j["url"] for j in scored)
        all_seen |= set(j["url"] for j in near_misses)
        all_seen |= set(j["url"] for j in final_verified)
        save_seen_urls(all_seen)
        
        # ---- Save smart deduplication data ----
        save_smart_seen(smart_seen)
        dup_count = filter_debug.get("duplicate", 0)
        if dup_count > 0:
            print(f"Smart dedup: skipped {dup_count} duplicate jobs")

        # ── Persist metrics & health ──
        try:
            if _metrics:
                _metrics.record_funnel(filter_debug)
                _metrics.record_timing("total", time.time() - start_time)
                _metrics.persist_metrics()
                if _log:
                    _log.info(f"scan done matched={len(final_verified)} fetched={len(all_jobs)} health={_metrics.get_health()['health_score']}%")
        except Exception as e:
            print(f"metrics final persist failed: {e}")

        elapsed_final = f"{time.time() - start_time:.1f}"
        print(f"Scan complete in {elapsed_final}s. Telegram: {telegram_sent}, Email: {email_sent}")

        # Health check alert
        if fetcher_errors > 0:
            try:
                alert_msg = f"\u26a0\ufe0f CareerOps health alert: {fetcher_errors} source(s) failed this scan. Check: https://github.com/waleedba19/career-ops-scanner/actions"
                await send_telegram(alert_msg)
            except Exception:
                pass
        
        # Scheduler status
        scheduler_status = scheduler.get_status()
        print(f"  [scheduler] Status: {scheduler_status['elapsed']:.0f}s elapsed, {scheduler_status['remaining']:.0f}s remaining")
        print(f"  [scheduler] Tiers: {scheduler_status['available_tiers']}, AI jobs: {scheduler_status['max_ai_jobs']}")

        # Output JSON result for GitHub Actions
        result = {
            "matched": len(scored),
            "old_verified": len(old_verified),
            "near_miss_count": len(near_misses),
            "verified_count": len(final_verified),
            "expired_count": len(expired),
            "all_count": len(all_jobs),
            "source_count": source_count,
            "elapsed": elapsed_final,
            "telegram_sent": telegram_sent,
            "email_sent": email_sent,
            "score_dist": score_dist,
        }
        print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_scan())
