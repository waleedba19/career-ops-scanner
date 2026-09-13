"""Ollama Scoring Tools — Local LLM for job scoring and document generation."""
import json
import re
from typing import Type
from pydantic import BaseModel, Field

try:
    from crewai_tools import BaseTool
except ImportError:
    class BaseTool:
        name: str = ""
        description: str = ""
        def _run(self, *args, **kwargs):
            raise NotImplementedError


class OllamaScoringInput(BaseModel):
    """Input for Ollama scoring."""
    job_title: str = Field(..., description="Job title")
    job_description: str = Field(..., description="Job description")
    company: str = Field(default="", description="Company name")


class OllamaScoringTool(BaseTool):
    """Score job match using Ollama LLM."""
    name: str = "ollama_scorer"
    description: str = "Score how well a job matches Arabic translator profile"
    args_schema: Type[BaseModel] = OllamaScoringInput

    def _run(self, job_title: str, job_description: str, company: str = "") -> str:
        """Score job using Ollama."""
        try:
            import urllib.request
            
            prompt = f"""You are an expert job matcher. Score this job 0-100 based on match
with this profile:
- Name: Waleed Ballag
- Skills: Arabic-English translation, legal translation, ESL teaching, academic supervision
- Experience: 5+ years translation, 15 theses supervised
- Requirements: Remote work, worldwide, no visa restrictions

Job to score:
Title: {job_title}
Company: {company}
Description: {job_description[:1000]}

Score each criteria:
1. Arabic translation match (40 points) - Does title/description mention Arabic, translation, linguist?
2. Remote work (20 points) - Is it remote/worldwide?
3. ESL/teaching match (15 points) - Does it involve teaching, ESL, tutoring?
4. Salary match (15 points) - Is salary above $40,000/year?
5. Application ease (10 points) - Is it on Greenhouse/Lever/Ashby?

Return ONLY a JSON object with this format:
{{"score": <0-100>, "category": "<Arabic Translation|ESL|Editing|Admin|Other>", "reasons": ["reason1", "reason2"]}}"""

            data = json.dumps({
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False
            }).encode()
            
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            
            response = result.get("response", "")
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                return json_match.group(0)
            else:
                return json.dumps({"score": 0, "category": "Other", "reasons": ["Could not parse Ollama response"]})
        except Exception as e:
            return json.dumps({"score": 0, "category": "Other", "reasons": [f"Ollama error: {str(e)}"]})


class OllamaWritingInput(BaseModel):
    """Input for Ollama document generation."""
    job_title: str = Field(..., description="Job title")
    job_description: str = Field(..., description="Job description")
    company: str = Field(default="", description="Company name")
    document_type: str = Field(default="cover_letter", description="Type: cover_letter or summary")


class OllamaWritingTool(BaseTool):
    """Generate tailored documents using Ollama LLM."""
    name: str = "ollama_writer"
    description: str = "Generate tailored cover letter or CV summary"
    args_schema: Type[BaseModel] = OllamaWritingInput

    def _run(self, job_title: str, job_description: str, company: str = "", 
             document_type: str = "cover_letter") -> str:
        """Generate document using Ollama."""
        try:
            import urllib.request
            
            if document_type == "cover_letter":
                prompt = f"""Write a professional cover letter (250-350 words) for this job application.

Applicant Profile:
- Name: Waleed Ballag
- Title: Arabic-English Translator | ESL Instructor | Localization Specialist
- Experience: 5+ years translation, legal translation, academic supervision
- Skills: Arabic (native), English (C1), SPSS, academic editing
- Location: Libya (remote worldwide)

Job Details:
Title: {job_title}
Company: {company}
Description: {job_description[:800]}

Requirements:
- Professional, academic, personable tone
- Highlight Arabic translation expertise
- Mention legal translation experience
- Show enthusiasm for the role
- Keep to 250-350 words

Write ONLY the cover letter text, no headers or explanations:"""
            else:
                prompt = f"""Write a professional CV summary (100-150 words) for this job application.

Applicant Profile:
- Name: Waleed Ballag
- Title: Arabic-English Translator | ESL Instructor
- Experience: 5+ years translation, 15 theses supervised
- Skills: Arabic (native), English (C1), legal/academic translation

Job Details:
Title: {job_title}
Company: {company}

Write ONLY the summary text:"""

            data = json.dumps({
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False
            }).encode()
            
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
            
            return result.get("response", "Error generating document")
        except Exception as e:
            return f"Document generation error: {str(e)}"


class KeywordMatchInput(BaseModel):
    """Input for keyword matching."""
    job_text: str = Field(..., description="Job title and description text")


class KeywordMatchTool(BaseTool):
    """Fast keyword-based job scoring (no LLM needed)."""
    name: str = "keyword_matcher"
    description: str = "Score job based on keyword matching"
    args_schema: Type[BaseModel] = KeywordMatchInput

    def _run(self, job_text: str) -> str:
        """Score job using keyword matching."""
        text = job_text.lower()
        
        score = 0
        reasons = []
        
        # Arabic translation keywords (40 points max)
        arabic_keywords = ["arabic", "translator", "translation", "linguist", "localization"]
        arabic_matches = sum(1 for kw in arabic_keywords if kw in text)
        if arabic_matches >= 2:
            score += 40
            reasons.append(f"Strong Arabic translation match ({arabic_matches} keywords)")
        elif arabic_matches == 1:
            score += 25
            reasons.append(f"Some Arabic translation match ({arabic_matches} keyword)")
        
        # Remote work (20 points)
        remote_keywords = ["remote", "work from home", "worldwide", "anywhere", "distributed"]
        if any(kw in text for kw in remote_keywords):
            score += 20
            reasons.append("Remote work available")
        
        # ESL/teaching (15 points)
        esl_keywords = ["esl", "efl", "tesol", "tefl", "teacher", "tutor", "teaching", "instructor"]
        if any(kw in text for kw in esl_keywords):
            score += 15
            reasons.append("ESL/teaching role")
        
        # Translation services (15 points)
        translation_keywords = ["translator", "translation", "interpreter", "linguist", "localization"]
        if any(kw in text for kw in translation_keywords):
            score += 15
            reasons.append("Translation services")
        
        # Seniority penalties
        senior_keywords = ["senior", "lead", "director", "head", "principal", "staff"]
        if any(kw in text for kw in senior_keywords):
            score -= 20
            reasons.append("Senior level (may be overqualified)")
        
        # Wrong language keywords
        wrong_lang = ["hindi", "spanish", "french", "german", "chinese", "japanese", "korean"]
        if any(kw in text for kw in wrong_lang) and "arabic" not in text:
            score -= 30
            reasons.append("Wrong language focus")
        
        score = max(0, min(100, score))
        
        # Determine category
        if arabic_matches >= 1:
            category = "Arabic Translation"
        elif any(kw in text for kw in esl_keywords):
            category = "ESL"
        elif any(kw in text for kw in translation_keywords):
            category = "Translation"
        else:
            category = "Other"
        
        return json.dumps({
            "score": score,
            "category": category,
            "reasons": reasons
        })


class CompanyReputationInput(BaseModel):
    """Input for company reputation check."""
    company_name: str = Field(..., description="Company name to check")


class CompanyReputationTool(BaseTool):
    """Check company reputation for translation/language services."""
    name: str = "company_reputation"
    description: str = "Check if company is reputable for translation work"
    args_schema: Type[BaseModel] = CompanyReputationInput

    def _run(self, company_name: str) -> str:
        """Check company reputation."""
        # Known translation/language companies (trusted)
        trusted_companies = {
            "transperfect": {"rating": "excellent", "type": "LSP", "arabic": True},
            "lionbridge": {"rating": "excellent", "type": "LSP", "arabic": True},
            "rws": {"rating": "excellent", "type": "LSP", "arabic": True},
            "keywords studios": {"rating": "good", "type": "LSP", "arabic": True},
            "appen": {"rating": "good", "type": "AI data", "arabic": True},
            "telus international": {"rating": "good", "type": "AI data", "arabic": True},
            "centific": {"rating": "good", "type": "AI data", "arabic": True},
            "welocalize": {"rating": "good", "type": "LSP", "arabic": True},
            "oneforma": {"rating": "good", "type": "AI data", "arabic": True},
            "scale ai": {"rating": "excellent", "type": "AI data", "arabic": True},
            "surge ai": {"rating": "good", "type": "AI data", "arabic": True},
            "proz": {"rating": "excellent", "type": "marketplace", "arabic": True},
            "tarjama": {"rating": "good", "type": "MENA LSP", "arabic": True},
            "tamatem games": {"rating": "good", "type": "MENA tech", "arabic": True},
            "careem": {"rating": "good", "type": "MENA tech", "arabic": True},
            "languagebird": {"rating": "good", "type": "ESL", "arabic": True},
            "vipkid": {"rating": "good", "type": "ESL", "arabic": True},
            "cambly": {"rating": "good", "type": "ESL", "arabic": True},
            "preply": {"rating": "good", "type": "ESL", "arabic": True},
            "italki": {"rating": "good", "type": "ESL", "arabic": True},
        }
        
        company_lower = company_name.lower().strip()
        
        for key, info in trusted_companies.items():
            if key in company_lower or company_lower in key:
                return json.dumps({
                    "trusted": True,
                    "rating": info["rating"],
                    "type": info["type"],
                    "arabic_relevant": info["arabic"],
                    "bonus": 15 if info["rating"] == "excellent" else 10
                })
        
        return json.dumps({
            "trusted": False,
            "rating": "unknown",
            "type": "unknown",
            "arabic_relevant": False,
            "bonus": 0
        })
