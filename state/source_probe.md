# Source probe — 2026-09-14 09:11 UTC

_Ran from: github-actions · 157 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 44 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 24 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 58 | 404/410 → slug or endpoint is wrong |
| needs_key | 8 | add the secret and re-run |
| error | 4 | DNS/TLS/timeout |

## Answer: **37 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 224 | Ingenieur HKLS (m/w/d); HR Business Partner (m/w/d); Performance Marketing Manager (m/f/x) |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 419 | Technical Product Lead AI Finance App; Software Engineer; HR Operations Specialist |
| ✅ ok | `baseline:wwr` | 87 | 200 | 423 | OKX: Affiliate Business Development Manager, ; Datadog: Director, Enterprise Sales; OKX: Affiliate Business Development Manager |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 673 | Staff Software Engineer (SRE); GTM Talent Community; IT Associate |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 39 | Malayalam Document Expert - Fully Remote \| Up; Client Delivery Operations Manager; Remote - Federal IT Project Manager, Microsof |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 178 | Comprehensive Law Firm Management ERP; Video Editor &amp; Screen Recorder Needed for; Minimalist Premium Brand Identity Creation |
| ✅ ok | `baseline:remotive` | 16 | 200 | 118 | Remote Office Assistant; AI Response Evaluator; Inside Sales Contractor |

## precision-queries  <sub>ok 8 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 429 | HR Operations Specialist; Marketing Student Assistant; Social Comms |
| ✅ ok | `precision:jobicy-teaching` | 50 | 200 | 767 | Senior Editor, Energy and Sustainability, Del; Senior Editor, AI and Technology, Deloitte Gl; Manager, Cyber Compliance, Deloitte Global Te |
| ✅ ok | `precision:wwr-all-other` | 46 | 200 | 139 | Datadog: Director, Enterprise Sales; Fastly: Threat Detection Analyst (Japanese &a; Toptal : Professional Photoshop Artists |
| ✅ ok | `precision:workingnomads-api` | 44 | 200 | 370 | Product Lead (Strategy + Full Stack); Face Deduplication Collection; Senior Google Ads Account Manager - Remote (W |
| ✅ ok | `precision:jobicy-translation` | 42 | 200 | 759 | Translation Project Manager; Alliance Manager, Translational Medicine; Project Director, Qualitative Research |
| ✅ ok | `precision:remotive-translator` | 16 | 200 | 12 | Remote Office Assistant; AI Response Evaluator; Inside Sales Contractor |
| ✅ ok | `precision:remotive-teacher` | 16 | 200 | 13 | Remote Office Assistant; AI Response Evaluator; Inside Sales Contractor |
| ✅ ok | `precision:remotive-writer` | 16 | 200 | 13 | Remote Office Assistant; AI Response Evaluator; Inside Sales Contractor |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 8 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 201 | Analyst,Underwriter; Writing and Annotation Task - Fula (Adlam Scr; P&C Middle Market Energy Renewal Underwriter |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 418 | [Studio Support Div.] Korean Localization Spe; Mandarin Translator; Chinese Translator |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 421 | PhD Fellow in Literary Studies, Art History o; Afrikaans Linguist CAT III; [Studio Support Div.] Korean Localization Spe |
| ✅ ok | `linkedin:guest-esl` | 10 | 200 | 428 | Entry-Level ESOL Online Tutor (Ref:EDU14/26); ESL Teacher (Online English Instructor); MY English Teacher (Full-Time) |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 452 | Copyediting Specialist; Editor, Alto; Proofreader |

## freelance  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 207 | Marketing PDF Translation Expertise Needed; Amharic to Somali Document Translation; Arabic Multimodal LLM Fine-Tuning |
| ✅ ok | `freelancer:api-esl` | 20 | 200 | 154 | Video Editor & Screen Recorder Needed for Fac; International Actor for Short Brand Videos; Need Traffic-Boosting SEO Backlinks |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 155 | Instagram Reels Creator for Dubai Real Estate; Video Editor & Screen Recorder Needed for Fac; Event Recap Video Production |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 60 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 44 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 69 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 231 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 137 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 103 | 200 | 84 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 111 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 21 | 200 | 30 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 37 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Forward Deployed Engineering Manager |
| ⚪ empty | `ashby:deel` | 0 | 200 | 39 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 80 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 86 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 61 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 439 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 417 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 59 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 98 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 34 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 370 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 158 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 51 | 200 | 387 | シニア3D背景アーティスト; 3D 背景アーティスト; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 365 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 168 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 374 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 337 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 393 | 243423 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 327 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 332 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2568 | 132990 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 384 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 322 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 18 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 321 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 46 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 331 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 18 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 31 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 41 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 33 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 22 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 29 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 289 | 186383 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 253 | 213026 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 729 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 399 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 204 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 392 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 18 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 87 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 135 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 36 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 32 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 82 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 322 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 19 | 200 | 42 | Business Development/ Sales Executive - EMEA ; Community & Support Intern - UAE Nationals; Community and Support Specialist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 85 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 192 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 84 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 35 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 2</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 203 | 200 | 556 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 1395 | P2P Growth Operations Manager (CIS/CEE); Sr. Customer Success Manager - Pharma (Biling; Account Executive |
| ✅ ok | `html:jobgether` | 6 | 200 | 326 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 396 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 537 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 104 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 99 | HTTP 403 + challenge page |
| 💥 error | `html:remote-co` | 0 |  | 15288 | timeout >15s |
| 💥 error | `html:europeremotely` | 0 |  | 267 | ClientConnectorError: Cannot connect to host europeremotely.com:443 ssl:False [Connection reset by peer] |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2090 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 156 | 428469 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 69 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 286 | HTTP 403 |

## esl-boards  <sub>ok 2 · empty 0 · blocked 0 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:eslbase` | 43 | 200 | 1084 | Get job alerts; Get job alerts; IGCSE English Teacher Vacancy in Jakarta, Ind |
| ✅ ok | `html:eslcafe-international` | 12 | 200 | 241 | Job Center; International Job Board; Korean Job Board |
| ❓ not_found | `html:tefl-online` | 0 | 404 | 177 | HTTP 404 |
| ❓ not_found | `html:teachaway-online` | 0 | 404 | 430 | HTTP 404 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 180 | 200 | 1412 | Openings; Search; FHI 360 |
| ✅ ok | `html:impactpool-arabic` | 12 | 200 | 1525 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Consultants template


WHO - World Health Org; Communications Specialist -Communications and |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 368 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 204 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1717 | Jobs in Jordan (45); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 53 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 54 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 194 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 225 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 270 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 99 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15091 | timeout >15s |

## academic-editing-watchers  <sub>ok 1 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 2307 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 27 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 167 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 332 | 45802 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 218 | 45802 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 152 | 45802 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 386 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 256 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 229 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 515 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 598 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 515 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 348 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 1138 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 325 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 382 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 391 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 366 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 358 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 341 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 345 | HTTP 404 |

## Ready-to-paste config (only boards that answered with jobs)

```python
# GREENHOUSE_COMPANIES additions — 3 boards
    ("Invisible Technologies", "agency"),   # 831 jobs
    ("Labelbox / Alignerr", "labelbox"),   # 10 jobs
    ("Turing", "turing"),   # 21 jobs
```

```python
# ASHBY_COMPANIES additions — 1 boards
    ("Mercor", "mercor"),   # 103 jobs
```

```python
# WORKABLE_COMPANIES additions — 1 boards
    ("Tamatem Games", "tamatem"),   # 19 jobs
```

```python
# SMARTRECRUITERS_COMPANIES additions — 2 boards
    ("Keywords Studios", "KeywordsStudios"),   # 51 jobs
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
