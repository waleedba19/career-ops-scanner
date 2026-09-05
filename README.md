# CareerOps Job Scanner — GitHub Actions

AI-powered job scanner that runs on GitHub Actions, analyzing 50+ remote job sources to find roles matching your profile (translator, ESL teacher, editor, data entry specialist, virtual assistant).

## How It Works

1. **Fetches jobs** from 45+ sources: Greenhouse boards (34 companies), Lever, Remotive, RemoteOK, We Work Remotely, Jobicy, Nodesk, Arbeitnow, YayRemote, Remote1stJobs, Real Work From Anywhere
2. **Scores each job** using weighted keyword matching across 4 categories: Translation, ESL, Editing, Admin
3. **Filters** by freshness (24h), location (worldwide-friendly), residency restrictions, and seniority penalties
4. **Verifies liveness** of top jobs via HTTP HEAD requests
5. **Ollama AI analysis** (local, no API costs) generates personalized "why this fits" explanations
6. **Sends notifications** via Telegram + Email (with Excel attachment via Brevo)
7. **Generates Excel report** with 5 sheets: All Jobs, Fresh Matches, Applications, Cover Letters, Daily Log

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
