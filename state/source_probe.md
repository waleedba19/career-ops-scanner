# Source probe — 2026-11-09 11:58 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 38 | responded with parseable jobs → **can be added** |
| empty | 20 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 17 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 61 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 6 | DNS/TLS/timeout |

## Answer: **31 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 300 | 200 | 155 | Werkstudent (m/w/d) - Karriereberatung, Coach; Mitarbeiter in der Kundenberatung (m/w/d) - o; Social Media Manager:in (Werkstudium oder Pra |
| ✅ ok | `baseline:wwr` | 100 | 200 | 793 | Midi Health: Nurse Practitioner - Arizona (AZ; True Talent Solutions Partners: Strategic Pro; Dimont &amp; Associates, LLC: Hazard Claims A |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 457 | Account Executive Enterprise; AI Developer; Junior Market Analyst |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 189 | Devices & IOT Field Engineering Manager; Early Childhood Teacher; Senior Product Designer, Design Systems |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 94 | Account Development; Senior Director of Experience Design; Sr. Engineer - Packaging Execution (CA Based  |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 111 | Collaboration Opportunity &ndash; Revenue Sha; Editor Video Pendek Sosial Media; Filipino High-Ticket Sales Closer |
| ✅ ok | `baseline:remotive` | 12 | 200 | 99 | Tier III Service Desk Engineer; US Remote Patient Care Advocate (Customer Ser; Freelance Writer |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 382 | AI Content Reviewer Video Annotation; Paid Media Manager US ; Senior Software Engineer II Applied AI |
| ✅ ok | `precision:wwr-all-other` | 99 | 200 | 539 | Midi Health: Nurse Practitioner - Arizona (AZ; Photon Medical Group: Remote Nurse Practition; NM MITCHELL CONSULTANCY LTD: Remote Schedulin |
| ✅ ok | `precision:jobicy-translation` | 50 | 200 | 155 | Talent Pool: Romansh Speakers (Switzerland); Spanish Patent Language Lead; Spanish (Spain) to English Pharmacovigilance  |
| ✅ ok | `precision:workingnomads-api` | 18 | 200 | 99 | New Business Manager; AI Content Reviewer, Video Annotation; Technical Operations Lead |
| ✅ ok | `precision:remotive-translator` | 12 | 200 | 20 | Tier III Service Desk Engineer; US Remote Patient Care Advocate (Customer Ser; Freelance Writer |
| ✅ ok | `precision:remotive-teacher` | 12 | 200 | 14 | Tier III Service Desk Engineer; US Remote Patient Care Advocate (Customer Ser; Freelance Writer |
| ✅ ok | `precision:remotive-writer` | 12 | 200 | 19 | Tier III Service Desk Engineer; US Remote Patient Care Advocate (Customer Ser; Freelance Writer |

## aggregator-keyed  <sub>ok 0 · empty 0 · blocked 1 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| 🔑 needs_key | `jsearch:arabic-translator` | 0 |  |  | missing secret(s): RAPIDAPI_KEY |
| 🔑 needs_key | `adzuna:gb` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `adzuna:us` | 0 |  |  | missing secret(s): ADZUNA_APP_ID, ADZUNA_APP_KEY |
| 🔑 needs_key | `jooble:arabic-translator` | 0 |  |  | missing secret(s): JOOBLE_API_KEY |
| 🔑 needs_key | `careerjet:arabic-translator` | 0 |  |  | missing secret(s): CAREERJET_AFFID |
| 🔑 needs_key | `reliefweb:arabic` | 0 |  |  | missing secret(s): RELIEFWEB_APPNAME |
| 🔑 needs_key | `reed:arabic-translator` | 0 |  |  | missing secret(s): REED_API_KEY_B64 |
| ⛔ blocked | `themuse:writing-editing` | 0 | 403 | 32 | HTTP 403 + challenge page |

## linkedin  <sub>ok 3 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 274 | Site Mandarin Translator; 华星-翻译类（本硕）; Indonesian-Mandarin Translator |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 372 | Junior/ Middle Specialist with Portuguese &am; Subject Matter Expert Manager, Domain Expert ; Associate Language Specialist – Spanish IRC30 |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 372 | Telugu Proofreader; Proofreader; Redaktor / Korektor |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 124 | Amharic to English Legal Translation - 09/11/; Oromo Interview Audio Transcription; Technical SEO Audit & Fixes for Salla E-comme |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 131 | Video editing; Professional Social Media Video Editor - 09/1; Long-Term Sports Reels Editor |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 80 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 187 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 63 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 97 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 827 | 200 | 219 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `html:dataannotation` | 133 | 200 | 179 | Software EngineerCodingUp to $150+ / hr312 hi; GeneralistGeneralUp to $50 / hr452 hired rece; Data ScientistData &amp; MLUp to $150+ / hr92 |
| ✅ ok | `ashby:mercor` | 91 | 200 | 64 | Software Engineer, Systems & Platform Applied; Infrastructure Software Engineer ; Strategic Project Lead |
| ✅ ok | `greenhouse:turing` | 47 | 200 | 43 | Account Director, Enterprise AI - Consumer Pa; Account Executive, Frontier AI; AI Engagement Lead |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 166 | Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments; Forward Deployed Research Scientist |
| ⚪ empty | `ashby:deel` | 0 | 200 | 42 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 105 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 91 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 51 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 442 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 435 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 51 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 15 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 11 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 336 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 25 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 0 · not_found 15 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 31 | 200 | 400 | Rendering Engineer; シニア3D背景アーティスト; Technical Designer – Japan & Global Game Deve |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 360 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 184 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 391 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 371 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 151 | 5576 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 375 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 347 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 4053 | 133429 bytes, text/html |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 325 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 324 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 13 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 337 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 29 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 30 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 116 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |
| 💥 error | `html:futuregroup-careers` | 0 |  | 496 | ServerDisconnectedError: Server disconnected |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 0 · not_found 17 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 446 | 163022 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 197 | 220902 bytes, text/html |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 1581 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 401 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 187 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 458 | HTTP 404 |
| ❓ not_found | `personio:lingoda` | 0 | 404 | 310 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 123 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 214 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 42 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 41 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 84 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 182 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 10 | 200 | 54 | AI Artist; AI Artist; Community & Support Intern - UAE Nationals |
| ❓ not_found | `lever:anghami` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 174 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 247 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 30 | HTTP 404 |

## remote-boards  <sub>ok 5 · empty 1 · blocked 1 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `json:remote1stjobs` | 34776 | 200 | 3589 | Business Development Manager, Custom Assay Se; Business Development Manager, Immunoassays & ; Business Development Manager, Immunoassays &  |
| ✅ ok | `html:remowork-arabic` | 212 | 200 | 346 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `rss:remotejobleads` | 16 | 200 | 675 | Digital Designer; Cloud Network Engineer; Python/GenAI Engineer |
| ✅ ok | `html:jobgether` | 6 | 200 | 228 | Job search playbook; Jobseekers guide; Review Jobgether &nbsp;→ |
| ✅ ok | `html:dailyremote` | 2 | 200 | 131 | Job Application Tracker; Search Jobs by Job Title |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 143 | 79774 bytes, text/html |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 490 | HTTP 403 |
| 💥 error | `rss:euremotejobs` | 0 | 520 | 486 | HTTP 520 |
| 💥 error | `html:remote-co` | 0 |  | 15638 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1833 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 96 | 387747 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 68 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 275 | HTTP 403 |

## un-ngo  <sub>ok 2 · empty 0 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:impactpool-arabic` | 18 | 200 | 502 | Arabic interpreter


IRC - International Resc; Administration Associate


UNOPS - United Nat; Diaspora Engagement Project Associate


UNV - |
| ✅ ok | `html:idealist-arabic` | 4 | 200 | 232 | Find a Job; Jobs; Find a Job |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 44 | HTTP 403 + challenge page |
| ⛔ blocked | `html:untalent-arabic` | 0 | 403 | 297 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 1 · blocked 4 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1534 | Jobs in Jordan (53); Jobs in Saudi Arabia (6); Jobs in Qatar (3) |
| ⚪ empty | `html:mostaql-writing-translation` | 0 | 202 | 278 | 2387 bytes, text/html |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 129 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 58 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 138 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 282 | HTTP 403 |
| ❓ not_found | `html:ureed-translation` | 0 | 404 | 3159 | HTTP 404 |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15210 | timeout >15s |

## academic-editing-watchers  <sub>ok 0 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 61 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 232 | HTTP 404 |
| 💥 error | `watch:cactus` | 0 |  | 143 | ClientConnectorDNSError: Cannot connect to host www.cactusglobal.com:443 ssl:False [Name or service not known] |

## ats-new  <sub>ok 0 · empty 3 · blocked 3 · not_found 12 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 264 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 207 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 210 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 215 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 70 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 79 | HTTP 403 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 1172 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 801 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 430 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 414 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 430 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 351 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 352 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 355 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 333 | HTTP 404 |
| ❓ not_found | `personio:appen` | 0 | 404 | 553 | HTTP 404 |
| ❓ not_found | `personio:centific` | 0 | 404 | 663 | HTTP 404 |
| ❓ not_found | `personio:surgeai` | 0 | 404 | 589 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 827 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 47 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 91 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 10 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 31 jobs
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
