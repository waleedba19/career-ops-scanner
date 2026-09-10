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
# Profile-optimized: AI-data, language, EdTech, translation-focused companies
GREENHOUSE_COMPANIES = [
    # AI Data / Linguist Marketplaces (highest relevance)
    ("xAI", "xai"), ("Scale AI", "scaleai"), ("Outlier", "outlier"),
    ("Surge AI", "surgeai"), ("Micro1", "micro1"), ("Prolific", "prolific"),
    ("Telus International", "telusinternational"), ("Toloka", "toloka"),
    ("Appen", "appen"), ("Centific", "centific"),
    # Language & Translation
    ("Smartling", "smartling"), ("Lokalise", "lokalise"), ("Phrase", "phrase"),
    ("Unbabel", "unbabel"), ("Lilt", "lilt"), ("Acclaro", "acclaro"),
    ("Andovar", "andovar"), ("Straker", "straker"), ("RWS", "rws"),
    ("Lionbridge", "lionbridge"), ("TransPerfect", "transperfect"),
    ("Keywords Studios", "keywordsstudios"), ("Welocalize", "welocalize"),
    ("Cactus", "cactus"), ("Editage", "editage"), ("Enago", "enago"),
    ("Wordvice", "wordvice"), ("Scribbr", "scribbr"), ("Scribendi", "scribendi"),
    ("PaperTrue", "papertrue"), ("ProofreadNow", "proofreadnow"),
    # EdTech / ESL
    ("Duolingo", "duolingo"), ("Outschool", "outschool"), ("Khan Academy", "khanacademy"),
    ("Coursera", "coursera"), ("Preply", "preply"), ("Babbel", "babbel"),
    ("Busuu", "busuu"), ("Lingoda", "lingoda"), ("Engoo", "engoo"),
    ("Novakid", "novakid"), ("Open English", "openenglish"),
    ("VIPKid", "vipkid"), ("Qkids", "qkids"), ("Magic Ears", "magicears"),
    ("GoGoKid", "gogokid"), ("Ziyou Da", "ziyouda"),
    ("italki", "italki"), ("Cambly", "cambly"), ("Native Camp", "nativecamp"),
    ("TutorABC", "tutorabc"), ("Lingostar", "lingostar"),
    ("Nagwa", "nagwa"), ("Abwaab", "abwaab"), ("Noon Academy", "noonacademy"),
    ("Edraak", "edraak"), ("Almentor", "almentor"), ("Baims", "baims"),
    # MENA / Arabic Content
    ("OKX", "okx"), ("WPP Media", "wppmedia"), ("Anghami", "anghami"),
    ("Tamatem", "tamatem"), ("Mawdoo3", "mawdoo3"), ("Sarwa", "sarwa"),
    ("Careem", "careem"), ("Noon", "noon"), ("Tarjama", "tarjama"),
    ("Saudisoft", "saudisoft"), ("Future Group", "futuregroup"),
    ("Blend", "blend"), ("Alconost", "alconost"), ("Andovar", "andovar"),
    # Remote-first Tech (relevant ones)
    ("KAYAK", "kayak"), ("Mozilla", "mozilla"), ("GitLab", "gitlab"),
    ("Cloudflare", "cloudflare"), ("Automattic", "automattic"),
    ("Buffer", "buffer"), ("Zapier", "zapier"), ("Toptal", "toptal"),
    ("Remote.com", "remote"), ("Deel", "deel"), ("Oyster", "oyster"),
    ("Papaya Global", "papayaglobal"), ("Rippling", "rippling"),
    # Content & Writing
    ("Contentful", "contentful"), ("Notion", "notion"), ("Figma", "figma"),
    ("Canva", "canva"), ("Visme", "visme"), ("Prezi", "prezi"),
    # Publishing & Media
    ("Headspace", "headspace"), ("Calm", "calm"), ("Headspace", "headspace"),
    ("Masterclass", "masterclass"), ("Skillshare", "skillshare"),
    ("Udemy", "udemy"), ("LinkedIn Learning", "linkedinlearning"),
    # More AI/Data Companies
    ("Labelbox", "labelbox"), ("Invisible", "agency"), ("Turing", "turing"),
    ("Handshake", "joinhandshake"), ("Scale AI", "scaleai"),
    ("Snorkel AI", "snorkelai"), ("Weights & Biases", "wandb"),
    ("LangChain", "langchain"), ("Pinecone", "pinecone"),
    ("Cohere", "cohere"), ("Mistral", "mistral"),
    ("Anthropic", "anthropic"), ("OpenAI", "openai"),
    # Gaming (localization)
    ("Riot Games", "riotgames"), ("Electronic Arts", "ea"),
    ("Ubisoft", "ubisoft"), ("Take-Two", "take2"),
    ("Playrix", "playrix"), ("Supercell", "supercell"),
    # More Translation/Language
    ("Gengo", "gengo"), ("One Hour Translation", "onehourtranslation"),
    ("TextMaster", "textmaster"), ("Flitto", "flitto"),
    ("Translated", "translated"), ("Smartcat", "smartcat"),
]
LEVER_COMPANIES = [
    ("Appen", "appen"),
    ("Unbabel", "unbabel"),
    ("Lilt", "lilt"),
    ("Anghami", "anghami"),
    ("Noon Academy", "noonacademy"),
    ("Vice Media", "vice"),
    ("Figma", "figma"),
    ("Notion", "notion"),
    ("Coinbase", "coinbase"),
    ("Square", "square"),
    ("DoorDash", "doordash"),
    ("Flexport", "flexport"),
    ("GitLab", "gitlab"),
    ("Postmates", "postmates"),
    ("WeWork", "wework"),
    ("N26", "n26"),
    ("Revolut", "revolut"),
    ("Monzo", "monzo"),
    ("Nubank", "nubank"),
    ("Klarna", "klarna"),
]

# ── Profile-specific ATS boards (live-verified by the Probe Sources workflow,
#    state/source_probe.md, 2026-09-06). Same shape as GREENHOUSE_COMPANIES.
#    Add a slug here only after the probe reports it `ok`.
GREENHOUSE_PROFILE_BOARDS = [
    ("Invisible (AI Trainer projects)", "agency"),   # 829 jobs incl. Arabic Language Specialist, worldwide remote
    ("Labelbox / Alignerr", "labelbox"),             # 10 jobs — Arabic language expert roles appear here
    ("Turing", "turing"),                            # 26 jobs — LLM training linguists
    ("Prolific", "prolific"),                        # AI data annotation, research
    ("Deel", "deel"),                                # Global hiring, remote roles
    ("Handshake", "joinhandshake"),                  # AI/ML jobs
    ("Toloka", "toloka"),                            # Data annotation, Arabic
    ("TELUS International", "telusinternational"),   # AI training, linguists
    ("Welocalize", "welocalize"),                    # Localization, translation
    ("RWS", "rws"),                                  # Language services
    ("Keywords Studios", "KeywordsStudios"),          # Game localization
    ("TransPerfect", "TransPerfect"),                # LSP
    ("Lionbridge", "lionbridge"),                    # Language services
    ("Appen", "appen"),                              # AI data
    ("Centific", "centific"),                        # Formerly OneForma
    ("Surge AI", "surgeai"),                         # AI linguists
    ("Micro1", "micro1"),                            # AI expert marketplace
]
ASHBY_COMPANIES = [
    ("Mercor", "mercor"),                            # 96 jobs — AI expert marketplace
    ("Deel", "deel"),                                # Global hiring
    ("Scale AI", "scaleai"),                         # AI data
    ("Papaya Global", "papayaglobal"),               # Global payroll
    ("Remote.com", "remote"),                        # Global HR
    ("Oyster", "oyster"),                            # Global employment
    ("Lano", "lano"),                                # Global payments
    ("Velocity Global", "velocityglobal"),           # Global HR
    ("Multiplier", "multiplier"),                    # Global employment
    ("Globalization Partners", "globalizationpartners"),
]
WORKABLE_COMPANIES = [
    ("Tamatem Games", "tamatem"),                    # 18 jobs — Arabic game localization (Jordan, remote-friendly)
    ("Abwaab", "abwaab"),                            # EdTech, MENA
    ("Nagwa", "nagwa"),                              # EdTech, Egypt (Arabic content)
    ("Noon Academy", "noonacademy"),                 # EdTech, Saudi
    ("Edraak", "edraak"),                            # EdTech, Egypt
    ("Almentor", "almentor"),                        # EdTech, MENA
    ("Baims", "baims"),                              # EdTech, Kuwait
    ("Careem", "careem"),                            # Tech, UAE
    ("Tarjama", "tarjama"),                          # Translation, UAE
    ("Saudisoft", "saudisoft"),                      # Tech, Saudi
]
SMARTRECRUITERS_COMPANIES = [
    ("Keywords Studios", "KeywordsStudios"),         # game localization / Arabic LQA
    ("TransPerfect", "TransPerfect"),                # LSP — linguists, project managers
    ("Lionbridge", "lionbridge"),                    # Language services
    ("RWS", "rws"),                                  # Language services
    ("Appen", "appen"),                              # AI data
    ("TELUS International", "telusinternational"),   # AI training
    ("Concentrix", "concentrix"),                    # BPO, language services
    ("Teleperformance", "teleperformance"),          # BPO, multilingual
    ("Alorica", "alorica"),                          # BPO, customer service
    ("Sitel", "sitel"),                              # BPO, multilingual
]
RECRUITEE_COMPANIES = [
    ("Lingoda", "lingoda"),                          # ESL, online teaching
    ("Preply", "preply"),                            # Language tutoring
    ("Cambly", "cambly"),                            # ESL, online teaching
    ("italki", "italki"),                            # Language tutoring
    ("Verbling", "verbling"),                        # Language tutoring
    ("FluentU", "fluentu"),                          # Language learning
    ("Rosetta Stone", "rosettastone"),               # Language learning
    ("Babbel", "babbel"),                            # Language learning
    ("Busuu", "busuu"),                              # Language learning
    ("Memrise", "memrise"),                          # Language learning
]
TEAMTAILOR_COMPANIES = [
    ("Novakid", "novakid"),                          # ESL, online teaching
    ("Open English", "openenglish"),                 # ESL, Latin America
    ("VIPKid", "vipkid"),                            # ESL, China
    ("Qkids", "qkids"),                              # ESL, China
    ("Magic Ears", "magicears"),                     # ESL, China
    ("GoGoKid", "gogokid"),                          # ESL, China
    ("Native Camp", "nativecamp"),                   # ESL, Japan
    ("TutorABC", "tutorabc"),                        # ESL, Taiwan
    ("Engoo", "engoo"),                              # ESL, Japan
    ("DMM Eikaiwa", "dmmeikaiwa"),                   # ESL, Japan
]

# ── Additional ATS boards ──
BAMBOOHR_COMPANIES = [
    ("Nagwa", "nagwa"),                              # EdTech, Egypt
    ("Abwaab", "abwaab"),                            # EdTech, MENA
    ("Noon Academy", "noonacademy"),                 # EdTech, Saudi
]
BREEZY_COMPANIES = [
    ("Tarjama", "tarjama"),                          # Translation, UAE
    ("Saudisoft", "saudisoft"),                      # Tech, Saudi
    ("Careem", "careem"),                            # Tech, UAE
]
PINPOINT_COMPANIES = [
    ("Edraak", "edraak"),                            # EdTech, Egypt
    ("Almentor", "almentor"),                        # EdTech, MENA
    ("Baims", "baims"),                              # EdTech, Kuwait
]
RIPPLING_COMPANIES = [
    ("Deel", "deel"),                                # Global hiring
    ("Remote.com", "remote"),                        # Global HR
    ("Oyster", "oyster"),                            # Global employment
]
JOBVITE_COMPANIES = [
    ("TELUS International", "telusinternational"),   # AI training, linguists
    ("Concentrix", "concentrix"),                    # BPO, language services
    ("Teleperformance", "teleperformance"),          # BPO, multilingual
]
PERSONIO_COMPANIES = [
    ("Appen", "appen"),                              # AI data
    ("Centific", "centific"),                        # Formerly OneForma
    ("Surge AI", "surgeai"),                         # AI linguists
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
