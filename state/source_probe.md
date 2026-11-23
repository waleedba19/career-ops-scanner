# Source probe — 2026-11-23 13:30 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 39 | responded with parseable jobs → **can be added** |
| empty | 24 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 12 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 62 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 5 | DNS/TLS/timeout |

## Answer: **32 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 300 | 200 | 156 | Working Student, Export Control/ Internationa; Senior Sales Manager, Regional Enterprise; Business Development Representative (German s |
| ✅ ok | `baseline:remoteok` | 100 | 200 | 471 | Product Manager, Developer Ecosystem; Manager, Technical Accounting and Equity Repo; Senior SRE, Site Experience |
| ✅ ok | `baseline:wwr` | 100 | 200 | 660 | Affirm: Analytics Lead, Full Stack; Oportun: Senior Manager, Risk Strategy (R1434; Coinbase: Compliance, Senior Associate |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 143 | Business Development Representative; Business Services Team Manager; Cloud Platform Engineer |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 66 | Hematology Physician; Medical Oncologist; Pediatric Hematology/Oncology Physician |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 125 | Money and work; Promote Global Export Accelerator Program; LIANZA &mdash; Sito web multilingue e piattaf |
| ✅ ok | `baseline:remotive` | 16 | 200 | 58 | Content Reviewer - United States; Tech Lead Full-Stack Rails Engineer; Content Creator - YouTube |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:wwr-all-other` | 118 | 200 | 549 | Oportun: Senior Manager, Risk Strategy (R1434; Coinbase: Compliance, Senior Associate; Talkspace: General Application for Clinical a |
| ✅ ok | `precision:remoteok-writing` | 40 | 200 | 573 | Business Development Specialist Arabic speake; Technical Lead Norm Compliance; Research Engineer Privacy and Anonymization |
| ✅ ok | `precision:workingnomads-api` | 37 | 200 | 252 | Looking For Online ESL Teachers - Remote- Joi; Case Manager (Philippines); Content Reviewer - United States |
| ✅ ok | `precision:jobicy-translation` | 28 | 200 | 38 | Sr. Clinical Research Associate (Brazil); English to Belarusian Review Lead for UI, Mar; Sr. Marketing Designer |
| ✅ ok | `precision:remotive-translator` | 16 | 200 | 14 | Content Reviewer - United States; Tech Lead Full-Stack Rails Engineer; Content Creator - YouTube |
| ✅ ok | `precision:remotive-teacher` | 16 | 200 | 13 | Content Reviewer - United States; Tech Lead Full-Stack Rails Engineer; Content Creator - YouTube |
| ✅ ok | `precision:remotive-writer` | 16 | 200 | 12 | Content Reviewer - United States; Tech Lead Full-Stack Rails Engineer; Content Creator - YouTube |

## aggregator-keyed  <sub>ok 0 · empty 0 · blocked 0 · not_found 1 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| 🔑 needs_key | `jsearch:arabic-translator` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `adzuna:gb` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `adzuna:us` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `jooble:arabic-translator` | 0 |  |  | missing secret(s): JOOBLE_API_KEY |
| 🔑 needs_key | `careerjet:arabic-translator` | 0 |  |  | missing secret(s): CAREERJET_AFFID |
| 🔑 needs_key | `reliefweb:arabic` | 0 |  |  | missing secret(s): RELIEFWEB_APPNAME |
| 🔑 needs_key | `reed:arabic-translator` | 0 |  |  | missing secret(s): REED_API_KEY_B64 |
| ❓ not_found | `themuse:writing-editing` | 0 | 404 | 143 | HTTP 404 |

## linkedin  <sub>ok 0 · empty 0 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⛔ blocked | `linkedin:guest-arabic-translator` | 0 | 429 | 69 | HTTP 429 |
| ⛔ blocked | `linkedin:guest-arabic-linguist` | 0 | 429 | 99 | HTTP 429 |
| ⛔ blocked | `linkedin:guest-proofreader` | 0 | 429 | 49 | HTTP 429 |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 126 | shree ji handicraf; Food Review Reels Editor; 2d ai music video |
| ✅ ok | `workana:writing-translation` | 2 | 200 | 195 | Freelance Jobs; Writing &amp; Translation |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 123 | 2371 bytes, text/html |
| ⛔ blocked | `freelancer:api-arabic` | 0 | 200 | 118 | HTTP 200 + challenge page |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 192 | HTTP 403 |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 120 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 827 | 200 | 169 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `html:dataannotation` | 133 | 200 | 141 | Software EngineerCodingUp to $150+ / hr312 hi; GeneralistGeneralUp to $50 / hr452 hired rece; Data ScientistData &amp; MLUp to $150+ / hr92 |
| ✅ ok | `ashby:mercor` | 108 | 200 | 59 | Strategic Project Lead; Strategic Projects Lead, Deeptune; Administrative Generalist |
| ✅ ok | `greenhouse:turing` | 31 | 200 | 49 | AI Engagement Lead; Client Director, Financial Services (BFSI); Client Engagement Lead - Pharma & Life Scienc |
| ✅ ok | `greenhouse:labelbox` | 13 | 200 | 38 | Director of Marketing; Forward Deployed Engineer, Enterprise Account; Forward Deployed Engineering Manager |
| ⚪ empty | `ashby:deel` | 0 | 200 | 15 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 63 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 57 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 77 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 384 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 370 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 281 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 36 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 0 · not_found 15 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 28 | 200 | 383 | Rendering Engineer; シニア3D背景アーティスト; 3D 背景アーティスト |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 391 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 253 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 540 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 380 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 176 | 5576 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 391 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 357 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2746 | 133427 bytes, text/html |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 554 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 280 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 72 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 41 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 37 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 124 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |
| 💥 error | `html:futuregroup-careers` | 0 |  | 398 | ServerDisconnectedError: Server disconnected |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 0 · not_found 17 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 506 | 166616 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 229 | 220847 bytes, text/html |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 178 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 423 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 200 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 379 | HTTP 404 |
| ❓ not_found | `personio:lingoda` | 0 | 404 | 288 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 154 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 74 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 220 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 8 | 200 | 55 | AI Artist; AI Artist; AI Artist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 12516 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 198 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 314 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 41 | HTTP 404 |

## remote-boards  <sub>ok 5 · empty 1 · blocked 1 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `json:remote1stjobs` | 34274 | 200 | 3231 | Medical Editor - Market Access Marketing; Account Executive, Healthcare and Pharmaceuti; Digital Onboarding Specialist I - Lisbon / Ma |
| ✅ ok | `html:remowork-arabic` | 208 | 200 | 755 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `rss:remotejobleads` | 16 | 200 | 478 | Legal Expert (Employment &#038; Labor); Paralegal (General); STEM / Quant Bachelor |
| ✅ ok | `html:jobgether` | 8 | 200 | 253 | Job search playbook; Job search playbook; Job search playbook |
| ✅ ok | `html:dailyremote` | 2 | 200 | 106 | Job Application Tracker; Search Jobs by Job Title |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 175 | 79774 bytes, text/html |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 454 | HTTP 403 |
| 💥 error | `rss:euremotejobs` | 0 | 520 | 477 | HTTP 520 |
| 💥 error | `html:remote-co` | 0 |  | 15904 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 2 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1923 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:translatorscafe` | 0 | 200 | 390 | 0 bytes, text/html |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 199 | 391820 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 46 | HTTP 403 + challenge page |

## un-ngo  <sub>ok 4 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 186 | 200 | 1212 | Openings; Search; WVI - World Vision International |
| ✅ ok | `html:impactpool-arabic` | 14 | 200 | 906 | Arabic Language Interpreter


IRC - Internati; Interpreter (Arabic-French)


IOM - Internati; Closing today:
Global Roving and Emergency Re |
| ✅ ok | `html:unjobs-translation` | 4 | 200 | 979 | Roster - Conference Interpreter, Geneva, Swit; Linguist Talent Pool, London, United Kingdom; Register as a Conference and Language Service |
| ✅ ok | `html:idealist-arabic` | 4 | 200 | 286 | Find a Job; Jobs; Find a Job |

## mena-boards  <sub>ok 1 · empty 1 · blocked 4 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1491 | Jobs in Jordan (36); Jobs in Saudi Arabia (6); Jobs in Qatar (3) |
| ⚪ empty | `html:mostaql-writing-translation` | 0 | 202 | 338 | 2387 bytes, text/html |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 86 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 37 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 91 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 222 | HTTP 403 |
| ❓ not_found | `html:ureed-translation` | 0 | 404 | 2177 | HTTP 404 |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15271 | timeout >15s |

## academic-editing-watchers  <sub>ok 2 · empty 0 · blocked 0 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 1474 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ✅ ok | `watch:scribbr` | 7 | 200 | 86 | Jobs; Jobs; Jobs |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 292 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 6 · blocked 0 · not_found 12 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 346 | 46385 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 246 | 46385 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 221 | 46385 bytes, text/html |
| ⚪ empty | `jobvite:telus` | 0 | 200 | 581 | 56415 bytes, text/html |
| ⚪ empty | `jobvite:concentrix` | 0 | 200 | 275 | 56415 bytes, text/html |
| ⚪ empty | `jobvite:teleperformance` | 0 | 200 | 272 | 56415 bytes, text/html |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 323 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 479 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 427 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 403 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 429 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 374 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 510 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 497 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 440 | HTTP 404 |
| ❓ not_found | `personio:appen` | 0 | 404 | 612 | HTTP 404 |
| ❓ not_found | `personio:centific` | 0 | 404 | 591 | HTTP 404 |
| ❓ not_found | `personio:surgeai` | 0 | 404 | 580 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 827 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 13 jobs
    ("Turing", "turing"),   # 31 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 108 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 8 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 28 jobs
    ("TransPerfect", "TransPerfect"),   # 18 jobs
```

```json
// source_registry.json additions
{"url": "https://weworkremotely.com/categories/all-other-remote-jobs.rss", "source_name": "wwr-all-other", "type": "rss"},
{"url": "https://www.workingnomads.com/api/exposed_jobs/", "source_name": "workingnomads-api", "type": "json"},
{"url": "https://www.remotejobleads.com/feed/", "source_name": "remotejobleads", "type": "rss"},
{"url": "https://www.remote1stjobs.com/jobs.json", "source_name": "remote1stjobs", "type": "json"},
```

## Secrets to add for the keyed aggregators

Settings → Secrets and variables → Actions → New repository secret: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `CAREERJET_AFFID`, `JOOBLE_API_KEY`, `RAPIDAPI_KEY`, `REED_API_KEY_B64`, `RELIEFWEB_APPNAME`
