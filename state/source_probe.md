# Source probe — 2026-09-16 19:40 UTC

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
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 290 | Senior Category Manager Non-Food (m/w/d); Senior Category Manager (m/w/d); Principal Data Strategist (m/f/d) |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 549 | Sr Solutions Architect; Junior Payroll Assistant; Customer Experience Representative |
| ✅ ok | `baseline:wwr` | 86 | 200 | 328 | Koast.ai: Head of Technical Support @ Koast.a; Powered by search: Senior SEO &amp; Organic G; Powered by search: Senior Performance Marketi |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 711 | Edge Functions Engineer; Product Lead - Infrastructure; Mantle Squad - Global |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 121 | TV, Video, Audio & Display Strategist; Customer Service Advisor (Polish); Product Designer |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 117 | Modern Responsive Business Website; Recruiter for Candidate Research Needed; Structural Evaluation for Joist Separation |
| ✅ ok | `baseline:remotive` | 13 | 200 | 152 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |

## precision-queries  <sub>ok 8 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 708 | HR Operations Specialist; Marketing Student Assistant; Social Comms |
| ✅ ok | `precision:wwr-all-other` | 58 | 200 | 136 | Powered by search: Senior SEO &amp; Organic G; Powered by search: Senior Performance Marketi; TELUS Digital: Personalized Internet Ads Asse |
| ✅ ok | `precision:workingnomads-api` | 53 | 200 | 437 | Senior SEO & Organic Growth Strategist; Senior Performance Marketing Strategist; Personalized Internet Ads Assessor - English  |
| ✅ ok | `precision:jobicy-teaching` | 50 | 200 | 809 | Postgres Deployment Engineer (Nix); Sales & CX Enablement Partner; Senior Manager, Enterprise Customer Success |
| ✅ ok | `precision:jobicy-translation` | 45 | 200 | 849 | Translation Project Manager; Alliance Manager, Translational Medicine; English to Spanish (LatAm) for Life Sciences  |
| ✅ ok | `precision:remotive-translator` | 13 | 200 | 19 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |
| ✅ ok | `precision:remotive-teacher` | 13 | 200 | 26 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |
| ✅ ok | `precision:remotive-writer` | 13 | 200 | 25 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 8 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 465 | Writing and Annotation Task - Fula (Adlam Scr; P&C Middle Market Energy Renewal Underwriter; Especialista de FP&A & Labour |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 428 | Portuguese translator specialist (M/F); Translator - Abu Dhabi Government entity; Translation Coordinator - Translation support |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 291 | PhD Level Linguist III; Language-Enabled OSINT Collector (WMD Focused; Portuguese translator specialist (M/F) |
| ✅ ok | `linkedin:guest-esl` | 10 | 200 | 426 | English Tutor; IELTS Language Trainer; English Tutor |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 239 | Copy Editor / Senior Copy Editor (NY); Senior Editor; Copy Editor |

## freelance  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 159 | Arabic Trip Vlog Clip Trimming; High Detail 2D to 3D CAD; French-Russian Marketing Translation |
| ✅ ok | `freelancer:api-esl` | 20 | 200 | 173 | Expert AI Automation & Voice Agent Engineer; Romanian Finance Appointment Setter Needed - ; Type Scanned Handwritten Document into PDF fo |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 148 | Arabic Trip Vlog Clip Trimming; Artwork/visuals for my music; 60-Second Facility Promo Video |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 176 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 113 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 121 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 118 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 228 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 107 | 200 | 63 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 311 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 20 | 200 | 36 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 53 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Forward Deployed Engineering Manager |
| ⚪ empty | `ashby:deel` | 0 | 200 | 37 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 202 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 141 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 107 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 389 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 371 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 101 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 50 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 27 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 341 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 27 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 24 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 49 | 200 | 368 | シニア3D背景アーティスト; 3D 背景アーティスト; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 389 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 422 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 478 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 328 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 656 | 243543 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 358 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 339 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 6192 | 133286 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 362 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 1083 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 324 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 30 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 30 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 110 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 30 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 41 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 28 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 30 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 147 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 24 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 73 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 818 | 176962 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 1679 | 213026 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 868 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 132 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 359 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 151 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 404 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 81 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 187 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 86 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 12822 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 27 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 85 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 263 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 22 | 200 | 75 | Business Development/ Sales Executive - EMEA ; Community & Partnerships Manager; Community & Partnerships Manager |
| ❓ not_found | `lever:anghami` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 126 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 330 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 73 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 203 | 200 | 791 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 1524 | Tax Analyst (Direct Tax); Senior Manager, Coach & Instructor Enablement; Engineering Manager, Language Security (remot |
| ✅ ok | `html:jobgether` | 6 | 200 | 384 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 175 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 620 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 183 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 202 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 454 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15576 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1910 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 147 | 434162 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 120 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 301 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 225 | 200 | 1417 | Openings; Search; Médecins du Monde |
| ✅ ok | `html:impactpool-arabic` | 14 | 200 | 1264 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Communications Specialist -Communications and; HR Intern


UNOPS - United Nations Office for |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 234 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 178 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1665 | Jobs in Jordan (55); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 82 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 122 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 181 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 241 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 325 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 125 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15207 | timeout >15s |

## academic-editing-watchers  <sub>ok 1 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 12211 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 42 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 394 | HTTP 404 |

## esl-boards  <sub>ok 2 · empty 0 · blocked 0 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:eslbase` | 43 | 200 | 1086 | Get job alerts; Get job alerts; English Teaching Jobs in Vietnam with VUS |
| ✅ ok | `html:eslcafe-international` | 12 | 200 | 412 | Job Center; International Job Board; Korean Job Board |
| ❓ not_found | `html:tefl-online` | 0 | 404 | 141 | HTTP 404 |
| ❓ not_found | `html:teachaway-online` | 0 | 404 | 297 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 239 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 188 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 163 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 383 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 217 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 81 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 778 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 687 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 695 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 261 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 266 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 326 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 390 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 396 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 403 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 377 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 356 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 362 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 831 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 20 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 107 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 22 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 49 jobs
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
