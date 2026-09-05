import sys
sys.path.insert(0, '.')
from company_research import research_companies_batch
from cover_letter_generator import generate_all_cover_letters
from interview_prep import generate_interview_prep_for_top_matches

test_jobs = [{
    "title": "ESL Teacher",
    "company": "KAYAK",
    "url": "https://example.com/test",
    "location": "Remote",
    "posted": "",
    "description": "Teach English online",
    "match_score": 100,
    "category": "ESL",
    "score": 100,
}]

# Company research
res = research_companies_batch(test_jobs)
cr = res[0].get("company_research", {})
print(f"Company research: legitimacy={cr.get('legitimacy_score', 0)}, signals={cr.get('positive_signals', [])}")

# Cover letter
import asyncio
res2 = asyncio.run(generate_all_cover_letters(test_jobs))
cl = res2[0].get("cover_letter_path", "NONE")
ai = res2[0].get("cover_letter_ai", False)
print(f"Cover letter: path={cl}, ai_enhanced={ai}")

# Interview prep
res3 = generate_interview_prep_for_top_matches(test_jobs, min_score=85)
prep = res3[0].get("interview_prep_generated", False)
print(f"Interview prep generated: {prep}")

print("\nAll 3 modules: OK")
