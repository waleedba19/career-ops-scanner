# CareerOps Job Scanner — GitHub Actions

[![Tests](https://github.com/waleedba19/career-ops-scanner/actions/workflows/tests.yml/badge.svg)](https://github.com/waleedba19/career-ops-scanner/actions/workflows/tests.yml)
[![CareerOps Job Scan](https://github.com/waleedba19/career-ops-scanner/actions/workflows/scan.yml/badge.svg)](https://github.com/waleedba19/career-ops-scanner/actions/workflows/scan.yml)

AI-powered job scanner that runs on GitHub Actions, analyzing 50+ remote job sources to find roles matching your profile (translator, ESL teacher, editor, data entry specialist, virtual assistant).

## How It Works

1. **Fetches jobs** from 45+ sources: Greenhouse boards (34 companies), Lever, Remotive, RemoteOK, We Work Remotely, Jobicy, Nodesk, Arbeitnow, YayRemote, Remote1stJobs, Real Work From Anywhere
2. **Scores each job** using weighted keyword matching across 4 categories: Translation, ESL, Editing, Admin
3. **Filters** by freshness (24h), location (worldwide-friendly), residency restrictions, and seniority penalties
4. **Verifies liveness** of top jobs via HTTP HEAD requests
5. **Ollama AI analysis** (local, no API costs) generates personalized "why this fits" explanations
6. **Sends notifications** via Telegram + Email (with Excel attachment via Brevo)
7. **Generates Excel report** with 5 sheets: All Jobs, Fresh Matches, Applications, Cover Letters, Daily Log — **red rows = jobs you haven't applied to yet**
8. **Remembers everything** — seen jobs, applications, learning data, and source discoveries persist between runs in the `state/` folder
9. **Grows coverage over time** — auto-discovery crawls job pages for new feeds and APIs on every run

## Required GitHub Secrets

Set these in **Settings > Secrets and variables > Actions**:

| Secret | Purpose |
|--------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token for notifications |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `BREVO_API_KEY` | Brevo (formerly Sendinblue) API key for email |
| `TO_EMAIL` | Email address to receive scan reports |

## Schedule

The scanner runs 3x daily via cron:
- **05:00 UTC** — Morning scan
- **13:00 UTC** — Afternoon scan
- **20:00 UTC** — Night scan

## Manual Trigger

Go to **Actions > CareerOps Job Scan > Run workflow** to trigger a scan manually.

## How It Stays Smart (persistent memory)

GitHub Actions runners are wiped after every run, so the scanner stores its state
in the `state/` folder of this repo (via the GitHub API) and restores it before
each scan:

- **No repeated messages** — jobs you've already seen are never reported again
- **Application tracking** — jobs you applied to are marked green; unapplied ones
  stay **red** in the Excel sheet, email, and Telegram
- **Evolution brain** — scan streaks, best days, and trends accumulate (look for
  the 🔥 streak in your daily message — that's your "it ran today" heartbeat)
- **Learning module** — your application history keeps fine-tuning match scores
- **Source discovery** — new job sources found on one run are remembered and used
  on the next, so coverage grows over time

## Daily Heartbeat

Every scan message includes the scan streak and totals. If a scan ever fails,
you get a Telegram alert with a link to the failed run instead of silence.

## Files

```
.github/workflows/scan.yml    — GitHub Actions workflow
scanner.py                    — Main scanner (fetching, scoring, filtering)
ollama_analyzer.py            — AI job analysis via local Ollama
notifier.py                   — Telegram + Email notifications
excel_generator.py            — Excel (.xls) report generation
requirements.txt              — Python dependencies
```

## Ollama AI Analysis

The scanner installs Ollama on the runner and pulls the `qwen2.5:1.5b` model for AI-powered job analysis. This is a small, fast model that fits within GitHub Actions runner limits.

If Ollama is unavailable, the scanner falls back gracefully and runs without AI insights.

## Local Development

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
export BREVO_API_KEY="..."
export TO_EMAIL="..."
python scanner.py
```
