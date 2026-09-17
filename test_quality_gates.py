"""
Offline quality gates — the three promises:
  1. Scorer does not 100% Twilio pricing / Hindi / Spanish / platform-admin
  2. Stub pages (portal, get started, quote) never qualify
  3. AI location FAIL and Remote-US never notify

Also replays production fresh_matches_history.json when present.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scanner import (
    MIN_MATCH_SCORE,
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
        ("Virtual Assistant",
         "Data entry and administrative support. Remote worldwide.",
         "Remote (Worldwide)"),
        ("Localization Specialist Arabic",
         "Arabic localization specialist for MENA. Language localization, l10n.",
         "Remote"),
        ("Data Entry Clerk",
         "Remote data entry. Work from anywhere worldwide. No country restriction.",
         "Remote worldwide"),
    ]
    for title, desc, loc in cases:
        sc = get_match_score(title, desc)
        ok = would_notify(title, desc, loc)
        check(f"{title} → notify (score={sc['score']} {sc['category']})", ok,
              f"score={sc} worldwide={is_open_worldwide(loc, desc)}")


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

    # Country-locked remotes must not reach the notify list. Every one of these
    # arrived as a 100% STRONG MATCH on 2026-09-16 despite being untakeable.
    country_locked = [
        ("Localization Specialist (Traductor/a)", "Remote — Valladolid, Spain"),
        ("Copy Editor / Senior Copy Editor (NY)", "Remote — New York, NY"),
        ("Copy Editor", "Remote — Princeton, NJ"),
        ("Copy Editor", "Remote — Rogers, AR"),
        ("Senior Copy Editor (Financial Content)", "Remote — Mexico City, Mexico"),
        ("Copy Editor", "Remote — Celina, OH"),
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

    # The 2026-09-16 leak came from substring matching: "remote" was in
    # ALLOWED_LOCATIONS, so "Remote — <anywhere>" short-circuited to True.
    for trap in ("Remote — Valladolid, Spain", "Remote — Berlin, Germany",
                 "Remote — Kuala Lumpur, Malaysia", "Remote — Dublin, Ireland"):
        check(f"{trap} is country-locked", not is_open_worldwide(trap, ""))

    # Word boundaries: these must not be matched by neighbouring substrings.
    for trap in ("Remote — Oman", "Remote — Morocco", "Remote — Cairo, Egypt"):
        check(f"MENA kept: {trap}", is_open_worldwide(trap, ""))
    check("'any' does not match inside Germany", not is_open_worldwide("Remote — Germany", ""))
    check("'asia' does not match inside Malaysia", not is_open_worldwide("Remote — Malaysia", ""))
    check("'us' does not match inside Russia", not is_open_worldwide("Remote — Russia", ""))

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


def test_ollama_pipeline():
    """Ollama analysis against a real local HTTP server (no network/model needed).

    Guards the silent-failure modes: prose-wrapped JSON, a response that ignores
    format=json, and the `format: json` / fallback-model retry wiring.
    """
    print("\n=== Ollama analyzer (fake server round-trip) ===")
    import asyncio
    from aiohttp import web
    import ollama_analyzer as OA

    seen = []

    async def tags(_request):
        return web.json_response({"models": [
            {"name": OA.MODEL, "model": OA.MODEL},
            {"name": "test-fallback", "model": "test-fallback"},
        ]})

    async def gen(request):
        body = await request.json()
        seen.append(body)
        # Primary model returns prose; the fallback must rescue the parse.
        if body["model"] == OA.MODEL:
            return web.json_response({"response": "Here is my assessment: definitely not JSON"})
        return web.json_response({"response": json.dumps({
            "overall_score": 91, "verdict": "Strong Fit", "one_line_summary": "ok",
        })})

    orig_url, orig_fallback = OA.OLLAMA_URL, OA.FALLBACK_MODEL
    OA.FALLBACK_MODEL = "test-fallback"

    async def run():
        app = web.Application()
        app.router.add_get("/api/tags", tags)
        app.router.add_post("/api/generate", gen)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "127.0.0.1", 11437).start()
        OA.OLLAMA_URL = "http://127.0.0.1:11437"
        try:
            out = await OA.analyze_jobs_with_ollama([
                {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
            ])
            return out[0]
        finally:
            await runner.cleanup()

    try:
        job = asyncio.run(run())
    finally:
        OA.OLLAMA_URL, OA.FALLBACK_MODEL = orig_url, orig_fallback

    check("analyzer records the AI verdict", job.get("ai_verdict") == "Strong Fit", str(job.get("ai_verdict")))
    check("analyzer records the AI score", job.get("ai_overall_score") == 91)
    check("every request asks for JSON output", all(b.get("format") == "json" for b in seen))
    check("falls back to the smaller model on parse failure",
          [b["model"] for b in seen] == [OA.MODEL, "test-fallback"], str([b["model"] for b in seen]))

    # When the fallback tag is not installed, retry must stay on the primary
    # model instead of 404-ing on a tag CI never pulled.
    seen.clear()
    OA.FALLBACK_MODEL = "not-installed"

    async def run2():
        app = web.Application()
        app.router.add_get("/api/tags", tags)
        app.router.add_post("/api/generate", gen)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "127.0.0.1", 11438).start()
        OA.OLLAMA_URL = "http://127.0.0.1:11438"
        try:
            out = await OA.analyze_jobs_with_ollama([
                {"title": "Arabic Translator", "company": "X", "description": "d", "location": "Remote"},
            ])
            return out[0]
        finally:
            await runner.cleanup()

    try:
        asyncio.run(run2())
    finally:
        OA.OLLAMA_URL, OA.FALLBACK_MODEL = orig_url, orig_fallback
    check("missing fallback tag falls back to the primary model",
          [b["model"] for b in seen] == [OA.MODEL, OA.MODEL], str([b["model"] for b in seen]))


def main():
    print("QUALITY GATES — deep offline verification")
    test_true_positives()
    test_false_positives()
    test_location_and_stubs()
    test_digest_regressions()
    test_ollama_pipeline()
    test_replay_history()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
