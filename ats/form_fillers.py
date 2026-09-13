"""ATS Form Fillers — Automated job application forms for different ATS platforms."""
import json
from typing import Dict, Optional


class ATSFormFiller:
    """Base class for ATS form fillers."""
    
    def __init__(self):
        self.filled_fields = []
        self.errors = []
    
    def fill_form(self, page, form_data: Dict) -> Dict:
        """Fill form and return results."""
        raise NotImplementedError
    
    def _fill_field(self, page, selector: str, value: str, field_name: str) -> bool:
        """Fill a single field."""
        try:
            element = page.query_selector(selector)
            if element:
                element.fill(value)
                self.filled_fields.append(f"{field_name}: {value[:50]}")
                return True
        except Exception as e:
            self.errors.append(f"{field_name}: {str(e)[:50]}")
        return False
    
    def _upload_file(self, page, selector: str, file_path: str, field_name: str) -> bool:
        """Upload a file."""
        try:
            element = page.query_selector(selector)
            if element:
                element.set_input_files(file_path)
                self.filled_fields.append(f"{field_name}: {file_path}")
                return True
        except Exception as e:
            self.errors.append(f"{field_name}: {str(e)[:50]}")
        return False
    
    def get_results(self) -> Dict:
        """Get fill results."""
        return {
            "filled": self.filled_fields,
            "errors": self.errors,
            "success": len(self.filled_fields) > 0 and len(self.errors) == 0
        }


class GreenhouseFiller(ATSFormFiller):
    """Fill Greenhouse ATS forms."""
    
    def fill_form(self, page, form_data: Dict) -> Dict:
        """Fill Greenhouse application form."""
        self.filled_fields = []
        self.errors = []
        
        # Greenhouse field selectors
        field_map = {
            "first_name": ["input[name='job_application[first_name]']", "#first_name"],
            "last_name": ["input[name='job_application[last_name]']", "#last_name"],
            "email": ["input[name='job_application[email]']", "#email"],
            "phone": ["input[name='job_application[phone]']", "#phone"],
            "location": ["input[name='job_application[location]']", "#location"],
            "linkedin": ["input[name*='linkedin']", "input[name*='LinkedIn']"],
            "website": ["input[name*='website']", "input[name*='url']"],
        }
        
        # Fill basic fields
        for field, value in form_data.items():
            if value and field in field_map:
                for selector in field_map[field]:
                    if self._fill_field(page, selector, value, field):
                        break
        
        # Fill cover letter
        if "cover_letter" in form_data:
            textarea = page.query_selector("textarea[name*='cover_letter']")
            if textarea:
                textarea.fill(form_data["cover_letter"])
                self.filled_fields.append("cover_letter: filled")
        
        # Upload resume
        if "resume_path" in form_data:
            self._upload_file(page, "input[type='file']", form_data["resume_path"], "resume")
        
        return self.get_results()


class LeverFiller(ATSFormFiller):
    """Fill Lever ATS forms."""
    
    def fill_form(self, page, form_data: Dict) -> Dict:
        """Fill Lever application form."""
        self.filled_fields = []
        self.errors = []
        
        # Lever field selectors
        field_map = {
            "first_name": ["input[name='name'] input", "input[name='name']"],
            "email": ["input[name='email']"],
            "phone": ["input[name='phone']"],
            "linkedin": ["input[name='urls[LinkedIn]']"],
            "website": ["input[name='urls[Portfolio]']"],
        }
        
        for field, value in form_data.items():
            if value and field in field_map:
                for selector in field_map[field]:
                    if self._fill_field(page, selector, value, field):
                        break
        
        # Fill cover letter
        if "cover_letter" in form_data:
            textarea = page.query_selector("textarea[name='comments']")
            if textarea:
                textarea.fill(form_data["cover_letter"])
                self.filled_fields.append("cover_letter: filled")
        
        # Upload resume
        if "resume_path" in form_data:
            self._upload_file(page, "input[type='file']", form_data["resume_path"], "resume")
        
        return self.get_results()


class AshbyFiller(ATSFormFiller):
    """Fill Ashby ATS forms."""
    
    def fill_form(self, page, form_data: Dict) -> Dict:
        """Fill Ashby application form."""
        self.filled_fields = []
        self.errors = []
        
        # Ashby field selectors
        field_map = {
            "first_name": ["input[name='firstName']", "input[placeholder*='First']"],
            "last_name": ["input[name='lastName']", "input[placeholder*='Last']"],
            "email": ["input[name='email']", "input[type='email']"],
            "phone": ["input[name='phone']", "input[type='tel']"],
            "linkedin": ["input[name='linkedInUrl']"],
            "website": ["input[name='website']"],
        }
        
        for field, value in form_data.items():
            if value and field in field_map:
                for selector in field_map[field]:
                    if self._fill_field(page, selector, value, field):
                        break
        
        # Fill cover letter
        if "cover_letter" in form_data:
            textarea = page.query_selector("textarea[name='coverLetter']")
            if textarea:
                textarea.fill(form_data["cover_letter"])
                self.filled_fields.append("cover_letter: filled")
        
        # Upload resume
        if "resume_path" in form_data:
            self._upload_file(page, "input[type='file']", form_data["resume_path"], "resume")
        
        return self.get_results()


class WorkableFiller(ATSFormFiller):
    """Fill Workable ATS forms."""
    
    def fill_form(self, page, form_data: Dict) -> Dict:
        """Fill Workable application form."""
        self.filled_fields = []
        self.errors = []
        
        # Workable field selectors
        field_map = {
            "first_name": ["input[name='firstname']"],
            "last_name": ["input[name='lastname']"],
            "email": ["input[name='email']"],
            "phone": ["input[name='phone']"],
        }
        
        for field, value in form_data.items():
            if value and field in field_map:
                for selector in field_map[field]:
                    if self._fill_field(page, selector, value, field):
                        break
        
        # Fill cover letter
        if "cover_letter" in form_data:
            textarea = page.query_selector("textarea[name='cover_letter']")
            if textarea:
                textarea.fill(form_data["cover_letter"])
                self.filled_fields.append("cover_letter: filled")
        
        # Upload resume
        if "resume_path" in form_data:
            self._upload_file(page, "input[type='file']", form_data["resume_path"], "resume")
        
        return self.get_results()


class GenericFiller(ATSFormFiller):
    """Fill generic application forms using smart detection."""
    
    def fill_form(self, page, form_data: Dict) -> Dict:
        """Fill generic form using smart field detection."""
        self.filled_fields = []
        self.errors = []
        
        # Smart field detection patterns
        field_patterns = {
            "first_name": ["first.?name", "fname", "given.?name"],
            "last_name": ["last.?name", "lname", "surname", "family.?name"],
            "email": ["email", "e-mail", "mail"],
            "phone": ["phone", "tel", "mobile", "contact"],
            "linkedin": ["linkedin", "linked.?in"],
            "website": ["website", "portfolio", "url", "homepage"],
        }
        
        # Get all input fields
        inputs = page.query_selector_all("input[type='text'], input[type='email'], input[type='tel'], input[type='url']")
        
        for input_el in inputs:
            name = (input_el.get_attribute("name") or "").lower()
            placeholder = (input_el.get_attribute("placeholder") or "").lower()
            label = ""
            
            # Try to find associated label
            try:
                input_id = input_el.get_attribute("id")
                if input_id:
                    label_el = page.query_selector(f"label[for='{input_id}']")
                    if label_el:
                        label = label_el.inner_text().lower()
            except:
                pass
            
            # Match field
            field_text = f"{name} {placeholder} {label}"
            
            for field_name, patterns in field_patterns.items():
                if field_name in form_data and form_data[field_name]:
                    for pattern in patterns:
                        if re.search(pattern, field_text, re.I):
                            self._fill_field(page, f"input[name='{name}']", form_data[field_name], field_name)
                            break
        
        # Fill textareas
        textareas = page.query_selector_all("textarea")
        for textarea in textareas:
            name = (textarea.get_attribute("name") or "").lower()
            if "cover" in name or "letter" in name:
                if "cover_letter" in form_data:
                    textarea.fill(form_data["cover_letter"])
                    self.filled_fields.append("cover_letter: filled")
        
        # Upload resume
        if "resume_path" in form_data:
            self._upload_file(page, "input[type='file']", form_data["resume_path"], "resume")
        
        return self.get_results()


def get_filler_for_ats(ats_type: str) -> ATSFormFiller:
    """Get the appropriate filler for an ATS type."""
    fillers = {
        "greenhouse": GreenhouseFiller,
        "lever": LeverFiller,
        "ashby": AshbyFiller,
        "workable": WorkableFiller,
    }
    
    filler_class = fillers.get(ats_type.lower(), GenericFiller)
    return filler_class()


# Import re for GenericFiller
import re
