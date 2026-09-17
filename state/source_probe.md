# Source probe — 2026-09-17 06:32 UTC

_Ran from: github-actions · 149 candidates · concurrency 6 · timeout 15s_

| status | count | meaning |
|---|---:|---|
| ok | 39 | responded with parseable jobs → **can be added** |
| empty | 19 | 200 but nothing parsed → wrong parser or no jobs right now |
| blocked | 25 | 403/429/999/captcha → do not scrape from this IP; use an aggregator or ATS route |
| not_found | 56 | 404/410 → slug or endpoint is wrong |
| needs_key | 7 | add the secret and re-run |
| error | 3 | DNS/TLS/timeout |

## Answer: **32 new sources responded with jobs** (+7 baseline references)

## baseline  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `baseline:arbeitnow` | 250 | 200 | 211 | Key Account Executive; Principal Database Performance Engineer - Cor; Senior Partner |
| ✅ ok | `baseline:remoteok` | 99 | 200 | 475 | Principal Product Manager; Sr Solutions Architect; Junior Payroll Assistant |
| ✅ ok | `baseline:wwr` | 86 | 200 | 320 | True Publicity: Undergrad Student - Remote, P; Koast.ai: Head of Technical Support @ Koast.a; Powered by search: Senior SEO &amp; Organic G |
| ✅ ok | `baseline:jobicy` | 20 | 200 | 602 | Edge Functions Engineer; Product Lead - Infrastructure; Mantle Squad - Global |
| ✅ ok | `baseline:himalayas` | 20 | 200 | 83 | Senior Cloud Platform Engineer; V102C Bilingual Immigration Receptionist; Chief Legal Officer (CLO) |
| ✅ ok | `baseline:freelancer-rss` | 20 | 200 | 169 | Android Screenshot &amp; Command APK; High-Performance Sports Sneaker Design -- 2; Razorpay Link Integration &amp; Banner Fix |
| ✅ ok | `baseline:remotive` | 13 | 200 | 120 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |

## precision-queries  <sub>ok 7 · empty 0 · blocked 0 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `precision:remoteok-writing` | 100 | 200 | 400 | HR Operations Specialist; Marketing Student Assistant; Social Comms |
| ✅ ok | `precision:wwr-all-other` | 59 | 200 | 157 | True Publicity: Undergrad Student - Remote, P; Powered by search: Senior SEO &amp; Organic G; Powered by search: Senior Performance Marketi |
| ✅ ok | `precision:workingnomads-api` | 53 | 200 | 291 | Senior SEO & Organic Growth Strategist; Senior Performance Marketing Strategist; Personalized Internet Ads Assessor - English  |
| ✅ ok | `precision:jobicy-translation` | 44 | 200 | 757 | Translation Project Manager; Alliance Manager, Translational Medicine; English to Spanish (LatAm) for Life Sciences  |
| ✅ ok | `precision:remotive-translator` | 13 | 200 | 18 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |
| ✅ ok | `precision:remotive-teacher` | 13 | 200 | 18 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |
| ✅ ok | `precision:remotive-writer` | 13 | 200 | 18 | Tech Lead Full-Stack Rails Engineer; Remote Office Assistant; AI Response Evaluator |

## aggregator-keyed  <sub>ok 1 · empty 0 · blocked 0 · not_found 0 · needs_key 7 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `themuse:writing-editing` | 20 | 200 | 204 | Especialista de FP&A & Labour; Data Partner - Creative Writer -  Remote - As; Prompt-Response Writer |
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
| ✅ ok | `linkedin:guest-arabic-translator` | 10 | 200 | 543 | Portuguese translator specialist (M/F); Translator - Abu Dhabi Government entity; Translation Coordinator - Translation support |
| ✅ ok | `linkedin:guest-arabic-linguist` | 10 | 200 | 481 | PhD Level Linguist III; Language-Enabled OSINT Collector (WMD Focused; Portuguese translator specialist (M/F) |
| ✅ ok | `linkedin:guest-proofreader` | 10 | 200 | 404 | Copy Editor / Senior Copy Editor (NY); Indegene: Copy Editor (US; fully remote); Senior Editor |

## freelance  <sub>ok 2 · empty 1 · blocked 3 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `freelancer:api-arabic` | 20 | 200 | 132 | English-French Translation ; Chinese-Kurdish Game Help Translation; French-Speaking ESG & Sustainability Course D |
| ✅ ok | `freelancer:api-proofreading` | 20 | 200 | 142 | Music video editing; Dynamic Promo Video Editing; Wedding Reception Influencer Host |
| ⚪ empty | `pph:search-arabic` | 0 | 202 | 146 | 2371 bytes, text/html |
| ⛔ blocked | `guru:arabic-translation` | 0 | 403 | 114 | HTTP 403 |
| ⛔ blocked | `workana:writing-translation` | 0 | 403 | 98 | HTTP 403 + challenge page |
| ⛔ blocked | `truelancer:arabic` | 0 | 429 | 97 | HTTP 429 |

## ats-language-ai  <sub>ok 5 · empty 6 · blocked 0 · not_found 11 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `greenhouse:agency` | 831 | 200 | 271 | 3D Modeling & Python Specialist - Freelance A; Accounting Specialist - Freelance AI Trainer ; Actuarial Science Specialist - Freelance AI T |
| ✅ ok | `ashby:mercor` | 107 | 200 | 91 | Infrastructure Engineer ; Strategic Project Lead; Strategic Projects Lead, Deeptune |
| ✅ ok | `html:dataannotation` | 94 | 200 | 40 | Software EngineerCoding$75 – $150+ / hr312 hi; GeneralistGeneral$25 – $50 / hr452 hired rece; Data ScientistData &amp; ML$75 – $150+ / hr92 |
| ✅ ok | `greenhouse:turing` | 20 | 200 | 36 | AI Engagement Lead; Chief of Staff (CEO's Office); Client Director, Frontier Data - US |
| ✅ ok | `greenhouse:labelbox` | 10 | 200 | 123 | Accounts Payable, Spend Management Coordinato; Cyber Security Intern; Forward Deployed Engineering Manager |
| ⚪ empty | `ashby:deel` | 0 | 200 | 45 | 28 bytes, application/json |
| ⚪ empty | `workable:prolific` | 0 | 200 | 141 | 46 bytes, application/json |
| ⚪ empty | `workable:superannotate` | 0 | 200 | 119 | 53 bytes, application/json |
| ⚪ empty | `workable:toloka` | 0 | 200 | 115 | 46 bytes, application/json |
| ⚪ empty | `smartrecruiters:TELUSInternational` | 0 | 200 | 447 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:Welocalize` | 0 | 200 | 414 | 52 bytes, application/json |
| ❓ not_found | `greenhouse:joinhandshake` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `greenhouse:surgeai` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `ashby:surgeai` | 0 | 404 | 89 | HTTP 404 |
| ❓ not_found | `greenhouse:mercor` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `ashby:micro1` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `ashby:pareto` | 0 | 404 | 40 | HTTP 404 |
| ❓ not_found | `greenhouse:superannotate` | 0 | 404 | 18 | HTTP 404 |
| ❓ not_found | `greenhouse:clickworker` | 0 | 404 | 35 | HTTP 404 |
| ❓ not_found | `lever:welocalize` | 0 | 404 | 324 | HTTP 404 |
| ❓ not_found | `greenhouse:welocalize` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `greenhouse:centific` | 0 | 404 | 23 | HTTP 404 |

## ats-lsp  <sub>ok 4 · empty 5 · blocked 1 · not_found 15 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `smartrecruiters:KeywordsStudios` | 45 | 200 | 375 | シニア3D背景アーティスト; 3D 背景アーティスト; Game Designer – Japan & Global Game Developme |
| ✅ ok | `smartrecruiters:TransPerfect` | 18 | 200 | 352 | Account Manager - Client Services; Spanish Quality Manager & Tester; Project Coordinator |
| ✅ ok | `html:tarjama-careers` | 5 | 200 | 413 | 07
Careers; Open on LinkedIn; View all open positions |
| ✅ ok | `html:torjoman-careers` | 2 | 200 | 341 | العربية; Careers |
| ⚪ empty | `smartrecruiters:Acolad` | 0 | 200 | 335 | 52 bytes, application/json |
| ⚪ empty | `html:transperfect-careers` | 0 | 200 | 287 | 243545 bytes, text/html |
| ⚪ empty | `smartrecruiters:Lionbridge` | 0 | 200 | 338 | 52 bytes, application/json |
| ⚪ empty | `smartrecruiters:RWS` | 0 | 200 | 333 | 52 bytes, application/json |
| ⚪ empty | `html:saudisoft-careers` | 0 | 200 | 5855 | 133286 bytes, text/html |
| ⛔ blocked | `html:futuregroup-careers` | 0 | 403 | 387 | HTTP 403 |
| ❓ not_found | `lever:unbabel` | 0 | 404 | 467 | HTTP 404 |
| ❓ not_found | `greenhouse:unbabel` | 0 | 404 | 23 | HTTP 404 |
| ❓ not_found | `lever:lilt` | 0 | 404 | 319 | HTTP 404 |
| ❓ not_found | `ashby:lilt` | 0 | 404 | 9 | HTTP 404 |
| ❓ not_found | `greenhouse:phrase` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `greenhouse:crowdin` | 0 | 404 | 21 | HTTP 404 |
| ❓ not_found | `lever:crowdin` | 0 | 404 | 333 | HTTP 404 |
| ❓ not_found | `greenhouse:keywordsstudios` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:acclaro` | 0 | 404 | 20 | HTTP 404 |
| ❓ not_found | `workable:argosmultilingual` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `workable:alconost` | 0 | 404 | 24 | HTTP 404 |
| ❓ not_found | `workable:straker` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `workable:getblend` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `greenhouse:languageline` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `greenhouse:propio` | 0 | 404 | 21 | HTTP 404 |
| 💥 error | `html:lionbridge-careers` | 0 |  | 25 | ClientResponseError: 400, message='Got more than 8190 bytes when reading: b"default-src \'self\' \'unsafe-inlin |

## ats-edtech  <sub>ok 0 · empty 2 · blocked 1 · not_found 16 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `html:nagwa-careers` | 0 | 200 | 379 | 176964 bytes, text/html |
| ⚪ empty | `html:almentor-careers` | 0 | 200 | 243 | 213026 bytes, text/html |
| ⛔ blocked | `personio:lingoda` | 0 | 429 | 606 | HTTP 429 |
| ❓ not_found | `greenhouse:preply` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `lever:preply` | 0 | 404 | 83 | HTTP 404 |
| ❓ not_found | `greenhouse:babbel` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `teamtailor:babbel` | 0 | 404 | 536 | HTTP 404 |
| ❓ not_found | `greenhouse:busuu` | 0 | 404 | 22 | HTTP 404 |
| ❓ not_found | `recruitee:lingoda` | 0 | 404 | 250 | HTTP 404 |
| ❓ not_found | `teamtailor:lingoda` | 0 | 404 | 534 | HTTP 404 |
| ❓ not_found | `greenhouse:cambly` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `lever:cambly` | 0 | 404 | 683 | HTTP 404 |
| ❓ not_found | `recruitee:novakid` | 0 | 404 | 150 | HTTP 404 |
| ❓ not_found | `workable:novakid` | 0 | 404 | 26 | HTTP 404 |
| ❓ not_found | `greenhouse:openenglish` | 0 | 404 | 25 | HTTP 404 |
| ❓ not_found | `greenhouse:engoo` | 0 | 404 | 19 | HTTP 404 |
| ❓ not_found | `workable:abwaab` | 0 | 404 | 27 | HTTP 404 |
| ❓ not_found | `lever:noonacademy` | 0 | 404 | 87 | HTTP 404 |
| ❓ not_found | `html:edraak-careers` | 0 | 404 | 292 | HTTP 404 |

## ats-mena  <sub>ok 1 · empty 0 · blocked 0 · not_found 4 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `workable:tamatem` | 22 | 200 | 56 | Business Development/ Sales Executive - EMEA ; Community & Partnerships Manager; Community & Partnerships Manager |
| ❓ not_found | `lever:anghami` | 0 | 404 | 120 | HTTP 404 |
| ❓ not_found | `recruitee:tamatem` | 0 | 404 | 257 | HTTP 404 |
| ❓ not_found | `html:mawdoo3-careers` | 0 | 404 | 238 | HTTP 404 |
| ❓ not_found | `workable:sarwa` | 0 | 404 | 26 | HTTP 404 |

## remote-boards  <sub>ok 3 · empty 1 · blocked 4 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:remowork-arabic` | 203 | 200 | 622 | Jobs; Job Tracker; Browse Job Categories |
| ✅ ok | `json:remote1stjobs` | 50 | 200 | 1535 | Sales Development Representative, Early Stage; Director of Product, Governance & Compliance; Bilingual Content Creator, Khan Academy Kids  |
| ✅ ok | `html:jobgether` | 6 | 200 | 225 | Job  Search  Tips; Jobseekers guide; Review Jobgether &nbsp;→ |
| ⚪ empty | `html:dynamitejobs` | 0 | 200 | 3423 | 79755 bytes, text/html |
| ⛔ blocked | `rss:euremotejobs` | 0 | 403 | 199 | HTTP 403 |
| ⛔ blocked | `rss:remotejobleads` | 0 | 403 | 105 | HTTP 403 + challenge page |
| ⛔ blocked | `html:dailyremote` | 0 | 403 | 98 | HTTP 403 + challenge page |
| ⛔ blocked | `html:europeremotely` | 0 | 403 | 438 | HTTP 403 |
| 💥 error | `html:remote-co` | 0 |  | 15039 | timeout >15s |

## translation-boards  <sub>ok 1 · empty 1 · blocked 2 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:translationdirectory` | 2 | 200 | 1906 | Need More Linguistic Jobs?; Do you work for these translation agencies?  |
| ⚪ empty | `html:gotranscript` | 0 | 200 | 158 | 434087 bytes, text/html |
| ⛔ blocked | `html:proz-translation-jobs` | 0 | 403 | 35 | HTTP 403 + challenge page |
| ⛔ blocked | `html:translatorscafe` | 0 | 403 | 372 | HTTP 403 |

## un-ngo  <sub>ok 3 · empty 0 · blocked 1 · not_found 0 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:untalent-arabic` | 206 | 200 | 1611 | Openings; Search; FHI 360 |
| ✅ ok | `html:impactpool-arabic` | 14 | 200 | 844 | Interpreter – Arabic/Sudanese Arabic


IRC - ; Communications Specialist -Communications and; HR Intern


UNOPS - United Nations Office for |
| ✅ ok | `html:idealist-arabic` | 8 | 200 | 211 | Find a Job; Jobs; Communications |
| ⛔ blocked | `html:unjobs-translation` | 0 | 403 | 23 | HTTP 403 + challenge page |

## mena-boards  <sub>ok 1 · empty 0 · blocked 6 · not_found 0 · needs_key 0 · error 1</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `html:akhtaboot-translator` | 4 | 200 | 1739 | Jobs in Jordan (52); Jobs in Saudi Arabia (4); Jobs in UAE (1) |
| ⛔ blocked | `html:bayt-translator` | 0 | 403 | 125 | HTTP 403 + challenge page |
| ⛔ blocked | `html:wuzzuf-translator` | 0 | 403 | 49 | HTTP 403 + challenge page |
| ⛔ blocked | `html:gulftalent-translator` | 0 | 403 | 181 | HTTP 403 + challenge page |
| ⛔ blocked | `html:tanqeeb-translator` | 0 | 403 | 210 | HTTP 403 |
| ⛔ blocked | `html:mostaql-writing-translation` | 0 | 403 | 301 | HTTP 403 |
| ⛔ blocked | `html:ureed-translation` | 0 | 403 | 101 | HTTP 403 + challenge page |
| 💥 error | `html:naukrigulf-translator` | 0 |  | 15723 | timeout >15s |

## academic-editing-watchers  <sub>ok 1 · empty 0 · blocked 1 · not_found 1 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ✅ ok | `watch:cactus` | 18 | 200 | 1944 | Employer Brand Promise; Life at CACTUS; Open Positions |
| ⛔ blocked | `watch:scribbr` | 0 | 403 | 105 | HTTP 403 + challenge page |
| ❓ not_found | `watch:scribendi` | 0 | 404 | 177 | HTTP 404 |

## ats-new  <sub>ok 0 · empty 3 · blocked 6 · not_found 9 · needs_key 0 · error 0</sub>

| status | id | items | http | ms | sample / detail |
|---|---|---:|---:|---:|---|
| ⚪ empty | `bamboohr:nagwa` | 0 | 200 | 253 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:abwaab` | 0 | 200 | 120 | 45560 bytes, text/html |
| ⚪ empty | `bamboohr:noonacademy` | 0 | 200 | 194 | 45560 bytes, text/html |
| ⛔ blocked | `jobvite:telus` | 0 | 403 | 351 | HTTP 403 |
| ⛔ blocked | `jobvite:concentrix` | 0 | 403 | 221 | HTTP 403 |
| ⛔ blocked | `jobvite:teleperformance` | 0 | 403 | 166 | HTTP 403 |
| ⛔ blocked | `personio:appen` | 0 | 429 | 771 | HTTP 429 |
| ⛔ blocked | `personio:centific` | 0 | 429 | 694 | HTTP 429 |
| ⛔ blocked | `personio:surgeai` | 0 | 429 | 722 | HTTP 429 |
| ❓ not_found | `breezy:tarjama` | 0 | 404 | 415 | HTTP 404 |
| ❓ not_found | `breezy:saudisoft` | 0 | 404 | 247 | HTTP 404 |
| ❓ not_found | `breezy:careem` | 0 | 404 | 339 | HTTP 404 |
| ❓ not_found | `pinpoint:edraak` | 0 | 404 | 371 | HTTP 404 |
| ❓ not_found | `pinpoint:almentor` | 0 | 404 | 451 | HTTP 404 |
| ❓ not_found | `pinpoint:baims` | 0 | 404 | 326 | HTTP 404 |
| ❓ not_found | `rippling:deel` | 0 | 404 | 315 | HTTP 404 |
| ❓ not_found | `rippling:remote` | 0 | 404 | 340 | HTTP 404 |
| ❓ not_found | `rippling:oyster` | 0 | 404 | 245 | HTTP 404 |

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
    ("Keywords Studios", "KeywordsStudios"),   # 45 jobs
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
