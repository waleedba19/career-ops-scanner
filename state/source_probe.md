# Source probe — 2026-10-05 10:46 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 38 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 25 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 56 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 4 | DNS/TLS/timeout |

## Answer: **31 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 325 | 200 | 304 | Pflichtpraktikant Kommunikationsdesign & UX/U; Finance & Controlling Analyst (m/w/d); Praktikant Marketing Manager (m/w/d) |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 653 | Head of Operations; Junior Crypto Analyst & Trader; Enterprise Sales Development Representative |
| ✅ ok | `baseline:wwr` | 89 | 200 | 424 | Town Web: Senior Support Engineer; Wrike: Director, Global GTM Strategy &amp; Op; Wrike: Business Systems Security Analyst |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 115 | Finance Expression of Interest Form; RN Clinical Navigator - Part time/Weekends; Senior Physical Environment Surveyor - Health |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 155 | Fine-Tune a BERT Model for Text Classificatio; Virtual Assistant- Office admin and research ; Interface Functionality Bug Testing |
| ✅ ok | `baseline:remotive` | 18 | 200 | 162 | Freelance Copywriter; Senior React Full-stack Developer; Senior back-end Engineer |
| ✅ ok | `baseline:jobicy` | 16 | 200 | 734 | External Contractor - Mentor role for Data Pr; Senior Full Stack Engineer; Solutions Architect for Automotive |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 502 | Senior .NET Software Engineer; HR Operations Specialist; Marketing Student Assistant |
| ✅ ok | `precision:wwr-all-other` | 70 | 200 | 228 | Wrike: Business Systems Security Analyst; Gong.io: Professional Services Consultant; Datadog: Director, Enterprise Sales Engineeri |
| ✅ ok | `precision:workingnomads-api` | 56 | 200 | 1083 | AI Content Analyst (No Experience Required); Data Analyst (No Experience Required); Live Photo Collection Study in India |
| ✅ ok | `precision:remotive-translator` | 18 | 200 | 20 | Freelance Copywriter; Senior React Full-stack Developer; Senior back-end Engineer |
| ✅ ok | `precision:remotive-teacher` | 18 | 200 | 19 | Freelance Copywriter; Senior React Full-stack Developer; Senior back-end Engineer |
| ✅ ok | `precision:remotive-writer` | 18 | 200 | 19 | Freelance Copywriter; Senior React Full-stack Developer; Senior back-end Engineer |
| ✅ ok | `precision:jobicy-translation` | 14 | 200 | 779 | Localization Operations Specialist; Enterprise Account Executive, US; Customer Success Associate (Sustainability) |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 306 | Underwriter - Ports & Terminals; Data Enterprise Reporter; Blending Control Technician |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 433 | Arapça Tercüman; Multilingual Translator \| Administrative &amp; Translator |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 474 | Arapça Tercüman; Afrikaans Linguist CAT III; Jr. Language-Enabled OSINT Collector (CONUS) |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 501 | Senior Copy Editor; Sr Medical Editor; Junior Data Content Editor |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 206 | Drupal 7-11 Site Upgrade & Migration & Templa; Islamic studies on Marriage Divorce and Intim; German to English Translator required for tra |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 208 | Customer Testimonial Promo Video Editing; Instagram Reels Video Editing; Fast-Paced Gaming Reel Editing |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 187 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 105 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 116 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 214 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 833 | 200 | 284 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 114 | 200 | 126 | Software Engineer, Systems & Platform Applied; Infrastructure Software Engineer ; Strategic Project Lead |
| ✅ ok | `html:dataannotation` | 107 | 200 | 138 | Software EngineerCoding$40 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$40 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 30 | 200 | 65 | AI Engagement Lead; Chief of Staff (CEO's Office); Community Manager |
| ✅ ok | `greenhouse:labelbox` | 9 | 200 | 78 | Cyber Security Intern; Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments |
| ⚪ empty | `ashby:deel` | 0 | 200 | 127 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 98 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 87 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 102 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 496 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 481 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 74 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 142 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 47 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 73 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 66 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 608 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 48 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 35 | 200 | 378 | Technical Designer – Japan & Global Game Deve; Game Programmer – Japan & Global Game Develop; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 383 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 707 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 759 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 413 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 289 | 243432 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 381 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 377 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2938 | 133429 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 368 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 226 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 221 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 75 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 63 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 67 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 61 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 48 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 328 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 1660 | 177425 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 205 | 214595 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 777 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 458 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 285 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 411 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 48 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 67 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 280 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 67 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 51 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 511 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 22 | 200 | 78 | Business Development/ Sales Executive - EMEA ; Community & Partnerships Manager; Community & Partnerships Manager |
| ❓ not_found | `lever:anghami` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 336 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 336 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 76 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `json:remote1stjobs` | 1609 | 200 | 748 | Account Manager - DACH; Regional Sales Director, East; Supply Category Lead, Services   |
| ✅ ok | `html:remowork-arabic` | 193 | 200 | 847 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `html:jobgether` | 8 | 200 | 270 | Job search playbook; Job search playbook; Job search playbook |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 263 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 282 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 110 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 174 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 562 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15392 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2127 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 265 | 399107 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 103 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 377 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 172 | 200 | 1156 | Openings; Search; WHO - World Health Organization |
| ✅ ok | `html:impactpool-arabic` | 14 | 200 | 1178 | Part Time Arabic Language Teacher


UNOG - Un; Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic-Turkish)


UNV - United N |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 442 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 87 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 3 | 200 | 1449 | Jobs in Jordan (62); Jobs in Saudi Arabia (2); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 88 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 166 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 298 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 340 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 431 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 193 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15110 | timeout >15s |

## academic-editing-watchers  <sub>ok 0 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 126 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 407 | HTTP 404 |
| 💥 error | `watch:cactus` | 0 |  | 126 | ClientConnectorDNSError: Cannot connect to host www.cactusglobal.com:443 ssl:False [Name or service not known] |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 265 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 209 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 206 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 551 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 500 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 391 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 766 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 656 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 711 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 498 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 386 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 484 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 460 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 485 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 478 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 412 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 283 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 326 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 833 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 9 jobs
    ("Turing", "turing"),   # 30 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 114 jobs
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
