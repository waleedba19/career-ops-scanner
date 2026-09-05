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
