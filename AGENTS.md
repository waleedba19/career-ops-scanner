# CareerOps Scanner — Project Instructions

## Overview
This is an autonomous job search system that runs 3x daily on GitHub Actions. It finds remote jobs matching the user's profile, generates PDF cover letters, and delivers results via Telegram + Email + Excel.

## User Profile
- **Name**: Waleed
- **Email**: waleedzydeco19@gmail.com
- **Location**: Libya (UTC+2)
- **Skills**: Arabic/English translation, ESL teaching, editing, data entry, virtual assistance, bilingual content creator
- **Experience**: 5+ years in translation, content creation, and virtual assistance
- **Requirements**: Remote only, worldwide, no visa/residency restrictions

## Schedule
- **07:00 AM Libya** (05:00 UTC) — Morning Intel
- **03:00 PM Libya** (13:00 UTC) — Afternoon Briefing  
- **10:00 PM Libya** (20:00 UTC) — Night Digest

## Matching Rules
1. **75%+ match score** required for Fresh Matches
2. **Worldwide remote only** — no specific country locations
3. **No visa/residency blockers** — reject jobs requiring citizenship/work permits
4. **No paid platforms** — filter out FlexJobs, TopHire, Wellfound, ZipRecruiter
5. **6-day freshness window** — jobs older than 6 days are excluded
6. **30-minute fresh window** — jobs posted within 30 minutes get priority

## Negative Keywords (Auto-Reject)
- Enterprise sales, quota, commission, business development
- Account executive, sales representative, business partner
- Head of, director, VP, chief, country manager
- Senior manager, senior director, senior lead
- Content producer, social media lead, brand manager
- Payroll, field enablement, revenue, pipeline

## Positive Keywords (Auto-Match)
- Translation, translator, localization, interpreter
- ESL, English teacher, language teacher
- Copywriter, content writer, content creator
- Data entry, virtual assistant, executive assistant
- Proofreader, editor, bilingual, multilingual
- Arabic, Arabic-English, MENA region

## Sources (53+ sites)
### Remote Job Boards
- RemoteOK, Remotive, We Work Remotely, Jobicy, NodesK
- Arbeitnow, Yay Remote, Remote1stJobs, Real Work From Anywhere
- Himalayas, JustRemote, Working Nomads, Jobspresso, HireLatam

### Freelance Platforms
- Freelancer.com, PeoplePerHour, Guru.com
- Mostaql, For9a, Khamsat, Ureed, Wuzzuf

### Translation & Language
- ProZ, Gengo, Smartling, Unbabel, RWS, Carmel
- Lionbridge, TransPerfect, Appen

### Major Job Platforms
- LinkedIn, Indeed, Glassdoor, Bayt, GulfTalent, NaukriGulf
- Craigslist, Upwork, Fiverr, Toptal

### Arabic/MENA Specific
- Mostaql, For9a, Khamsat, Ureed, Wuzzuf, Daleel, Aqar, Tajer

## Ollama AI Scoring
- **Model**: qwen2.5:1.5b
- **Dimensions**: Technical (30%), Experience (25%), Behavioral (15%), Location (Pass/Fail), Career (30%)
- **Minimum Score**: 70/100 for AI verification
- **Purpose**: Verify job relevance beyond keyword matching

## Delivery
### Telegram
- Professional card format with job details
- Evolution intelligence summary
- Source performance report
- Reminders for unapplied jobs

### Email (Brevo)
- HTML email with job cards
- Excel attachment (5 sheets)
- PDF cover letters attached (up to 10 per scan)
- Evolution intelligence report

### Excel (5 sheets)
1. **All Jobs** — Full scan dump
2. **Fresh Matches** — Accumulated 75-100% matches
3. **Applications** — Track which jobs you've applied to
4. **Cover Letters** — Generated PDF letters with file paths
5. **Daily Log** — Scan history

## Cover Letters
- Auto-generated for every Fresh Match
- PDF format, ready to submit
- Personalized with user's CV details from `cv_profile.json`
- Different templates for translation, teaching, writing, general
- Attached to email for easy download

## Learning & Evolution
### Source Manager
- Tracks which sources return jobs
- Auto-removes dead sources after 14 days
- Auto-discovers new sources via RSS/JSON
- Source quality scoring

### Evolution Tracker
- Tracks trends over 90 days
- Best categories, best sources
- Streak days, best day records
- Acceptance rate tracking

## File Structure
```
scanner.py          — Main scanner (fetching, filtering, scoring)
notifier.py         — Telegram + Email delivery
excel_generator.py  — Excel generation (5 sheets)
cover_letter_generator.py — PDF cover letter generation
cv_profile.json     — User's CV details
source_manager.py   — Source performance tracking
evolution_tracker.py — Learning and trends
ollama_analyzer.py  — AI job scoring
source_discovery.py — Auto-discover new sources
```

## Rules for AI Assistant
1. **Never stop the system** — it must run forever
2. **Never remove working fetchers** — only add new ones
3. **Never lower the 75% match threshold** — quality over quantity
4. **Always test before pushing** — run a test scan first
5. **Log everything** — source breakdown, errors, performance
6. **Learn from failures** — if a source fails, log it and move on
7. **Evolve messages** — Telegram/Email content should improve over time
8. **Track applications** — help user know which jobs they applied to
9. **Generate cover letters** — every match gets a PDF letter
10. **Remind about unapplied jobs** — don't let opportunities slip

## Emergency Procedures
- If Ollama fails → keyword scoring continues as fallback
- If a fetcher fails → other fetchers continue, log the error
- If Telegram fails → email still sends
- If email fails → Excel still generates
- If Excel fails → Telegram + Email still work

## Monthly Maintenance
- Review source performance in Excel
- Update `cv_profile.json` with new experience
- Check for new job sites to add
- Review filter effectiveness
- Update negative/positive keywords if needed
