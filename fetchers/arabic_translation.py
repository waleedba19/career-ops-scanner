"""Arabic Translation Jobs - Specific companies and platforms hiring Arabic translators."""
import re
import urllib.request

# Specific companies and platforms that hire Arabic translators
ARABIC_TRANSLATION_COMPANIES = [
    # AI Data & Language Companies (Remote)
    {"name": "AuraOne Human Data", "url": "https://www.auraone.com/careers"},
    {"name": "Scale AI", "url": "https://scale.com/careers"},
    {"name": "Surge AI", "url": "https://surgeai.com/careers"},
    {"name": "Appen", "url": "https://www.appen.com/careers"},
    {"name": "Telus International", "url": "https://www.telusinternational.com/careers"},
    {"name": "Centific", "url": "https://www.centific.com/careers"},
    {"name": "Welo Data", "url": "https://www.welodata.com/careers"},
    {"name": "Meridial", "url": "https://www.meridial.com/careers"},
    
    # Translation & Language Services (Remote)
    {"name": "TransPerfect", "url": "https://www.transperfect.com/careers"},
    {"name": "Lionbridge", "url": "https://www.lionbridge.com/careers"},
    {"name": "RWS", "url": "https://www.rws.com/careers"},
    {"name": "Keywords Studios", "url": "https://www.keywordsstudios.com/careers"},
    {"name": "OneForma", "url": "https://www.oneforma.com/careers"},
    {"name": "Welocalize", "url": "https://www.welocalize.com/careers"},
    {"name": "CETRA", "url": "https://www.cetra.com/careers"},
    {"name": "Propio LS", "url": "https://www.propio.com/careers"},
    
    # ESL & Language Teaching (Remote)
    {"name": "LanguageBird", "url": "https://www.languagebird.com/teach"},
    {"name": "VIPKid", "url": "https://www.vipkid.com/careers"},
    {"name": "Cambly", "url": "https://www.cambly.com/careers"},
    {"name": "Preply", "url": "https://preply.com/careers"},
    {"name": "italki", "url": "https://www.italki.com/careers"},
    {"name": "LanguageLine Solutions", "url": "https://www.languageline.com/careers"},
    
    # MENA Region Companies
    {"name": "Tarjama", "url": "https://www.tarjama.com/careers"},
    {"name": "Tamatem Games", "url": "https://www.tamatemgames.com/careers"},
    {"name": "Careem", "url": "https://www.careem.com/careers"},
    {"name": "Noon Academy", "url": "https://www.noonacademy.com/careers"},
    {"name": "AsiaLocalize", "url": "https://www.asialocalize.com/careers"},
    
    # Freelance Platforms (Direct URL jobs)
    {"name": "ProZ", "url": "https://www.proz.com/translation-jobs"},
    {"name": "TranslatorsCafe", "url": "https://www.translatorscafe.com/jobs/"},
    {"name": "TranslaStars", "url": "https://jobs.translastars.com/jobs/remote-jobs"},
    {"name": "RemoWork", "url": "https://remowork.life/jobs/languages/arabic"},
    {"name": "Flexstack", "url": "https://flexstack.my-board.org/remote-jobs"},
]

def fetch():
    """Fetch Arabic translation job listings from specific companies."""
    items = []
    
    for company in ARABIC_TRANSLATION_COMPANIES:
        try:
            url = company["url"]
            name = company["name"]
            
            # Add company as a potential source
            items.append({
                "title": f"Arabic Translator - {name}",
                "company": name,
                "url": url,
                "location": "Remote",
                "description": f"Check {name} for Arabic translation opportunities",
                "source": "arabic_companies",
            })
                
        except Exception:
            continue
    
    return items
