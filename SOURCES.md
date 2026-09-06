# CareerOps — Source Coverage Audit & Expansion Plan

_Last audited: 2026-09-06 against branch `arena/01a077cd-career-ops-scanner`._

This document answers three questions honestly:

1. **How many sources actually run today?** (not what the READMEs claim)
2. **Which sources actually produce matches for Waleed's profile?** (evidence from `state/`)
3. **What can we add, how, and how many?** (a verified-able catalog + a probe tool)

---

## 1. TL;DR — claimed vs. real

| Metric | Number | Where it comes from |
|---|---|---|
| Sources the docs claim | "30+" (README), "53+" (AGENTS.md), "88" (ARCHITECTURE) | marketing drift |
| `fetch_*` functions defined in `scanner.py` | **101** | `grep "^async def fetch_"` |
| …of which are **never called** (dead code) | **71** (56 distinct sites + 15 duplicate variants) | call-site analysis |
| Sources that run in production (`CAREEROPS_TIER_CAP=2` in `scan.yml`) | **19** | `run_scan()` + `fetchers/registry.py` |
| Extra sources unlocked at tier 3 (currently **off**) | +9 → 28 max | `if tier_cap >= 3:` block |
| Jobs fetched (cumulative in `state/source_performance.json`) | ~28,000 | |
| Fresh matches produced (cumulative, `evolution_brain.json`) | **13** | 0.05 % conversion |

**The 19 that really run:** greenhouse (34 company boards), lever (1 board: Appen), remotive, remoteok, weworkremotely, jobicy, arbeitnow, himalayas, nodesk, yayremote, remote1stjobs, realworkfromanywhere, workingnomads, jobspresso, justremote, hirelatam, proz, smartcat, gotranscript.

**Dead code that the docs still advertise as sources:** indeed, linkedin, glassdoor, ziprecruiter, wellfound, upwork, fiverr, toptal, craigslist, flexjobs, appen*, lionbridge, transperfect, gengo, smartling*, unbabel, rws, carmel, translated, one_hour_translation, flitto, textmaster, preply, cambly, vipkid, qkids, magic_ears, italki, lingoda, amazingtalker, twenix, novakid, lingoace, nativecamp, tutorabc, eslgorilla, tefl_com, teachaway, recruitee, ashby, smartrecruiters, teamtailor, workbeam, remote.co, dailyremote, jobgether, landing.jobs, khamsat, daleel, aqar, tajer, naukrigulf, jooble, adzuna, meetfrank. (*covered indirectly via Greenhouse/Lever boards.)

Most of the dead fetchers were never functional anyway: `fetch_indeed` scrapes a Cloudflare-protected page, `fetch_linkedin` requests a `format=rss` feed that does not exist, `fetch_adzuna` uses a fake `app_key`, `fetch_jooble` calls the API without a key, `fetch_ashby`/`fetch_smartrecruiters`/`fetch_recruitee` hit endpoints without a company slug, and ~15 "ESL/translation" stubs returned **one hard-coded fake job** each (which is why `italki`, `lingoace`, `tutorabc`, `eslgorilla` show "1 fetched / 1 match" in the state files — those were not real matches).

---

## 2. Evidence — what actually produces matches

From `state/source_performance.json` + `state/evolution_brain.json`:

| Source | Fetched | Matches | Conversion | Status today |
|---|---:|---:|---:|---|
| **freelancer** (RSS) | 80 | 16 | **20 %** | ❌ tier 3 → **not running in production** |
| gotranscript | 6 | 2 | 33 % | ✅ running |
| qkids | 8 | 2 | 25 % | ❌ dead code |
| cambly | 8 | 1 | 12 % | ❌ dead code |
| textmaster | 12 | 1 | 8 % | ❌ dead code |
| nodesk | 240 | 1 | 0.4 % | ✅ running |
| remoteok | 1,000 | 1 | 0.1 % | ✅ running |
| **greenhouse** (34 boards) | **20,850** | **0** | 0 % | ✅ running |
| jobicy | 3,565 | 0 | 0 % | ✅ running |
| weworkremotely | 1,456 | 0 | 0 % | ✅ running |
| remotive / himalayas / lever / remote1stjobs / justremote / jobspresso | ~1,100 | 0 | 0 % | ✅ running |

**Takeaways**

- **"Deep and strong" ≠ "more sites".** The system already pulls 28k jobs and gets 13 matches. Volume from generic tech boards (Stripe, Airbnb, Figma, Reddit… on Greenhouse) is pure noise for an Arabic-translation / ESL / academic-editing profile.
- **The single best source is switched off.** `freelancer` is 400× more efficient than Greenhouse and is gated behind `tier_cap >= 3`, which the workflow never enables.
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
| A1 | Promote `freelancer`, `peopleperhour`, `guru`, `gotranscript` to tier ≤ 2 | Best conversion in the whole system; currently off |
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
| Today | 19 (28 at tier 3) | ~2 | — |
| **Phase 1** — Tier A + JSearch + Adzuna + LinkedIn guest + freelancer API | ~30 | 10–20 | 1 day: config + 3 fetchers + 3 secrets |
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
