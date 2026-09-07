# Source probe — 2026-09-07 08:34 UTC

_Ran from: github-actions · 150 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 47 | responded with parseable jobs → **can be added** |
| empty | 18 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 22 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 51 | 404/410 → slug or endpoint is wrong |
| needs_key | 8 | add the secret and re-run |
| error | 4 | DNS/TLS/timeout |

## Answer: **40 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 203 | Performance Marketing Manager (m/w/d) - Berli; Senior BI Developer (m/w/d); Buchhalter Mieten (m/w/d) Teilzeit |
| ✅ ok | `baseline:remoteok` | 100 | 200 | 366 | AI Response Analyst; Junior Crypto Analyst & Trader; Customer Support & Success Specialist |
| ✅ ok | `baseline:wwr` | 91 | 200 | 419 | Veracode: Principal Account Executive; Legion: Director of Production Engineering; Fastly: Senior SRE - Networks |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 637 | International Audio/Video Remote Armenian Int; International Audio/Video Remote Arabic Inter; International Audio/Video Remote Afghani/Dari |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 157 | Change Business Partner - MRP; Senior Associate, Underwriter (Remote, any st; Principal Technology Architect |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 49 | Edit Konten E-Learning Teknologi; Middle Eastern Buyers&rsquo; Sourcing Agent \|; Recruitment Specialist for Talent Acquisition |
| ✅ ok | `baseline:remotive` | 18 | 200 | 119 | Sales Jedi; SaaS Product Support Jedi; Freelance Writer |

## precision-queries  <sub>ok 8 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 345 | AI Response Analyst; courier; Senior Level Designer |
| ✅ ok | `precision:jobicy-teaching` | 50 | 200 | 727 | Specialty Insurance Underwriter/Coverage Atto; Senior Solutions Architect - ACE; Network IT Specialist |
| ✅ ok | `precision:wwr-all-other` | 49 | 200 | 159 | Ace Ventures: Executive Personal Assistant to; Reddit: Director, Privacy Legal; LawnStarter: Software Engineering Manager |
| ✅ ok | `precision:jobicy-translation` | 42 | 200 | 714 | Translation Project Manager; Alliance Manager, Translational Medicine; Junior Web Builder (Fully Remote, PH-Based On |
| ✅ ok | `precision:workingnomads-api` | 32 | 200 | 372 | AI Image Evaluation Analyst; AI Content Analyst (No Experience Required); Data Analyst (No Experience Required) |
| ✅ ok | `precision:remotive-translator` | 18 | 200 | 16 | Sales Jedi; SaaS Product Support Jedi; Freelance Writer |
| ✅ ok | `precision:remotive-teacher` | 18 | 200 | 29 | Sales Jedi; SaaS Product Support Jedi; Freelance Writer |
| ✅ ok | `precision:remotive-writer` | 18 | 200 | 12 | Sales Jedi; SaaS Product Support Jedi; Freelance Writer |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 8 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 468 | (Contract)  IDAM Analyst; Analyst,Underwriter; Analyst,Underwriter |
| 🔑 needs_key | `jsearch:arabic-translator` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `jsearch:esl-teacher` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `adzuna:gb` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `adzuna:us` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `jooble:arabic-translator` | 0 |  |  | missing secret(s): JOOBLE_API_KEY |
| 🔑 needs_key | `careerjet:arabic-translator` | 0 |  |  | missing secret(s): CAREERJET_AFFID |
| 🔑 needs_key | `reliefweb:arabic` | 0 |  |  | missing secret(s): RELIEFWEB_APPNAME |
| 🔑 needs_key | `reed:arabic-translator` | 0 |  |  | missing secret(s): REED_API_KEY_B64 |

## linkedin  <sub>ok 4 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 420 | Linguist — Arabic &amp; Spanish (Localization; Localization Specialist; Independent Contractor Translators &amp; Inte |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 429 | Linguist — Arabic &amp; Spanish (Localization; Language Enabled OSINT Collector (WMD Focused; Linguist I |
| ✅ ok | `linkedin:guest-esl` | 10 | 200 | 456 | English Tutor; Product Trainer; Hourly-Paid Teacher of English |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 455 | Content Writer/Editor; English Editor (Cover Letter Required); Scientific Editor, Medicine and Life Sciences |

## freelance  <sub>ok 3 · empty 1 · blocked 2 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 165 | Arabic B2G Profile & Cards; Complete B2C Travel Booking Platform for TAHL; تصميم ملف تعريفي احترافي باللغة العربية لبواب |
| ✅ ok | `freelancer:api-esl` | 20 | 200 | 183 | Mexico-Based E-Commerce Admin Consultant; Write 250-Page Managerial Economics Textbook; Remote Telemarketer - Philippines (Experience |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 133 | YouTube Documentary-Style Video Editor Requir; Engaging Promotional Video Editing; AI Video Editing Research |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 233 | 2371 bytes, text/html |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 102 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 33 | HTTP 429 |
| ❓ not_found | `guru:arabic-translation` | 0 | 404 | 135 | HTTP 404 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 829 | 200 | 159 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 96 | 200 | 52 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 79 | 200 | 56 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 26 | 200 | 35 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 80 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Deployment Lead |
| ⚪ empty | `ashby:deel` | 0 | 200 | 40 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 130 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 109 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 88 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 369 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 337 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 8 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 350 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 20 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 48 | 200 | 385 | ゲームエンジンプログラマー; Video Game Engine Programmer; Unreal Engineプログラマー |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 374 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 452 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 476 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 338 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 347 | 243621 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 352 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 335 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2458 | 132990 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 455 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 319 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 315 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 330 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 111 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 29 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 20 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 109 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 506 | 186380 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 100 | 213025 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 656 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 81 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 410 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 162 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 393 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 171 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 28 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 344 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 248 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 19 | 200 | 41 | Business Development/ Sales Executive - EMEA ; Community & Support Intern - UAE Nationals; Community and Support Specialist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 147 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 179 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 93 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 36 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 209 | 200 | 1594 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 2624 | Senior Solutions Architect; Spanish & English Speaking Customer Service -; Spanish and English Speaking Customer Service |
| ✅ ok | `html:jobgether` | 6 | 200 | 208 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 149 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 569 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 30 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 99 | HTTP 403 + challenge page |
| 💥 error | `html:remote-co` | 0 |  | 15527 | timeout >15s |
| 💥 error | `html:europeremotely` | 0 |  | 325 | ClientConnectorError: Cannot connect to host europeremotely.com:443 ssl:False [Connection reset by peer] |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1860 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 182 | 428357 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 53 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 257 | HTTP 403 |

## esl-boards  <sub>ok 2 · empty 0 · blocked 0 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:eslbase` | 44 | 200 | 1120 | Get job alerts; Get job alerts; Hiring Online English teachers! Earn 8 to 20  |
| ✅ ok | `html:eslcafe-international` | 12 | 200 | 349 | Job Center; International Job Board; Korean Job Board |
| ❓ not_found | `html:tefl-online` | 0 | 404 | 139 | HTTP 404 |
| ❓ not_found | `html:teachaway-online` | 0 | 404 | 226 | HTTP 404 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 192 | 200 | 1099 | Openings; Search; Save the Children |
| ✅ ok | `html:impactpool-arabic` | 14 | 200 | 663 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic)


IOM - International Or; Interpreter (Arabic)


IOM - International Or |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 156 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 45 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 5 | 200 | 1548 | Jobs in Jordan (47); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 159 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 100 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 105 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 230 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 301 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 58 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15265 | timeout >15s |

## academic-editing-watchers  <sub>ok 3 · empty 1 · blocked 1 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 1867 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ✅ ok | `watch:enago` | 9 | 200 | 78 | Academic Editor; Reviewer and Journal Expert; Senior Scientific Editor |
| ✅ ok | `watch:papertrue` | 3 | 201 | 584 | Jobs; Jobs; Jobs |
| ⚪ empty | `watch:prs` | 0 | 200 | 514 | 342275 bytes, text/html |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 100 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 203 | HTTP 404 |
| ❓ not_found | `watch:wordvice` | 0 | 404 | 1458 | HTTP 404 |

## major-platforms-blocked  <sub>ok 1 · empty 1 · blocked 5 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `wellfound:html` | 68 | 200 | 319 | Find Jobs; Senior Research Engineer; Senior Software Engineer, Security |
| ⚪ empty | `google:jobs` | 0 | 200 | 70 | 91858 bytes, text/html |
| ⛔ blocked | `indeed:html` | 0 | 401 | 21 | HTTP 401 + challenge page |
| ⛔ blocked | `indeed:rss` | 0 | 403 | 7 | HTTP 403 + challenge page |
| ⛔ blocked | `glassdoor:html` | 0 | 403 | 49 | HTTP 403 |
| ⛔ blocked | `ziprecruiter:html` | 0 | 403 | 100 | HTTP 403 + challenge page |
| ⛔ blocked | `upwork:search` | 0 | 403 | 49 | HTTP 403 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 829 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 26 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 96 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 19 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 48 jobs
    ("TransPerfect", "TransPerfect"),   # 18 jobs
```

```json
// source_registry.json additions
{"url": "https://weworkremotely.com/categories/all-other-remote-jobs.rss", "source_name": "wwr-all-other", "type": "rss"},
{"url": "https://www.workingnomads.com/api/exposed_jobs/", "source_name": "workingnomads-api", "type": "json"},
{"url": "https://www.themuse.com/api/public/jobs?page=1&category=Writing%20and%20Editing&level=Mid%20Level", "source_name": "writing-editing", "type": "json"},
{"url": "https://www.remote1stjobs.com/jobs.json", "source_name": "remote1stjobs", "type": "json"},
```

## Secrets to add for the keyed aggregators

Settings → Secrets and variables → Actions → New repository secret: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `CAREERJET_AFFID`, `JOOBLE_API_KEY`, `RAPIDAPI_KEY`, `REED_API_KEY_B64`, `RELIEFWEB_APPNAME`
