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
        ("ESL Instructor",
         "TESOL certified English teacher for Arabic speakers. Remote worldwide.",
         "Remote worldwide"),
        ("English Teacher Online",
         "Teach English as a second language TESOL. Remote worldwide.",
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


def main():
    print("QUALITY GATES — deep offline verification")
    test_true_positives()
    test_false_positives()
    test_location_and_stubs()
    test_replay_history()
    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
