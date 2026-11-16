# Source probe — 2026-11-16 11:54 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 43 | responded with parseable jobs → **can be added** |
| empty | 23 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 9 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 62 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 5 | DNS/TLS/timeout |

## Answer: **36 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 300 | 200 | 189 | Werkstudent:in / Praktikant:in Customer Succe; Cloud Engineer (Generative AI & LLM) (m/w/d); Praktikant für Nachhaltiges Investment (m/w/d |
| ✅ ok | `baseline:wwr` | 100 | 200 | 966 | BBE Marketing Inc: Business Development Manag; FELYRI CONSULTING LIMITED: Research Consultan; Roofr: Sales Development Representative |
| ✅ ok | `baseline:remoteok` | 97 | 200 | 1003 | Global Partnerships BD Lead; Scaled Account Manager EMEA; Software Engineer AI Tooling |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 262 | Senior DevOps Engineer; IT Department Lead - Remote, Worldwide; Site Reliability Engineer |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 128 | Implementation Specialist, US; Content Designer, AI Experiences; SAP Close Automation Consultant, Global (UK a |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 129 | Comprehensive Fintech App Flow Analysis; Fix Google Title Duplication; Pixel Animator for Horror Platformer |
| ✅ ok | `baseline:remotive` | 16 | 200 | 108 | Content Creator - YouTube; Remote Office Assistant; Senior Data Engineer |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 99 | 200 | 879 | Global Partnerships BD Lead; Research Engineer Privacy and Anonymization; Freelance Question Reviewers |
| ✅ ok | `precision:wwr-all-other` | 91 | 200 | 558 | FELYRI CONSULTING LIMITED: Research Consultan; D2B: Australian Healthcare Recruiter (AU Expe; D2B: Senior Roofing Estimator &amp; Takeoff S |
| ✅ ok | `precision:workingnomads-api` | 34 | 200 | 568 | QA Testers Wanted to Jump on an AI Assistant ; Senior React Full-stack Developer; Senior UI & UX Designer |
| ✅ ok | `precision:jobicy-translation` | 24 | 200 | 211 | Solution Consultant; Senior Manager, Services Portfolio Production; Sr. Clinical Research Associate (Hungary) |
| ✅ ok | `precision:remotive-translator` | 16 | 200 | 18 | Content Creator - YouTube; Remote Office Assistant; Senior Data Engineer |
| ✅ ok | `precision:remotive-teacher` | 16 | 200 | 38 | Content Creator - YouTube; Remote Office Assistant; Senior Data Engineer |
| ✅ ok | `precision:remotive-writer` | 16 | 200 | 19 | Content Creator - YouTube; Remote Office Assistant; Senior Data Engineer |

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
| ❓ not_found | `themuse:writing-editing` | 0 | 404 | 324 | HTTP 404 |

## linkedin  <sub>ok 3 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 335 | 西班牙语翻译; Translator Mandarin (TM); Translator (English ↔ Korean)번역 담당 |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 281 | General Qualifications Examiner - Internation; 音乐内容与本地化编辑（上海onsite）; Afrikaans Linguist CAT III |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 303 | Senior Copy Editor; Editor; Arabic Linguistics Editor |

## freelance  <sub>ok 3 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 158 | Russian-Bulgarian Website Translation; Thai translator needed (long term); Handwritten Letter Typing & Translation |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 169 | Excel Data Entry & Some Corrections; High-Energy Band Showreel Video; Complete TikTok Video Podcast Setup |
| ✅ ok | `workana:writing-translation` | 2 | 200 | 398 | Freelance Jobs; Writing &amp; Translation |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 204 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 151 | HTTP 403 |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 143 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 827 | 200 | 328 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `html:dataannotation` | 133 | 200 | 126 | Software EngineerCodingUp to $150+ / hr312 hi; GeneralistGeneralUp to $50 / hr452 hired rece; Data ScientistData &amp; MLUp to $150+ / hr92 |
| ✅ ok | `ashby:mercor` | 91 | 200 | 71 | Infrastructure Software Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `greenhouse:turing` | 45 | 200 | 89 | Account Director, Enterprise AI - Consumer Pa; AI Engagement Lead; Client Director, Financial Services (BFSI) |
| ✅ ok | `greenhouse:labelbox` | 11 | 200 | 44 | Forward Deployed Engineer, Enterprise Account; Forward Deployed Engineering Manager; Forward Deployed Engineer, RL Environments |
| ⚪ empty | `ashby:deel` | 0 | 200 | 41 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 157 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 191 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 166 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 491 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 466 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 171 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 15 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 128 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 33 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 0 · not_found 15 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 29 | 200 | 438 | Rendering Engineer; シニア3D背景アーティスト; 3D 背景アーティスト |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 446 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 438 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 869 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 406 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 234 | 5576 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 369 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 386 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 3140 | 133429 bytes, text/html |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 78 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 85 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 102 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 105 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 113 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 114 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 81 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 36 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 386 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |
| 💥 error | `html:futuregroup-careers` | 0 |  | 428 | ServerDisconnectedError: Server disconnected |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 0 · not_found 17 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 988 | 163022 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 264 | 220902 bytes, text/html |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 576 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 258 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 440 | HTTP 404 |
| ❓ not_found | `personio:lingoda` | 0 | 404 | 793 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 43 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 224 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 108 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 37 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 105 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 704 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 8 | 200 | 109 | AI Artist; AI Artist; AI Artist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 17 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 231 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 374 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 100 | HTTP 404 |

## remote-boards  <sub>ok 5 · empty 1 · blocked 1 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `json:remote1stjobs` | 37806 | 200 | 3829 | Senior Product Manager - Growth; Senior Product Manager - Growth; Senior Manager, Accounting |
| ✅ ok | `html:remowork-arabic` | 211 | 200 | 685 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `rss:remotejobleads` | 16 | 200 | 637 | Project Manager; Project Manager (LATAM &#8211; Remote); Bioinformatics Scientist |
| ✅ ok | `html:jobgether` | 7 | 200 | 311 | Job search playbook; Job search playbook; Jobseekers guide |
| ✅ ok | `html:dailyremote` | 2 | 200 | 254 | Job Application Tracker; Search Jobs by Job Title |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 179 | 79774 bytes, text/html |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 594 | HTTP 403 |
| 💥 error | `rss:euremotejobs` | 0 | 520 | 663 | HTTP 520 |
| 💥 error | `html:remote-co` | 0 |  | 15445 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2351 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 412 | 387893 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 72 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 441 | HTTP 403 |

## un-ngo  <sub>ok 4 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 196 | 200 | 1419 | Openings; Search; FHI 360 |
| ✅ ok | `html:impactpool-arabic` | 16 | 200 | 1103 | Interpreter (Arabic)


IOM - International Or; Interpreter (Arabic-French)


IOM - Internati; Global Roving and Emergency Response HAS Mana |
| ✅ ok | `html:unjobs-translation` | 4 | 200 | 1048 | Roster - Conference Interpreter, Geneva, Swit; Linguist Talent Pool, London, United Kingdom; Register as a Conference and Language Service |
| ✅ ok | `html:idealist-arabic` | 4 | 200 | 152 | Find a Job; Jobs; Find a Job |

## mena-boards  <sub>ok 1 · empty 1 · blocked 4 · not_found 1 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1742 | Jobs in Jordan (40); Jobs in Saudi Arabia (6); Jobs in Qatar (3) |
| ⚪ empty | `html:mostaql-writing-translation` | 0 | 202 | 476 | 2387 bytes, text/html |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 121 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 88 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 148 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 460 | HTTP 403 |
| ❓ not_found | `html:ureed-translation` | 0 | 404 | 1552 | HTTP 404 |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15025 | timeout >15s |

## academic-editing-watchers  <sub>ok 2 · empty 0 · blocked 0 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 2352 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ✅ ok | `watch:scribbr` | 7 | 200 | 129 | Jobs; Jobs; Jobs |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 428 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 6 · blocked 0 · not_found 12 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 432 | 46385 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 434 | 46385 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 428 | 46385 bytes, text/html |
| ⚪ empty | `jobvite:telus` | 0 | 200 | 660 | 180122 bytes, text/html |
| ⚪ empty | `jobvite:concentrix` | 0 | 200 | 782 | 180122 bytes, text/html |
| ⚪ empty | `jobvite:teleperformance` | 0 | 200 | 695 | 180122 bytes, text/html |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 526 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 633 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 452 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 556 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 564 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 541 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 250 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 207 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 542 | HTTP 404 |
| ❓ not_found | `personio:appen` | 0 | 404 | 806 | HTTP 404 |
| ❓ not_found | `personio:centific` | 0 | 404 | 828 | HTTP 404 |
| ❓ not_found | `personio:surgeai` | 0 | 404 | 735 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 827 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 11 jobs
    ("Turing", "turing"),   # 45 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 91 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 8 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 29 jobs
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
