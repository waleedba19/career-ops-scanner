"""Arabic Translation Jobs - Specific companies and platforms hiring Arabic translators."""
import re
import urllib.request
from . import _shared

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
            
            # Fetch the careers page using urllib
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
            html = _shared.strip_html(raw)[:5000]
            
            # Look for job listings - simple pattern matching
            job_patterns = [
                r'arabic[^<]*translator[^<]*',
                r'translator[^<]*arabic[^<]*',
                r'arabic[^<]*translation[^<]*',
                r'translation[^<]*arabic[^<]*',
                r'linguist[^<]*arabic[^<]*',
                r'esl[^<]*arabic[^<]*',
            ]
            
            for pattern in job_patterns:
                matches = re.findall(pattern, html, re.I)
                for match in matches[:3]:  # Limit to 3 per pattern
                    if not isinstance(match, str):
                        continue
                    
                    # Clean up the job title
                    title = re.sub(r'<[^>]+>', '', match).strip()
                    if not title or len(title) < 5:
                        continue
                    
                    job_url = url
                    
                    key = f"{name}|{title[:50]}"
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    items.append({
                        "title": f"{name} - {title[:100]}"[:160],
                        "company": name,
                        "url": job_url,
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
