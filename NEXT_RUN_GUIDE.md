# NEXT RUN GUIDE — CareerOps Scanner (human-live)

**Repo:** `waleedba19/career-ops-scanner` (same repo — no new repo, no new things)
**Session branch:** `arena/01a073ec-career-ops-scanner` → PR → `main`
**Companion files:** `NEXT_RUN_GUIDE.txt` (plain-text copy) · `ARena_HUMAN_LIVE_FIXES.patch` (restore bundle)

---

## 1. What this run fixed

**Problem:** At 00:11 Libya (22:11 UTC) the Telegram + Gmail digests showed
**5th Sept** instead of **6th Sept**, and the messages read like a template
(every run identical, "Best regards," + the same 0-match block).

**Fix (3 commits on top of `origin/main` = `4cba49b`):**

| Commit | What |
|---|---|
| `daa7039` feat: human-live | Libya live time everywhere + varied human messages + time-sensitive Excel |
| `7fc7e5a` fix: complete green | Legacy aliases for test compatibility + Libya live preview |
| `83a061f` chore: bundle patch | `ARena_HUMAN_LIVE_FIXES.patch` restore kit |

### a) Libya live time (the date bug)

- `LIBYA_TZ = timezone(timedelta(hours=2))` (Africa/Tripoli, UTC+2, no DST since 2013)
  + `now_libya()` in `notifier.py`, `excel_generator.py`, `evolution_tracker.py`,
  `cover_letter_generator.py`, `interview_prep.py`; `scanner.py` main flow uses it for
  the Excel filename, scan time and **email subject**.
- 00:11 Libya now correctly shows **2026-09-06** (was 2026-09-05 via UTC).
- `time_str` shows `00:11 AM Libya (22:11 UTC)` — Libya first, UTC in parentheses.
- Scan labels follow Libya hours (runs land 07:00 / 15:00 / 22:00 Libya).
- Evolution brain day-boundary, streaks and "Live as of" follow the Libya day.
- Cover-letter PDF date lines + file names use the Libya date.

### b) Varied human messages (no more copy-paste feel)

- **HUMAN_GREETINGS** — 3 per scan slot (Morning Intel / Afternoon Briefing / Night Digest),
  rotated by `(hour + minute) % 3` → back-to-back runs in the same slot read differently.
- **HUMAN_CLOSINGS** — 4 closings, rotated by `(minute + second) % 4` → changes almost every run.
- **NO_MATCH_NOTES** — 3 different 0-match texts, picked by a stable hash
  of `(date + scan_num) % 3` → same run reproduces, different run differs.
- Example header: `🌙 Night Digest — Sunday, September 06, 2026 — 12:31 AM Libya`
  followed by a rotating line like `Late check — I stayed up so you don't have to.`
- Next-scan line is Libya time: `Next scan: 07:00 Libya (tomorrow morning)`.

### c) Excel sensitive to time/date/events

- Titles: `… — Live as of 12:31 AM Libya …` on All Jobs and Fresh Matches sheets.
- **market_pulse** by hour:
  - Morning: `fresh before the US wakes — early posts are quiet and less contested`
  - Mid-day: `European wave — most postings land 9 AM-4 PM CET, right in this window`
  - Night: `less competition now; US evening posts are just starting to appear`
- Rotating **human_note** on Fresh Matches (4 variants, hour-based).
- Daily Log sheet: dates + times in **Libya** (header says so).

### d) Legacy aliases (keeps old test suites green)

- `company_research.py`: `research_company = get_company_research`
- `cover_letter_generator.py`: `generate_cover_letter(job) → generate_cover_letter_pdf(job)`
- `interview_prep.py`: `generate_interview_prep(job) → generate_interview_questions(job, load_cv_profile())`

---

## 2. Verification results (this sandbox, offline)

```
python -m compileall -q .            → exit 0
python test_all_modules.py           → 6/6 ALL TESTS PASSED
python test_e2e_fixed.py             → 10/10 VERIFICATION COMPLETE
notifier check                       → now_libya() 01:42 Libya  vs  now_utc() 23:42 UTC
                                       date 2026-09-06 (Libya) vs 2026-09-05 (UTC) — correct
timeout 300 python scanner.py        → full pipeline, 52 sources, offline 0 fetched
                                       (graceful), Excel saved, exit 0
```

On GitHub Actions (with internet) a full scan takes ~2-5 min and reviews
thousands of listings across 52 sources.

---

## 3. How to use this in the next run

### If the new chat cloned `main` AFTER this work merged

Nothing to do. Everything (code + patch + guides) is already in the clone.
Just run the verification block in §4, then `gh workflow run scan.yml`.

### If the new chat is BLIND (fresh clone missing these commits)

```bash
git fetch origin
git checkout -B work origin/main
# restore the whole human-live change set in one apply:
git apply ARena_HUMAN_LIVE_FIXES.patch
# or straight from GitHub if the local file is missing:
curl -s https://raw.githubusercontent.com/waleedba19/career-ops-scanner/main/ARena_HUMAN_LIVE_FIXES.patch | git apply
```

If `git apply` complains (context drift), the patch is just two logical
changes — re-apply by hand:
1. the `now_libya()` / greeting / closing / Excel changes (§1),
2. the three legacy aliases (§1d) — they are the only thing the tests need.

---

## 4. Verification block (copy-paste, any sandbox)

```bash
cd career-ops-scanner
python -m compileall -q . && echo "OK compileall"
python test_all_modules.py          # expect: 6/6 ALL TESTS PASSED
python test_e2e_fixed.py            # expect: 10/10 VERIFICATION COMPLETE
python -c "from notifier import now_libya, now_utc; print(now_libya(), now_utc())"
timeout 300 python scanner.py       # full mode: expect exit 0, 'Excel saved', graceful offline
gh workflow run scan.yml            # trigger the real 52-source scan on GitHub
```

### What green looks like

- `test_all_modules.py` → `Total: 6/6 tests passed`
- `test_e2e_fixed.py` → all 10 steps `Status: OK` + `VERIFICATION COMPLETE`
- `now_libya()` date **one day ahead** of `now_utc()` between 22:00-24:00 UTC
- scanner → `Excel saved: …/careerops-scan-<LIBYA-date>.xls`, exit 0
- Actions → `Tests` workflow: test + docker jobs ✓; `CareerOps Job Scan` ✓

### Things that must NEVER appear in a message again

- a UTC date as the headline date (e.g. `2026-09-05` when it's 06 in Libya)
- the same greeting/closing on two different runs
- `Time (UTC)` in the Excel Daily Log
