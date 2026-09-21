# Source probe — 2026-09-21 09:13 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 39 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 24 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 56 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 4 | DNS/TLS/timeout |

## Answer: **32 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 191 | Director of Product Management - Data Streami; Senior Software Engineer; Associate Medical Editor  - US Students (MD/D |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 485 | Senior .NET Software Engineer; Frontend Engineer; Backend Software Engineer |
| ✅ ok | `baseline:wwr` | 83 | 200 | 470 | EBANX: [Talent Pool] Business Development Spe; BetterHelp: Licensed Clinical Marriage and Fa; BetterHelp: Licensed  Certified Social Worker |
| ✅ ok | `baseline:remotive` | 20 | 200 | 87 | Frontend Web Application Developer; Senior Shopify Developer; 🇩🇪 Kundenservice Mobilfunk Inbound - innerhal |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 700 | Senior Web Security Engineer, Browser Platfor; Norwegian Tech Linguistic Tester; Graduate Customer Success Manager |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 99 | AI Performance Engineer; Gestionnaire des Achats; Environmental Specialist (#, PA, US, _) |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 55 | Realistic Ecommerce Hero Image -- 2; Beginner Drone Training Workshop; Looking for video editing project |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 411 | Senior .NET Software Engineer; HR Operations Specialist; Marketing Student Assistant |
| ✅ ok | `precision:wwr-all-other` | 55 | 200 | 237 | BetterHelp: Licensed Clinical Marriage and Fa; BetterHelp: Licensed  Certified Social Worker; Sezzle: Accountant |
| ✅ ok | `precision:workingnomads-api` | 54 | 200 | 495 | Head of Engineering; Phone Sales Agent - Restock; Phone Sales Recovery Agent |
| ✅ ok | `precision:jobicy-translation` | 36 | 200 | 879 | Translation Project Manager; Alliance Manager, Translational Medicine; Norwegian Tech Linguistic Tester |
| ✅ ok | `precision:remotive-translator` | 20 | 200 | 17 | Frontend Web Application Developer; Senior Shopify Developer; 🇩🇪 Kundenservice Mobilfunk Inbound - innerhal |
| ✅ ok | `precision:remotive-teacher` | 20 | 200 | 18 | Frontend Web Application Developer; Senior Shopify Developer; 🇩🇪 Kundenservice Mobilfunk Inbound - innerhal |
| ✅ ok | `precision:remotive-writer` | 20 | 200 | 23 | Frontend Web Application Developer; Senior Shopify Developer; 🇩🇪 Kundenservice Mobilfunk Inbound - innerhal |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 297 | Prompt-Response Writer; Underwriter - Ports & Terminals; Data Enterprise Reporter |
| 🔑 needs_key | `jsearch:arabic-translator` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `adzuna:gb` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `adzuna:us` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `jooble:arabic-translator` | 0 |  |  | missing secret(s): JOOBLE_API_KEY |
| 🔑 needs_key | `careerjet:arabic-translator` | 0 |  |  | missing secret(s): CAREERJET_AFFID |
| 🔑 needs_key | `reliefweb:arabic` | 0 |  |  | missing secret(s): RELIEFWEB_APPNAME |
| 🔑 needs_key | `reed:arabic-translator` | 0 |  |  | missing secret(s): REED_API_KEY_B64 |

## linkedin  <sub>ok 3 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 524 | Freelance Native Linguists – TEP &amp; MTPE P; Translator; Acil İlan: Arapça–Türkçe Tercüman |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 402 | Italian Expert \| $36/hr \| Remote; AI Tutor - Bulgarian; Multilingual Roles in Bulgaria (Up to €2,200/ |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 415 | Copy Editor; Copy Editor; English Editor Novi Sad |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 261 | Spanish to English translation(long term).; TikTok Comedy Video Script Translation; Create Wikipedia Page |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 177 | Psychology Blog Article Series; Looking for video editing project; Virtual Assistant for Resume Writing & Admin  |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 220 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 183 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 60 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 105 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 145 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 109 | 200 | 63 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 127 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 21 | 200 | 101 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 80 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Forward Deployed Engineering Manager |
| ⚪ empty | `ashby:deel` | 0 | 200 | 24 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 179 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 169 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 78 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 414 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 386 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 41 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 76 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 113 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 51 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 94 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 47 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 295 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 91 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 35 | 200 | 405 | シニア3D背景アーティスト; 3D 背景アーティスト; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 360 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 571 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 528 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 370 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 255 | 243546 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 347 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 357 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 7063 | 133286 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 1128 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 263 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 253 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 67 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 42 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 199 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 812 | 176967 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 263 | 213024 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 789 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 66 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 38 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 440 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 229 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 521 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 67 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 185 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 53 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 73 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 457 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 22 | 200 | 83 | Business Development/ Sales Executive - EMEA ; Community & Partnerships Manager; Community & Partnerships Manager |
| ❓ not_found | `lever:anghami` | 0 | 404 | 74 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 173 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 323 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 43 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 192 | 200 | 562 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 1727 | Backend Engineer, Control Plane; Senior Software Engineer, Data & Platform Ser; Senior Software Engineer - AI |
| ✅ ok | `html:jobgether` | 8 | 200 | 247 | Job search playbook; Job search playbook; Job search playbook |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 213 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 729 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 122 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 133 | HTTP 403 + challenge page |
| 💥 error | `html:remote-co` | 0 |  | 15818 | timeout >15s |
| 💥 error | `html:europeremotely` | 0 |  | 401 | ClientConnectorError: Cannot connect to host europeremotely.com:443 ssl:False [Connection reset by peer] |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2897 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 295 | 436120 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 34 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 325 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 182 | 200 | 1561 | Openings; Search; UNHCR - UN High Commissioner for Refugees |
| ✅ ok | `html:impactpool-arabic` | 15 | 200 | 1232 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic and French)


IOM - Inter; Communications Specialist -Communications and |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 383 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 221 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 3 | 200 | 1956 | Jobs in Jordan (54); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 128 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 59 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 221 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 294 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 315 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 74 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15397 | timeout >15s |

## academic-editing-watchers  <sub>ok 1 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 2298 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 36 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 387 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 292 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 117 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 182 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 459 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 189 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 161 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 636 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 579 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 640 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 840 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 373 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 343 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 723 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 631 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 438 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 488 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 394 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 366 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 831 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 21 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 109 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 22 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 35 jobs
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
