# Source probe — 2026-11-02 11:34 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 36 | responded with parseable jobs → **can be added** |
| empty | 21 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 19 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 60 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 6 | DNS/TLS/timeout |

## Answer: **29 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 300 | 200 | 192 | Senior Customer Success Manager (m/f/d); Netzwerkadministrator / IT-Systemadministrato; Senior Artist Manager / Influencer Manager (m |
| ✅ ok | `baseline:wwr` | 100 | 200 | 1774 | LOTARO: Head of Lead Generation \| Remote (m/w; Smartsheet: Senior Channel Account Manager; Upgrade: Dealer Development Manager (Portland |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 810 | Virtual Destination Wedding Coordinator; Virtual Scheduling Assistant; Partner Operations Manager |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 99 | Director, Application Development Engineering; CX Named Account Manager \| Thailand (Virtual,; Associate Director US Oncology Marketing Pati |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 43 | Food Brand Social Media Photography; Comprehensive Offline Product Price Compariso; Record POV Videos for AI Training |
| ✅ ok | `baseline:remotive` | 12 | 200 | 90 | Full-Stack Developer; Senior Back-end Developer; Head of Engineering |
| ✅ ok | `baseline:jobicy` | 3 | 200 | 424 | Director of Creative Strategy; Multigres Engineer; Cloud Support Engineer |

## precision-queries  <sub>ok 6 · empty 1 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 446 | Accounting & Finance Manager; Senior Software Engineer II Applied AI; Principal Software Engineer |
| ✅ ok | `precision:wwr-all-other` | 85 | 200 | 2026 | Upgrade: Dealer Development Manager (Portland; Upgrade: Dealer Development Manager (Las Vega; Glossier: Director of Co-Manufacturing &amp;  |
| ✅ ok | `precision:workingnomads-api` | 35 | 200 | 502 | Senior Magento Developer; Senior Back-end Developer; Looking For Online ESL Teachers - Remote- Joi |
| ✅ ok | `precision:remotive-translator` | 12 | 200 | 16 | Full-Stack Developer; Senior Back-end Developer; Head of Engineering |
| ✅ ok | `precision:remotive-teacher` | 12 | 200 | 37 | Full-Stack Developer; Senior Back-end Developer; Head of Engineering |
| ✅ ok | `precision:remotive-writer` | 12 | 200 | 69 | Full-Stack Developer; Senior Back-end Developer; Head of Engineering |
| ⚪ empty | `precision:jobicy-translation` | 0 | 200 | 297 | 567 bytes, application/json |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 348 | Blending Control Technician; Captives Underwriter; Prompt-Response Writer US |
| 🔑 needs_key | `jsearch:arabic-translator` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `adzuna:gb` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `adzuna:us` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `jooble:arabic-translator` | 0 |  |  | missing secret(s): JOOBLE_API_KEY |
| 🔑 needs_key | `careerjet:arabic-translator` | 0 |  |  | missing secret(s): CAREERJET_AFFID |
| 🔑 needs_key | `reliefweb:arabic` | 0 |  |  | missing secret(s): RELIEFWEB_APPNAME |
| 🔑 needs_key | `reed:arabic-translator` | 0 |  |  | missing secret(s): REED_API_KEY_B64 |

## linkedin  <sub>ok 1 · empty 0 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 307 | Copy Editor (Remote); Copy Editor (Remote); Authored Works Review (Editor) |
| ⛔ blocked | `linkedin:guest-arabic-translator` | 0 | 429 | 83 | HTTP 429 |
| ⛔ blocked | `linkedin:guest-arabic-linguist` | 0 | 429 | 57 | HTTP 429 |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 166 | Urgent One-Page Japanese Translation required; Saudi Arabic Marketing Translator; CSV Import & Translation |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 197 | Retype Photo Pages Into PDF; Brand Design & Web Content; AI-Powered B2B Video Creator |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 95 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 63 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 27 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 102 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 827 | 200 | 171 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `html:dataannotation` | 112 | 200 | 299 | Software EngineerCodingUp to $150+ / hr312 hi; GeneralistGeneralUp to $50 / hr452 hired rece; Data ScientistData &amp; MLUp to $150+ / hr92 |
| ✅ ok | `ashby:mercor` | 108 | 200 | 48 | Software Engineer, Systems & Platform Applied; Infrastructure Software Engineer ; Strategic Project Lead |
| ✅ ok | `greenhouse:turing` | 40 | 200 | 60 | Account Director - Consumer Packaged Goods - ; AI Engagement Lead; Client Director, Financial Services (BFSI) |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 46 | Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments; Forward Deployed Research Scientist |
| ⚪ empty | `ashby:deel` | 0 | 200 | 19 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 1373 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 162 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 122 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 459 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 412 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 51 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 110 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 79 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 87 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 103 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 40 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 0 · not_found 15 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 35 | 200 | 404 | Rendering Engineer; シニア3D背景アーティスト; Technical Designer – Japan & Global Game Deve |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 418 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 194 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 1044 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 386 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 108 | 4718 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 402 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 395 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 3267 | 133430 bytes, text/html |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 84 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 215 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 93 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 88 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 99 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 102 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 44 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 517 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |
| 💥 error | `html:futuregroup-careers` | 0 |  | 190 | ServerDisconnectedError: Server disconnected |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 0 · not_found 17 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 755 | 163022 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 180 | 220902 bytes, text/html |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 44 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 388 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 444 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 45 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 245 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 454 | HTTP 404 |
| ❓ not_found | `personio:lingoda` | 0 | 404 | 113 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 58 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 29 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 216 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 94 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 106 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 445 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 11 | 200 | 98 | Business Development / Sales Executive; Community & Support Intern - UAE Nationals; Freelance Marketing Artist: Video Editor, Mot |
| ❓ not_found | `lever:anghami` | 0 | 404 | 28 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 237 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 431 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 93 | HTTP 404 |

## remote-boards  <sub>ok 5 · empty 1 · blocked 1 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `json:remote1stjobs` | 30281 | 200 | 3235 | Strategic Account Manager; GTM Associate; Founding Enterprise Account Executive, DACH |
| ✅ ok | `html:remowork-arabic` | 205 | 200 | 599 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `rss:remotejobleads` | 16 | 200 | 595 | Medical Coder / CDI Specialist &#8211; AI Eva; AI Recruiter (AIR); AI Recruiter (AIR) |
| ✅ ok | `html:jobgether` | 7 | 200 | 394 | Job search playbook; Job search playbook; Jobseekers guide |
| ✅ ok | `html:dailyremote` | 2 | 200 | 399 | Job Application Tracker; Search Jobs by Job Title |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 235 | 79755 bytes, text/html |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 740 | HTTP 403 |
| 💥 error | `rss:euremotejobs` | 0 | 520 | 680 | HTTP 520 |
| 💥 error | `html:remote-co` | 0 |  | 15636 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2420 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 442 | 386155 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 28 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 383 | HTTP 403 |

## un-ngo  <sub>ok 2 · empty 0 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:impactpool-arabic` | 11 | 200 | 986 | Arabic interpreter


IRC - International Resc; Lead Strategic Coordinator


IsDB - Islamic D; ICLA Project Manager Palestine Gaza


NRC - N |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 165 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 48 | HTTP 403 + challenge page |
| ⛔ blocked | `html:untalent-arabic` | 0 | 403 | 265 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 1 · blocked 5 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1807 | Jobs in Jordan (55); Jobs in Qatar (3); Jobs in UAE (1) |
| ⚪ empty | `html:mostaql-writing-translation` | 0 | 202 | 438 | 2387 bytes, text/html |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 82 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 84 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 129 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 320 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 77 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15769 | timeout >15s |

## academic-editing-watchers  <sub>ok 0 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 68 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 467 | HTTP 404 |
| 💥 error | `watch:cactus` | 0 |  | 238 | ClientConnectorDNSError: Cannot connect to host www.cactusglobal.com:443 ssl:False [Name or service not known] |

## ats-new  <sub>ok 0 · empty 3 · blocked 3 · not_found 12 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 718 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 653 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 381 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 483 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 477 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 440 | HTTP 403 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 442 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 380 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 380 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 560 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 500 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 486 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 311 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 243 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 234 | HTTP 404 |
| ❓ not_found | `personio:appen` | 0 | 404 | 722 | HTTP 404 |
| ❓ not_found | `personio:centific` | 0 | 404 | 747 | HTTP 404 |
| ❓ not_found | `personio:surgeai` | 0 | 404 | 672 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 827 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 40 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 108 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 11 jobs
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
{"url": "https://www.remotejobleads.com/feed/", "source_name": "remotejobleads", "type": "rss"},
{"url": "https://www.remote1stjobs.com/jobs.json", "source_name": "remote1stjobs", "type": "json"},
```

## Secrets to add for the keyed aggregators

Settings → Secrets and variables → Actions → New repository secret: `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, `CAREERJET_AFFID`, `JOOBLE_API_KEY`, `RAPIDAPI_KEY`, `REED_API_KEY_B64`, `RELIEFWEB_APPNAME`
