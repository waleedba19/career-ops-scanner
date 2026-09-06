"""Registry — single source for which fetchers run, in which tier, and deduplicated."""
from typing import Callable

# Maps fetcher name -> (callable_name, tier, dedup_key)
# dedup_key groups variants (himalayas*, jobicy*, etc) so only the best runs
FETCHERS: list[tuple[str, str, int, str]] = [
    # Tier 1 — primary, high signal (always on)
    ("greenhouse", "fetch_greenhouse_batch", 1, "greenhouse"),
    ("lever", "fetch_lever_batch", 1, "lever"),
    ("remotive", "fetch_remotive", 1, "remotive"),
    ("remoteok", "fetch_remoteok", 1, "remoteok"),
    ("weworkremotely", "fetch_wwr", 1, "wwr"),
    ("jobicy", "fetch_jobicy_api", 1, "jobicy"),  # API is best; RSS fallback inside
    ("arbeitnow", "fetch_arbeitnow", 1, "arbeitnow"),
    ("himalayas", "fetch_himalayas_api", 1, "himalayas"),  # JSON API best
    ("nodesk", "fetch_nodesk", 2, "nodesk"),
    ("yayremote", "fetch_yayremote", 2, "yayremote"),
    ("remote1stjobs", "fetch_remote1stjobs", 2, "remote1st"),
    ("realworkfromanywhere", "fetch_realworkfromanywhere", 2, "realwork"),
    ("workingnomads", "fetch_workingnomads_json", 2, "workingnomads"),  # JSON endpoint (probe-verified); RSS twin 404s
    ("jobspresso", "fetch_jobspresso", 2, "jobspresso"),
    ("justremote", "fetch_justremote", 2, "justremote"),
    ("hirelatam", "fetch_hirelatam", 2, "hirelatam"),
    ("reddit_social", "fetch_reddit_social", 2, "reddit"),  # social signals: r/forhire, r/RemoteJobs, r/esl, ...
    ("eslgorilla", "fetch_eslgorilla", 2, "eslgorilla"),  # online ESL board, 300+ live listings (live-verified 2026-09-06)
    ("tes", "fetch_tes", 2, "tes"),  # 2,700+ teaching jobs, remote/online filter built in
    # ── Verified by the Probe Sources workflow (state/source_probe.md, 2026-09-06) ──
    # Tier 1: precision sources that returned profile-relevant jobs from the runner IP
    ("linkedin", "fetch_linkedin_guest", 1, "linkedin"),               # 4 profile queries, remote, last 24h
    ("freelancer_api", "fetch_freelancer_api", 1, "freelancer_api"),   # keyword-precise; RSS variant converts at 17%
    ("jobicy_tags", "fetch_jobicy_tags", 1, "jobicy_tags"),            # tag=translation/teaching/writing
    ("impactpool", "fetch_impactpool", 1, "impactpool"),               # UN/NGO — Arabic interpreter demand
    ("greenhouse_profile", "fetch_greenhouse_profile", 1, "greenhouse_profile"),  # Invisible/Labelbox/Turing boards
    ("ashby", "fetch_ashby_boards", 2, "ashby"),                       # Mercor
    ("workable", "fetch_workable_boards", 2, "workable"),              # Tamatem
    ("smartrecruiters", "fetch_smartrecruiters_boards", 2, "smartrecruiters"),  # Keywords Studios, TransPerfect
    ("themuse", "fetch_themuse", 2, "themuse"),                        # free public API, remote-filtered
    # Keyed aggregators — no-ops until the secret exists (RAPIDAPI_KEY, ADZUNA_*, JOOBLE_API_KEY, RELIEFWEB_APPNAME)
    ("jsearch", "fetch_jsearch", 1, "jsearch"),                        # Google for Jobs → Indeed/LinkedIn/Glassdoor
    ("adzuna", "fetch_adzuna", 1, "adzuna"),
    ("jooble", "fetch_jooble", 2, "jooble"),
    ("reliefweb", "fetch_reliefweb", 1, "reliefweb"),
    # Tier 2 — niche / freelance
    ("freelancer", "fetch_freelancer", 1, "freelancer"),  # promoted: 30 of 56 all-time matches came from here
    ("peopleperhour", "fetch_peopleperhour", 3, "peopleperhour"),
    ("guru", "fetch_guru", 3, "guru"),
]

TIER_MAP = {name: tier for name, _, tier, _ in FETCHERS}
DEDUP_KEYS = {dedup: name for name, _, _, dedup in FETCHERS}

def get_fetcher(name: str):
    return next((x for x in FETCHERS if x[0]==name), None)

def list_fetchers(max_tier: int = 3):
    """Return fetcher names up to tier."""
    return [name for name,_,tier,_ in FETCHERS if tier <= max_tier]

# Env-driven tier cap: 1=lean & fast, 2=balanced, 3=full sweep (default 2)
import os
try:
    TIER_CAP = int(os.getenv("CAREEROPS_TIER_CAP", "2"))
except: TIER_CAP = 2
TIER_CAP = max(1, min(3, TIER_CAP))
