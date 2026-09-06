"""
Comprehensive test for all new CareerOps modules
Tests: learning_module, company_research, interview_prep, cover_letter_generator
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_learning_module():
    """Test learning module functionality."""
    print("=" * 60)
    print("TEST 1: Learning Module")
    print("=" * 60)
    
    from learning_module import (
        load_learning_data, save_learning_data, record_application,
        adjust_scoring_based_on_learning, get_learning_insights
    )
    
    # Test 1: Load empty data
    data = load_learning_data()
    assert "applied_jobs" in data, "Missing applied_jobs key"
    assert "rejected_jobs" in data, "Missing rejected_jobs key"
    assert "skill_preferences" in data, "Missing skill_preferences key"
    print("[OK] Load empty data")
    
    # Test 2: Record application
    test_job = {
        "url": "https://test.com/job/123",
        "title": "ESL Teacher",
        "company": "Test School",
        "score": 85,
        "category": "Teaching",
        "source": "test",
        "ai_overall_score": 80,
        "ai_verdict": "Good match"
    }
    record_application("https://test.com/job/123", test_job, "applied")
    
    # Test 3: Verify recording
    data = load_learning_data()
    assert len(data["applied_jobs"]) == 1, "Application not recorded"
    assert data["applied_jobs"][0]["title"] == "ESL Teacher", "Wrong job recorded"
    assert data["skill_preferences"].get("Teaching", 0) == 1, "Skill preference not updated"
    print("[OK] Record application")
    
    # Test 4: Adjust scoring
    test_job2 = {
        "url": "https://test.com/job/456",
        "title": "ESL Teacher",
        "company": "Another School",
        "score": 80,
        "category": "Teaching",
        "ai_overall_score": 75,
    }
    adjusted = adjust_scoring_based_on_learning(test_job2)
    assert adjusted > 75, f"Score should be boosted above 75, got {adjusted}"
    print(f"[OK] Score adjustment: {test_job2['ai_overall_score']} -> {adjusted}")
    
    # Test 5: Get insights
    insights = get_learning_insights()
    assert "top_skills" in insights, "Missing top_skills"
    assert "acceptance_rate" in insights, "Missing acceptance_rate"
    print(f"[OK] Insights: {insights['total_applied']} applied, {insights['acceptance_rate']}% acceptance")
    
    print("[PASS] Learning Module: ALL TESTS PASSED\n")
    return True


def test_company_research():
    """Test company research module."""
    print("=" * 60)
    print("TEST 2: Company Research")
    print("=" * 60)
    
    from company_research import (
        get_company_research, should_boost_score, get_company_summary,
        research_companies_batch
    )
    
    # Test 1: Research legitimate company
    research = get_company_research("Greenhouse", "https://boards.greenhouse.io/test")
    assert research["legitimacy_score"] > 50, "Legitimate company should score > 50"
    assert "Uses professional ATS" in research["positive_signals"], "Should detect ATS"
    print(f"[OK] Greenhouse legitimacy: {research['legitimacy_score']}")
    print(f"  Positive signals: {research['positive_signals']}")
    
    # Test 2: Research freelance platform
    research2 = get_company_research("Freelancer", "https://www.freelancer.com/job/123")
    assert research2["legitimacy_score"] < 50, "Freelance platform should score < 50"
    print(f"[OK] Freelancer legitimacy: {research2['legitimacy_score']}")
    
    # Test 3: Score adjustment
    boost = should_boost_score(research)
    assert boost > 0, "Legitimate company should get boost"
    print(f"[OK] Score boost for legitimate: +{boost}")
    
    # Test 4: Company summary
    summary = get_company_summary("Greenhouse", research)
    assert len(summary) > 0, "Summary should not be empty"
    print(f"[OK] Summary: {summary}")
    
    # Test 5: Batch research
    test_jobs = [
        {"company": "RemoteOK", "url": "https://remoteok.com/job/1", "score": 80},
        {"company": "Upwork", "url": "https://upwork.com/freelance/1", "score": 75},
    ]
    researched = research_companies_batch(test_jobs)
    assert len(researched) == 2, "Should research all jobs"
    assert "company_research" in researched[0], "Should add company_research field"
    print(f"[OK] Batch research: {len(researched)} jobs enriched")
    
    print("[PASS] Company Research: ALL TESTS PASSED\n")
    return True


def test_interview_prep():
    """Test interview preparation module."""
    print("=" * 60)
    print("TEST 3: Interview Preparation")
    print("=" * 60)
    
    from interview_prep import (
        generate_interview_questions, save_interview_prep,
        generate_interview_prep_for_top_matches, get_interview_prep_summary
    )
    
    # Load CV profile
    from cover_letter_generator import load_cv_profile
    profile = load_cv_profile()
    
    # Test 1: Generate questions
    test_job = {
        "title": "ESL Instructor",
        "company": "Language Academy",
        "description": "Teaching English to Arabic speakers",
        "score": 90,
        "url": "https://test.com/job/789"
    }
    questions = generate_interview_questions(test_job, profile)
    
    assert "opening" in questions, "Missing opening questions"
    assert "experience" in questions, "Missing experience questions"
    assert "skills" in questions, "Missing skills questions"
    assert len(questions["opening"]) >= 1, "Should have at least 1 opening question"
    print(f"[OK] Generated questions:")
    for category, qs in questions.items():
        if qs:
            print(f"  {category}: {len(qs)} questions")
    
    # Test 2: Verify question structure
    q = questions["opening"][0]
    assert "question" in q, "Missing question field"
    assert "suggested_answer" in q, "Missing suggested_answer field"
    assert "tips" in q, "Missing tips field"
    print(f"[OK] Question structure: OK")
    print(f"  Sample: {q['question'][:80]}...")
    
    # Test 3: Save prep materials
    prep_path = save_interview_prep(test_job, questions)
    assert Path(prep_path).exists(), "Prep file should exist"
    saved = json.loads(Path(prep_path).read_text())
    assert "questions" in saved, "Saved file should have questions"
    print(f"[OK] Saved to: {prep_path}")
    
    # Test 4: Generate for top matches
    test_jobs = [
        {"title": "Translation", "company": "Corp A", "score": 90, "description": "translation work"},
        {"title": "Teaching", "company": "School B", "score": 80, "description": "teaching english"},
        {"title": "Admin", "company": "Office C", "score": 70, "description": "admin work"},
    ]
    prepped = generate_interview_prep_for_top_matches(test_jobs, min_score=85)
    assert prepped[0].get("interview_prep_generated") == True, "High score should get prep"
    assert prepped[1].get("interview_prep_generated") == False, "Score 80 should not get prep"
    assert prepped[2].get("interview_prep_generated") == False, "Score 70 should not get prep"
    print(f"[OK] Top matches prep: {sum(1 for j in prepped if j.get('interview_prep_generated'))}/3 jobs")
    
    # Test 5: Summary
    summary = get_interview_prep_summary(prepped)
    assert len(summary) > 0, "Summary should not be empty"
    print(f"[OK] Summary: {summary[:100]}...")
    
    print("[PASS] Interview Preparation: ALL TESTS PASSED\n")
    return True


async def test_cover_letter_ai():
    """Test AI-enhanced cover letter generation."""
    print("=" * 60)
    print("TEST 4: AI Cover Letter Generation")
    print("=" * 60)
    
    from cover_letter_generator import (
        generate_ai_cover_letter_content, generate_cover_letter_pdf,
        load_cv_profile
    )
    
    profile = load_cv_profile()
    
    # Test 1: Check if Ollama is available
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://localhost:11434/api/tags")
            if resp.status_code != 200:
                print("[WARN] Ollama not available - AI cover letters will use templates")
                return True
    except Exception:
        print("[WARN] Ollama not available - AI cover letters will use templates")
        return True
    
    # Test 2: Generate AI content
    test_job = {
        "title": "Legal Translator",
        "company": "Law Firm",
        "description": "Translate legal documents Arabic-English. Requires experience with contracts."
    }
    
    ai_content = await generate_ai_cover_letter_content(test_job, profile)
    
    if ai_content:
        assert "opening" in ai_content, "Missing opening paragraph"
        assert "experience" in ai_content, "Missing experience paragraph"
        assert "skills" in ai_content, "Missing skills paragraph"
        assert "closing" in ai_content, "Missing closing paragraph"
        print(f"[OK] AI content generated:")
        print(f"  Opening: {ai_content['opening'][:80]}...")
        print(f"  Experience: {ai_content['experience'][:80]}...")
    else:
        print("[WARN] AI content generation returned None (Ollama may be busy)")
    
    # Test 3: Generate PDF (template-based)
    test_job["ai_cover_letter_content"] = ai_content
    pdf_path = generate_cover_letter_pdf(test_job)
    assert Path(pdf_path).exists(), "PDF file should exist"
    assert pdf_path.endswith(".pdf"), "Should be a PDF file"
    print(f"[OK] PDF generated: {pdf_path}")
    print(f"  File size: {Path(pdf_path).stat().st_size} bytes")
    
    print("[PASS] AI Cover Letter: ALL TESTS PASSED\n")
    return True


def test_excel_integration():
    """Test Excel integration with learning module."""
    print("=" * 60)
    print("TEST 5: Excel Integration")
    print("=" * 60)
    
    from excel_generator import mark_applied, get_application_status
    
    # Test 1: Mark as applied
    test_url = "https://test.com/job/excel-test"
    mark_applied(test_url, "Applied", "Test application")
    
    # Test 2: Check status
    status = get_application_status(test_url)
    assert status == "Applied", f"Status should be 'Applied', got '{status}'"
    print(f"[OK] Mark applied: status = {status}")
    
    # Test 3: Verify learning module recorded it
    from learning_module import load_learning_data
    data = load_learning_data()
    found = any(j["url"] == test_url for j in data["applied_jobs"])
    assert found, "Learning module should record the application"
    print(f"[OK] Learning module recorded: {found}")
    
    print("[PASS] Excel Integration: ALL TESTS PASSED\n")
    return True


def test_scanner_integration():
    """Test scanner imports and integration."""
    print("=" * 60)
    print("TEST 6: Scanner Integration")
    print("=" * 60)
    
    try:
        import scanner
        print("[OK] Scanner imports successfully")
        
        # Check new functions exist
        assert hasattr(scanner, 'record_application'), "Missing record_application"
        assert hasattr(scanner, 'adjust_scoring_based_on_learning'), "Missing adjust_scoring"
        assert hasattr(scanner, 'research_companies_batch'), "Missing research_companies"
        assert hasattr(scanner, 'generate_interview_prep_for_top_matches'), "Missing interview_prep"
        print("[OK] All new functions available in scanner")
        
    except Exception as e:
        print(f"[FAIL] Scanner integration failed: {e}")
        return False
    
    print("[PASS] Scanner Integration: ALL TESTS PASSED\n")
    return True


def test_reddit_social():
    """Test Reddit social-signal fetcher (offline parser + wiring)."""
    print("=" * 60)
    print("TEST 7: Reddit Social Signals")
    print("=" * 60)

    from fetchers.social import parse_reddit_listing, fetch_reddit_social, REDDIT_TARGETS
    from fetchers.registry import TIER_MAP, list_fetchers

    # Wiring: registered + active under the current tier cap
    assert "reddit_social" in list_fetchers(2), "reddit_social missing from tier<=2 fleet"
    assert TIER_MAP.get("reddit_social") == 2, "reddit_social should be tier 2"
    print(f"[OK] Fleet wiring: {len(REDDIT_TARGETS)} community targets, tier 2")

    # Parser: valid payload
    payload = {"data": {"children": [
        {"data": {"title": "Hiring: Remote ESL teacher (evenings)",
                  "permalink": "/r/forhire/comments/abc123/hiring_esl/",
                  "subreddit": "forhire", "selftext": "Looking for a native-level instructor...",
                  "created_utc": 1757100000}},
        {"data": {"title": "Arabic-English freelance translation",
                  "permalink": "https://www.reddit.com/r/Translation/comments/xyz/",
                  "subreddit": "Translation", "selftext": "",
                  "created_utc": 1757200000}},
        {"data": {"title": "", "permalink": "/r/esl/comments/bad/",
                  "subreddit": "esl", "selftext": "no title should be skipped"}},
    ]}}
    jobs = parse_reddit_listing(payload)
    assert len(jobs) == 2, f"expected 2 parsed jobs, got {len(jobs)}"
    assert jobs[0]["source"] == "reddit_social"
    assert jobs[0]["company"] == "r/forhire"
    assert jobs[0]["url"].startswith("https://www.reddit.com/r/forhire/")
    assert jobs[0]["posted"].startswith("2025-09-05"), jobs[0]["posted"]
    assert jobs[1]["url"].startswith("https://www.reddit.com/r/Translation/")
    assert jobs[0]["title"] == "Hiring: Remote ESL teacher (evenings)"
    print(f"[OK] Parser: 2/2 valid posts parsed, 1 malformed skipped")

    # Parser: hostile inputs
    assert parse_reddit_listing(None) == []
    assert parse_reddit_listing({}) == []
    assert parse_reddit_listing({"data": None}) == []
    print("[OK] Parser: hostile payloads handled")

    print("[PASS] Reddit Social Signals: ALL TESTS PASSED\n")
    return True


def test_new_boards():
    """Test the two newly added niche boards (offline parsers + wiring)."""
    print("=" * 60)
    print("TEST 8: New Niche Boards (ESL Gorilla + TES)")
    print("=" * 60)

    from scanner import parse_eslgorilla_html, parse_tes_html
    from fetchers.registry import TIER_MAP, list_fetchers

    # Wiring: both registered + active under the current tier cap
    for name in ("eslgorilla", "tes"):
        assert name in list_fetchers(2), f"{name} missing from tier<=2 fleet"
        assert TIER_MAP.get(name) == 2, f"{name} should be tier 2"
    print("[OK] Fleet wiring: eslgorilla + tes registered, tier 2")

    # --- ESL Gorilla parser: mixed card + bullet markup, dedup, non-remote filter ---
    esl_html = (
        '<a href="https://eslgorilla.com/jobs/online-english-teacher-remote-meridian">'
        '<h3>Online English Teacher &ndash; Remote | Up to $17/50-min Class</h3>'
        '<p>fully online classes. Flexible schedule, worldwide candidates welcome.</p></a>'
        '<a href="https://eslgorilla.com/jobs/kids-esl-teacher-blinc">'
        '<strong>Kids ESL Teacher - BlingABC</strong><span>Remote</span></a>'
        '<li><a href="https://eslgorilla.com/jobs/online-esl-teacher-novacat">Online ESL Teacher — Remote</a></li>'
        '<li><a href="https://eslgorilla.com/jobs/adult-conversation-jobs">Adult Conversation Practice — Worldwide</a></li>'
        '<li><a href="https://eslgorilla.com/jobs/offline-campus-lagos">In-person Campus Teacher — Lagos, Nigeria</a></li>'
        # duplicate slug should be dropped
        '<li><a href="https://eslgorilla.com/jobs/online-esl-teacher-novacat">Online ESL Teacher — Remote</a></li>'
    )
    jobs = parse_eslgorilla_html(esl_html)
    assert len(jobs) == 4, f"expected 4 unique ESL jobs (dup + non-remote filtered), got {len(jobs)}"
    assert all("Lagos" not in j["title"] + j["location"] for j in jobs), "non-remote job must be filtered"
    assert all(j["source"] == "eslgorilla" for j in jobs)
    assert all("&ndash;" not in j["title"] for j in jobs), "entities must be unescaped"
    bullet = next(j for j in jobs if j["url"].endswith("/online-esl-teacher-novacat"))
    assert bullet["title"] == "Online ESL Teacher" and bullet["location"] == "Remote", bullet
    assert jobs[0]["salary"] == "$17", jobs[0]["salary"]
    print(f"[OK] ESL Gorilla parser: {len(jobs)} jobs, dedup + non-remote filter + entity unescape")

    # --- TES parser: keeps remote/online only, drops in-person UK, dedups Apply link ---
    tes_html = (
        '<a href="https://www.tes.com/jobs/vacancy/remote-online-english-teacher-2341001">Remote Online English Teacher</a>'
        '<span>£25 - £30 per hour</span><span>New</span>'
        '<img alt="Lingua Online Academy logo" src="x.jpg"><span>Remote (Worldwide)</span>'
        '<p>We are seeking a passionate online English teacher to work fully remotely from anywhere.</p><span>Today</span>'
        '<a href="https://www.tes.com/jobs/vacancy/remote-online-english-teacher-2341001">Apply</a>'
        '<a href="https://www.tes.com/jobs/vacancy/ks2-teacher-wandsworth-2341763">KS2 Teacher - Maternity Cover</a>'
        '<img alt="Dolphin School logo" src="y.jpg"><span>Wandsworth</span>'
        '<p>We are seeking a committed Key Stage 2 Teacher for a full-time maternity cover role.</p><span>Today</span>'
        '<a href="https://www.tes.com/jobs/vacancy/online-ell-tutor-global-2341770"><strong>Online ELL Tutor</strong></a>'
        '<img alt="Global Edu logo" src="z.jpg"><span>Remote</span>'
        '<p>Looking for an experienced ELL tutor to deliver online lessons. Work remotely worldwide.</p><span>2 days ago</span>'
    )
    tjobs = parse_tes_html(tes_html)
    assert len(tjobs) == 2, f"expected 2 TES remote jobs (in-person UK dropped), got {len(tjobs)}"
    assert all(j["source"] == "tes" for j in tjobs)
    assert any(j["title"] == "Remote Online English Teacher" and j["company"] == "Lingua Online Academy" for j in tjobs)
    assert any(j["title"] == "Online ELL Tutor" and j["company"] == "Global Edu" for j in tjobs)
    assert not any("Wandsworth" in (j["title"] + j["company"] + j["location"]) for j in tjobs), "in-person UK must be filtered"
    print(f"[OK] TES parser: {len(tjobs)} remote jobs, in-person UK filtered, Apply-link dedup")

    # Hostile / empty inputs
    assert parse_eslgorilla_html("") == []
    assert parse_eslgorilla_html("no job links here") == []
    assert parse_tes_html("") == []
    assert parse_tes_html("<p>nothing</p>") == []
    print("[OK] Hostile/empty inputs handled")

    print("[PASS] New Niche Boards (ESL Gorilla + TES): ALL TESTS PASSED\n")
    return True


def main():
    """Run all tests."""
    import shutil
    from pathlib import Path as _Path

    print("\n" + "=" * 60)
    print("CAREEROPS COMPREHENSIVE TEST SUITE")
    print("=" * 60 + "\n")

    # Isolate test state: these tests write to output/ (learning_data.json,
    # applications.json, company cache, interview prep, cover letter PDFs).
    # Back up the real data first and restore it afterwards so tests can be
    # re-run and never pollute production data.
    output_dir = _Path(__file__).parent / "output"
    backup_dir = _Path(__file__).parent / "output_test_backup"
    had_output = output_dir.exists()
    if had_output:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(output_dir, backup_dir)
        # copytree only copies — remove the original so tests start clean
        shutil.rmtree(output_dir)

    try:
        results = []

        # Run synchronous tests
        results.append(("Learning Module", test_learning_module()))
        results.append(("Company Research", test_company_research()))
        results.append(("Interview Preparation", test_interview_prep()))
        results.append(("Excel Integration", test_excel_integration()))
        results.append(("Scanner Integration", test_scanner_integration()))
        results.append(("Reddit Social Signals", test_reddit_social()))
        results.append(("New Niche Boards", test_new_boards()))

        # Run async test
        results.append(("AI Cover Letter", asyncio.run(test_cover_letter_ai())))

        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} - {name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\nALL TESTS PASSED! System is ready.\n")
            return 0
        else:
            print(f"\n{total - passed} test(s) failed. Review output above.\n")
            return 1
    finally:
        # Restore the real data and remove any test artifacts
        if backup_dir.exists():
            if output_dir.exists():
                shutil.rmtree(output_dir)
            shutil.move(str(backup_dir), str(output_dir))
        elif output_dir.exists():
            shutil.rmtree(output_dir)


if __name__ == "__main__":
    sys.exit(main())
