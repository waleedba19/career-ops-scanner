# Source probe — 2026-09-28 10:05 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 38 | responded with parseable jobs → **can be added** |
| empty | 20 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 24 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 56 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 4 | DNS/TLS/timeout |

## Answer: **31 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 326 | 200 | 220 | Software Engineer; Partner Solutions Architect - MSP; Influencer Marketing Manager (m/w/d) \| Deutsc |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 627 | Director Payment Integrity; Danish Speaking Solutions Consultant Work Sof; MecÃ¡nico Automotriz DiagnÃ³stico y Presupues |
| ✅ ok | `baseline:wwr` | 80 | 200 | 329 | IxDF - Interaction Design Foundation: Course ; IxDF - Interaction Design Foundation: Educati; Collibra: CPS Solution Architect |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 840 | Cloud Support Engineer; Senior Software Engineer, Backend (Money Move; Engineering Manager - MLOps & Analytics |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 135 | Mobile Application Developer - AI Neobank App; Product Lead - AI Neobank App; Product Manager - AI Neobank App |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 92 | Private Project for Khairul Islam; Excel Data Entry &amp; Basic Formulas -- 2; MVP Development with Lovable UI/Any UI Platfo |
| ✅ ok | `baseline:remotive` | 17 | 200 | 246 | Content Reviewer - United States; Frontend Web Application Developer; Senior Shopify Developer |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 551 | Senior .NET Software Engineer; HR Operations Specialist; Marketing Student Assistant |
| ✅ ok | `precision:wwr-all-other` | 60 | 200 | 215 | Roblox: Developer Engagement Representative -; Roblox: Developer Engagement Representative -; Fivetran : Compensation &amp; Analytics Partn |
| ✅ ok | `precision:workingnomads-api` | 52 | 200 | 711 | Beekman Social - Account Manager; Stack .NET Developer / Algorithm Engineer – B; Senior back-end Engineer |
| ✅ ok | `precision:jobicy-translation` | 36 | 200 | 1000 | Alliance Manager, Translational Medicine; Translation Project Manager; Customer Success Manager |
| ✅ ok | `precision:remotive-translator` | 17 | 200 | 68 | Content Reviewer - United States; Frontend Web Application Developer; Senior Shopify Developer |
| ✅ ok | `precision:remotive-teacher` | 17 | 200 | 47 | Content Reviewer - United States; Frontend Web Application Developer; Senior Shopify Developer |
| ✅ ok | `precision:remotive-writer` | 17 | 200 | 46 | Content Reviewer - United States; Frontend Web Application Developer; Senior Shopify Developer |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 266 | Data Partner - Creative Writer -  Remote - As; Prompt-Response Writer; Underwriter - Ports & Terminals |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 457 | Tercüman; Mandarin Translator; Intèrprets, i mediador/es interculturals (àra |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 444 | Data Analysis - Linguist; Tenured/Tenure-track Position in the Departme; Linguist/Linguistic Researcher |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 479 | Proofreader, Editorial Team; Editor; editior |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 199 | Content Writer & Data/Research Assistant; Professional Finalisation & Multilingual Rest; Website & Logo Design |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 190 | Virtual Assistant for Text Generation and Pro; Audit Book Ghostwriting & Design; Rapid Handwritten Notes Typing |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 324 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 157 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 89 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 256 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 832 | 200 | 269 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 114 | 200 | 262 | Member of Technical Staff, Applied AI Backend; Infrastructure Software Engineer ; Strategic Project Lead |
| ✅ ok | `html:dataannotation` | 107 | 200 | 136 | Software EngineerCoding$40 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$40 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 34 | 200 | 66 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 69 | Cyber Security Intern; Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments |
| ⚪ empty | `ashby:deel` | 0 | 200 | 203 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 128 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 119 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 98 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 410 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 399 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 248 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 156 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 102 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 48 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 48 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 444 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 42 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 35 | 200 | 380 | シニア3D背景アーティスト; 3D 背景アーティスト; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 423 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 506 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 755 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 392 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 294 | 243431 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 435 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 399 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 5947 | 133287 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 202 | 527 | HTTP 202 + challenge page |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 358 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 280 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 61 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 213 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 88 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 51 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 58 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 58 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 95 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 48 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 223 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 1558 | 177422 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 113 | 214542 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 836 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 53 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 550 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 383 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 512 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 77 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 238 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 248 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 605 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 21 | 200 | 86 | Business Development/ Sales Executive - EMEA ; Community & Partnerships Manager; Community & Partnerships Manager |
| ❓ not_found | `lever:anghami` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 248 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 385 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 548 | HTTP 404 |

## remote-boards  <sub>ok 2 · empty 2 · blocked 3 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 198 | 200 | 865 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `html:jobgether` | 8 | 200 | 326 | Job search playbook; Job search playbook; Job search playbook |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 152 | 79755 bytes, text/html |
| ⚪ empty | `json:remote1stjobs` | 0 | 200 | 253 | 560 bytes, application/feed+json |
| ⛔ blocked | `rss:euremotejobs` | 0 | 202 | 667 | HTTP 202 + challenge page |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 90 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 92 | HTTP 403 + challenge page |
| 💥 error | `html:remote-co` | 0 |  | 15868 | timeout >15s |
| 💥 error | `html:europeremotely` | 0 |  | 369 | ClientConnectorError: Cannot connect to host europeremotely.com:443 ssl:False [Connection reset by peer] |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2063 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 286 | 392923 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 73 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 319 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 170 | 200 | 1353 | Openings; Search; WVI - World Vision International |
| ✅ ok | `html:impactpool-arabic` | 11 | 200 | 1191 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic and French)


IOM - Inter; Partnerships Specialist


UNOPS - United Nati |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 336 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 249 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 3 | 200 | 1757 | Jobs in Jordan (52); Jobs in UAE (1); Jobs in Saudi Arabia (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 104 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 115 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 312 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 305 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 423 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 133 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15494 | timeout >15s |

## academic-editing-watchers  <sub>ok 1 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 1366 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 75 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 418 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 361 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 220 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 274 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 584 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 493 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 419 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 608 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 677 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 717 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 495 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 380 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 498 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 513 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 395 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 563 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 291 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 351 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 330 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 832 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 34 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 114 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 21 jobs
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
```

## Secrets to add for the keyed aggregators

Settings → Secrets and variables → Actions → New repository secret: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `CAREERJET_AFFID`, `JOOBLE_API_KEY`, `RAPIDAPI_KEY`, `REED_API_KEY_B64`, `RELIEFWEB_APPNAME`
