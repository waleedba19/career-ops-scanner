# 🚀 CareerOps — Enterprise Job Intelligence Platform

[![Tests](https://github.com/waleedba19/career-ops-scanner/actions/workflows/tests.yml/badge.svg)](https://github.com/waleedba19/career-ops-scanner/actions/workflows/tests.yml)
[![CareerOps Scan](https://github.com/waleedba19/career-ops-scanner/actions/workflows/scan.yml/badge.svg)](https://github.com/waleedba19/career-ops-scanner/actions/workflows/scan.yml)
[![Dashboard](https://img.shields.io/badge/dashboard-live-38bdf8)](http://localhost:8000)
[![API](https://img.shields.io/badge/API-docs-0ea5e9)](http://localhost:8001/docs)

**AI-powered job intelligence that runs itself.** Built for **Waleed Ballag** — ESL Instructor, Academic Supervisor (15 theses), Arabic↔English Translator (Legal/Academic) from Libya. Finds *worldwide remote* roles across 30+ sources, scores with 4-bucket + AI 5-dimension evaluation, and delivers via Telegram + Email + Excel + **Live Dashboard + REST API**.

> **For anyone:** Fork, set 4 secrets, and get 3× daily scans forever — no servers to manage.

---

## ✨ What Makes It Big (Enterprise-Grade)

| Layer | What It Does | Tech |
|---|---|---|
| **Fetcher Registry** | 30+ sources deduped, tier-aware (1=lean 15, 2=balanced 30, 3=full sweep), circuit-breaker, rate-limited, retry+backoff | `config.py` + `fetchers/registry.py` |
| **Scoring Engine** | 4 buckets (Arabic Translation 40-70pts, ESL, Editing, Admin) + `REMOTE_MARKER` + seniority/negative filters + worldwide residency gating | `scanner.py` |
| **AI Analysis** | Local **Ollama `qwen2.5:1.5b`** (no API costs) 5-dimension scoring: Technical 30% / Experience 25% / Behavioral 15% / Location PASS-FAIL / Career 30% | `ollama_analyzer.py` |
| **Learning Loop** | Application feedback → scoring boost; company research → legitimacy + red-flags; evolution brain 90-day trends | `learning_module.py` `company_research.py` `evolution_tracker.py` |
| **Delivery** | Telegram cards, Brevo HTML email (Excel `.xls` 5 sheets + up to 10 PDF cover letters), **red=unapplied** | `notifier.py` `excel_generator.py` |
| **Observability** | Structured logs (`output/logs/*.jsonl`), Prometheus `health.json`/`metrics.json`, source performance report | `careerops_logger.py` `metrics.py` |
| **Dashboard** | Live dark-mode UI: KPIs, fresh matches table, evolution brain, daily log — auto-refresh 30s | `dashboard/app.py` → `:8000` |
| **REST API** | `GET /api/health` `GET /api/metrics` `GET /api/jobs?min_score&category` `GET /api/stats` `POST /api/apply` | `api_server.py` → `:8001` |
| **Persistence** | `state/` synced via GitHub Contents API (`state_sync.py`) — survives ephemeral runners | `.github/workflows/scan.yml` |
| **Deployment** | `Dockerfile` + `docker-compose.yml` (Ollama sidecar), `Makefile`, `.env.example` |  |

---

## 🏗️ Architecture

```
GitHub Actions (cron 05:00 / 13:00 / 20:00 UTC)
  ├─ state_sync.py download  (state/ → output/)
  ├─ Ollama (qwen2.5:1.5b)    ← cached, fallback to templates
  ├─ scanner.py               ← registry-driven fetchers (tier_cap=2), batch=8
  ├─ ollama_analyzer, company_research, cover_letters, interview_prep
  ├─ notifier (Telegram + Brevo) + excel_generator (5 sheets)
  └─ state_sync.py upload    (output/ → state/) + health/metrics

Local / Docker
  ├─ make dev  → dashboard :8000 + api :8001 + scanner
  └─ docker-compose up → careerops + ollama
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for deep dive, data flow, and scoring formulas.

---

## 🚦 Quick Start

### 1) GitHub Actions (zero servers)

1. Fork this repo
2. **Settings → Secrets and variables → Actions → New repository secret:**

| Secret | Where to get |
|---|---|
| `TELEGRAM_BOT_TOKEN` | @BotFather on Telegram |
| `TELEGRAM_CHAT_ID` | @userinfobot |
| `BREVO_API_KEY` | https://app.brevo.com/settings/keys/api |
| `TO_EMAIL` | your inbox |

3. **Actions → CareerOps Job Scan → Run workflow** (manual trigger) — watch it scan 5k+ jobs

### 2) Local

```bash
git clone https://github.com/waleedba19/career-ops-scanner
cd career-ops-scanner
pip install -r requirements.txt
cp .env.example .env  # fill secrets
python scanner.py                 # one scan
make dashboard  # http://localhost:8000
make api        # http://localhost:8001  (health, jobs, stats)
make dev        # all three in parallel
```

### 3) Docker (recommended for dashboard + Ollama)

```bash
docker-compose up --build -d
open http://localhost:8000   # dashboard
curl http://localhost:8001/api/health | jq
docker logs -f careerops-scanner
```

---

## ⚙️ Configuration (`config.py`)

All tuning via env (see `.env.example`):

```bash
OLLAMA_MODEL=qwen2.5:1.5b
CAREEROPS_TIER_CAP=2          # 1 lean, 2 balanced, 3 full (default 2)
CAREEROPS_MIN_SCORE=65
CAREEROPS_FRESH_H=0.5         # 30 min fresh window
CAREEROPS_BATCH_SIZE=8
CAREEROPS_ENABLE_OLLAMA=1
```

Fetcher tiers: Tier 1 (Greenhouse 34, Lever, Remotive, RemoteOK, WWR, Jobicy API, Arbeitnow, Himalayas API) always on; Tier 2 (+ Nodesk, YayRemote etc); Tier 3 (+ MENA/freelance). Controlled by `CAREEROPS_TIER_CAP`.

### 🔍 Source coverage — audit & expansion

**[SOURCES.md](SOURCES.md)** is the honest inventory: what actually runs today (31 sources at the production tier cap before the probe wiring → 34 after it, 38 once the optional API keys exist, with 6 probe-blocked hosts skipped — see §0.1), which of them produce matches, why Indeed / LinkedIn / Glassdoor can't be scraped directly and what the legit routes are, and a ~150-candidate expansion catalog (`source_candidates.json`).

```bash
make probe                                   # or: python probe_sources.py [--group ats-language-ai ...]
# GitHub: Actions → "Probe Sources" → Run workflow  (report in job summary + artifact)
```

Runs automatically (weekly + on every catalog change); the latest live report is committed to **[`state/source_probe.md`](state/source_probe.md)**. First run: **47 of 150 candidates respond with jobs from the runner** (LinkedIn guest search works; Indeed/Glassdoor/ZipRecruiter and all MENA boards are blocked).

The probe hits every candidate once from the runner's IP and reports `ok / empty / blocked / not_found / needs_key / error` with item counts, plus ready-to-paste `GREENHOUSE_COMPANIES` / Ashby / Workable snippets for the boards that answered. The `ok` list is the real answer to "how many sources can we add".

**Wired from the probe (`fetchers/verified.py`, add-only):** LinkedIn guest search (4 profile queries, remote + last 24 h), Freelancer projects API, Jobicy tag feeds, Impactpool (UN/NGO Arabic interpreter roles), Invisible / Labelbox / Turing Greenhouse boards, new Ashby / Workable / SmartRecruiters adapters (Mercor, Tamatem, Keywords Studios, TransPerfect), The Muse, Working Nomads JSON. Probe-blocked hosts (Bayt, Wuzzuf, GulfTalent, Mostaql, Ureed, ProZ) are skipped with a log line instead of wasting requests — set `CAREEROPS_FORCE_BLOCKED=1` to try them anyway.

**Optional secrets that unlock Indeed / LinkedIn / Glassdoor inventory legitimately** (each fetcher is a silent no-op until set): `RAPIDAPI_KEY` (JSearch), `ADZUNA_APP_ID` + `ADZUNA_APP_KEY`, `JOOBLE_API_KEY`, `RELIEFWEB_APPNAME`. Add them under *Settings → Secrets → Actions*; `scan.yml` already passes them through. Offline tests: `python test_verified_sources.py`.

---

## 📊 Outputs

- **Telegram** — professional cards with fit score, AI verdict, why-it-fits, apply link
- **Email (Brevo)** — HTML + text + Excel `.xls` (5 sheets: All Jobs / Fresh Matches / Applications / Cover Letters / Daily Log) + up to 10 PDF cover letters
- **Dashboard** `http://localhost:8000` — KPIs, tables, evolution, daily log
- **API** `http://localhost:8001` — `/health`, `/metrics` (Prometheus), `/jobs`, `/stats`, `/scan/history`, `POST /apply`
- **State** `state/*.json` — fresh_matches_history, smart_seen fingerprints, source_performance, evolution_brain (commit-persisted)

**Red rows = not applied yet** in Excel + Telegram unapplied reminder.

---

## 🧠 How It Learns

- **Smart dedup** — fingerprint `company|title[:30]|location[:20]` not just URL
- **Learning module** — applied/rejected → category (+10) and company affinity
- **Company research** — ATS detection, legitimacy score, red-flags
- **Evolution tracker** — 90-day streak, best day, trending categories/sources
- **Source manager** — auto-deactivates dead sources (14-day fail), discovers new RSS/JSON

---

## 🧪 Testing

```bash
python -m compileall -q .
python test_all_modules.py   # learning + research + interview + cover letters + excel
python test_improved.py      # freshness & scoring
pytest -q
```

---

## 📁 Project Layout

```
.
├── config.py               — single source of truth
├── scanner.py              — lean orchestrator (registry-driven, metrics hooks)
├── fetchers/               — base.py + registry.py (tier, dedup, circuit-breaker)
├── careerops_logger.py     — structured JSON logs
├── metrics.py              — health.json + prometheus text
├── dashboard/app.py        — live UI :8000
├── api_server.py           — REST API :8001 (FastAPI or stdlib fallback)
├── ollama_analyzer.py      — 5-dimension AI scoring
├── notifier.py             — Telegram + Brevo (fixed nested f-string bug)
├── excel_generator.py      — 5-sheet Excel
├── source_manager.py / evolution_tracker.py / learning_module.py
├── state/                  — persistent memory
├── output/                 — generated artifacts (gitignored)
├── Dockerfile / docker-compose.yml / Makefile / .env.example
└── .github/workflows/scan.yml  — cached Ollama, pip cache, tier Cap, artifacts
```

---

## 🔒 Secrets & Security

- No secrets in code — only `os.getenv` + GitHub Secrets
- `state_sync.py` uses short-lived `GITHUB_TOKEN` via Contents API
- Telegram failure alert on scan failure (workflow `if: failure()`)
- Brevo attachments capped at 5 MB (Excel) + 1 MB×10 PDFs

---

## 📦 Roadmap to Even Bigger

- [ ] Vector search (job embeddings) for semantic matching beyond keywords
- [ ] Playwright headless for JS-heavy boards
- [ ] Postgres + pgvector replace JSON state at scale
- [ ] Scheduler UI — adjust cron without editing YAML

---

**Made for Waleed — AI Job Search Intelligence that runs forever. 🔥**
