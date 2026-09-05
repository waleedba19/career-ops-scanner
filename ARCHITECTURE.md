# CareerOps Architecture — Enterprise Deep Dive

## 1. Vision
A self-running job intelligence platform that **fetches 5k+ jobs 3× daily, scores with deterministic + LLM layers, learns from user feedback, and delivers via 4 channels** — with zero servers to manage (GitHub Actions) and optional local/Docker dashboard.

## 2. Data Flow
```
Sources (30+)
  → Fetchers (registry, tier-aware, deduped, retry+circuit breaker)
  → Normalization (strip_html, normalize_date, extract_salary)
  → Filters (paid, age, positive/negative keywords, NON_TARGET_ROLE, worldwide residency)
  → Scoring (MATCH_BUCKETS → best 0-100, remote bonus, penalties)
  → Learning adjustment (applied history → boost)
  → Smart dedup (fingerprint company|title|location)
  → Liveness (HEAD top 6)
  → Ollama 5D (technical 30 / experience 25 / behavioral 15 / location PF / career 30)
  → Company research → Cover letters → Interview prep
  → Notifications (Telegram chunked 4k, Brevo HTML+Excel+PDFs)
  → Metrics + Health + State sync
```

## 3. Scoring Engine (Deterministic)

### Buckets
- **Arabic Translation** — `arabic translator|interpreter|linguist` 65pts, `arabic speaker 40-50`, `localization 50`, `translation 45`, `bilingual arabic 60`
- **ESL** — `esl|tesol|tefl 40`, `english teacher 35`, `tutoring 15`
- **Editing** — `proofread 35`, `academic editing 30`, `content writer 25`
- **Admin** — `data entry 42`, `virtual assistant 35`, `data annotation 24`

### Algorithm per bucket
```
hits = phrases matched in title/desc
weight = w*2.5 if title+desc else w*2 if title else w
score += weight per phrase
if hits>=2: +25
if desc_hits>=2: +15
if title_hits>0: *1.8
capped at 100, best bucket wins
+10 if REMOTE_MARKER else 0
-50 if NEGATIVE_KEYWORDS in title
-15 if SENIOR_PENALTY
rounded to nearest 5
```

### Filters (order, early reject)
1. `no_url` 2. `paid` (flexjobs etc) 3. `too_old` (>144h) 4. `no_positive` 5. `non_target` (NON_TARGET_ROLE without ALLOWLIST) 6. `negative` 7. `not_worldwide` (13 residency blockers + soft location blockers) 8. `low_score` (<65)

Fresh = `posted is None or age <=0.5h`. Near-miss = 50-64, capped 6.

## 4. AI Layer (Ollama)

- **Model:** `qwen2.5:1.5b` (local, unified via `OLLAMA_MODEL` env; workflow caches `~/.ollama`)
- **Prompt:** 5-dimension rubric with hard rules (engineer→<40, visa fail→overall<50)
- **Fallback:** template cover letters + no AI insight if Ollama unreachable
- **Dims:** technical_skills, experience_match, behavioral_fit, location_logistics (PASS/FAIL/FLAG), career_alignment → weighted overall; verdict Strong/Good/Moderate/Weak/Poor

## 5. Learning & Evolution

- `learning_module`: applied_jobs → skill_preferences, company_preferences, acceptance_rate; `adjust_scoring_based_on_learning` boosts +5-15
- `evolution_tracker`: streak (1-day gap), total_scans/matches, daily_history 90d, category_trends, source_trends, best_day
- `source_manager`: per-source fetched/matches, consecutive_empty → active/weak/inactive (14d), cleanup dead >30d inactive
- `company_research`: legitimacy_score, positive_signals (ATS), red_flags, score_adjustment
- `interview_prep`: questions per category for score>=85

## 6. Fetchers — Registry Pattern

`fetchers/registry.py` defines 18 deduped fetchers (vs 88 legacy). `TIER_CAP` env controls:

- **Tier1 (8):** greenhouse, lever, remotive, remoteok, wwr, jobicy_api, arbeitnow, himalayas_api
- **Tier2 (+8):** nodesk, yayremote, remote1stjobs, realworkfromanywhere, workingnomads, jobspresso, justremote, hirelatam (+ proz/smartcat/gotranscript if tier2)
- **Tier3 (+9):** MENA/freelance (mostaql, for9a, ureed, wuzzuf, bayt, gulftalent, freelancer, pph, guru)

Each fetcher wraps `with_retry(3, exponential backoff)` and `rate_limited(4/s)` via `fetchers/base.py` + circuit breaker (5 fails → 10min cooldown). Batch size 8, concurrency 25.

Legacy 40+ duplicates (himalayas_rss/worldwide, jobicy_rss/worldwide, remoteok_api, wwr_api, justremote_api, etc) removed — unified with internal fallback. Static stubs (italki etc returning 1 fake job) removed.

## 7. Persistence

- **Runtime:** `output/` (scan_history.json, seen_urls.json, fresh_matches_history.json, smart_seen.json, metrics.json, health.json, logs/)
- **Repo:** `state/` committed — synced by `state_sync.py` via GitHub Contents API (download before scan, upload after; no-op locally)
- **Limits:** seen_urls 5k, smart_seen fingerprints 10k, scan_history 100, daily_history 90, source daily_stats 30

## 8. Observability

- `careerops_logger.py`: console (human) + `output/logs/*.jsonl` (JSON per line) + `scan_events.jsonl`
- `metrics.py`: per-source fetched/matches/errors/latency, funnel, timings → `health.json` (status healthy/degraded/unhealthy, health_score 0-100) + `metrics.json` + Prometheus `/metrics`
- Workflow exports `health.json`/`metrics.json` as artifacts; dashboard polls `/api/health`

## 9. Delivery

- **Telegram:** chunked 4000 chars, `format_job_card` per match, near-miss compact, unapplied red reminder, source report, next scan hint
- **Email (Brevo):** HTML cards (inline CSS), text fallback, attachments: Excel (<5MB) + up to 10 PDFs (<1MB each)
- **Excel (XML .xls 5 sheets):** All Jobs (green winners/red near-miss), Fresh Matches (accumulated, red=unapplied/green=applied), Applications, Cover Letters, Daily Log
- **Dashboard:** dark theme, KPIs, tables, auto-refresh 30s, served via `dashboard/app.py` or FastAPI static
- **API:** REST (`api_server.py`) with FastAPI if available else stdlib fallback; health, metrics, jobs filter, stats, scan history, mark applied

## 10. Deployment

- **GitHub Actions:** checkout, state restore, Python 3.12 + pip cache, Ollama install+cache, qwen2.5:1.5b pull, lint, source_discovery, scanner, metrics export, state upload, failure Telegram, artifacts
- **Docker:** `python:3.12-slim` + `ollama/ollama` sidecar, healthcheck, volumes for state/output
- **Make:** `install, scan, dashboard, api, dev, test, lint, docker, clean`

## 11. Security

- Env-only secrets, short-lived GITHUB_TOKEN, Brevo key in header, no PII in logs
- Liveness HEAD, timeout 10-15s, ssl=False for broad compat, no sponsorship/visa leak

## 12. Roadmap

- Vector embeddings for semantic match
- Playwright for JS boards
- Postgres+pgvector for state at 100k jobs
- Admin UI for cron tuning
