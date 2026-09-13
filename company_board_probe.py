"""Company board probe — verifies every ATS slug the scanner actually calls.

Writes state/valid_company_slugs.json: {adapter: [[name, slug], ...]} for any
slug that returns HTTP 200 from the real endpoint used by the scanner. The
scanner loads this file each run and only fetches validated boards — which
kills the HTTP-404 spam and wasted requests.

Run: python company_board_probe.py
Output: state/valid_company_slugs.json
"""
import asyncio
import json
import sys
import time
from pathlib import Path

import aiohttp

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.5",
}
TIMEOUT = aiohttp.ClientTimeout(total=12)

# Real endpoints the scanner fetchers use for each adapter.
ADAPTER_URLS = {
    "greenhouse": lambda slug: f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
    "lever": lambda slug: f"https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": lambda slug: f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true",
    "workable": lambda slug: f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true",
}

# (adapter, config_list_name)
SOURCE_LISTS = {
    "greenhouse": ["GREENHOUSE_COMPANIES", "GREENHOUSE_PROFILE_BOARDS"],
    "lever": ["LEVER_COMPANIES"],
    "ashby": ["ASHBY_COMPANIES"],
    "workable": ["WORKABLE_COMPANIES"],
}


def _collect() -> dict[str, list[tuple[str, str]]]:
    """Collect unique (name, slug) per adapter from config."""
    out: dict[str, list[tuple[str, str]]] = {}
    seen: dict[str, set] = {}
    for adapter, list_names in SOURCE_LISTS.items():
        seen[adapter] = set()
        out[adapter] = []
        for list_name in list_names:
            for entry in getattr(config, list_name, []):
                try:
                    name, slug = entry[0], entry[1]
                except (IndexError, TypeError):
                    continue
                if slug in seen[adapter]:
                    continue
                seen[adapter].add(slug)
                out[adapter].append((name, slug))
    return out


async def _probe_one(session, adapter, name, slug, sem) -> tuple[str, tuple[str, str], bool, str]:
    url = ADAPTER_URLS[adapter](slug)
    async with sem:
        try:
            async with session.get(url, headers=HEADERS, timeout=TIMEOUT, ssl=False) as r:
                if r.status == 200:
                    return adapter, (name, slug), True, f"HTTP 200"
                return adapter, (name, slug), False, f"HTTP {r.status}"
        except Exception as e:
            return adapter, (name, slug), False, f"{type(e).__name__}: {str(e)[:60]}"


async def _run() -> None:
    sources = _collect()
    total = sum(len(v) for v in sources.values())
    print(f"Company board probe: {total} slugs across {len(sources)} adapters")
    ok: dict[str, list[list[str]]] = {}
    sem = asyncio.Semaphore(12)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for adapter, entries in sources.items():
            for (name, slug) in entries:
                tasks.append(_probe_one(session, adapter, name, slug, sem))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for res in results:
        if isinstance(res, tuple) and len(res) == 4:
            adapter, (name, slug), good, detail = res
            if good:
                ok.setdefault(adapter, []).append([name, slug])
            else:
                print(f"  ✗ {adapter}:{slug} ({name}) — {detail}")

    state = ROOT / "state"
    state.mkdir(parents=True, exist_ok=True)
    out = {"updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "valid": ok}
    path = state / "valid_company_slugs.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    summary = " | ".join(f"{a}: {len(v)}" for a, v in ok.items()) or "none"
    print(f"\nValid slugs -> {path} ({summary})")


if __name__ == "__main__":
    asyncio.run(_run())