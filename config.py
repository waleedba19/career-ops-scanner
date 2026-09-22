"""
CareerOps Central Configuration — Single Source of Truth
Enterprise-grade config with env overrides, path resolution, and feature flags.
"""
import os
from pathlib import Path
from datetime import timezone

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
STATE_DIR = ROOT / "state"
COVER_LETTER_DIR = OUTPUT_DIR / "cover_letters"
INTERVIEW_PREP_DIR = OUTPUT_DIR / "interview_prep"

# Ensure output exists for local runs (CI restores via state_sync.py)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Scanning ─────────────────────────────────────────────────────────────
MIN_MATCH_SCORE = int(os.getenv("CAREEROPS_MIN_SCORE", "50"))  # 75-100 STRONG, 50-74 GOOD, <50 REVIEW
MAX_AGE_HOURS = int(os.getenv("CAREEROPS_MAX_AGE_H", "336"))  # 14 days — remote jobs stay open 2-3 weeks
MAX_AGE_FRESH_HOURS = float(os.getenv("CAREEROPS_FRESH_H", "48"))  # 48h — most translation jobs post 1-2 days ago
NEAR_MISS_MIN = 40
NEAR_MISS_MAX = 49
NEAR_MISS_LIMIT = int(os.getenv("CAREEROPS_NEAR_MISS_LIMIT", "6"))
TOP_LIVENESS_CHECK = int(os.getenv("CAREEROPS_LIVENESS_TOP", "6"))
HISTORY_MAX = 5000
JOB_EXPIRY_DAYS = int(os.getenv("CAREEROPS_JOB_EXPIRY_DAYS", "3"))  # days before a match expires from notifications
FETCH_TIMEOUT = int(os.getenv("CAREEROPS_FETCH_TIMEOUT", "12"))
FETCH_BATCH_SIZE = int(os.getenv("CAREEROPS_BATCH_SIZE", "8"))
FETCH_CONCURRENCY = int(os.getenv("CAREEROPS_CONCURRENCY", "25"))

# ── Deduplication ────────────────────────────────────────────────────────
# A job seen once used to be suppressed forever, so the same inventory was
# re-served every scan and reached scoring zero times. Fingerprints and URLs
# now expire, so stale "seen" marks stop hiding still-open listings.
DEDUP_TTL_DAYS = int(os.getenv("CAREEROPS_DEDUP_TTL_DAYS", "14"))
DEDUP_ENABLED = os.getenv("CAREEROPS_DEDUP_ENABLED", "1") == "1"

# ── Matching quality ─────────────────────────────────────────────────────
# Max jobs sent to Groq AI for a personal note (keyword scoring stays primary).
AI_ANALYZE_CAP = int(os.getenv("CAREEROPS_AI_CAP", "10"))
# Top N previously-verified (old) jobs also get AI verification each run, so a
# poor-fit role that slipped through earlier scans is caught before the digest.
OLD_AI_VERIFY_CAP = int(os.getenv("CAREEROPS_OLD_AI_CAP", "8"))
# Final pre-delivery AI audit: re-verify the exact jobs about to be emailed /
# archived, then drop anything Groq still rates Poor/Weak. The AI prompt also
# reads the mistake ledger (state/mistakes.json) so it re-checks repeat patterns.
AUDIT_CAP = int(os.getenv("CAREEROPS_AUDIT_CAP", "8"))
# A job at a trusted translation/AI company with a high-relevance title is a
# match even without a keyword hit — accepted at this (lower) floor.
COMPANY_MIN_SCORE = int(os.getenv("CAREEROPS_COMPANY_MIN_SCORE", "40"))

# ── Employer email discovery ─────────────────────────────────────────────
# Resolve the employer's real inbox (search their site) instead of the job
# board's relay address. Runs on the top N matches only.
EMAIL_FINDER_ENABLED = os.getenv("CAREEROPS_EMAIL_FINDER", "1") == "1"
EMAIL_FIND_TARGETS = int(os.getenv("CAREEROPS_EMAIL_TARGETS", "10"))

# ── Sources ──────────────────────────────────────────────────────────────
# Primary tier — high signal, low noise — FOCUSED ON ARABIC TRANSLATION
TIER_1_SOURCES = [
    "greenhouse", "lever", "remotive", "remoteok", "weworkremotely",
    "jobicy", "arbeitnow", "himalayas", "jobicy_api",
    "translation_jobs", "linkedin",
    "preply", "toloka", "gengo",  # NEW
]
# Secondary tier — good volume — MENA Focus
TIER_2_SOURCES = [
    "nodesk", "yayremote", "remote1stjobs", "realworkfromanywhere",
    "workingnomads", "jobspresso", "justremote", "hirelatam",
    "writing_jobs", "edtech_jobs",
    "clickworker",  # NEW
]
# Tertiary — niche / MENA (noisy, use sparingly)
TIER_3_SOURCES = [
    "bayt", "gulftalent", "naukrigulf",
    "peopleperhour", "guru",
]

# Paid platforms — auto-reject (fees to apply)
PAID_PLATFORMS = ["flexjobs", "tophire", "wellfound", "ziprecruiter"]

# Sources the probe confirmed are BLOCKED from GitHub Actions IPs (403/429 +
# challenge pages) — requesting them only burns time. They are skipped unless
# CAREEROPS_FORCE_BLOCKED=1 (e.g. when running from a residential IP).
PROBE_BLOCKED_SOURCES = [
    "mostaql", "ureed", "wuzzuf", "bayt", "gulftalent", "proz",
    # 2026-09-17 Actions-IP probe: 403/challenge — skip to stop burning time.
    "guru", "dailyremote", "europeremotely", "euremotejobs", "remotejobleads",
]
FORCE_BLOCKED_SOURCES = os.getenv("CAREEROPS_FORCE_BLOCKED", "0") == "1"

# ── Worldwide feed sweep ─────────────────────────────────────────────────
# Extra RSS/JSON remote-job feeds, all HTTP-200 verified from GitHub Actions
# (state/source_probe.md, 2026-09-17). Fetched through the generic RSS/JSON
# fetcher, so adding a line here adds a source.
WORLDWIDE_FEEDS = [
    {"name": "wwr_customer_support", "url": "https://weworkremotely.com/categories/remote-customer-support-jobs.rss"},
    {"name": "wwr_design", "url": "https://weworkremotely.com/categories/remote-design-jobs.rss"},
    {"name": "wwr_sales_marketing", "url": "https://weworkremotely.com/categories/remote-sales-and-marketing-jobs.rss"},
    {"name": "wwr_management_finance", "url": "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"},
    {"name": "wwr_all_other", "url": "https://weworkremotely.com/categories/all-other-remote-jobs.rss"},
    {"name": "himalayas_rss", "url": "https://himalayas.app/jobs/rss"},
    {"name": "remotive_rss", "url": "https://remotive.com/remote-jobs/feed"},
]
MAX_WORLDWIDE_FEEDS = int(os.getenv("CAREEROPS_WORLDWIDE_MAX", "40"))

# ── Worldwide HTML board sweep ───────────────────────────────────────────
# Static job boards with no feed, verified returning jobs from GitHub Actions
# (2026-09-17). Parsed via JSON-LD JobPosting, falling back to job links. Only
# boards whose fallback yields real job titles are kept (nav-only pages dropped).
WORLDWIDE_HTML = [
    {"name": "untalent_arabic", "url": "https://untalent.org/jobs?q=arabic", "base": "https://untalent.org"},
    {"name": "jobgether", "url": "https://jobgether.com/remote-jobs", "base": "https://jobgether.com"},
]
MAX_WORLDWIDE_HTML = int(os.getenv("CAREEROPS_WORLDWIDE_HTML_MAX", "30"))

# Optional keyed aggregators — the sanctioned route to Indeed / LinkedIn /
# Glassdoor inventory. Each fetcher returns [] until its secret is present.
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")          # JSearch (Google for Jobs)
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "")
RELIEFWEB_APPNAME = os.getenv("RELIEFWEB_APPNAME", "")

# ── Groq (cloud AI — replaces local Ollama) ─────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# ── Notifications ────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
TO_EMAIL = os.getenv("TO_EMAIL", "")

# ── User Profile ─────────────────────────────────────────────────────────
USER_TIMEZONE = timezone.utc  # scanner runs in UTC; display converts to Libya UTC+2
LIBYA_UTC_OFFSET = 2

# ── Feature Flags ───────────────────────────────────────────────────────
ENABLE_AI = os.getenv("CAREEROPS_ENABLE_AI", "1") == "1"
ENABLE_COMPANY_RESEARCH = os.getenv("CAREEROPS_ENABLE_RESEARCH", "1") == "1"
ENABLE_COVER_LETTERS = os.getenv("CAREEROPS_ENABLE_LETTERS", "1") == "1"
ENABLE_INTERVIEW_PREP = os.getenv("CAREEROPS_ENABLE_PREP", "1") == "1"
ENABLE_DASHBOARD = os.getenv("CAREEROPS_ENABLE_DASHBOARD", "1") == "1"

# ── HTTP ─────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.5",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.6",
}

# ── Greenhouse ───────────────────────────────────────────────────────────
# ── Translation-only companies ────────────────────────────────────────────
# Only companies that ACTUALLY hire translators, interpreters, ESL teachers,
# localization specialists, and AI data annotators. Every non-translation
# company has been removed — the scanner is for Arabic↔English jobs ONLY.
GREENHOUSE_COMPANIES = [
    # Translation & Localization LSPs (core)
    ("TransPerfect", "transperfect"), ("Lionbridge", "lionbridge"),
    ("RWS", "rws"), ("Welocalize", "welocalize"),
    ("Keywords Studios", "keywordsstudios"),
    ("Smartling", "smartling"), ("Lokalise", "lokalise"), ("Phrase", "phrase"),
    ("Unbabel", "unbabel"), ("Lilt", "lilt"), ("Acclaro", "acclaro"),
    ("Andovar", "andovar"), ("Straker", "straker"),
    ("Cactus", "cactus"), ("Editage", "editage"), ("Enago", "enago"),
    ("Wordvice", "wordvice"), ("Scribbr", "scribbr"), ("Scribendi", "scribendi"),
    ("PaperTrue", "papertrue"), ("ProofreadNow", "proofreadnow"),
    ("Gengo", "gengo"), ("One Hour Translation", "onehourtranslation"),
    ("TextMaster", "textmaster"), ("Flitto", "flitto"),
    ("Translated", "translated"), ("Smartcat", "smartcat"),
    ("Alconost", "alconost"), ("Blend", "blend"),
    # AI Data Annotation / Linguist Marketplaces
    ("Scale AI", "scaleai"), ("Outlier", "outlier"),
    ("Surge AI", "surgeai"), ("Micro1", "micro1"), ("Prolific", "prolific"),
    ("Telus International", "telusinternational"), ("Toloka", "toloka"),
    ("Appen", "appen"), ("Centific", "centific"),
    ("Labelbox", "labelbox"), ("Invisible", "agency"), ("Turing", "turing"),
    # Arabic/MENA Content & EdTech (hiring Arabic speakers)
    ("Nagwa", "nagwa"), ("Abwaab", "abwaab"), ("Noon Academy", "noonacademy"),
    ("Edraak", "edraak"), ("Almentor", "almentor"), ("Baims", "baims"),
    ("Tamatem", "tamatem"), ("Mawdoo3", "mawdoo3"), ("Tarjama", "tarjama"),
    ("Saudisoft", "saudisoft"), ("Future Group", "futuregroup"),
    ("Anghami", "anghami"),
    # Remote-first that hire translators/language specialists
    ("Toptal", "toptal"), ("Deel", "deel"),
]
LEVER_COMPANIES = [
    ("Unbabel", "unbabel"), ("Lilt", "lilt"),
    ("Anghami", "anghami"), ("Noon Academy", "noonacademy"),
]

# ── Profile-specific ATS boards (translation/language/AI-data only) ──────
GREENHOUSE_PROFILE_BOARDS = [
    ("Invisible (AI Trainer projects)", "agency"),
    ("Labelbox / Alignerr", "labelbox"),
    ("Turing", "turing"),
    ("Prolific", "prolific"),
    ("Deel", "deel"),
    ("Toloka", "toloka"),
    ("TELUS International", "telusinternational"),
    ("Welocalize", "welocalize"),
    ("RWS", "rws"),
    ("Keywords Studios", "KeywordsStudios"),
    ("TransPerfect", "TransPerfect"),
    ("Lionbridge", "lionbridge"),
    ("Appen", "appen"),
    ("Centific", "centific"),
    ("Surge AI", "surgeai"),
    ("Micro1", "micro1"),
]
ASHBY_COMPANIES = [
    ("Mercor", "mercor"),
    ("Scale AI", "scaleai"),
    ("Deel", "deel"),
]
WORKABLE_COMPANIES = [
    ("Tamatem Games", "tamatem"),
    ("Abwaab", "abwaab"),
    ("Nagwa", "nagwa"),
    ("Noon Academy", "noonacademy"),
    ("Edraak", "edraak"),
    ("Almentor", "almentor"),
    ("Baims", "baims"),
    ("Tarjama", "tarjama"),
    ("Saudisoft", "saudisoft"),
]
SMARTRECRUITERS_COMPANIES = [
    ("Keywords Studios", "KeywordsStudios"),
    ("TransPerfect", "TransPerfect"),
    ("Lionbridge", "lionbridge"),
    ("RWS", "rws"),
    ("Appen", "appen"),
    ("TELUS International", "telusinternational"),
]
RECRUITEE_COMPANIES = [
    ("Smartling", "smartling"),
    ("Lokalise", "lokalise"),
    ("Phrase", "phrase"),
    ("Unbabel", "unbabel"),
    ("Lilt", "lilt"),
    ("Gengo", "gengo"),
    ("Translated", "translated"),
    ("Smartcat", "smartcat"),
    ("TransPerfect", "TransPerfect"),
    ("Lionbridge", "lionbridge"),
]
TEAMTAILOR_COMPANIES = [
    ("Tarjama", "tarjama"),
    ("Saudisoft", "saudisoft"),
    ("Tamatem Games", "tamatem"),
    ("Welocalize", "welocalize"),
    ("Keywords Studios", "keywordsstudios"),
    ("TransPerfect", "transperfect"),
    ("Lionbridge", "lionbridge"),
    ("RWS", "rws"),
    ("Appen", "appen"),
    ("TELUS International", "telusinternational"),
]

# ── Additional ATS boards ──
BAMBOOHR_COMPANIES = [
    ("Nagwa", "nagwa"),
    ("Abwaab", "abwaab"),
    ("Noon Academy", "noonacademy"),
]
JOBVITE_COMPANIES = [
    ("TELUS International", "telusinternational"),
]
PERSONIO_COMPANIES = [
    ("Appen", "appen"),
    ("Centific", "centific"),
    ("Surge AI", "surgeai"),
]

# ── Scoring ──────────────────────────────────────────────────────────────
SCORING_WEIGHTS = {
    "arabic_translation": 1.0,
    "editing": 0.80,
    "admin": 0.75,
}

# ── Dashboard / API ──────────────────────────────────────────────────────
DASHBOARD_HOST = os.getenv("CAREEROPS_DASH_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("CAREEROPS_DASH_PORT", "8000"))
API_PORT = int(os.getenv("CAREEROPS_API_PORT", "8001"))
