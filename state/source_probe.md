# Source probe — 2026-09-10 23:39 UTC

_Ran from: github-actions · 150 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 47 | responded with parseable jobs → **can be added** |
| empty | 18 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 24 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 50 | 404/410 → slug or endpoint is wrong |
| needs_key | 8 | add the secret and re-run |
| error | 3 | DNS/TLS/timeout |

## Answer: **40 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 308 | Data Engineer:in / IT Support (m/w/d); Performance Marketing Working Student – Talen; Mitarbeiter /Leiter (w\|m\|d) interne Qualitäts |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 532 | Business Development Manager; Quality Dispense Technician North; Social Comms |
| ✅ ok | `baseline:wwr` | 90 | 200 | 517 | Toptal: Power Platform Solutions Architect; TestGorilla: Sr. People &amp; Talent Operatio; Coaching.com: Membership Coordinator |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 927 | IT Associate; Enterprise Sales VP, Labor and Trust; Product Manager, Orchestrator |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 126 | Senior Graphic Designer - AM; Senior AI Product Manager, EMEA; Lead Analyst, Credit Risk Strategy |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 161 | Thorough Code Review of Decentralized, Encryp; Bangun Toko Shopify Minimalis Modern; WordPress &amp; GHL Virtual Assistant |
| ✅ ok | `baseline:remotive` | 18 | 200 | 102 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |

## precision-queries  <sub>ok 8 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 831 | Social Comms; AI Response Analyst; Senior Level Designer |
| ✅ ok | `precision:jobicy-teaching` | 50 | 200 | 1147 | AI Engineer - FDE (Forward Deployed Engineer); Work from home as a Private Online German Tut; Senior Customer Marketing Manager |
| ✅ ok | `precision:wwr-all-other` | 50 | 200 | 196 | TestGorilla: Sr. People &amp; Talent Operatio; Toptal: Senior Security Compliance Consultant; Salesloft: Enterprise Account Director |
| ✅ ok | `precision:jobicy-translation` | 44 | 200 | 1115 | Translation Project Manager; Alliance Manager, Translational Medicine; Senior Brand Designer, Experiential |
| ✅ ok | `precision:workingnomads-api` | 43 | 200 | 823 | Client Success Manager; Video Creator (100% remote); Senior Java & React Developer |
| ✅ ok | `precision:remotive-translator` | 18 | 200 | 22 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |
| ✅ ok | `precision:remotive-teacher` | 18 | 200 | 21 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |
| ✅ ok | `precision:remotive-writer` | 18 | 200 | 19 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 8 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 346 | Analyst,Underwriter; Analyst,Underwriter; P&C Middle Market Energy Renewal Underwriter |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 429 | Arabic Linguist CAT II - CENTCOM; مترجم طبي عربي–تركي; Arabic Copywriter |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 517 | Examiner - International GCSE - Arabic as a F; Arabic Linguist CAT II - CENTCOM; Search Evaluator Specialist - Arabic Speaking |
| ✅ ok | `linkedin:guest-esl` | 10 | 200 | 425 | Reading Tutor – PH; English Tutor; Corporate English Trainer |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 453 | Editorial Proofreader \| US Shift (7:00 PM Onw; Editor: Bioinformatics (Work-from-home); Marketing Copy Editor &amp; Proofreader |

## freelance  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 199 | Polish Speakers Needed for 813 Short Sentence;  Egypt Arabic Speakers Needed for 438 Short S; Convert MRMS GRIB2 to GEMPAK |
| ✅ ok | `freelancer:api-esl` | 20 | 200 | 222 | AI Training: Image Reviewing & Annotation -- ; AI Training Subject Matter Expert — Accountin; SEO Content Writer for Diverse Topics |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 216 | Quick Chrome Addon Enhancement; Female Content Creator & Video Editor Needed; YouTube Gaming Video Editor |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 223 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 85 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 72 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 148 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 252 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 101 | 200 | 99 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 410 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 22 | 200 | 50 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 79 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Deployment Lead |
| ⚪ empty | `ashby:deel` | 0 | 200 | 137 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 194 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 194 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 144 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 436 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 420 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 122 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 17 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 107 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 600 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 35 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 53 | 200 | 440 | Technical Artist ; Game Designer – Japan & Global Game Developme; Game Programmer – Japan & Global Game Develop |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 404 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 343 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 1026 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 421 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 330 | 243745 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 402 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 378 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 5641 | 132990 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 297 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 59 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 67 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 91 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 376 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 114 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 114 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 106 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 114 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 46 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 604 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 792 | 186382 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 1771 | 213026 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 1032 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 478 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 251 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 487 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 18 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 263 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 108 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 104 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 18 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 914 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 19 | 200 | 122 | Business Development/ Sales Executive - EMEA ; Community & Support Intern - UAE Nationals; Community and Support Specialist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 263 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 463 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 126 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 202 | 200 | 1073 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 2015 | Security Engineer ; Risk Partnerships Manager, Banks & Treasury; Product Manager, Sail Core |
| ✅ ok | `html:jobgether` | 6 | 200 | 343 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 322 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 1061 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 85 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 68 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 595 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15939 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 3165 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 487 | 428358 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 64 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 476 | HTTP 403 |

## esl-boards  <sub>ok 2 · empty 0 · blocked 0 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:eslbase` | 43 | 200 | 1511 | Get job alerts; Get job alerts; English Teaching Jobs in Vietnam with VUS |
| ✅ ok | `html:eslcafe-international` | 12 | 200 | 182 | Job Center; International Job Board; Korean Job Board |
| ❓ not_found | `html:tefl-online` | 0 | 404 | 576 | HTTP 404 |
| ❓ not_found | `html:teachaway-online` | 0 | 404 | 402 | HTTP 404 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 190 | 200 | 1664 | Openings; Search; WFP - World Food Programme |
| ✅ ok | `html:impactpool-arabic` | 10 | 200 | 1378 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic)


IOM - International Or; Consultants template


WHO - World Health Org |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 406 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 56 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1935 | Jobs in Jordan (51); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 115 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 79 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 141 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 420 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 461 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 124 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15697 | timeout >15s |

## academic-editing-watchers  <sub>ok 3 · empty 1 · blocked 1 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 2020 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ✅ ok | `watch:enago` | 9 | 200 | 705 | Academic Editor; Reviewer and Journal Expert; Senior Scientific Editor |
| ✅ ok | `watch:papertrue` | 3 | 201 | 440 | Jobs; Jobs; Jobs |
| ⚪ empty | `watch:prs` | 0 | 200 | 707 | 345101 bytes, text/html |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 199 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 458 | HTTP 404 |
| ❓ not_found | `watch:wordvice` | 0 | 404 | 1313 | HTTP 404 |

## major-platforms-blocked  <sub>ok 1 · empty 1 · blocked 5 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `wellfound:html` | 70 | 200 | 387 | Find Jobs; Enterprise Solutions Engineer; Design Engineer, Site |
| ⚪ empty | `google:jobs` | 0 | 200 | 125 | 92864 bytes, text/html |
| ⛔ blocked | `indeed:html` | 0 | 401 | 39 | HTTP 401 + challenge page |
| ⛔ blocked | `indeed:rss` | 0 | 403 | 13 | HTTP 403 + challenge page |
| ⛔ blocked | `glassdoor:html` | 0 | 403 | 75 | HTTP 403 |
| ⛔ blocked | `ziprecruiter:html` | 0 | 403 | 66 | HTTP 403 + challenge page |
| ⛔ blocked | `upwork:search` | 0 | 403 | 111 | HTTP 403 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 831 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 22 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 101 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 19 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 53 jobs
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
