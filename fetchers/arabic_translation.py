"""Arabic Translation Jobs - Specific companies and platforms hiring Arabic translators."""
import re
from ._shared import get, strip_html

# Specific companies and platforms that hire Arabic translators
ARABIC_TRANSLATION_COMPANIES = [
    # AI Data & Language Companies (Remote)
    {"name": "AuraOne Human Data", "url": "https://www.auraone.com/careers", "type": "ai_data"},
    {"name": "Scale AI", "url": "https://scale.com/careers", "type": "ai_data"},
    {"name": "Surge AI", "url": "https://surgeai.com/careers", "type": "ai_data"},
    {"name": "Appen", "url": "https://www.appen.com/careers", "type": "ai_data"},
    {"name": "Telus International", "url": "https://www.telusinternational.com/careers", "type": "ai_data"},
    {"name": "Centific", "url": "https://www.centific.com/careers", "type": "ai_data"},
    {"name": "Welo Data", "url": "https://www.welodata.com/careers", "type": "ai_data"},
    {"name": "Meridial", "url": "https://www.meridial.com/careers", "type": "ai_data"},
    
    # Translation & Language Services (Remote)
    {"name": "TransPerfect", "url": "https://www.transperfect.com/careers", "type": "translation"},
    {"name": "Lionbridge", "url": "https://www.lionbridge.com/careers", "type": "translation"},
    {"name": "RWS", "url": "https://www.rws.com/careers", "type": "translation"},
    {"name": "Keywords Studios", "url": "https://www.keywordsstudios.com/careers", "type": "translation"},
    {"name": "OneForma", "url": "https://www.oneforma.com/careers", "type": "translation"},
    {"name": "Welocalize", "url": "https://www.welocalize.com/careers", "type": "translation"},
    {"name": "CETRA", "url": "https://www.cetra.com/careers", "type": "translation"},
    {"name": "Propio LS", "url": "https://www.propio.com/careers", "type": "translation"},
    
    # ESL & Language Teaching (Remote)
    {"name": "LanguageBird", "url": "https://www.languagebird.com/teach", "type": "esl"},
    {"name": "VIPKid", "url": "https://www.vipkid.com/careers", "type": "esl"},
    {"name": "Cambly", "url": "https://www.cambly.com/careers", "type": "esl"},
    {"name": "Preply", "url": "https://preply.com/careers", "type": "esl"},
    {"name": "italki", "url": "https://www.italki.com/careers", "type": "esl"},
    {"name": "LanguageLine Solutions", "url": "https://www.languageline.com/careers", "type": "esl"},
    
    # MENA Region Companies
    {"name": "Tarjama", "url": "https://www.tarjama.com/careers", "type": "translation"},
    {"name": "Tamatem Games", "url": "https://www.tamatemgames.com/careers", "type": "localization"},
    {"name": "Careem", "url": "https://www.careem.com/careers", "type": "tech"},
    {"name": "Noon Academy", "url": "https://www.noonacademy.com/careers", "type": "edtech"},
    {"name": "AsiaLocalize", "url": "https://www.asialocalize.com/careers", "type": "translation"},
    
    # Freelance Platforms (Direct URL jobs)
    {"name": "ProZ", "url": "https://www.proz.com/translation-jobs", "type": "freelance"},
    {"name": "TranslatorsCafe", "url": "https://www.translatorscafe.com/jobs/", "type": "freelance"},
    {"name": "TranslaStars", "url": "https://jobs.translastars.com/jobs/remote-jobs", "type": "freelance"},
    {"name": "RemoWork", "url": "https://remowork.life/jobs/languages/arabic", "type": "freelance"},
    {"name": "Flexstack", "url": "https://flexstack.my-board.org/remote-jobs", "type": "freelance"},
]

def fetch(timeout: int = 15) -> list[dict]:
    """Fetch Arabic translation job listings from specific companies."""
    items = []
    seen = set()
    
    for company in ARABIC_TRANSLATION_COMPANIES:
        try:
            url = company["url"]
            name = company["name"]
            
            # Fetch the careers page
            raw = get(url, timeout)
            html = strip_html(raw, limit=5000)
            
            # Look for job listings
            job_patterns = [
                r'(?:arabic|translator|translation|localization|linguist|esl|language)[^<]*',
                r'href="([^"]*(?:arabic|translator|translation|linguist)[^"]*)"',
            ]
            
            for pattern in job_patterns:
                matches = re.findall(pattern, html, re.I)
                for match in matches[:5]:  # Limit to 5 per company
                    if isinstance(match, tuple):
                        job_url = match[0] if match else ""
                    else:
                        job_url = url
                    
                    # Clean up the job title
                    title = re.sub(r'<[^>]+>', '', match).strip() if isinstance(match, str) else ""
                    if not title:
                        title = f"{name} - Arabic Translation"
                    
                    # Ensure URL is complete
                    if job_url and not job_url.startswith("http"):
                        job_url = url.rstrip('/') + '/' + job_url.lstrip('/')
                    
                    key = f"{name}|{job_url}"
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    items.append({
                        "title": title[:160],
                        "company": name,
                        "url": job_url or url,
                        "location": "Remote",
                        "description": f"Arabic translation opportunity at {name}",
                        "source": "arabic_translation_companies",
                        "tags": ["arabic", "translation", "remote"],
                    })
            
            # If no specific jobs found, add company as a potential source
            if not any(i["company"] == name for i in items):
                items.append({
                    "title": f"Arabic Translator - {name}",
                    "company": name,
                    "url": url,
                    "location": "Remote",
                    "description": f"Check {name} for Arabic translation opportunities",
                    "source": "arabic_translation_companies",
                    "tags": ["arabic", "translation", "remote"],
                })
                
        except Exception:
            continue
    
    return items
