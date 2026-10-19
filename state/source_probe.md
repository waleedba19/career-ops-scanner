# Source probe — 2026-10-19 09:13 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 37 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 20 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 60 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 6 | DNS/TLS/timeout |

## Answer: **30 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 300 | 200 | 200 | Expansion Customer Success Manager (m/w/d); Senior Generative AI Engineer (m/w/d); Junior Customer Success Manager (m/w/d) |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 897 | Graduate Transport Planner; Key Account Manager Danish Market Native Spea; Technical Account Manager |
| ✅ ok | `baseline:wwr` | 89 | 200 | 864 | Expel: Technical Account Manager; Expel: Systems Engineer; Current: Senior Product Designer (Webflow) Te |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 284 | Conceptual Copywriter; Conceptual Art Director; Account Director |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 89 | Game Director; Creative Strategist UGC & Performance Ads (m/; MLOps Senior [Risk Team] |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 158 | Educational Lecture PowerPoint Design; Homepage CTA Button Integration; Korean Employment History Verification |
| ✅ ok | `baseline:remotive` | 12 | 200 | 119 | Software Engineer, AI Coding Tasks; Tech Lead Full-Stack Rails Engineer; Remote Office Assistant |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 558 | Senior Software Engineer II Applied AI; Principal Software Engineer; Senior Sales Executive Central Region |
| ✅ ok | `precision:wwr-all-other` | 70 | 200 | 707 | Talkspace: Care Coordinator; Upstart: Compliance Manager, BSA/AML Program; Upstart: Capital Markets Manager |
| ✅ ok | `precision:workingnomads-api` | 42 | 200 | 877 | Video Creator (100% remote); Senior AI Engineer / Architect; Language specialist |
| ✅ ok | `precision:remotive-translator` | 12 | 200 | 31 | Software Engineer, AI Coding Tasks; Tech Lead Full-Stack Rails Engineer; Remote Office Assistant |
| ✅ ok | `precision:remotive-teacher` | 12 | 200 | 32 | Software Engineer, AI Coding Tasks; Tech Lead Full-Stack Rails Engineer; Remote Office Assistant |
| ✅ ok | `precision:remotive-writer` | 12 | 200 | 34 | Software Engineer, AI Coding Tasks; Tech Lead Full-Stack Rails Engineer; Remote Office Assistant |
| ✅ ok | `precision:jobicy-translation` | 10 | 200 | 208 | Product Owner, Growth; Product Owner, Payments and Infrastructure; Strategic Sourcing Lead – Fulfillment - Mexic |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 391 | Captives Underwriter; Prompt-Response Writer US; Copywriter (Contract) |
| 🔑 needs_key | `jsearch:arabic-translator` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `adzuna:gb` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `adzuna:us` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `jooble:arabic-translator` | 0 |  |  | missing secret(s): JOOBLE_API_KEY |
| 🔑 needs_key | `careerjet:arabic-translator` | 0 |  |  | missing secret(s): CAREERJET_AFFID |
| 🔑 needs_key | `reliefweb:arabic` | 0 |  |  | missing secret(s): RELIEFWEB_APPNAME |
| 🔑 needs_key | `reed:arabic-translator` | 0 |  |  | missing secret(s): REED_API_KEY_B64 |

## linkedin  <sub>ok 2 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 317 | Arabic Translator - Egyptian Dialect (Onsite); Machine Translation Post-Editor for Regional ; 葡萄牙语翻译 |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 322 | Editor; Editorial Associate; Proofreader |
| ⛔ blocked | `linkedin:guest-arabic-linguist` | 0 | 429 | 257 | HTTP 429 |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 192 | YouTube Entertainment Video Editing ARABIC ED; Merge Excel Spreadsheets; AI Receptionist Kiosk Full-Stack Developer |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 238 | Bulk Vintage Photo Editing; Middle Grade Book Developmental Editor; Gender reveal video editing 90 seconds |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 75 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 81 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 87 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 128 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 833 | 200 | 171 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 112 | 200 | 97 | Software Engineer, Systems & Platform Applied; Infrastructure Software Engineer ; Strategic Project Lead |
| ✅ ok | `html:dataannotation` | 112 | 200 | 294 | Software EngineerCodingUp to $150+ / hr312 hi; GeneralistGeneralUp to $50 / hr452 hired rece; Data ScientistData &amp; MLUp to $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 29 | 200 | 78 | AI Engagement Lead; Chief of Staff (CEO's Office); Compliance Analyst |
| ✅ ok | `greenhouse:labelbox` | 7 | 200 | 66 | Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments; Forward Deployed Research Scientist |
| ⚪ empty | `ashby:deel` | 0 | 200 | 255 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 214 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 190 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 155 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 486 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 535 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 58 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 153 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 74 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 79 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 117 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 74 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 181 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 61 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 64 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 0 · not_found 15 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 34 | 200 | 555 | シニア3D背景アーティスト; Technical Designer – Japan & Global Game Deve; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 444 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 315 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 893 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 473 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 589 | 4718 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 422 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 447 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2948 | 133429 bytes, text/html |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 2030 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 184 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 59 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 62 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 100 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 99 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 110 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 95 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 62 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 60 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 447 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |
| 💥 error | `html:futuregroup-careers` | 0 |  | 172 | ServerDisconnectedError: Server disconnected |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 0 · not_found 17 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 1203 | 177424 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 240 | 215154 bytes, text/html |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 168 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 41 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 496 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 59 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 192 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 527 | HTTP 404 |
| ❓ not_found | `personio:lingoda` | 0 | 404 | 882 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 60 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 214 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 98 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 59 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 94 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 103 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 844 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 9 | 200 | 132 | Business Development/ Sales Executive - EMEA ; Community & Support Intern - UAE Nationals; Internship Night - For Emirati Nationals |
| ❓ not_found | `lever:anghami` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 175 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 467 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 100 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 197 | 200 | 867 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `rss:remotejobleads` | 16 | 200 | 582 | Part-Time Contract Video Producer (Line Produ; Part-Time Contract Video Producer (Line Produ; Business Analyst &#8211; AI Evaluator / AI Tr |
| ✅ ok | `html:jobgether` | 8 | 200 | 357 | Job search playbook; Job search playbook; Job search playbook |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 216 | 79755 bytes, text/html |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 95 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 649 | HTTP 403 |
| ⛔ blocked | `json:remote1stjobs` | 0 | 503 | 328 | HTTP 503 |
| 💥 error | `rss:euremotejobs` | 0 | 520 | 253 | HTTP 520 |
| 💥 error | `html:remote-co` | 0 |  | 15479 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2266 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 333 | 387979 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 87 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 554 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 182 | 200 | 1981 | Openings; Search; WHO - World Health Organization |
| ✅ ok | `html:impactpool-arabic` | 14 | 200 | 1151 | Arabic interpreter


IRC - International Resc; Lead Strategic Coordinator


IsDB - Islamic D; HR Administration Officer


ICRC - Internatio |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 418 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 82 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1374 | Jobs in Jordan (50); Jobs in Qatar (3); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 88 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 97 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 132 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 311 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 441 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 81 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15175 | timeout >15s |

## academic-editing-watchers  <sub>ok 0 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 93 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 327 | HTTP 404 |
| 💥 error | `watch:cactus` | 0 |  | 100 | ClientConnectorDNSError: Cannot connect to host www.cactusglobal.com:443 ssl:False [Name or service not known] |

## ats-new  <sub>ok 0 · empty 3 · blocked 3 · not_found 12 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 485 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 485 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 419 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 511 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 457 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 432 | HTTP 403 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 650 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 451 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 474 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 468 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 471 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 470 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 391 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 286 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 240 | HTTP 404 |
| ❓ not_found | `personio:appen` | 0 | 404 | 801 | HTTP 404 |
| ❓ not_found | `personio:centific` | 0 | 404 | 788 | HTTP 404 |
| ❓ not_found | `personio:surgeai` | 0 | 404 | 768 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 833 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 7 jobs
    ("Turing", "turing"),   # 29 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 112 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 9 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 34 jobs
    ("TransPerfect", "TransPerfect"),   # 18 jobs
```

```json
// source_registry.json additions
{"url": "https://weworkremotely.com/categories/all-other-remote-jobs.rss", "source_name": "wwr-all-other", "type": "rss"},
{"url": "https://www.workingnomads.com/api/exposed_jobs/", "source_name": "workingnomads-api", "type": "json"},
{"url": "https://www.themuse.com/api/public/jobs?page=1&category=Writing%20and%20Editing&level=Mid%20Level", "source_name": "writing-editing", "type": "json"},
{"url": "https://www.remotejobleads.com/feed/", "source_name": "remotejobleads", "type": "rss"},
```

## Secrets to add for the keyed aggregators

Settings → Secrets and variables → Actions → New repository secret: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `CAREERJET_AFFID`, `JOOBLE_API_KEY`, `RAPIDAPI_KEY`, `REED_API_KEY_B64`, `RELIEFWEB_APPNAME`
