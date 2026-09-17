"""Registry — true registry with lazy loading for CareerOps fetchers."""
import os
from typing import Callable, Optional
from .base import BaseFetcher, FetchResult

# Registry mapping: name -> (tier, module_path, class_name)
# Lazy loading: fetcher modules are only imported when needed
# FOCUSED ON: Arabic-English Translation, Localization, Bilingual Content
REGISTRY: dict[str, dict] = {
    # Tier 1 — primary, high signal (always on) - Translation & Language Focus
    "greenhouse": {"tier": 1, "module": "fetchers.verified", "class": "fetch_greenhouse_batch"},
    "lever": {"tier": 1, "module": "fetchers.verified", "class": "fetch_lever_batch"},
    "remotive": {"tier": 1, "module": "scanner", "class": "fetch_remotive"},
    "remoteok": {"tier": 1, "module": "scanner", "class": "fetch_remoteok"},
    "weworkremotely": {"tier": 1, "module": "scanner", "class": "fetch_wwr"},
    "jobicy": {"tier": 1, "module": "scanner", "class": "fetch_jobicy_api"},
    "arbeitnow": {"tier": 1, "module": "scanner", "class": "fetch_arbeitnow"},
    "himalayas": {"tier": 1, "module": "scanner", "class": "fetch_himalayas_api"},
    "linkedin": {"tier": 1, "module": "fetchers.verified", "class": "fetch_linkedin_guest"},
    "jobicy_tags": {"tier": 1, "module": "fetchers.verified", "class": "fetch_jobicy_tags"},
    "impactpool": {"tier": 1, "module": "fetchers.verified", "class": "fetch_impactpool"},
    "jsearch": {"tier": 1, "module": "fetchers.verified", "class": "fetch_jsearch"},
    "adzuna": {"tier": 1, "module": "fetchers.verified", "class": "fetch_adzuna"},
    "reliefweb": {"tier": 1, "module": "fetchers.verified", "class": "fetch_reliefweb"},
    "upwork": {"tier": 1, "module": "fetchers.verified", "class": "fetch_upwork"},
    "stackoverflow": {"tier": 1, "module": "fetchers.verified", "class": "fetch_stackoverflow"},
    "github_jobs": {"tier": 1, "module": "fetchers.verified", "class": "fetch_github_jobs"},
    "hackernews": {"tier": 1, "module": "fetchers.verified", "class": "fetch_hackernews"},
    "indeed": {"tier": 1, "module": "fetchers.verified", "class": "fetch_indeed"},
    "translation_jobs": {"tier": 1, "module": "fetchers.verified", "class": "fetch_translation_jobs"},
    # Dedicated translation/localization boards. These were missing from the
    # registry, so _should_run() fell back to tier 3 and the tier cap silently
    # disabled them.
    "smartcat": {"tier": 1, "module": "scanner", "class": "fetch_smartcat"},
    "gotranscript": {"tier": 1, "module": "scanner", "class": "fetch_gotranscript"},
    "workbeam": {"tier": 2, "module": "scanner", "class": "fetch_workbeam"},
    "proz": {"tier": 2, "module": "scanner", "class": "fetch_proz"},
    "arabic_companies": {"tier": 1, "module": "fetchers.arabic_translation", "class": "fetch"},
    "nodesk": {"tier": 1, "module": "scanner", "class": "fetch_nodesk"},
    
    # Tier 2 — balanced (good volume) - Asian/South Asian & MENA Focus
    "yayremote": {"tier": 2, "module": "scanner", "class": "fetch_yayremote"},
    "remote1stjobs": {"tier": 2, "module": "scanner", "class": "fetch_remote1stjobs"},
    "realworkfromanywhere": {"tier": 2, "module": "scanner", "class": "fetch_realworkfromanywhere"},
    "workingnomads": {"tier": 2, "module": "fetchers.verified", "class": "fetch_workingnomads_json"},
    "jobspresso": {"tier": 2, "module": "scanner", "class": "fetch_jobspresso"},
    "justremote": {"tier": 2, "module": "scanner", "class": "fetch_justremote"},
    "hirelatam": {"tier": 2, "module": "scanner", "class": "fetch_hirelatam"},
    "reddit_social": {"tier": 2, "module": "fetchers.social", "class": "fetch_reddit_social"},
    "ashby": {"tier": 2, "module": "fetchers.verified", "class": "fetch_ashby_boards"},
    "workable": {"tier": 2, "module": "fetchers.verified", "class": "fetch_workable_boards"},
    "smartrecruiters": {"tier": 2, "module": "fetchers.verified", "class": "fetch_smartrecruiters_boards"},
    "themuse": {"tier": 2, "module": "fetchers.verified", "class": "fetch_themuse"},
    "jooble": {"tier": 2, "module": "fetchers.verified", "class": "fetch_jooble"},
    "remowork": {"tier": 2, "module": "fetchers.verified", "class": "fetch_remowork"},
    "recruitee": {"tier": 2, "module": "fetchers.verified", "class": "fetch_recruitee_boards"},
    "teamtailor": {"tier": 2, "module": "fetchers.verified", "class": "fetch_teamtailor_boards"},
    "euremotejobs": {"tier": 2, "module": "fetchers.verified", "class": "fetch_euremotejobs"},
    "remotejobleads": {"tier": 2, "module": "fetchers.verified", "class": "fetch_remotejobleads"},
    "bamboohr": {"tier": 2, "module": "fetchers.verified", "class": "fetch_bamboohr_boards"},
    "jobvite": {"tier": 2, "module": "fetchers.verified", "class": "fetch_jobvite_boards"},
    "personio": {"tier": 2, "module": "fetchers.verified", "class": "fetch_personio_boards"},
    "landing_jobs": {"tier": 2, "module": "fetchers.verified", "class": "fetch_landing_jobs"},
    "flexjobs": {"tier": 2, "module": "fetchers.verified", "class": "fetch_flexjobs"},
    "remote_co": {"tier": 2, "module": "fetchers.verified", "class": "fetch_remote_co"},
    "toptal": {"tier": 2, "module": "fetchers.verified", "class": "fetch_toptal"},
    "wellfound": {"tier": 2, "module": "fetchers.verified", "class": "fetch_wellfound"},
    "edtech_jobs": {"tier": 2, "module": "fetchers.verified", "class": "fetch_edtech_jobs"},
    "writing_jobs": {"tier": 2, "module": "fetchers.verified", "class": "fetch_writing_jobs"},
    
    # Tier 3 — niche / MENA / freelance (noisy, use sparingly)
    "peopleperhour": {"tier": 3, "module": "scanner", "class": "fetch_peopleperhour"},
    "guru": {"tier": 3, "module": "scanner", "class": "fetch_guru"},
    "dailyremote": {"tier": 3, "module": "fetchers.verified", "class": "fetch_dailyremote"},
    "dynamitejobs": {"tier": 3, "module": "fetchers.verified", "class": "fetch_dynamitejobs"},
    "europeremotely": {"tier": 3, "module": "fetchers.verified", "class": "fetch_europeremotely"},
    "bayt": {"tier": 3, "module": "fetchers.verified", "class": "fetch_bayt"},
    "gulftalent": {"tier": 3, "module": "fetchers.verified", "class": "fetch_gulftalent"},
    "naukrigulf": {"tier": 3, "module": "fetchers.verified", "class": "fetch_naukrigulf"},
    "mostaql": {"tier": 3, "module": "fetchers.verified", "class": "fetch_mostaql"},
    "for9a": {"tier": 3, "module": "fetchers.verified", "class": "fetch_for9a"},
}

# Blocked sources (from probe testing)
PROBE_BLOCKED_SOURCES = ["mostaql", "ureed", "wuzzuf", "bayt", "gulftalent", "proz"]

# Derived convenience view: name -> tier. Kept because callers/tests import it.
TIER_MAP: dict[str, int] = {name: info["tier"] for name, info in REGISTRY.items()}
FORCE_BLOCKED_SOURCES = os.getenv("CAREEROPS_FORCE_BLOCKED", "0") == "1"

# Circuit breaker state
_circuit: dict[str, float] = {}
FAIL_THRESHOLD = 5
COOLDOWN_SEC = 600


def _circuit_open(name: str) -> bool:
    """Check if a source is in circuit breaker state."""
    import time
    opened = _circuit.get(name, 0)
    return time.time() < opened


def _mark_failure(name: str):
    """Mark a source as failed."""
    import time
    _circuit[name] = time.time() + COOLDOWN_SEC


def _mark_success(name: str):
    """Mark a source as successful (reset circuit)."""
    _circuit.pop(name, None)


def get_fetcher(name: str) -> Optional[dict]:
    """Get fetcher info by name."""
    return REGISTRY.get(name)


def list_fetchers(max_tier: int = 3) -> list[str]:
    """Return fetcher names up to tier."""
    return [name for name, info in REGISTRY.items() if info["tier"] <= max_tier]


def get_available_tiers() -> list[int]:
    """Get list of available tiers."""
    tiers = set(info["tier"] for info in REGISTRY.values())
    return sorted(tiers)


def fetch_source(name: str, tier_cap: int = 0) -> list[dict]:
    """Fetch one source; returns list of raw job dicts."""
    import time
    
    if name not in REGISTRY:
        return []
    
    info = REGISTRY[name]
    
    # Check tier cap
    if tier_cap and info["tier"] > tier_cap:
        return []
    
    # Check blocked sources
    if not FORCE_BLOCKED_SOURCES and name in PROBE_BLOCKED_SOURCES:
        print(f"  [{name}] blocked by probe - skipping")
        return []
    
    # Check circuit breaker
    if _circuit_open(name):
        print(f"  [{name}] circuit open - skipping")
        return []
    
    # Lazy load the fetcher function
    try:
        import importlib
        module = importlib.import_module(info["module"])
        fetch_fn = getattr(module, info["class"])
        
        # For now, we need to pass a session - this will be refactored
        # when we modularize the fetchers
        import aiohttp
        async def _fetch():
            async with aiohttp.ClientSession() as session:
                return await fetch_fn(session)
        
        # Run the async function
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(asyncio.run, _fetch()).result()
                return result
            else:
                return loop.run_until_complete(_fetch())
        except RuntimeError:
            return asyncio.run(_fetch())
        
    except Exception as e:
        _mark_failure(name)
        print(f"  [{name}] ERROR: {e}")
        return []


def fetch_all(tier_cap: int = 3, names: list[str] | None = None) -> dict[str, list[dict]]:
    """Fetch all sources up to tier cap."""
    out = {}
    for name in (names or list(REGISTRY)):
        out[name] = fetch_source(name, tier_cap)
    return out


# Env-driven tier cap: 1=lean & fast, 2=balanced, 3=full sweep (default 2)
try:
    TIER_CAP = int(os.getenv("CAREEROPS_TIER_CAP", "2"))
except:
    TIER_CAP = 2
TIER_CAP = max(1, min(3, TIER_CAP))
