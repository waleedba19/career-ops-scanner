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
MIN_MATCH_SCORE = int(os.getenv("CAREEROPS_MIN_SCORE", "65"))
MAX_AGE_HOURS = int(os.getenv("CAREEROPS_MAX_AGE_H", "144"))  # 6 days
MAX_AGE_FRESH_HOURS = float(os.getenv("CAREEROPS_FRESH_H", "8"))  # 1 scan cycle (was 0.5)
NEAR_MISS_MIN = 50
NEAR_MISS_MAX = 64
NEAR_MISS_LIMIT = int(os.getenv("CAREEROPS_NEAR_MISS_LIMIT", "6"))
TOP_LIVENESS_CHECK = int(os.getenv("CAREEROPS_LIVENESS_TOP", "6"))
HISTORY_MAX = 5000
FETCH_TIMEOUT = int(os.getenv("CAREEROPS_FETCH_TIMEOUT", "12"))
FETCH_BATCH_SIZE = int(os.getenv("CAREEROPS_BATCH_SIZE", "8"))
FETCH_CONCURRENCY = int(os.getenv("CAREEROPS_CONCURRENCY", "25"))

# ── Sources ──────────────────────────────────────────────────────────────
# Primary tier — high signal, low noise
TIER_1_SOURCES = [
    "greenhouse", "lever", "remotive", "remoteok", "weworkremotely",
    "jobicy", "arbeitnow", "himalayas", "jobicy_api",
]
# Secondary tier — good volume
TIER_2_SOURCES = [
    "nodesk", "yayremote", "remote1stjobs", "realworkfromanywhere",
    "workingnomads", "jobspresso", "justremote", "hirelatam",
]
# Tertiary — niche / MENA / freelance (noisy, use sparingly)
TIER_3_SOURCES = [
    "mostaql", "for9a", "khamsat", "ureed", "wuzzuf",
    "bayt", "gulftalent", "naukrigulf",
    "freelancer", "peopleperhour", "guru",
]

# Paid platforms — auto-reject (fees to apply)
PAID_PLATFORMS = ["flexjobs", "tophire", "wellfound", "ziprecruiter"]

# Sources the probe confirmed are BLOCKED from GitHub Actions IPs (403/429 +
# challenge pages) — requesting them only burns time. They are skipped unless
# CAREEROPS_FORCE_BLOCKED=1 (e.g. when running from a residential IP).
PROBE_BLOCKED_SOURCES = ["mostaql", "ureed", "wuzzuf", "bayt", "gulftalent", "proz"]
FORCE_BLOCKED_SOURCES = os.getenv("CAREEROPS_FORCE_BLOCKED", "0") == "1"

# Optional keyed aggregators — the sanctioned route to Indeed / LinkedIn /
# Glassdoor inventory. Each fetcher returns [] until its secret is present.
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")          # JSearch (Google for Jobs)
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "")
RELIEFWEB_APPNAME = os.getenv("RELIEFWEB_APPNAME", "")

# ── Ollama ───────────────────────────────────────────────────────────────
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")  # unified model
OLLAMA_FALLBACK_MODEL = "qwen2.5:0.5b"

# ── Notifications ────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
TO_EMAIL = os.getenv("TO_EMAIL", "")

# ── User Profile ─────────────────────────────────────────────────────────
USER_TIMEZONE = timezone.utc  # scanner runs in UTC; display converts to Libya UTC+2
LIBYA_UTC_OFFSET = 2

# ── Feature Flags ───────────────────────────────────────────────────────
ENABLE_OLLAMA = os.getenv("CAREEROPS_ENABLE_OLLAMA", "1") == "1"
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
GREENHOUSE_COMPANIES = [
    ("KAYAK", "kayak"), ("2K", "2k"), ("xAI", "xai"), ("OKX", "okx"),
    ("WPP Media", "wppmedia"), ("Duolingo", "duolingo"), ("Smartling", "smartling"),
    ("Lokalise", "lokalise"), ("Scale AI", "scaleai"), ("Outschool", "outschool"),
    ("Khan Academy", "khanacademy"), ("Mozilla", "mozilla"), ("Riot Games", "riotgames"),
    ("Coursera", "coursera"), ("Cloudflare", "cloudflare"), ("GitLab", "gitlab"),
    ("Discord", "discord"), ("Figma", "figma"), ("Airbnb", "airbnb"),
    ("Stripe", "stripe"), ("Asana", "asana"), ("Twitch", "twitch"),
    ("Roblox", "roblox"), ("Squarespace", "squarespace"), ("Reddit", "reddit"),
    ("Pinterest", "pinterest"), ("Coinbase", "coinbase"), ("Instacart", "instacart"),
    ("Okta", "okta"), ("Datadog", "datadog"), ("Contentful", "contentful"),
    ("OneTrust", "onetrust"), ("Block", "block"), ("Twilio", "twilio"),
]
LEVER_COMPANIES = [("Appen", "appen")]

# ── Profile-specific ATS boards (live-verified by the Probe Sources workflow,
#    state/source_probe.md, 2026-09-06). Same shape as GREENHOUSE_COMPANIES.
#    Add a slug here only after the probe reports it `ok`.
GREENHOUSE_PROFILE_BOARDS = [
    ("Invisible (AI Trainer projects)", "agency"),   # 829 jobs incl. Arabic Language Specialist, worldwide remote
    ("Labelbox / Alignerr", "labelbox"),             # 10 jobs — Arabic language expert roles appear here
    ("Turing", "turing"),                            # 26 jobs — LLM training linguists
]
ASHBY_COMPANIES = [
    ("Mercor", "mercor"),                            # 96 jobs — AI expert marketplace
]
WORKABLE_COMPANIES = [
    ("Tamatem Games", "tamatem"),                    # 18 jobs — Arabic game localization (Jordan, remote-friendly)
]
SMARTRECRUITERS_COMPANIES = [
    ("Keywords Studios", "KeywordsStudios"),         # game localization / Arabic LQA
    ("TransPerfect", "TransPerfect"),                # LSP — linguists, project managers
]

# ── Scoring ──────────────────────────────────────────────────────────────
SCORING_WEIGHTS = {
    "arabic_translation": 1.0,
    "esl": 0.85,
    "editing": 0.80,
    "admin": 0.75,
}

# ── Dashboard / API ──────────────────────────────────────────────────────
DASHBOARD_HOST = os.getenv("CAREEROPS_DASH_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("CAREEROPS_DASH_PORT", "8000"))
API_PORT = int(os.getenv("CAREEROPS_API_PORT", "8001"))
