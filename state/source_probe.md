# Source probe — 2026-09-10 23:45 UTC

_Ran from: github-actions · 157 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 44 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 25 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 58 | 404/410 → slug or endpoint is wrong |
| needs_key | 8 | add the secret and re-run |
| error | 3 | DNS/TLS/timeout |

## Answer: **37 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 295 | Data Engineer:in / IT Support (m/w/d); Performance Marketing Working Student – Talen; Mitarbeiter /Leiter (w\|m\|d) interne Qualitäts |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 445 | Business Development Manager; Quality Dispense Technician North; Social Comms |
| ✅ ok | `baseline:wwr` | 90 | 200 | 504 | Toptal: Power Platform Solutions Architect; TestGorilla: Sr. People &amp; Talent Operatio; Coaching.com: Membership Coordinator |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 61 | IT Associate; Enterprise Sales VP, Labor and Trust; Product Manager, Orchestrator |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 154 | Senior Graphic Designer - AM; Senior AI Product Manager, EMEA; Lead Analyst, Credit Risk Strategy |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 111 | Thorough Code Review of Decentralized, Encryp; Bangun Toko Shopify Minimalis Modern; WordPress &amp; GHL Virtual Assistant |
| ✅ ok | `baseline:remotive` | 18 | 200 | 99 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |

## precision-queries  <sub>ok 8 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 385 | Social Comms; AI Response Analyst; Senior Level Designer |
| ✅ ok | `precision:jobicy-teaching` | 50 | 200 | 52 | AI Engineer - FDE (Forward Deployed Engineer); Work from home as a Private Online German Tut; Senior Customer Marketing Manager |
| ✅ ok | `precision:wwr-all-other` | 50 | 200 | 173 | TestGorilla: Sr. People &amp; Talent Operatio; Toptal: Senior Security Compliance Consultant; Salesloft: Enterprise Account Director |
| ✅ ok | `precision:jobicy-translation` | 44 | 200 | 13 | Translation Project Manager; Alliance Manager, Translational Medicine; Senior Brand Designer, Experiential |
| ✅ ok | `precision:workingnomads-api` | 43 | 200 | 440 | Client Success Manager; Video Creator (100% remote); Senior Java & React Developer |
| ✅ ok | `precision:remotive-translator` | 18 | 200 | 16 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |
| ✅ ok | `precision:remotive-teacher` | 18 | 200 | 16 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |
| ✅ ok | `precision:remotive-writer` | 18 | 200 | 17 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 8 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 303 | Analyst,Underwriter; Analyst,Underwriter; P&C Middle Market Energy Renewal Underwriter |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 342 | Language Services Coordinator; Kurdish/Arabic Travel Only Linguist (2026-020; Chinese Translator |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 256 | Arabic Linguist CAT II - CENTCOM; Kurdish/Arabic Travel Only Linguist (2026-020; AI Tutor - Spanish |
| ✅ ok | `linkedin:guest-esl` | 10 | 200 | 277 | Virtual ELL Teacher; High School English Teacher; Virtual Middle School ELA Teacher |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 313 | Editorial Proofreader \| US Shift (7:00 PM Onw; Editor: Bioinformatics (Work-from-home); Marketing Copy Editor &amp; Proofreader |

## freelance  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 152 | Polish Speakers Needed for 813 Short Sentence;  Egypt Arabic Speakers Needed for 438 Short S; Convert MRMS GRIB2 to GEMPAK |
| ✅ ok | `freelancer:api-esl` | 20 | 200 | 145 | AI Training: Image Reviewing & Annotation -- ; AI Training Subject Matter Expert — Accountin; SEO Content Writer for Diverse Topics |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 159 | Urgent Shopify Editing for Mobile; Quick Chrome Addon Enhancement; Female Content Creator & Video Editor Needed |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 76 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 112 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 106 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 125 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 170 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 101 | 200 | 86 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 158 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 22 | 200 | 39 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 44 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Deployment Lead |
| ⚪ empty | `ashby:deel` | 0 | 200 | 87 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 76 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 51 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 58 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 451 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 461 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 114 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 28 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 349 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 28 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 23 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 53 | 200 | 379 | Technical Artist ; Game Designer – Japan & Global Game Developme; Game Programmer – Japan & Global Game Develop |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 357 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 526 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 371 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 347 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 539 | 243745 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 336 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 328 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2595 | 132990 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 386 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 329 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 316 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 12 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 324 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 165 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 21 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 31 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 502 | 186381 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 96 | 213026 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 782 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 27 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 355 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 203 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 418 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 110 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 544 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 19 | 200 | 49 | Business Development/ Sales Executive - EMEA ; Community & Support Intern - UAE Nationals; Community and Support Specialist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 208 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 204 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 111 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 202 | 200 | 479 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 3031 | Security Engineer ; Risk Partnerships Manager, Banks & Treasury; Product Manager, Sail Core |
| ✅ ok | `html:jobgether` | 6 | 200 | 335 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 2672 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 554 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 35 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 36 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 455 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15969 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1904 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 211 | 428358 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 113 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 344 | HTTP 403 |

## esl-boards  <sub>ok 2 · empty 0 · blocked 0 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:eslbase` | 43 | 200 | 964 | Get job alerts; Get job alerts; English Teaching Jobs in Vietnam with VUS |
| ✅ ok | `html:eslcafe-international` | 12 | 200 | 190 | Job Center; International Job Board; Korean Job Board |
| ❓ not_found | `html:tefl-online` | 0 | 404 | 156 | HTTP 404 |
| ❓ not_found | `html:teachaway-online` | 0 | 404 | 286 | HTTP 404 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 190 | 200 | 1240 | Openings; Search; WFP - World Food Programme |
| ✅ ok | `html:impactpool-arabic` | 10 | 200 | 876 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic)


IOM - International Or; Consultants template


WHO - World Health Org |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 356 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 31 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1607 | Jobs in Jordan (51); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 95 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 59 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 112 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 162 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 229 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 67 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15238 | timeout >15s |

## academic-editing-watchers  <sub>ok 1 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 2825 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 29 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 388 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 237 | 45802 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 342 | 45802 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 138 | 45802 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 233 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 64 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 63 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 472 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 738 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 545 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 2373 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 112 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 111 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 365 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 385 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 367 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 404 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 357 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 534 | HTTP 404 |

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
