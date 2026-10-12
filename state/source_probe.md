# Source probe — 2026-10-12 11:14 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 38 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 20 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 61 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 4 | DNS/TLS/timeout |

## Answer: **31 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 325 | 200 | 314 | Projektmanager / Customer Success Manager - W; Mitarbeiter Sekretariat & Administration (m/w; TGA - Ingenieur / Versorgungstechniker / Tech |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 637 | Marketing and Sales Administrator; Technical Account Manager; Manager Clinical Data Management |
| ✅ ok | `baseline:wwr` | 89 | 200 | 781 | Amwell: Sr Product Marketing Manager; Glean: Enterprise Account Executive, Ohio Val; Keeper Security: Associate Talent Acquisition |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 134 | Remote Full Cycle Recruiter/ Talent Acquisiti; Connectivity Developer - Employment Contract ; Sales Development Representative (SDR) |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 189 | SaaS Document Automation Platform Development; Albania Bachelor&rsquo;s Degree Verification; BlindForward SaaS Blueprint &amp; PoC |
| ✅ ok | `baseline:remotive` | 15 | 200 | 153 | Inside Sales Contractor; Tier III Service Desk Engineer; Software Engineer / AI Code Trainer (Python,  |
| ✅ ok | `baseline:jobicy` | 12 | 200 | 209 | IT Associate; Enterprise Sales VP, Labor and Trust; International Audio/Video Remote Kurdish and  |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 441 | Marketing and Sales Administrator; Academic Dean for MiaPrep Online Academy of O; Senior .NET Software Engineer |
| ✅ ok | `precision:wwr-all-other` | 74 | 200 | 300 | Amwell: Sr. Counsel, Government &amp; Commerc; Current: Senior Paid Media Strategist (Freela; Datadog: Key Accounts Executive - EMEA |
| ✅ ok | `precision:workingnomads-api` | 50 | 200 | 676 | Senior Backend Developer (Node.js / Nest.js); Senior Backend Developer (Python); Senior Business Central Developer |
| ✅ ok | `precision:remotive-translator` | 15 | 200 | 27 | Inside Sales Contractor; Tier III Service Desk Engineer; Software Engineer / AI Code Trainer (Python,  |
| ✅ ok | `precision:remotive-teacher` | 15 | 200 | 27 | Inside Sales Contractor; Tier III Service Desk Engineer; Software Engineer / AI Code Trainer (Python,  |
| ✅ ok | `precision:remotive-writer` | 15 | 200 | 28 | Inside Sales Contractor; Tier III Service Desk Engineer; Software Engineer / AI Code Trainer (Python,  |
| ✅ ok | `precision:jobicy-translation` | 12 | 200 | 139 | Senior Web Developer; Regional Sales Operations Manager - EMEA; Strategic Sourcer – Fulfillment - Brazil |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 330 | Underwriter - Ports & Terminals; Data Enterprise Reporter; Production Supervisor - 12 Hour Weekend Shift |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 461 | Arabic Editor and Language Specialist (Nation; Localization Specialist - Spanish EU; Project Associate (Cultural Mediator) |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 496 | Localization Specialist - Spanish EU; Arabic Editor and Language Specialist (Nation; Localization Specialist |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 505 | Remote Proofreader; 文案编辑; Localization Copy Editor |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 220 | Youth Career Mobile App Development; French-Spanish Legal Document Translation; Native English Editor for Spiritual Book — Ja |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 230 | CIBIL Report PDF Editor; YouTube Growth & Editing Expert; Instagram Travel Reel Creation |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 184 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 225 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 147 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 161 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 833 | 200 | 217 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `html:dataannotation` | 112 | 200 | 235 | Software EngineerCoding$40 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$40 – $150+ / hr92 |
| ✅ ok | `ashby:mercor` | 111 | 200 | 89 | Software Engineer, Systems & Platform Applied; Infrastructure Software Engineer ; Strategic Project Lead |
| ✅ ok | `greenhouse:turing` | 29 | 200 | 65 | AI Engagement Lead; Chief of Staff (CEO's Office); Community Manager |
| ✅ ok | `greenhouse:labelbox` | 8 | 200 | 55 | Cyber Security Intern; Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments |
| ⚪ empty | `ashby:deel` | 0 | 200 | 84 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 124 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 131 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 101 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 443 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 404 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 74 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 102 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 60 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 51 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 244 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 52 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 35 | 200 | 494 | シニア3D背景アーティスト; Technical Designer – Japan & Global Game Deve; Game Programmer – Japan & Global Game Develop |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 410 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 489 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 680 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 386 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 304 | 246172 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 395 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 372 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 5024 | 133430 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 426 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 223 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 214 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 60 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 48 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 48 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 90 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 64 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 104 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 54 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 320 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 0 · not_found 17 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 1372 | 177426 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 310 | 215348 bytes, text/html |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 73 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 48 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 516 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 267 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 408 | HTTP 404 |
| ❓ not_found | `personio:lingoda` | 0 | 404 | 626 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 49 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 272 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 66 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 90 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 716 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 22 | 200 | 118 | Business Development/ Sales Executive - EMEA ; Community & Partnerships Manager; Community & Partnerships Manager |
| ❓ not_found | `lever:anghami` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 245 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 355 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 52 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `json:remote1stjobs` | 1609 | 200 | 559 | Account Manager - DACH; Regional Sales Director, East; Supply Category Lead, Services   |
| ✅ ok | `html:remowork-arabic` | 193 | 200 | 588 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `html:jobgether` | 9 | 200 | 301 | Job search playbook; Job search playbook; Job search playbook |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 592 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 737 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 144 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 170 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 663 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15835 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1988 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 254 | 399108 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 175 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 322 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 192 | 200 | 1629 | Openings; Search; IOM - UN Migration |
| ✅ ok | `html:impactpool-arabic` | 13 | 200 | 978 | Part Time Arabic Language Teacher


UNOG - Un; Arabic editor individual contractor


UNEP - ; Interpreter (Arabic-French)


IOM - Internati |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 350 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 260 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 5 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 3 | 200 | 1420 | Jobs in Jordan (57); Jobs in UAE (1); Jobs in Saudi Arabia (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 202 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 204 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 300 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 250 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 370 | HTTP 403 |
| ❓ not_found | `html:ureed-translation` | 0 | 404 | 1754 | HTTP 404 |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15952 | timeout >15s |

## academic-editing-watchers  <sub>ok 0 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 126 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 471 | HTTP 404 |
| 💥 error | `watch:cactus` | 0 |  | 109 | ClientConnectorDNSError: Cannot connect to host www.cactusglobal.com:443 ssl:False [Name or service not known] |

## ats-new  <sub>ok 0 · empty 3 · blocked 3 · not_found 12 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 377 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 287 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 264 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 803 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 658 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 458 | HTTP 403 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 397 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 496 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 365 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 442 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 404 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 482 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 319 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 570 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 595 | HTTP 404 |
| ❓ not_found | `personio:appen` | 0 | 404 | 610 | HTTP 404 |
| ❓ not_found | `personio:centific` | 0 | 404 | 670 | HTTP 404 |
| ❓ not_found | `personio:surgeai` | 0 | 404 | 677 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 833 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 8 jobs
    ("Turing", "turing"),   # 29 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 111 jobs
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
