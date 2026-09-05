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
    ("workingnomads", "fetch_workingnomads", 2, "workingnomads"),
    ("jobspresso", "fetch_jobspresso", 2, "jobspresso"),
    ("justremote", "fetch_justremote", 2, "justremote"),
    ("hirelatam", "fetch_hirelatam", 2, "hirelatam"),
    # Tier 2 — niche / freelance (opt-in via env if needed)
    ("freelancer", "fetch_freelancer", 3, "freelancer"),
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
