"""
Offline quality gates — the three promises:
  1. Scorer does not 100% Twilio pricing / Hindi / Spanish / platform-admin
  2. Stub pages (portal, get started, quote) never qualify
  3. AI location FAIL and Remote-US never notify

Also replays production fresh_matches_history.json when present.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scanner import (
    MIN_MATCH_SCORE,
    ai_poor_fit,
    drop_unqualified_matches,
    get_match_score,
    is_in_person_gig,
    is_open_worldwide,
    is_stub_listing,
    location_ai_fail,
    matches_negative,
    matches_positive,
)

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [OK] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def would_notify(title, desc, loc="Remote", extra=None) -> bool:
    job = {
        "title": title,
        "description": desc,
        "location": loc,
        "url": "https://example.com/job/1",
        **(extra or {}),
    }
    if is_stub_listing(job) or is_in_person_gig(job):
        return False
    if not is_open_worldwide(loc, desc):
        return False
    if matches_negative(title, desc):
        return False
    if not matches_positive(title, desc):
        return False
    sc = get_match_score(title, desc)
    if sc["score"] < MIN_MATCH_SCORE:
        return False
    job["score"] = sc["score"]
    job["category"] = sc["category"]
    kept = drop_unqualified_matches([job])
    return len(kept) == 1


def test_true_positives():
    print("\n=== True positives (must still notify) ===")
    cases = [
        ("Arabic Translator (Remote Worldwide)",
         "Legal Arabic-English translation. Fully remote, work from anywhere.",
         "Remote"),
        ("Arabic-English Translator",
         "Legal Arabic-English translation for MENA clients. Fully remote worldwide.",
         "Remote worldwide"),
        ("Freelance Translator (Arabic)",
         "Arabic to English translation and proofreading. Work from anywhere.",
         "Remote"),
("Localization Specialist Arabic",
          "Arabic localization specialist for MENA. Language localization, l10n.",
          "Remote"),
    ]
    for title, desc, loc in cases:
        sc = get_match_score(title, desc)
        ok = would_notify(title, desc, loc)
        check(f"{title} → notify (score={sc['score']} {sc['category']})", ok,
              f"score={sc} worldwide={is_open_worldwide(loc, desc)}")


def test_strict_secondary_categories():
    print("\n=== Strict: secondary / Arabic-adjacent-but-not-translation = REVIEW only ===")
    cases = [
        ("Virtual Assistant",
         "Data entry and administrative support. Remote worldwide.",
         "Remote (Worldwide)"),
        ("Data Entry Clerk",
         "Remote data entry. Work from anywhere worldwide. No country restriction.",
         "Remote worldwide"),
        ("Data Entry - Arabic Speaker",
         "Arabic-speaking data entry clerk for document processing. Remote.",
         "Remote (Worldwide)"),
        ("Proofreader - Arabic",
         "Review and proofread Arabic translations for accuracy. Remote.",
         "Remote (Worldwide)"),
        ("Arabic (Egyptian) Language Expert - Freelance AI Trainer Project",
         "Egyptian Arabic linguistic data for AI training. Native Arabic required. Remote.",
         "Remote (Worldwide)"),
        ("Arabic Voice Actor - Freelance AI Trainer Project",
         "Arabic voice recording for AI training data. Native Arabic speaker. Remote.",
         "Remote (Worldwide)"),
        ("English Language Specialist - Freelance AI Trainer Project",
         "English linguistic data for AI training. Remote worldwide.",
         "Remote (Worldwide)"),
        ("Arabic/English speaking Content Moderator",
         "Moderate user-generated content. Arabic and English fluent required. Remote.",
         "Remote (Worldwide)"),
        ("Virtual Assistant - Arabic/English",
         "Bilingual VA: scheduling, email, data entry in Arabic and English. Remote.",
         "Remote (Worldwide)"),
    ]
    for title, desc, loc in cases:
        sc = get_match_score(title, desc)
        ok = (not would_notify(title, desc, loc)) and sc["score"] < MIN_MATCH_SCORE
        check(f"{title} → REVIEW only (score={sc['score']} {sc['category']})", ok,
              f"score={sc} worldwide={is_open_worldwide(loc, desc)}")


def test_email_regression():
    """2026-09-19 scan — only the Legal Translator must stay; the other four
    NEW matches (IRIS² engineer, Copywriter, AR Specialist, Ashby CSM) must
    never reach the digest again. Also verifies the purge keeps the good old
    matches."""
    print("\n=== 2026-09-19 email regression (only Legal Translator survives) ===")
    good = [
        ("Legal Translator", "A&O Shearman", "Remote — Dubai, Dubai, United Arab Emirates",
         "Legal Translator. Arabic English legal translation of contracts and court documents."),
        ("Construction Translator / Interpreter", "SISK Group", "Remote",
         "Construction translator and interpreter for site coordination. Arabic-English."),
        ("Localisation Specialist - Arabic to English", "Revolut", "Remote",
         "Localise our app content from English to Arabic. Bilingual Arabic-English."),
        ("Interpreter (Arabic and English)", "IOM", "Remote",
         "Arabic-English interpreting and translation for field missions."),
    ]
    bad = [
        ("IRIS² Lead Ground Segment Service Engineer", "untalent_arabic", "Remote",
         "IRIS2 Lead Ground Segment Service Engineer at ESA. The IRIS² satellite constellation ground segment service."),
        ("Translator (Zeekr)", "Zeekr International", "Remote — Tanjong Malim, Perak, Malaysia",
         "Trilingual Translation & Business Support Specialist (Chinese / Malay / English). Chinese-Malay-English written and oral translation, on-site interpretation, localized content optimization for our Malaysia operations."),
        ("Translator (Generic)", "QIMA", "Remote",
         "Translate product inspection reports and client correspondence. Remote."),
        ("Translator (English-only snippet)", "Talent Ferry", "Remote",
         "Translate materials for our international team. Remote."),
        ("Conceptual Copywriter", "Superside", "Anywhere, Remote",
         "Superside is looking for a talented Conceptual Copywriter to ideate and execute impactful creative work. You will help translate complex technical ideas into campaigns."),
        ("AR Specialist Contractor", "Stride", "US Nationwide - Remote",
         "MedCerts is a national online career training school. HD-quality video-based instruction, virtual simulation."),
        ("Mid-Market Customer Success Manager - EMEA", "Ashby", "Remote - European Union",
         "Hiring our next CSM in EMEA to shape services for the mid-market segment."),
    ]
    for title, company, loc, desc in good:
        sc = get_match_score(title, desc)
        ok = would_notify(title, desc, loc, {"company": company}) and sc["score"] >= MIN_MATCH_SCORE
        check(f"KEEP {title[:45]} (score={sc['score']} {sc['category']})", ok,
              f"score={sc}")
    for title, company, loc, desc in bad:
        sc = get_match_score(title, desc)
        ok = (not would_notify(title, desc, loc, {"company": company})
              or ai_poor_fit({"ai_verdict": "Poor Fit", "ai_overall_score": 39}))
        check(f"DROP {title[:45]} (score={sc['score']} {sc['category']})", ok,
              f"score={sc}")
    # A "Translator" whose language pair is invisible must never be STRONG.
    sc_bare = get_match_score("Translator", "")
    check("Bare 'Translator' (no language info) is never STRONG",
          sc_bare["score"] < 75, f"score={sc_bare}")


def test_false_positives():
    print("\n=== False positives (must NOT notify) ===")
    cases = [
        ("Principal Price Realization Strategy Manager",
         "Global Pricing & Localization. Translate complex pricing concepts into narratives.",
         "Remote - US"),
        ("Senior Impartner Admin, PRM",
         "Impartner PRM Salesforce admin. Localized multi-lingual partner portals.",
         "Remote - Canada"),
        ("Data Entry Clerk",
         "Location: United States Only. Must currently reside in the United States. "
         "Location Restriction: United States only. Candidates outside the United States are not eligible.",
         ""),
        ("Hindi content writing",
         "skilled Hindi writer. Proofreading, Editing, Content Writing, Copywriting",
         "Remote (Worldwide)"),
        ("Psychiatrist Appointment Translation",
         "English to Spanish translator. Medical Translation. Castilian Spanish.",
         "Remote (Worldwide)"),
        ("Cebuano Language Specialist - Freelance AI Trainer Project",
         "Cebuano linguistic data collection and evaluation for AI model training. Remote worldwide.",
         "Remote (Worldwide)"),
        ("Guaraní Language Expert - Freelance AI Trainer Project",
         "Write and rate Guaraní prompts. Native Guaraní fluency required.",
         "Remote (Worldwide)"),
        ("Māori Language Specialist - Freelance AI Trainer Project",
         "Māori speech and text data annotation. Remote worldwide.",
         "Remote (Worldwide)"),
        ("K'iche' (Mayan) Language Specialist - Freelance AI Trainer Project",
         "K'iche' linguistic data for AI. Remote.",
         "Remote (Worldwide)"),
        ("Freelance Translator - Turkmen (Turkmenistan)",
         "Translate documents into Turkmen. Remote worldwide.",
         "Remote (Worldwide)"),
        ("Teacher's Portal",
         "English teaching platform",
         "Remote (Worldwide)"),
        ("Get Started",
         "English tutoring platform for native speakers",
         "Remote (Worldwide)"),
        ("Translator - Request a Quote",
         "Professional translation platform",
         "Remote (Worldwide)"),
        ("Mystery shopping CDMX",
         "pedir una cotización de manera presencial. Virtual Assistant, Local Job",
         "Remote (Worldwide)"),
        ("Marketing Manager, Arabic Speaker - Freelancer, 12 month contract",
         "Drive marketing campaigns for the Arabic market. Native Arabic speaker preferred.", 
         "Remote (Worldwide)"),
    ]
    for title, desc, loc in cases:
        ok = not would_notify(title, desc, loc)
        sc = get_match_score(title, desc)
        check(f"DROP {title[:50]} (score={sc['score']} {sc['category']})", ok,
              f"would_notify=True score={sc}")


def test_location_and_stubs():
    print("\n=== Location + stub helpers ===")
    check("Remote worldwide OK", is_open_worldwide("Remote", "Work from anywhere worldwide"))
    check("Remote - US blocked", not is_open_worldwide("Remote - US", "Remote first company"))
    check("Remote - Canada blocked", not is_open_worldwide("Remote - Canada", "Based in Ontario"))
    check("US-only desc blocked", not is_open_worldwide(
        "", "Location Restriction: United States only. Must reside in the United States."))
    check("portal is stub", is_stub_listing({
        "title": "Teacher's Portal", "url": "https://teacher.qkids.com",
        "description": "English teaching platform",
    }))
    check("get started is stub", is_stub_listing({
        "title": "Get Started", "url": "https://www.cambly.com/onboarding?accountTypes=tutorsignup-en",
        "description": "English tutoring platform for native speakers",
    }))
    check("quote page is stub", is_stub_listing({
        "title": "Translator - Request a Quote",
        "url": "https://www.acolad.com/en/services/translation/estimate?utm_source=textmaster",
        "description": "Professional translation platform",
    }))
    check("CDATA title is stub", is_stub_listing({
        "title": "<![CDATA[Hindi content writing ]]>",
        "url": "https://www.freelancer.com/projects/x",
        "description": "writer",
    }))
    check("presencial is in-person", is_in_person_gig({
        "title": "CDMX", "description": "manera presencial", "location": "Remote",
        "url": "https://x",
    }))
    check("AI FAIL detected", location_ai_fail({"ai_location_verdict": "FAIL"}))
    kept = drop_unqualified_matches([{
        "title": "Arabic Translator",
        "description": "Arabic-English legal translation remote worldwide",
        "location": "Remote",
        "url": "https://example.com/real",
        "ai_location_verdict": "FAIL",
    }])
    check("AI FAIL hard-drops notify list", kept == [])


def test_linkedin_remote_truthfulness():
    print("\n=== LinkedIn remote truthfulness (no fake Remote claims) ===")
    from fetchers.verified import _linkedin_location, _workplace_infer
    from scanner import _ONSITE_ANCHOR, is_open_worldwide_for_company

    loc = _linkedin_location("Baltimore, Maryland, United States", "On-site", "", True)
    check("On-site tag wins over f_WT=2", loc.startswith("On-site"), loc)
    loc = _linkedin_location("Abu Dhabi, United Arab Emirates", "Hybrid", "", True)
    check("Hybrid tag wins over f_WT=2", loc.startswith("Hybrid"), loc)
    loc = _linkedin_location("Dubai, United Arab Emirates", "Remote", "", True)
    check("Remote tag kept only when verified", loc.startswith("Remote"), loc)

    fisher = ("This is an in-office role. Based on your role, tenure, and performance "
              "eligibility you may have the opportunity to participate in our hybrid "
              "work from home program.")
    check("in-office description -> On-site", _workplace_infer(fisher) == "On-site", _workplace_infer(fisher))
    loc = _linkedin_location("Irving, TX", "", fisher, True)
    check("Fisher class never labelled Remote", loc.startswith("On-site"), loc)

    check("fully remote desc -> Remote",
          _workplace_infer("Fully remote position. Work from anywhere in the world.") == "Remote",
          "")
    check("hybrid desc -> Hybrid",
          _workplace_infer("Hybrid role - 3 days in office, 2 remote.") == "Hybrid",
          "")

    loc = _linkedin_location("Dubai, United Arab Emirates", "", "", False)
    check("unverified detail -> real city, NO Remote claim", loc == "Dubai, United Arab Emirates", loc)

    check("US-based candidates blocked", not is_open_worldwide(
        "Remote", "Posted pay ranges apply to US-based candidates."))
    check("US-based employees blocked", not is_open_worldwide(
        "Remote", "This role is open to US-based employees only."))
    check("only open to US blocked", not is_open_worldwide(
        "Remote", "Position only open to US candidates."))
    check("ONLY stress: US-based company remote worldwide still passes", is_open_worldwide(
        "Remote", "Join a US-based startup. Fully remote, we hire worldwide."))

    # Single-slot notifier: no phantom 18:00 delivery anywhere.
    from notifier import SCAN_LABELS, get_scan_label, next_scan_time
    check("exactly one daily slot", len(SCAN_LABELS) == 1, str(SCAN_LABELS))
    check("label is always Daily Digest", get_scan_label()["label"] == "Daily Digest",
          get_scan_label()["label"])
    ns = next_scan_time()
    check("next_scan_time is 09:00, never 18:00", "09:00" in ns and "18:00" not in ns, ns)

    # Workplace anchor: postings explicitly tied to an office must be dropped
    # even when the card says "Remote" — this is the Wasael/Fisher class that
    # re-entered the 2026-09-24 digest after the first fix shipped.
    fisher = ("Financial Arabic Translator. This is an in-office role. "
              "You may be eligible for our hybrid work from home program.")
    check("Fisher class: in-office role not worldwide", not is_open_worldwide(
        "Remote — Riyadh, Riyadh, Saudi Arabia", fisher))
    check("_ONSITE_ANCHOR fires on Fisher copy", bool(_ONSITE_ANCHOR.search(fisher)))
    wasael = ("Arabic Translator for the Department of Municipalities & Transportation. "
              "This is an on-site position; you must attend the office in Abu Dhabi.")
    check("Wasael class: on-site position not worldwide", not is_open_worldwide(
        "Remote — Abu Dhabi, Abu Dhabi Emirate, United Arab Emirates", wasael))
    check("_ONSITE_ANCHOR fires on Wasael copy", bool(_ONSITE_ANCHOR.search(wasael)))
    check("anchor survives for_company path", not is_open_worldwide_for_company(
        "Remote — Riyadh, Saudi Arabia", "This is an in-office role.", "Fisher Investments"))
    check("fully remote + occasional on-site visits still passes", is_open_worldwide(
        "Remote", "Fully remote. Occasional on-site visits to clients may be required."))
    check("hybrid-friendly copy alone does not drop a remote role", is_open_worldwide(
        "Remote — Berlin, Germany", "Remote-first team; hybrid-friendly company culture."))

    # Bare US metro under a remote tag = US-anchored (IRC class).
    check("bare Baltimore remote = US-anchored, blocked", not is_open_worldwide(
        "Remote | Baltimore", "IRC - International Rescue Committee"))
    check("bare Chicago remote = blocked", not is_open_worldwide(
        "Remote — Chicago", "Part-time interpreter"))
    check("Remote — New York, United States still blocked (country)", not is_open_worldwide(
        "Remote — New York, United States", ""))

    # Known office-bound companies are hard-blocked at every gate.
    check("known-onsite company Fisher hard-blocked", not is_open_worldwide_for_company(
        "Remote — Riyadh, Saudi Arabia", "In-house translation team.", "Fisher Investments"))
    check("known-onsite company Wasael hard-blocked", not is_open_worldwide_for_company(
        "Remote — Abu Dhabi, UAE", "Translate for the municipality.", "Wasael Property Management"))
    check("known-onsite company IRC hard-blocked", not is_open_worldwide_for_company(
        "Remote | Baltimore", "", "International Rescue Committee"))
    check("unrelated company unaffected by known-onsite list", is_open_worldwide_for_company(
        "Remote — Dubai, UAE", "Project management, hybrid.", "23 Studios"))


def test_replay_history():
    print("\n=== Replay production fresh_matches_history.json ===")
    path = Path(__file__).parent / "state" / "fresh_matches_history.json"
    if not path.exists():
        print("  [SKIP] no history file")
        return
    jobs = json.loads(path.read_text())
    print(f"  replay n={len(jobs)}")
    kept, dropped = [], []
    for j in jobs:
        title, desc, loc = j.get("title", ""), j.get("description", ""), j.get("location", "")
        extra = {
            "url": j.get("url", "https://example.com/x"),
            "ai_location_verdict": j.get("ai_location_verdict", ""),
            "ai_scoring": j.get("ai_scoring") or {},
        }
        if would_notify(title, desc, loc, extra):
            kept.append(j)
        else:
            dropped.append(j)
    print(f"  would keep {len(kept)} / drop {len(dropped)}")
    for j in dropped:
        print(f"    DROP [{j.get('score')}] {str(j.get('title', ''))[:70]}")
    for j in kept:
        print(f"    KEEP [{j.get('score')}] {str(j.get('title', ''))[:70]}")
    # Known junk from 2026-09-05 scan must be gone
    junk_needles = [
        "Price Realization",
        "Impartner",
        "Teacher's Portal",
        "Get Started",
        "Request a Quote",
        "Hindi content",
        "Psychiatrist Appointment",
        "presencial",
        "United States Only",
        "Astrek",
    ]
    kept_blob = " ".join(
        f"{k.get('title','')} {k.get('company','')} {k.get('description','')[:80]}"
        for k in kept
    )
    for needle in junk_needles:
        check(f"history no longer keeps {needle!r}", needle.lower() not in kept_blob.lower())


def test_digest_regressions():
    """Regressions from the 2026-09-16 digest that shipped broken cards."""
    print("\n=== Digest regressions (2026-09-16) ===")
    from scanner import _libya_today, get_company_website

    # Country-locked remotes must not reach the notify list. The 2026-09-16
    # leak was US/UK/Canada-market roles; those stay hard-dropped.
    country_locked = [
        ("Copy Editor / Senior Copy Editor (NY)", "Remote — New York, NY"),
        ("Copy Editor", "Remote — Princeton, NJ"),
        ("Copy Editor", "Remote — Rogers, AR"),
        ("Copy Editor", "Remote — Celina, OH"),
        ("Copy Editor", "Remote — US"),
        ("Copy Editor", "Remote — Canada"),
        ("Copy Editor", "Remote — United Kingdom"),
    ]
    survivors = drop_unqualified_matches([
        {"title": t, "description": "localization copy editor remote freelance",
         "location": l, "url": f"https://example.com/{i}"}
        for i, (t, l) in enumerate(country_locked)
    ])
    check("country-locked remotes hard-dropped", survivors == [],
          f"leaked {[j['location'] for j in survivors]}")

    check("Dubai remote still accepted (MENA-friendly)",
          is_open_worldwide("Remote — Dubai, United Arab Emirates", ""))
    check("plain worldwide remote still accepted", is_open_worldwide("Remote", ""))

    # Policy (Fix 3, 2026-09-17): a bare country after "Remote" is a timezone
    # hint, not a residency lock, so these are accepted. Explicit residency /
    # work-authorisation wording in the description is still hard-blocked.
    for allowed in ("Remote — Valladolid, Spain", "Remote — Berlin, Germany",
                    "Remote — Kuala Lumpur, Malaysia", "Remote — Dublin, Ireland"):
        check(f"{allowed} accepted as remote", is_open_worldwide(allowed, ""))

    # Word boundaries: place names must not be matched by neighbouring
    # substrings ("any" in Germany, "asia" in Malaysia, "us" in Russia).
    from scanner import ALLOWED_LOCATION_RE, BLOCKED_COUNTRY_RE
    check("'any' does not match inside Germany", not ALLOWED_LOCATION_RE.search("germany"))
    check("'asia' does not match inside Malaysia", not ALLOWED_LOCATION_RE.search("malaysia"))
    check("'us' does not match inside Russia", not BLOCKED_COUNTRY_RE.search("russia"))

    # MENA remotes stay accepted.
    for trap in ("Remote — Oman", "Remote — Morocco", "Remote — Cairo, Egypt"):
        check(f"MENA kept: {trap}", is_open_worldwide(trap, ""))

    # Fabricated URLs: "IRC - International Rescue Committee" mangled to
    # "irc-internationalrescuemmittee.com" by mid-word ' co' stripping.
    check("unknown company gets no guessed website",
          get_company_website("IRC - International Rescue Committee") == "")
    check("mangled website no longer generated",
          "mmittee" not in get_company_website("International Criminal Court"))
    check("known company still resolves", get_company_website("TransPerfect") != "")

    # "msa" is an acronym, not always Modern Standard Arabic.
    check("bare 'MSA' no longer scores a marine surveyor",
          get_match_score(
              "Surveyor I",
              "conventional surveying practices, vessels and marine structures, MSA safety training",
          )["score"] == 0)
    check("MSA with Arabic context still matches",
          get_match_score("Arabic Translator", "Modern Standard Arabic (MSA) required")["score"] >= 75)

    # "Why this fits" must not leak raw regex quantifiers.
    why = " ".join(get_match_score(
        "Freelance Translator", "ICC freelance translation")["why"])
    check("no '.{0,40}' artifact in why text", ".{" not in why, why)

    # Digest date is Libya local (UTC+2), never raw UTC. Compare against the
    # UTC calendar day so a run between 22:00-24:00 UTC proves the offset.
    from datetime import datetime, timezone, timedelta
    libya_day = _libya_today()
    utc_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    check("digest date is a valid ISO day", len(libya_day) == 10 and libya_day[4] == "-")
    check("digest date is Libya (>=) UTC day", libya_day >= utc_day,
          f"libya={libya_day} utc={utc_day}")


def test_ai_pipeline():
    """Groq AI analysis with mocked SDK calls.

    Guards the silent-failure modes: prose-wrapped JSON, missing API key,
    and the retry wiring.
    """
    print("\n=== Groq AI analyzer (mocked round-trip) ===")
    import asyncio
    from unittest.mock import patch, MagicMock
    import groq_analyzer as GA

    def make_mock_response(content):
        mock = MagicMock()
        mock.choices = [MagicMock()]
        mock.choices[0].message.content = content
        return mock

    # Test 1: Missing API key — jobs returned unchanged
    with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=False):
        out = asyncio.run(GA.analyze_jobs_with_ollama([
            {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
        ]))
        check("missing API key returns jobs unchanged",
              "ai_overall_score" not in out[0],
              str(out[0].get("ai_overall_score")))

    # Test 2: Valid response → 5D scoring
    valid_json = json.dumps({
        "overall_score": 91, "verdict": "Strong Fit",
        "one_line_summary": "Great fit",
        "technical_skills": {"score": 90, "reason": "exact match"},
        "experience_match": {"score": 85, "reason": "relevant"},
        "behavioral_fit": {"score": 95, "reason": "remote"},
        "location_logistics": {"verdict": "PASS", "reason": "worldwide"},
        "career_alignment": {"score": 92, "reason": "aligned"},
        "strengths": ["Arabic"], "gaps": [],
        "recommendation": "Apply", "interview_prep": "Q1?",
    })

    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=False), \
         patch.object(GA, "Groq") as MockGroq:
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response(valid_json)

        out = asyncio.run(GA.analyze_jobs_with_ollama([
            {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
        ]))

    check("analyzer records the AI verdict", out[0].get("ai_verdict") == "Strong Fit", str(out[0].get("ai_verdict")))
    check("analyzer records the AI score", out[0].get("ai_overall_score") == 91)

    # Test 3: Prose-wrapped JSON → fallback parse must still find it
    prose_response = "Here is my assessment:\n" + valid_json + "\nDone."
    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=False), \
         patch.object(GA, "Groq") as MockGroq:
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        mock_client.chat.completions.create.return_value = make_mock_response(prose_response)

        out = asyncio.run(GA.analyze_jobs_with_ollama([
            {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
        ]))

    check("prose-wrapped JSON still parsed",
          out[0].get("ai_overall_score") == 91)

    # Test 4: Non-JSON response → retry on second call, then simple insight
    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=False), \
         patch.object(GA, "Groq") as MockGroq:
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = [
            make_mock_response("Here is my assessment: definitely not JSON"),
            make_mock_response(valid_json),
        ]

        out = asyncio.run(GA.analyze_jobs_with_ollama([
            {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
        ]))

    check("retry with valid JSON on second call",
          out[0].get("ai_overall_score") == 91)

    # Test 5: API error → graceful fallback, jobs unchanged
    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=False), \
         patch.object(GA, "Groq") as MockGroq:
        mock_client = MagicMock()
        MockGroq.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "Connection failed"
        )

        out = asyncio.run(GA.analyze_jobs_with_ollama([
            {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
        ]))

    check("API error returns jobs unchanged",
          "ai_overall_score" not in out[0],
          str(out[0].get("ai_overall_score") if out else None))

    # Test 6: Retry budget fits 360min workflow timeout
    AI_ANALYZE_CAP = 3
    retry_attempts = 3  # max_retries=2 -> 3 total attempts per call
    max_seconds_per_call = 60  # Groq is fast, but generous
    worst_job_s = max_seconds_per_call * retry_attempts * AI_ANALYZE_CAP
    check("worst-case AI time fits the 360min workflow timeout",
          worst_job_s < 360 * 60,
          f"worst case {worst_job_s / 60:.0f}min")


def main():
    print("QUALITY GATES — deep offline verification")
    test_true_positives()
    test_strict_secondary_categories()
    test_email_regression()
    test_false_positives()
    test_location_and_stubs()
    test_linkedin_remote_truthfulness()
    test_digest_regressions()
    test_ai_pipeline()
    test_replay_history()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
