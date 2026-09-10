# Source probe — 2026-09-10 23:41 UTC

_Ran from: github-actions · 168 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 47 | responded with parseable jobs → **can be added** |
| empty | 21 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 30 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 59 | 404/410 → slug or endpoint is wrong |
| needs_key | 8 | add the secret and re-run |
| error | 3 | DNS/TLS/timeout |

## Answer: **40 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 261 | Data Engineer:in / IT Support (m/w/d); Performance Marketing Working Student – Talen; Mitarbeiter /Leiter (w\|m\|d) interne Qualitäts |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 579 | Business Development Manager; Quality Dispense Technician North; Social Comms |
| ✅ ok | `baseline:wwr` | 90 | 200 | 446 | Toptal: Power Platform Solutions Architect; TestGorilla: Sr. People &amp; Talent Operatio; Coaching.com: Membership Coordinator |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 940 | IT Associate; Enterprise Sales VP, Labor and Trust; Product Manager, Orchestrator |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 147 | Senior Graphic Designer - AM; Senior AI Product Manager, EMEA; Lead Analyst, Credit Risk Strategy |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 155 | Thorough Code Review of Decentralized, Encryp; Bangun Toko Shopify Minimalis Modern; WordPress &amp; GHL Virtual Assistant |
| ✅ ok | `baseline:remotive` | 18 | 200 | 156 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |

## precision-queries  <sub>ok 8 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 519 | Social Comms; AI Response Analyst; Senior Level Designer |
| ✅ ok | `precision:jobicy-teaching` | 50 | 200 | 1115 | AI Engineer - FDE (Forward Deployed Engineer); Work from home as a Private Online German Tut; Senior Customer Marketing Manager |
| ✅ ok | `precision:wwr-all-other` | 50 | 200 | 242 | TestGorilla: Sr. People &amp; Talent Operatio; Toptal: Senior Security Compliance Consultant; Salesloft: Enterprise Account Director |
| ✅ ok | `precision:jobicy-translation` | 44 | 200 | 124 | Translation Project Manager; Alliance Manager, Translational Medicine; Senior Brand Designer, Experiential |
| ✅ ok | `precision:workingnomads-api` | 43 | 200 | 701 | Client Success Manager; Video Creator (100% remote); Senior Java & React Developer |
| ✅ ok | `precision:remotive-translator` | 18 | 200 | 25 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |
| ✅ ok | `precision:remotive-teacher` | 18 | 200 | 29 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |
| ✅ ok | `precision:remotive-writer` | 18 | 200 | 29 | Inside Sales Contractor; Tier III Service Desk Engineer; Sales Jedi |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 8 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 384 | Analyst,Underwriter; Analyst,Underwriter; P&C Middle Market Energy Renewal Underwriter |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 382 | Arabic Linguist CAT II - CENTCOM; مترجم طبي عربي–تركي; Arabic Copywriter |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 320 | Arabic Linguist CAT II - CENTCOM; Kurdish/Arabic Travel Only Linguist (2026-020; AI Tutor - Spanish |
| ✅ ok | `linkedin:guest-esl` | 10 | 200 | 338 | Reading Tutor – PH; English Tutor; Corporate English Trainer |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 339 | Copyediting Specialist; Copyediting Specialist; Copy Editor |

## freelance  <sub>ok 3 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 197 | Polish Speakers Needed for 813 Short Sentence;  Egypt Arabic Speakers Needed for 438 Short S; Convert MRMS GRIB2 to GEMPAK |
| ✅ ok | `freelancer:api-esl` | 20 | 200 | 228 | AI Training: Image Reviewing & Annotation -- ; AI Training Subject Matter Expert — Accountin; SEO Content Writer for Diverse Topics |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 231 | Quick Chrome Addon Enhancement; Female Content Creator & Video Editor Needed; YouTube Gaming Video Editor |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 118 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 114 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 120 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 139 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 213 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 101 | 200 | 114 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 107 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 22 | 200 | 75 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 115 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Deployment Lead |
| ⚪ empty | `ashby:deel` | 0 | 200 | 77 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 152 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 141 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 144 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 431 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 415 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 53 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 164 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 61 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 87 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 84 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 60 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 167 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 55 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 53 | 200 | 460 | Technical Artist ; Game Designer – Japan & Global Game Developme; Game Programmer – Japan & Global Game Develop |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 417 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 345 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 843 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 411 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 271 | 243741 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 400 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 396 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 2793 | 132990 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 202 | 188 | HTTP 202 + challenge page |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 148 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 53 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 10282 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 105 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 59 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 199 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 55 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 122 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 105 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 113 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 100 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 54 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 435 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 882 | 186384 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 420 | 213026 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 997 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 54 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 39 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 474 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 52 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 193 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 584 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 57 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 194 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 115 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 56 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 115 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 90 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 670 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 19 | 200 | 125 | Business Development/ Sales Executive - EMEA ; Community & Support Intern - UAE Nationals; Community and Support Specialist |
| ❓ not_found | `lever:anghami` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 210 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 556 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 113 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 202 | 200 | 772 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 2002 | Security Engineer ; Risk Partnerships Manager, Banks & Treasury; Product Manager, Sail Core |
| ✅ ok | `html:jobgether` | 6 | 200 | 331 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 1341 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 202 | 767 | HTTP 202 + challenge page |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 93 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 173 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 565 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15968 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 2354 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 381 | 428358 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 93 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 431 | HTTP 403 |

## esl-boards  <sub>ok 2 · empty 0 · blocked 0 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:eslbase` | 43 | 200 | 1536 | Get job alerts; Get job alerts; English Teaching Jobs in Vietnam with VUS |
| ✅ ok | `html:eslcafe-international` | 12 | 200 | 277 | Job Center; International Job Board; Korean Job Board |
| ❓ not_found | `html:tefl-online` | 0 | 404 | 470 | HTTP 404 |
| ❓ not_found | `html:teachaway-online` | 0 | 404 | 5851 | HTTP 404 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 190 | 200 | 2330 | Openings; Search; WFP - World Food Programme |
| ✅ ok | `html:impactpool-arabic` | 10 | 200 | 1031 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Interpreter (Arabic)


IOM - International Or; Consultants template


WHO - World Health Org |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 443 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 69 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 2231 | Jobs in Jordan (51); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 78 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 185 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 104 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 314 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 515 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 105 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15172 | timeout >15s |

## academic-editing-watchers  <sub>ok 3 · empty 1 · blocked 1 · not_found 2 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 2023 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ✅ ok | `watch:enago` | 9 | 200 | 702 | Academic Editor; Reviewer and Journal Expert; Senior Scientific Editor |
| ✅ ok | `watch:papertrue` | 3 | 201 | 550 | Jobs; Jobs; Jobs |
| ⚪ empty | `watch:prs` | 0 | 200 | 726 | 345101 bytes, text/html |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 87 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 403 | HTTP 404 |
| ❓ not_found | `watch:wordvice` | 0 | 404 | 1376 | HTTP 404 |

## major-platforms-blocked  <sub>ok 1 · empty 1 · blocked 5 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `wellfound:html` | 70 | 200 | 430 | Find Jobs; Enterprise Solutions Engineer; Design Engineer, Site |
| ⚪ empty | `google:jobs` | 0 | 200 | 675 | 92928 bytes, text/html |
| ⛔ blocked | `indeed:html` | 0 | 401 | 60 | HTTP 401 + challenge page |
| ⛔ blocked | `indeed:rss` | 0 | 403 | 36 | HTTP 403 + challenge page |
| ⛔ blocked | `glassdoor:html` | 0 | 403 | 83 | HTTP 403 |
| ⛔ blocked | `ziprecruiter:html` | 0 | 403 | 75 | HTTP 403 + challenge page |
| ⛔ blocked | `upwork:search` | 0 | 403 | 141 | HTTP 403 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 519 | 45802 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 491 | 45802 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 443 | 45802 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 716 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 517 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 381 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 677 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 622 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 905 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 280 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 224 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 250 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 473 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 470 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 451 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 369 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 297 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 221 | HTTP 404 |

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
