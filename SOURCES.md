# CareerOps — Source Coverage Audit & Expansion Plan

_Last audited: 2026-09-06 against `main` @ `5a123fe` (after PRs #3–#5: tier cap 3, `eslgorilla`/`tes`/`reddit_social` added)._

This document answers three questions honestly:

1. **How many sources actually run today?** (not what the READMEs claim)
2. **Which sources actually produce matches for Waleed's profile?** (evidence from `state/`)
3. **What can we add, how, and how many?** (a verified-able catalog + a probe tool)

---

## 0. Live probe result — 2026-09-06 18:25 UTC, from the GitHub Actions runner

The `Probe Sources` workflow now runs automatically (weekly Mon 03:30 UTC, on every push to `main` or PR touching the catalog, and on demand). The latest report is always at **[`state/source_probe.md`](state/source_probe.md)**. First live run over all 150 candidates:

| status | count | meaning |
|---|---:|---|
| ✅ **ok** | **47** | responded with parseable jobs from the runner IP |
| ⛔ blocked | 22 | 403/429/challenge page — Indeed, Glassdoor, ZipRecruiter, Upwork, ProZ, Bayt, Wuzzuf, GulfTalent, Mostaql, Ureed, UNjobs, TranslatorsCafe, Scribbr… |
| ❓ not_found | 51 | slug guesses that don't exist on that ATS (Unbabel/Lilt/Preply/Babbel/Cambly… are on a different ATS — next iteration tries the alternatives) |
| ⚪ empty | 18 | endpoint valid, 0 items right now, or page needs a JS/JSON-LD parser (Nagwa, TransPerfect, Prolific, Deel, TELUS, Lionbridge, RWS, Acolad) |
| 🔑 needs_key | 8 | JSearch ×2, Adzuna ×2, Jooble, Careerjet, ReliefWeb, Reed — add the secrets and they light up |
| 💥 error | 4 | timeouts / oversized headers |

**Highest-value confirmed sources (now wired — see §0.1):**

| Source | Items | Why it matters |
|---|---:|---|
| `linkedin:guest-*` (4 profile queries, remote, last 24 h) | 10 each | **LinkedIn works from the runner** — samples: *Translator – Emirati Talent*, *Hourly-Paid Teacher of English*, *English Editor*, *Scientific Editor* |
| `greenhouse:agency` (Invisible) | 829 | Largest AI-trainer board incl. Arabic Language Specialist roles, worldwide |
| `precision:jobicy-translation` | 44 | keyword-filtered feed — *Translation Project Manager* in first results |
| `un-ngo: impactpool-arabic` | 15 | *Interpreter – Arabic/Sudanese Arabic (IOM)*, *Interpreter (Arabic)* |
| `html:remowork-arabic` | 209 | curated remote-Arabic board |
| `freelancer:api-*` (3 queries) | 20 each | keyword-precise version of the 17 %-conversion RSS |
| `ashby:mercor`, `greenhouse:turing`, `greenhouse:labelbox`, `html:dataannotation` | 96 / 26 / 10 / 79 | AI-data linguist marketplaces |
| `smartrecruiters:KeywordsStudios`, `smartrecruiters:TransPerfect` | 48 / 18 | game localisation / LSP boards |
| `workable:tamatem`, `html:tarjama-careers` | 18 / 5 | Arabic game localisation, Arabic LSP |
| `precision:workingnomads-api` | 32 | structured JSON replaces the HTML scrape (*AI Content Analyst*) |
| `esl-boards: eslcafe-international`, `eslbase` | 12 / 44 | ESL boards |
| `themuse:writing-editing` | 20 | free, no key |

### 0.1 What got wired into the scan after the probe (`fetchers/verified.py`)

Add-only, registered in `fetchers/registry.py`, dispatched from `run_scan()`, covered offline by `test_verified_sources.py` (78 checks: parsers on real-shaped payloads, key-less no-ops, LinkedIn 999/429 behaviour, quality gates, wiring consistency).

| Registry name | Tier | What runs | Requests / scan |
|---|:-:|---|---:|
| `linkedin` | 1 | LinkedIn guest search — 4 profile queries, `f_WT=2` (remote) + last 24 h; stops on HTTP 999, backs off on 429, never echoes the query into the description (that poisoned the scorer) | ≤ 4 |
| `freelancer_api` | 1 | Freelancer projects API, keyword-precise (`arabic translation`, `english teacher`, `proofreading editing`) | 3 |
| `freelancer` | 3 → **1** | the existing RSS fetcher — best converter in the system (30 of 56 all-time matches) now always runs | 1 |
| `jobicy_tags` | 1 | Jobicy tag feeds `translation` / `teaching` / `writing` | 3 |
| `impactpool` | 1 | Impactpool UN/NGO search (`arabic interpreter`, `arabic translator`, `translation`) | 3 |
| `greenhouse_profile` | 1 | `config.GREENHOUSE_PROFILE_BOARDS`: Invisible (`agency`), Labelbox/Alignerr, Turing — reuses `fetch_greenhouse` | 3 |
| `ashby` / `workable` / `smartrecruiters` | 2 | new ATS adapters over `config.ASHBY_COMPANIES` (Mercor), `WORKABLE_COMPANIES` (Tamatem), `SMARTRECRUITERS_COMPANIES` (Keywords Studios, TransPerfect — keyword-filtered list endpoint) | 1 / 1 / 12 |
| `themuse` | 2 | The Muse public API, Writing & Editing + Education, remote-filtered | 2 |
| `workingnomads` | 2 | switched to the JSON endpoint `api/exposed_jobs/` (the RSS twin 404s); old fetcher kept | 1 |
| `jsearch` · `adzuna` · `jooble` · `reliefweb` | 1 · 1 · 2 · 1 | keyed aggregators — **no-op until the secret exists** (`RAPIDAPI_KEY`, `ADZUNA_APP_ID`+`ADZUNA_APP_KEY`, `JOOBLE_API_KEY`, `RELIEFWEB_APPNAME`; already passed through in `scan.yml`) | 2 / 2 / 3 / 1 |

Also in the same change:

* **Probe-blocked hosts are skipped, not deleted.** `config.PROBE_BLOCKED_SOURCES` (`mostaql`, `ureed`, `wuzzuf`, `bayt`, `gulftalent`, `proz`) are logged as *"Skipping probe-blocked sources"* instead of spending 7 doomed requests per scan; `CAREEROPS_FORCE_BLOCKED=1` restores them (useful from a residential IP). `for9a` still runs — it answered.
* **Config-import bug fixed.** `scanner.py`'s `try: import config` block referenced `GREENHOUSE_COMPANIES` before it was defined, so every run silently fell into the `except` branch and ran on built-in defaults; the fallback now prints why it happened.
* The auto-discovered `state/source_registry.json` entries that duplicate a dedicated fetcher (remotive, WWR, jobicy, himalayas RSS twins) are skipped.

**Not wired on purpose** (probe "ok" but needs a real parser first): `html:remowork-arabic`, `html:untalent-arabic`, `html:eslbase`, `html:eslcafe-international` (samples were navigation text), `html:dataannotation` (titles concatenated with category + rate), `wellfound` (paid platform).

**Confirmed blocked from Actions (as predicted):** Indeed (401 + challenge), Glassdoor, ZipRecruiter, Upwork, and — notable — **all MENA boards (Bayt, Wuzzuf, GulfTalent, Mostaql, Ureed)** and **ProZ**, which the production scanner currently spends 6 requests/scan on for 0 results. Their inventory is reachable via JSearch/Adzuna/Jooble once the keys exist.

---

## 1. TL;DR — claimed vs. real

| Metric | Number | Where it comes from |
|---|---|---|
| Sources the docs claim | "30+" (README), "53+" (AGENTS.md), "88" (ARCHITECTURE) | marketing drift |
| `fetch_*` functions defined in `scanner.py` (+ `fetchers/social.py`) | **102** | `grep "^async def fetch_"` |
| …of which are **never called** (dead code) | **70** (55 distinct sites + 15 duplicate variants) | call-site analysis |
| Sources that run in production (`CAREEROPS_TIER_CAP=3` in `scan.yml` since PR #3) | **31** (19 registry + 3 translation + 9 MENA/freelance) | `run_scan()` + `fetchers/registry.py` |
| Sources that would run at the local default (`TIER_CAP=2`) | 22 | same |
| Jobs fetched (cumulative in `state/source_performance.json`) | ~55,400 | |
| Fresh matches produced (cumulative, 11 scans) | **41–56** | ~0.1 % conversion |

**The 31 that really run (tier cap 3):** greenhouse (34 company boards), lever (1 board: Appen), remotive, remoteok, weworkremotely, jobicy, arbeitnow, himalayas, nodesk, yayremote, remote1stjobs, realworkfromanywhere, workingnomads, jobspresso, justremote, hirelatam, reddit_social, eslgorilla, tes, proz, smartcat, gotranscript, mostaql, for9a, ureed, wuzzuf, bayt, gulftalent, freelancer, peopleperhour, guru.

**Dead code that the docs still advertise as sources:** indeed, linkedin, glassdoor, ziprecruiter, wellfound, upwork, fiverr, toptal, craigslist, flexjobs, appen*, lionbridge, transperfect, gengo, smartling*, unbabel, rws, carmel, translated, one_hour_translation, flitto, textmaster, preply, cambly, vipkid, qkids, magic_ears, italki, lingoda, amazingtalker, twenix, novakid, lingoace, nativecamp, tutorabc, eslgorilla, tefl_com, teachaway, recruitee, ashby, smartrecruiters, teamtailor, workbeam, remote.co, dailyremote, jobgether, landing.jobs, khamsat, daleel, aqar, tajer, naukrigulf, jooble, adzuna, meetfrank. (*covered indirectly via Greenhouse/Lever boards.)

Most of the dead fetchers were never functional anyway: `fetch_indeed` scrapes a Cloudflare-protected page, `fetch_linkedin` requests a `format=rss` feed that does not exist, `fetch_adzuna` uses a fake `app_key`, `fetch_jooble` calls the API without a key, `fetch_ashby`/`fetch_smartrecruiters`/`fetch_recruitee` hit endpoints without a company slug, and ~15 "ESL/translation" stubs returned **one hard-coded fake job** each (which is why `italki`, `lingoace`, `tutorabc`, `eslgorilla` show "1 fetched / 1 match" in the state files — those were not real matches).

---

## 2. Evidence — what actually produces matches

From `state/source_performance.json` + `state/evolution_brain.json`:

| Source | Fetched | Matches | Conversion | Status today |
|---|---:|---:|---:|---|
| **freelancer** (RSS) | 180 | 30 | **17 %** | ✅ running since PR #3 (tier cap 3) — by far the best source |
| himalayas (+ `himalayas_app` RSS dup) | 560 | 9 | 1.6 % | ✅ running (fetched twice — dedupe) |
| gotranscript | 18 | 2 | 11 % | ✅ running |
| search_discovered (DDG + sitemaps) | 160 | 3 | 1.9 % | ✅ running |
| qkids | 8 | 2 | 25 % | ❌ dead code |
| cambly | 8 | 1 | 12 % | ❌ dead code |
| textmaster | 12 | 1 | 8 % | ❌ dead code |
| nodesk / remote1stjobs / remoteok / jobicy | 8,200 | 4 | 0.05 % | ✅ running |
| **greenhouse** (34 boards) | **41,700** | **0** | 0 % | ✅ running |
| weworkremotely | 2,548 | 0 | 0 % | ✅ running |
| for9a | 828 | 0 | 0 % | ✅ running |
| remotive / lever / justremote / jobspresso / rws / smartling | ~1,000 | 0 | 0 % | ✅ running |

**Takeaways**

- **"Deep and strong" ≠ "more sites".** The system already pulls 55k jobs and gets ~50 matches. Volume from generic tech boards (Stripe, Airbnb, Figma, Reddit… on Greenhouse) is pure noise for an Arabic-translation / ESL / academic-editing profile.
- **One source produces more than half of all matches.** `freelancer` (30 of 56) converts at 17 % while Greenhouse converts at 0 % on 41,700 jobs. PR #3 turned it on; the next step is to query it precisely (Freelancer public API with `query=arabic translation`, Tier D below) instead of its generic RSS.
- **The Greenhouse company list is optimised for the wrong thing.** Of the 34 slugs, only ~8 are plausibly relevant (smartling, lokalise, duolingo, scaleai, outschool, khanacademy, coursera, okx). The other 26 cost 26 requests + ~20k jobs of noise per scan.
- **Coverage is measured in the wrong unit.** The metric that matters is _matches per source per week_, not source count. `source_manager.py` already tracks this — it just isn't used to decide what runs.

---

## 3. The truth about Indeed, LinkedIn, Glassdoor & co.

You asked specifically about Indeed. Here is the situation as of 2026:

| Platform | Free direct access? | Why | Legit route to the same inventory |
|---|---|---|---|
| **Indeed** | **No** | Publisher API deprecated in 2023; site is behind Cloudflare WAF + proprietary bot detection that blocks datacenter IPs (GitHub Actions runners are datacenter IPs). The legacy RSS feed is gone. Indeed also stopped giving free organic visibility to single-source feed jobs on 2026‑03‑31, so its free inventory is shrinking. | **JSearch** (Google for Jobs aggregate), **Adzuna**, **Jooble**, and — most importantly — the **upstream ATS boards** (Greenhouse/Lever/Workable/Ashby…) where those jobs are first published. |
| **LinkedIn** | **Low volume only** | No public read API. The guest endpoint `/jobs-guest/jobs/api/seeMoreJobPostings/search` works for small pulls but rate-limits (429) after ~10 pages per IP; a 999 response means "stop". No RSS (the dead fetcher's `format=rss` never existed). | A **targeted LinkedIn guest fetcher**: 4 profile queries × 1 page × `f_WT=2` (remote) × `f_TPR=r86400` (24 h) = 4 requests/run, ~100 fresh jobs. Well under limits. |
| **Glassdoor** | No | Cloudflare + heavy JS; even headless browsers on datacenter IPs get blocked. | JSearch (Google for Jobs mirrors Glassdoor). |
| **ZipRecruiter / Wellfound** | No (anti-bot) | Both are actually **free for job seekers** — `PAID_PLATFORMS` in `config.py` is wrong about them (only FlexJobs charges candidates). | JSearch mirrors ZipRecruiter. |
| **Upwork / Fiverr / Toptal** | No | Upwork RSS is login-gated and the API needs OAuth + approval; Fiverr and Toptal have no job postings to fetch (seller marketplace / vetted network). | Treat as manual/one-time. |
| **Google for Jobs** | Indirectly | Google aggregates Indeed + LinkedIn + Glassdoor + ZipRecruiter + career pages into one deduped feed. | **JSearch on RapidAPI** (free tier, small monthly cap) — one key gives you all of the above. |

**Bottom line:** the "Indeed opportunity" is real, but the way to capture it is (a) one aggregator key (JSearch) and (b) going _upstream_ to the ATS boards, not scraping indeed.com from Actions.

---

## 4. Expansion catalog — what we can add

Everything below is in machine-readable form in [`source_candidates.json`](source_candidates.json) and can be **verified in ~2 minutes** by running the `Probe Sources` workflow (see §7). Confidence: ✅ confirmed · 🟡 likely · ❔ guess (probe will tell).

### Tier A — Config-only quick wins (0 new code)

| # | Change | Why |
|---|---|---|
| A1 | Promote `freelancer` and `gotranscript` to tier 1 in `registry.py` (so they also run at `TIER_CAP=2`, e.g. locally / lean mode) | Best conversion in the whole system; today only on because the workflow forces tier 3 |
| A2 | Move the 26 irrelevant Greenhouse tech slugs to tier 3; keep the 8 language/EdTech ones | −26 requests, −20k noise jobs per scan |
| A3 | Add relevant Greenhouse/Lever slugs (see Tier E) | Same fetcher, right companies |
| A4 | Fix `PAID_PLATFORMS` (drop wellfound/ziprecruiter) | They're free for candidates |
| A5 | Make `run_scan()` honour `type: html` registry entries or stop discovering them | `source_discovery` found LinkedIn HTML (141 items) and it's silently ignored |
| A6 | Remove duplicate auto-discovered RSS entries (remotive/wwr/jobicy/himalayas are fetched twice) | wasted requests |

### Tier B — Generic ATS adapters (5 adapters unlock hundreds of companies)

These are **free, key-less, structured JSON** — the most reliable class of source that exists. Arbeitnow (already integrated) is itself built on these.

| ATS | Endpoint pattern | Format | Confidence |
|---|---|---|---|
| Greenhouse | `boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true` | JSON `jobs[]` | ✅ (in use) |
| Lever | `api.lever.co/v0/postings/{slug}?mode=json` | JSON list | ✅ (in use) |
| **Ashby** | `api.ashbyhq.com/posting-api/job-board/{slug}` | JSON `jobs[]` | ✅ |
| **Workable** | `apply.workable.com/api/v1/widget/accounts/{slug}?details=true` | JSON `jobs[]` | 🟡 |
| **SmartRecruiters** | `api.smartrecruiters.com/v1/companies/{co}/postings` + global search `jobs.smartrecruiters.com/sr-jobs/search?keyword=…` | JSON `content[]` / HTML | 🟡 |
| **Recruitee** | `{slug}.recruitee.com/api/offers/` | JSON `offers[]` | 🟡 |
| **Teamtailor** | `{slug}.teamtailor.com/jobs.rss` | RSS | 🟡 |
| Personio / BambooHR / Breezy / Jobvite | `{co}.jobs.personio.de/xml`, `{co}.bamboohr.com/careers/list`, `{co}.breezy.hr/json`, `jobs.jobvite.com/{co}` | XML/JSON/HTML | ❔ (phase 2) |
| Workday | `{tenant}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs` (POST) | JSON `jobPostings[]` | ❔ (used by big LSPs; fiddly) |
| **JSON-LD `JobPosting` generic parser** | any careers page | schema.org | — turns _any_ career page into a source |

### Tier C — Aggregator APIs with a free key (this is the Indeed answer)

| Source | What you get | Free quota | Secret needed | Confidence |
|---|---|---|---|---|
| **JSearch (RapidAPI)** | Google for Jobs = Indeed + LinkedIn + Glassdoor + ZipRecruiter + career pages, real-time, `remote_jobs_only` filter | Small monthly cap on Basic plan → budget ~2 queries/run or run once a day | `RAPIDAPI_KEY` | ✅ |
| **Adzuna** | Aggregated ads, 19 countries (gb, us, ca, au, de, fr, nl, …), `what_or` keyword search | 1,000 calls/month (≈ 11 per scan) | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` | ✅ |
| **Jooble** | Aggregator, 60+ countries incl. MENA, POST search | Free key by request form | `JOOBLE_API_KEY` | ✅ |
| **Careerjet** | Aggregator with `locale_code` per country | Free affiliate ID | `CAREERJET_AFFID` | 🟡 |
| **ReliefWeb** | UN/NGO humanitarian jobs — Arabic interpreter/translator demand is structurally high (Libya, Sudan, Syria, Yemen, Palestine ops) | Free, but appname must be **pre-approved** (since 2025‑11‑01) | `RELIEFWEB_APPNAME` | ✅ |
| Reed (UK), The Muse (US) | Regional aggregators | Free key | `REED_API_KEY`, `MUSE_API_KEY` | 🟡 (low priority) |
| USAJOBS | Free, but US-citizenship roles | — | — | ⛔ skip |

### Tier D — Targeted low-volume fetchers (one each)

| Source | Method | Notes |
|---|---|---|
| **LinkedIn guest search** | GET `linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=…&location=Worldwide&f_WT=2&f_TPR=r86400&start=0` | 4 queries/run, parse `base-card__full-link`, `base-search-card__title/__subtitle`, `<time datetime>`. Back off on 429, **stop on 999**. |
| **Freelancer public API** | GET `freelancer.com/api/projects/0.1/projects/active/?query=arabic translation&compact=true` | Keyword-precise version of the RSS that already converts at 20 % |
| **Mostaql / Ureed / Bayt / Wuzzuf keyword pages** | HTML | Already written (tier 3) — just point them at `translator` / `مترجم` queries instead of the front page |

### Tier E — Profile-specific company boards (the real "deep")

These companies hire exactly Waleed's profile, remotely, worldwide, and most publish via a free ATS endpoint. Verified examples from the live web (Sept 2026): Invisible's Greenhouse board `agency` lists "Arabic Language Specialist – AI Trainer" roles, **World Wide – Remote, $6–65/hr**; OKX's Greenhouse board lists "Arabic Language Manager, Localization (Remote)".

**AI-data / linguist marketplaces (highest pay, most postings, worldwide):**
Invisible (`greenhouse:agency` ✅), Scale AI / Outlier (`greenhouse:scaleai` ✅), xAI "AI Tutor – Arabic" (`greenhouse:xai` ✅), OKX (`greenhouse:okx` ✅), Appen (`lever:appen` ✅), Labelbox / Alignerr (`greenhouse:labelbox` 🟡), Prolific (`workable:prolific` 🟡), Deel (`ashby:deel` 🟡), Mercor (❔), Micro1 (❔), Turing (❔), SuperAnnotate SME Careers (❔), Handshake AI (`greenhouse:joinhandshake` 🟡), Toloka / Mindrift (❔), TELUS International AI, Welocalize (`jobvite` ❔), RWS TrainAI, Centific/OneForma, Surge AI, Pareto, DataAnnotation, Datamundi, Clickworker.

**Language service providers:**
Unbabel (`lever:unbabel` 🟡), Lilt (`lever:lilt` 🟡), Smartling ✅, Lokalise ✅, Phrase (❔), Crowdin, Acolad/TextMaster (had matches), Keywords Studios, TransPerfect, Lionbridge, RWS, Acclaro, Argos Multilingual, Andovar, Alconost, Straker, LanguageLine, Propio, **Tarjama (UAE — Arabic LSP)**, Torjoman, Saudisoft, Future Group (Egypt), Blend (ex-OneHourTranslation).

**EdTech / ESL:**
Duolingo ✅, Outschool ✅, Khan Academy ✅, Coursera ✅, Preply (`greenhouse:preply` 🟡), Babbel (🟡), Busuu (❔), Lingoda (`recruitee:lingoda` ❔), Cambly (❔), Novakid (❔), Open English (❔), Engoo, **Nagwa (Egypt — Arabic/English educational content, exact fit)**, Abwaab (`workable:abwaab` ❔), Noon Academy (`lever:noonacademy` ❔), Edraak, Almentor, Baims.

**Arabic content / MENA remote-first:**
Anghami (`lever:anghami` ❔), Tamatem — Arabic game localisation (`workable:tamatem` ❔), Mawdoo3, Kalimat, Sarwa.

**Academic editing (Academic Supervisor / 15 theses fit):**
Scribbr, Scribendi, Cactus/Editage, Enago, Wordvice, PaperTrue, Proof-Reading-Service, Kibin. These have static "freelance editor" pages → implement as **watchers** (alert on change), not fetchers.

### Tier F — Niche boards & feeds worth testing

| Group | Candidates |
|---|---|
| Remote boards with Arabic listings | **remowork.life/jobs/languages/arabic** (121 remote Arabic jobs, daily), euremotejobs.com (WP Job Manager RSS), remotejobleads.com (RSS), remote.co, dailyremote, dynamitejobs, europeremotely |
| Translation boards | ProZ ✅, TranslatorsCafe, TranslationDirectory, Smartcat ✅, GoTranscript ✅ |
| ESL boards | Dave's ESL Cafe (international), TEFL.com, TESall, ESLbase, Teach Away |
| UN / NGO | ReliefWeb (Tier C), UNjobs (theme: translation), Impactpool, UNTalent, Idealist |
| MENA boards | Bayt, GulfTalent, NaukriGulf, Wuzzuf, Tanqeeb, Akhtaboot, For9a ✅, Ureed ✅, Mostaql ✅ |
| Community | Reddit r/forhire JSON (❔ datacenter 403 risk) |

**Evergreen marketplaces (apply once, do not scan):** italki, Cambly tutors, Preply tutors, AmazingTalker, Native Camp, Palfish, Engoo, Fiverr, Toptal, Khamsat. The old stubs turned these into fake "1 new job" matches every scan — they belong in a one-time checklist, not the scanner.

---

## 5. What "deep" means beyond adding sites

1. **Precision queries instead of firehose + filter.** Most APIs accept search terms (Remotive `search=`, Jobicy `tag=`, Adzuna `what_or=`, JSearch `query=`, LinkedIn `keywords=`, Freelancer `query=`). Query the ~12 profile terms (`arabic translator`, `arabic linguist`, `localization`, `esl`, `english teacher online`, `proofreader`, `academic editor`, `transcription`, `subtitling`, `data annotation arabic`, `virtual assistant`, `content writer arabic`) and let scoring rank, rather than pulling 20k tech jobs and discarding 99.95 %.
2. **Enrich only the finalists.** Fetch the full job page for the top ~20 candidates before Ollama scores them — right now many sources pass a 1-line or empty `description`, so the 5-dimension AI score runs on nothing.
3. **Health classes per source:** `ok / empty / blocked(403·429·999·captcha) / not_found / parse_error / timeout`. Today everything is "0 jobs", so we can't tell a dead parser from a Cloudflare block. `source_manager` should auto-tier on this.
4. **Separate "posting sources" from "evergreen marketplaces" and "watchers".** Three different behaviours; today they're all "fetchers".
5. **Match-per-source scoreboard drives the tiers** (weekly): anything with matches in the last 14 days is tier 1 regardless of volume; anything with 0 matches in 30 days drops to tier 3.
6. **One JSON-LD `JobPosting` parser** so every company careers page discovered by search becomes a structured source for free.

---

## 6. How many, then? — targets

| Phase | Sources live | New matches expected/week (est.) | Effort |
|---|---:|---|---|
| Today | 31 (tier cap 3) | ~4–5 | — |
| **Phase 1** — Tier A + JSearch + Adzuna + LinkedIn guest + freelancer API | ~38 | 10–20 | 1 day: config + 3 fetchers + 3 secrets |
| **Phase 2** — ATS adapters (Ashby/Workable/SmartRecruiters/Recruitee/Teamtailor) + ~40 verified profile boards from the probe | ~70 (5 adapters × many companies count as boards, not sources) | 30–50 | 2–3 days |
| **Phase 3** — Jooble, Careerjet, ReliefWeb, MENA keyword pages, watchers, JSON-LD generic | ~90 | +10–20, incl. UN/NGO Arabic roles | 2 days |

Target: **~60–90 _healthy_ sources of which ≥ 40 are profile-specific**, not 100+ nominal ones. Beyond that, returns drop and Actions runtime (45-min limit) becomes the constraint.

---

## 7. Verify before you build — the probe

Because Indeed/LinkedIn/etc. behave differently from a datacenter IP than from your laptop, the only trustworthy answer to "which of these work?" comes from the GitHub Actions runner itself.

```bash
# locally (needs internet)
python probe_sources.py                      # all candidates
python probe_sources.py --group aggregator-keyed --group ai-data
python probe_sources.py --only greenhouse:agency,linkedin:guest-search
# results → output/source_probe.md + output/source_probe.json
```

Or on GitHub: **Actions → "Probe Sources" → Run workflow**. The report is attached as an artifact and printed in the job summary. Keyed sources are reported as `needs_key` until the corresponding secret exists (`RAPIDAPI_KEY`, `ADZUNA_APP_ID`/`ADZUNA_APP_KEY`, `JOOBLE_API_KEY`, `CAREERJET_AFFID`, `RELIEFWEB_APPNAME`).

The probe reports every candidate as `ok / empty / blocked / not_found / needs_key / error` with item counts and latency, and prints ready-to-paste `GREENHOUSE_COMPANIES` / `LEVER_COMPANIES` / Ashby / Workable slug lists for the boards that responded. **The `ok` list is the real answer to "how many can we add".**
