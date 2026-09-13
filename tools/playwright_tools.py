"""Playwright Browser Tools — Browser automation for job scraping."""
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


class PlaywrightScrapeInput(BaseModel):
    """Input for Playwright scraping."""
    url: str = Field(..., description="URL to scrape")
    wait_for: str = Field(default="networkidle", description="Wait strategy")


class PlaywrightScraperTool(BaseTool):
    """Scrape websites using Playwright browser automation."""
    name: str = "playwright_scraper"
    description: str = "Scrape a website using Playwright browser automation"
    args_schema: Type[BaseModel] = PlaywrightScrapeInput

    def _run(self, url: str, wait_for: str = "networkidle") -> str:
        """Scrape website using Playwright."""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until=wait_for, timeout=30000)
                
                # Get page content
                content = page.content()
                title = page.title()
                
                # Extract text content
                text = page.inner_text("body")
                
                # Find job-related links
                job_links = []
                links = page.query_selector_all("a[href]")
                for link in links[:50]:
                    href = link.get_attribute("href")
                    text_content = link.inner_text().strip()
                    
                    if href and text_content:
                        if any(kw in text_content.lower() for kw in 
                               ["translator", "translation", "linguist", "esl", "language", 
                                "arabic", "job", "position", "career", "apply"]):
                            if not href.startswith("http"):
                                from urllib.parse import urljoin
                                href = urljoin(url, href)
                            job_links.append(f"- {text_content[:100]}\n  URL: {href}")
                
                browser.close()
                
                result = f"Page Title: {title}\n\n"
                result += f"Text Content (first 2000 chars):\n{text[:2000]}\n\n"
                
                if job_links:
                    result += f"Job Links Found ({len(job_links)}):\n" + "\n".join(job_links[:15])
                else:
                    result += "No specific job links found on page"
                
                return result
        except ImportError:
            return "Error: playwright not installed"
        except Exception as e:
            return f"Playwright error: {str(e)}"


class PlaywrightFormFillInput(BaseModel):
    """Input for form filling."""
    url: str = Field(..., description="Application form URL")
    form_data: str = Field(..., description="JSON string of form data to fill")


class PlaywrightFormFiller(BaseTool):
    """Fill job application forms using Playwright."""
    name: str = "playwright_form_filler"
    description: str = "Fill a job application form using Playwright"
    args_schema: Type[BaseModel] = PlaywrightFormFillInput

    def _run(self, url: str, form_data: str) -> str:
        """Fill form using Playwright."""
        try:
            import json
            from playwright.sync_api import sync_playwright
            
            data = json.loads(form_data)
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # Visible for review
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                filled_fields = []
                
                # Fill common form fields
                field_mapping = {
                    "first_name": ["input[name*='first']", "input[name*='First']", "#first_name"],
                    "last_name": ["input[name*='last']", "input[name*='Last']", "#last_name"],
                    "email": ["input[type='email']", "input[name*='email']", "#email"],
                    "phone": ["input[type='tel']", "input[name*='phone']", "#phone"],
                    "linkedin": ["input[name*='linkedin']", "input[name*='LinkedIn']"],
                    "website": ["input[name*='website']", "input[name*='url']"],
                }
                
                for field_name, selectors in field_mapping.items():
                    if field_name in data:
                        for selector in selectors:
                            try:
                                element = page.query_selector(selector)
                                if element:
                                    element.fill(data[field_name])
                                    filled_fields.append(f"{field_name}: {data[field_name][:30]}...")
                                    break
                            except:
                                continue
                
                # Try to fill textarea fields (cover letter, etc.)
                textareas = page.query_selector_all("textarea")
                for textarea in textareas:
                    name = textarea.get_attribute("name") or ""
                    if "cover" in name.lower() or "letter" in name.lower():
                        if "cover_letter" in data:
                            textarea.fill(data["cover_letter"])
                            filled_fields.append("cover_letter: filled")
                    elif "description" in name.lower() or "summary" in name.lower():
                        if "summary" in data:
                            textarea.fill(data["summary"])
                            filled_fields.append("summary: filled")
                
                # Take screenshot for review
                page.screenshot(path="output/form_screenshot.png")
                
                browser.close()
                
                if filled_fields:
                    return f"Form filled successfully:\n" + "\n".join(filled_fields) + "\n\nScreenshot saved to output/form_screenshot.png"
                else:
                    return "No fields were filled. Form may have different structure."
        except ImportError:
            return "Error: playwright not installed"
        except json.JSONDecodeError:
            return "Error: Invalid JSON in form_data"
        except Exception as e:
            return f"Form fill error: {str(e)}"


class GreenhouseFormInput(BaseModel):
    """Input for Greenhouse ATS form."""
    url: str = Field(..., description="Greenhouse job application URL")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: str = Field(default="", description="Phone number")
    resume_path: str = Field(default="", description="Path to resume PDF")
    cover_letter: str = Field(default="", description="Cover letter text")


class GreenhouseFormTool(BaseTool):
    """Fill Greenhouse ATS application forms."""
    name: str = "greenhouse_form_filler"
    description: str = "Fill a Greenhouse ATS job application form"
    args_schema: Type[BaseModel] = GreenhouseFormInput

    def _run(self, url: str, first_name: str, last_name: str, email: str,
             phone: str = "", resume_path: str = "", cover_letter: str = "") -> str:
        """Fill Greenhouse form."""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                filled = []
                
                # Greenhouse form field selectors
                selectors = {
                    "first_name": ["input[name='job_application[first_name]']", "#first_name"],
                    "last_name": ["input[name='job_application[last_name]']", "#last_name"],
                    "email": ["input[name='job_application[email]']", "#email"],
                    "phone": ["input[name='job_application[phone]']", "#phone"],
                }
                
                # Fill fields
                for field, value in [("first_name", first_name), ("last_name", last_name),
                                     ("email", email), ("phone", phone)]:
                    if value:
                        for selector in selectors.get(field, []):
                            try:
                                el = page.query_selector(selector)
                                if el:
                                    el.fill(value)
                                    filled.append(f"{field}: {value}")
                                    break
                            except:
                                continue
                
                # Fill cover letter textarea
                if cover_letter:
                    textarea = page.query_selector("textarea[name*='cover_letter']")
                    if textarea:
                        textarea.fill(cover_letter)
                        filled.append("cover_letter: filled")
                
                # Upload resume if provided
                if resume_path:
                    try:
                        upload = page.query_selector("input[type='file']")
                        if upload:
                            upload.set_input_files(resume_path)
                            filled.append(f"resume: {resume_path}")
                    except:
                        filled.append("resume: upload field not found")
                
                # Take screenshot
                page.screenshot(path="output/greenhouse_form.png")
                
                browser.close()
                
                if filled:
                    return f"Greenhouse form filled:\n" + "\n".join(filled)
                else:
                    return "No fields filled in Greenhouse form"
        except Exception as e:
            return f"Greenhouse form error: {str(e)}"
