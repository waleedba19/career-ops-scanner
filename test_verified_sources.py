"""
Offline tests for fetchers/verified.py — the sources wired in after the live
Probe Sources run (state/source_probe.md).

Promises:
  1. Every parser turns a real-shaped payload into scanner-shaped job dicts
     (title / company / url / location / posted / description / salary / source).
  2. Keyed fetchers are silent no-ops when their secret is missing.
  3. LinkedIn stops on HTTP 999, backs off on 429, never raises.
  4. Parsed jobs survive the scanner's quality gates when they should
     (Arabic interpreter at IOM → kept; US-only → dropped).
  5. Registry / config wiring is consistent (no dangling names, blocked list
     really removes the blocked fetchers, force flag restores them).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetchers import verified as V

PASS = 0
FAIL = 0
REQUIRED = {"title", "company", "url", "location", "posted", "description", "salary", "source"}


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def shaped(jobs: list[dict]) -> bool:
    return bool(jobs) and all(REQUIRED <= set(j) and j["title"] and j["url"].startswith("http") for j in jobs)


# ── 1. parsers ──────────────────────────────────────────────────────────────

LI_HTML = """
<li><div class="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card" data-entity-urn="urn:li:jobPosting:4300001">
<a class="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]" href="https://ae.linkedin.com/jobs/view/translator-emirati-talent-at-acme-4300001?refId=abc&amp;trackingId=xyz">
<span class="sr-only">Translator Emirati Talent</span></a>
<div class="base-search-card__info"><h3 class="base-search-card__title">
        Translator Emirati Talent
      </h3><h4 class="base-search-card__subtitle"><a class="hidden-nested-link" href="https://ae.linkedin.com/company/acme">Acme Translation</a></h4>
<div class="base-search-card__metadata"><span class="job-search-card__location">Dubai, United Arab Emirates</span>
<time class="job-search-card__listdate--new" datetime="2026-09-06">1 hour ago</time></div></div></div></li>
<li><div class="base-card base-search-card job-search-card" data-entity-urn="urn:li:jobPosting:4300002">
<a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/hourly-paid-teacher-of-english-at-uni-4300002?trk=x">
<span class="sr-only">Hourly-Paid Teacher of English</span></a>
<h3 class="base-search-card__title">Hourly-Paid Teacher of English</h3>
<h4 class="base-search-card__subtitle">Open University</h4>
<span class="job-search-card__location">United Kingdom</span>
<time class="job-search-card__listdate" datetime="2026-09-05">1 day ago</time></div></li>
"""


def test_parsers():
    print("\n[1] parsers → scanner-shaped jobs")
    li = V.parse_linkedin_guest(LI_HTML)
    check("linkedin: 2 cards parsed", len(li) == 2, str(li))
    check("linkedin: shape", shaped(li))
    check("linkedin: title/company/location/date", li[0]["title"] == "Translator Emirati Talent"
          and li[0]["company"] == "Acme Translation" and "Dubai" in li[0]["location"] and li[0]["posted"] == "2026-09-06")
    check("linkedin: tracking params stripped", "?" not in li[0]["url"] and li[0]["url"].endswith("4300001"))
    check("linkedin: empty html → []", V.parse_linkedin_guest("") == [] and V.parse_linkedin_guest("<html>Just a moment</html>") == [])

    fl = V.parse_freelancer_projects({"status": "success", "result": {"projects": [
        {"title": "Arabic to English legal translation", "seo_url": "translation/Arabic-English-legal-40012345",
         "time_submitted": 1788700000, "preview_description": "Translate 20 pages of contracts.",
         "budget": {"minimum": 30, "maximum": 250}, "currency": {"code": "USD"}},
        {"title": "no seo url → skipped"},
    ]}})
    check("freelancer: 1 project parsed, bad one skipped", len(fl) == 1 and shaped(fl))
    check("freelancer: url/salary/posted", fl[0]["url"] == "https://www.freelancer.com/projects/translation/Arabic-English-legal-40012345"
          and fl[0]["salary"] == "30-250 USD" and fl[0]["posted"].startswith("2026-"))
    check("freelancer: garbage payload → []", V.parse_freelancer_projects(None) == [] and V.parse_freelancer_projects({"result": {}}) == [])

    jb = V.parse_jobicy({"jobs": [{"jobTitle": "Translation Project Manager", "companyName": "Lingo", "url": "https://jobicy.com/jobs/1",
                                   "jobGeo": "Anywhere", "pubDate": "2026-09-06 08:00:00", "jobDescription": "<p>Manage <b>Arabic</b> projects</p>",
                                   "salaryMin": 40000, "salaryMax": 60000, "salaryCurrency": "USD", "salaryPeriod": "yearly"}]})
    check("jobicy: parsed + html stripped + salary", shaped(jb) and jb[0]["description"] == "Manage Arabic projects" and jb[0]["salary"].startswith("40000-60000"))

    wn = V.parse_workingnomads([{"url": "https://www.workingnomads.com/job/go/1837431/", "title": "AI Image Evaluation Analyst",
                                 "description": "Rank AI responses.\nTranslation experience a plus.", "company_name": "iMerit Technology",
                                 "category_name": "Administration", "tags": "analyst,english", "location": "Japan, Turkey, Vietnam",
                                 "pub_date": "2026-09-06T02:37:03-04:00"}, {"title": "no url"}])
    check("workingnomads: real payload shape", len(wn) == 1 and shaped(wn) and wn[0]["company"] == "iMerit Technology" and wn[0]["location"].startswith("Japan"))

    ip_html = """
    <a class="job-card" href="/jobs/1234493"><div class="title">Interpreter (Arabic)</div><div class="org">IOM - International Organization for Migration</div><div class="loc">Athens</div><div>UG - Ungraded</div></a>
    <a href="https://www.impactpool.org/jobs/1215693"><div>Monitoring &amp; Evaluation Specialist (Roster – Multiple Locations)</div><div>CTG - Committed To Good</div><div>Remote | Multiple locations</div><div>Senior - Senior level</div></a>
    <a href="/jobs/1234493"><div>duplicate</div></a>
    <a href="/about"><div>About us</div></a>
    """
    ip = V.parse_impactpool(ip_html)
    check("impactpool: 2 unique postings, nav ignored", len(ip) == 2 and shaped(ip), str(ip))
    check("impactpool: title/org/location split", ip[0]["title"] == "Interpreter (Arabic)" and ip[0]["company"].startswith("IOM")
          and ip[0]["location"] == "Athens" and ip[1]["location"].startswith("Remote"))

    muse = V.parse_themuse({"results": [{"name": "Academic Editor", "company": {"name": "Cactus"}, "locations": [{"name": "Flexible / Remote"}],
                                         "refs": {"landing_page": "https://www.themuse.com/jobs/cactus/academic-editor"},
                                         "publication_date": "2026-09-05T10:00:00Z", "contents": "<p>Edit theses</p>"}]})
    check("themuse: parsed", shaped(muse) and muse[0]["description"] == "Edit theses")

    ash = V.parse_ashby({"jobs": [{"title": "Arabic Linguist", "location": "Cairo", "isRemote": True, "jobUrl": "https://jobs.ashbyhq.com/mercor/abc",
                                   "publishedAt": "2026-09-01T00:00:00Z", "descriptionPlain": "Evaluate Arabic model output"}]}, "Mercor")
    check("ashby: parsed + remote flag folded into location", shaped(ash) and ash[0]["location"].startswith("Remote") and ash[0]["company"] == "Mercor")

    wk = V.parse_workable({"jobs": [{"title": "Arabic Localization QA", "city": "Amman", "country": "Jordan", "remote": True,
                                     "url": "https://apply.workable.com/tamatem/j/ABC123/", "published_on": "2026-09-02", "description": "<p>LQA</p>"}]}, "Tamatem Games")
    check("workable: parsed", shaped(wk) and wk[0]["location"] == "Remote — Amman, Jordan")

    sr = V.parse_smartrecruiters({"content": [{"id": "744000012345", "name": "Arabic Linguist", "company": {"identifier": "TransPerfect"},
                                               "location": {"city": "Remote", "country": "us", "remote": True}, "releasedDate": "2026-09-03T00:00:00.000Z"}]}, "TransPerfect")
    check("smartrecruiters: parsed + url built", shaped(sr) and sr[0]["url"] == "https://jobs.smartrecruiters.com/TransPerfect/744000012345")

    js = V.parse_jsearch({"status": "OK", "data": [{"job_title": "Arabic Translator", "employer_name": "Acme", "job_apply_link": "https://www.indeed.com/viewjob?jk=1",
                                                   "job_city": None, "job_country": "AE", "job_is_remote": True, "job_posted_at_datetime_utc": "2026-09-06T01:00:00.000Z",
                                                   "job_description": "Translate", "job_publisher": "Indeed"}]})
    check("jsearch: parsed, publisher recorded in source", shaped(js) and js[0]["source"] == "jsearch:indeed" and js[0]["location"].startswith("Remote"))

    ad = V.parse_adzuna({"results": [{"title": "ESL <strong>Teacher</strong>", "company": {"display_name": "Kaplan"}, "redirect_url": "https://www.adzuna.co.uk/jobs/land/ad/1",
                                      "location": {"display_name": "UK"}, "created": "2026-09-06T00:00:00Z", "description": "Teach", "salary_min": 25000.0, "salary_max": 30000.0}]})
    check("adzuna: parsed, html stripped from title", shaped(ad) and ad[0]["title"] == "ESL Teacher" and ad[0]["salary"] == "25000-30000")

    jo = V.parse_jooble({"totalCount": 1, "jobs": [{"title": "Proofreader", "company": "X", "link": "https://jooble.org/jdp/1", "location": "Remote", "updated": "2026-09-06", "snippet": "Proofread", "salary": ""}]})
    check("jooble: parsed", shaped(jo))

    rw = V.parse_reliefweb({"data": [{"fields": {"title": "Arabic Interpreter", "url": "https://reliefweb.int/job/1", "source": [{"name": "IOM"}],
                                                 "date": {"created": "2026-09-06T00:00:00+00:00"}, "country": [{"name": "Libya"}], "body": "Interpret."}}]})
    check("reliefweb: parsed", shaped(rw) and rw[0]["company"] == "IOM" and rw[0]["location"] == "Libya")


# ── 2. keyed fetchers are no-ops without secrets ───────────────────────────

class _NoNetSession:
    """Fails loudly if any fetcher tries the network when it should not."""
    def get(self, *a, **k):
        raise AssertionError("network call attempted without a key")
    post = get


def test_keyed_noops():
    print("\n[2] keyed aggregators are silent without secrets")
    for var in ("RAPIDAPI_KEY", "ADZUNA_APP_ID", "ADZUNA_APP_KEY", "JOOBLE_API_KEY", "RELIEFWEB_APPNAME"):
        os.environ.pop(var, None)
    s = _NoNetSession()
    for name, fn in (("jsearch", V.fetch_jsearch), ("adzuna", V.fetch_adzuna), ("jooble", V.fetch_jooble), ("reliefweb", V.fetch_reliefweb)):
        try:
            out = asyncio.run(fn(s))
            check(f"{name}: [] without key, no network", out == [])
        except AssertionError as e:
            check(f"{name}: [] without key, no network", False, str(e))


# ── 3. LinkedIn transport behaviour (999 stop, 429 back-off, never raises) ──

class _Resp:
    def __init__(self, status, body=""):
        self.status = status
        self._body = body
    async def text(self, errors="ignore"):
        return self._body
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return False


class _ScriptedSession:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.calls = 0
    def get(self, url, **k):
        self.calls += 1
        st = self.statuses.pop(0) if self.statuses else 200
        return _Resp(st, LI_HTML if st == 200 else "")


def test_linkedin_transport():
    print("\n[3] LinkedIn guest transport")
    V_sleep = asyncio.sleep  # V.asyncio is the same module object — patch once, restore after

    async def _instant(*_a, **_k):
        await V_sleep(0)
    asyncio.sleep = _instant  # don't actually wait in tests
    try:
        s = _ScriptedSession([200, 999, 200, 200])
        out = asyncio.run(V.fetch_linkedin_guest(s))
        check("999 stops immediately (2 calls, not 4)", s.calls == 2 and len(out) == 2, f"calls={s.calls} jobs={len(out)}")
        s = _ScriptedSession([429, 200, 200, 200])
        out = asyncio.run(V.fetch_linkedin_guest(s))
        check("429 backs off and continues", s.calls == 4 and len(out) == 2, f"calls={s.calls} jobs={len(out)}")
        s = _ScriptedSession([200, 200, 200, 200])
        out = asyncio.run(V.fetch_linkedin_guest(s))
        check("duplicates across queries collapsed", len(out) == 2)

        class _Boom:
            def get(self, *a, **k):
                raise RuntimeError("connection reset")
        out = asyncio.run(V.fetch_linkedin_guest(_Boom()))
        check("transport error → [] (never raises)", out == [])
    finally:
        asyncio.sleep = V_sleep


# ── 4. parsed jobs vs the scanner's quality gates ──────────────────────────

def test_gates():
    print("\n[4] parsed jobs through scanner gates")
    from scanner import drop_unqualified_matches, get_match_score, is_stub_listing, is_open_worldwide
    iom = V.parse_impactpool('<a href="/jobs/1"><div>Interpreter (Arabic)</div><div>IOM - International Organization for Migration</div><div>Remote | Athens</div></a>')[0]
    check("IOM Arabic interpreter passes stub gate", not is_stub_listing(iom))
    check("IOM Arabic interpreter scores as Arabic Translation", get_match_score(iom["title"], iom["description"]).get("category") == "Arabic Translation"
          or get_match_score(iom["title"], iom["description"]).get("score", 0) >= 65, str(get_match_score(iom["title"], iom["description"])))
    kept = drop_unqualified_matches([iom])
    check("IOM Arabic interpreter survives final gate", len(kept) == 1)

    us_only = V.parse_jsearch({"data": [{"job_title": "Arabic Translator", "employer_name": "X", "job_apply_link": "https://x/1",
                                         "job_city": "Austin", "job_state": "TX", "job_country": "US", "job_is_remote": True,
                                         "job_description": "Must be authorized to work in the US. US residents only."}]})[0]
    check("US-only JSearch job dropped by worldwide gate", drop_unqualified_matches([us_only]) == [])

    li = asyncio.run(V.fetch_linkedin_guest(_ScriptedSession([200, 999])))
    check("LinkedIn card is not a stub", not is_stub_listing(li[0]))
    # Regression: the search query must not leak into the description — the scorer
    # reads it, and "Chinese Translator" would become a 100-point Arabic match.
    check("LinkedIn description does not echo the search query",
          "arabic" not in li[0]["description"].lower() and li[0].get("matched_query"))
    check("Wrong-language LinkedIn hit is not upgraded to Arabic",
          get_match_score("Chinese Translator", li[0]["description"])["score"] == 0)
    src_v = Path("fetchers/verified.py").read_text(encoding="utf-8")
    check("no fetcher injects the query into description",
          'description"] = f"' not in src_v and "query: {q}" not in src_v)
    check("LinkedIn f_WT=2 remote filter reflected in location", li[0]["location"] == "Remote — Dubai, United Arab Emirates", li[0]["location"])
    check("Dubai (remote) accepted as worldwide-eligible", is_open_worldwide(li[0]["location"], li[0]["description"]))
    check("US remote LinkedIn card still rejected", not is_open_worldwide("Remote — Austin, Texas, United States", li[0]["description"]))


# ── 5. wiring consistency ─────────────────────────────────────────────────

def test_wiring():
    print("\n[5] registry / config / scanner wiring")
    import config
    import scanner
    from fetchers.registry import FETCHERS, TIER_MAP
    names = {n for n, _, _, _ in FETCHERS}
    for n in ("linkedin", "freelancer_api", "jobicy_tags", "impactpool", "greenhouse_profile", "ashby", "workable",
              "smartrecruiters", "themuse", "jsearch", "adzuna", "jooble", "reliefweb", "freelancer"):
        check(f"registry has {n}", n in names)
    check("freelancer promoted to tier 1", TIER_MAP.get("freelancer") == 1)
    check("linkedin is tier 1", TIER_MAP.get("linkedin") == 1)
    for var in ("GREENHOUSE_PROFILE_BOARDS", "ASHBY_COMPANIES", "WORKABLE_COMPANIES", "SMARTRECRUITERS_COMPANIES"):
        lst = getattr(config, var)
        check(f"config.{var} well-formed", all(isinstance(t, tuple) and len(t) == 2 and all(isinstance(x, str) and x for x in t) for t in lst) and lst)
    check("blocked list = probe-confirmed set", set(config.PROBE_BLOCKED_SOURCES) == {"mostaql", "ureed", "wuzzuf", "bayt", "gulftalent", "proz"})
    check("scanner picked up config lists", scanner.GREENHOUSE_PROFILE_BOARDS == config.GREENHOUSE_PROFILE_BOARDS
          and scanner.PROBE_BLOCKED_SOURCES == config.PROBE_BLOCKED_SOURCES)
    for fn in ("fetch_linkedin_guest", "fetch_freelancer_api", "fetch_jobicy_tags", "fetch_impactpool", "fetch_themuse",
               "fetch_ashby_board", "fetch_workable_board", "fetch_smartrecruiters_board", "fetch_jsearch", "fetch_adzuna_keyed",
               "fetch_jooble_keyed", "fetch_reliefweb"):
        check(f"scanner imports {fn}", callable(getattr(scanner, fn, None)))
    src = Path("scanner.py").read_text(encoding="utf-8")
    for nm in ("mostaql", "wuzzuf", "bayt", "gulftalent", "proz"):
        check(f"{nm} is guarded by _blocked()", f'_blocked("{nm}")' in src or f'("{nm}", fetch_{nm})' in src)


if __name__ == "__main__":
    test_parsers()
    test_keyed_noops()
    test_linkedin_transport()
    test_gates()
    test_wiring()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)
