"""
JobSpy fetcher — Indeed + LinkedIn via the free `python-jobspy` scraper.

Why: (a) Indeed via JobSpy returns FULL job descriptions, which fixes the
language-blind matches (a bare "Translator" with a truncated description scored
90-100% even for Chinese/Malay postings); (b) LinkedIn adds a second query
angle. Google/Glassdoor/ZipRecruiter return 403 from runner IPs (Akamai) and
are deliberately excluded so we don't burn CI time.

Fails soft: if `python-jobspy` is missing or a site blocks us, this returns []
and the rest of the scan is unaffected. The whole batch is time-boxed so it can
never hang a scheduled run.
"""
import asyncio

QUERIES = [
    "Arabic translator",
    "Arabic interpreter",
    "English Arabic translation",
]
SITES = ["indeed", "linkedin"]
RESULTS_PER_QUERY = 8
HOURS_OLD = 168          # 7 days, consistent with MAX_AGE_HOURS
BATCH_TIMEOUT_SEC = 200  # hard cap so JobSpy can never stall the scan


def _row_to_job(row: dict, site: str) -> dict:
    url = str(row.get("job_url_direct") or row.get("job_url") or "").strip()
    title = str(row.get("title") or "").strip()
    description = str(row.get("description") or "").strip()
    location = str(row.get("location") or "").strip() or "Remote"
    posted = row.get("date_posted")
    if posted is not None and not isinstance(posted, str):
        try:
            posted = posted.isoformat()
        except Exception:
            posted = str(posted)
    return {
        "title": title,
        "company": str(row.get("company") or "").strip(),
        "url": url,
        "location": location,
        "description": description,
        "salary": str(row.get("salary") or ""),
        "posted": posted or "",
        "source": f"jobspy_{site}",
    }


def _fetch_sync() -> list[dict]:
    try:
        from jobspy import scrape_jobs
    except Exception as e:  # pragma: no cover - package may be absent
        print(f"  JobSpy unavailable: {e}")
        return []

    out: list[dict] = []
    seen: set[str] = set()
    for site in SITES:
        for query in QUERIES:
            try:
                df = scrape_jobs(
                    site_name=site,
                    search_term=query,
                    location="",
                    results_wanted=RESULTS_PER_QUERY,
                    hours_old=HOURS_OLD,
                    verbose=0,
                )
            except Exception as e:
                print(f"  jobspy {site}/{query!r} error: "
                      f"{type(e).__name__}: {str(e)[:120]}")
                continue
            if df is None or len(df) == 0:
                continue
            for _, raw in df.iterrows():
                job = _row_to_job(raw.to_dict(), site)
                url = job["url"]
                if not job["title"] or not url or url in seen:
                    continue
                seen.add(url)
                out.append(job)
    print(f"  JobSpy: {len(out)} jobs "
          f"(sites={'/'.join(SITES)}, queries={len(QUERIES)})")
    return out


async def fetch_jobspy(session) -> list[dict]:
    """Async entry point used by the scanner, with a hard time box."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_fetch_sync), timeout=BATCH_TIMEOUT_SEC
        )
    except Exception as e:
        print(f"  JobSpy batch failed: {type(e).__name__}: {str(e)[:120]}")
        return []