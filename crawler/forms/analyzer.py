import json
from typing import List, Dict, Any
from shared.logger import get_logger
from crawler.extractor.models import PageData
from .models import SemanticForm, FormField, FieldValidation

logger = get_logger(__name__)

class FormAnalyzer:
    """Enriches raw forms extracted from the DOM into SemanticForms."""

    def __init__(self, page_data: PageData):
        self.page_data = page_data

    def _parse_options(self, options_str: str) -> List[Dict[str, str]]:
        """Parses a delimited string of options into a list of dictionaries."""
        if not options_str:
            return []
        
        parsed = []
        for opt in options_str.split('|'):
            parts = opt.split('::', 1)
            if len(parts) == 2:
                parsed.append({"value": parts[0], "text": parts[1]})
        return parsed

    def _guess_form_intent(self, form_id: str, action: str, button_labels: List[str]) -> str:
        """Heuristically guesses the primary intent of the form."""
        combined_text = f"{form_id} {action} {' '.join(button_labels)}".lower()
        
        if any(kw in combined_text for kw in ['login', 'sign in', 'signin', 'auth']):
            return 'Login'
        if any(kw in combined_text for kw in ['register', 'sign up', 'signup', 'create account']):
            return 'Registration'
        if any(kw in combined_text for kw in ['search', 'find', 'query']):
            return 'Search'
        if any(kw in combined_text for kw in ['checkout', 'pay', 'billing']):
            return 'Checkout'
        if any(kw in combined_text for kw in ['contact', 'message', 'support']):
            return 'Contact'
            
        return 'Unknown'

    def analyze_forms(self) -> List[SemanticForm]:
        """Analyzes and enriches all forms found in the page data."""
        semantic_forms = []
        
        for raw_form in self.page_data.forms:
            fields = []
            
            for inp in raw_form.inputs:
                attrs = inp.attributes
                
                # Parse validation rules
                max_len_str = attrs.get('maxlength', '')
                max_len = int(max_len_str) if max_len_str and max_len_str.isdigit() else None
                
                validation = FieldValidation(
                    required=(attrs.get('required') == 'true'),
                    input_type=attrs.get('type', 'text'),
                    min_value=attrs.get('min') or None,
                    max_value=attrs.get('max') or None,
                    pattern=attrs.get('pattern') or None,
                    max_length=max_len
                )
                
                # Parse select options if present
                options = self._parse_options(attrs.get('options', ''))
                
                field = FormField(
                    name=attrs.get('name') or attrs.get('id') or inp.label,
                    logical_label=inp.label,
                    css_selector=inp.css_selector,
                    tag_name=inp.type,
                    validation=validation,
                    options=options
                )
                fields.append(field)
                
            button_labels = [btn.label for btn in raw_form.buttons]
            intent = self._guess_form_intent(raw_form.id, raw_form.action, button_labels)
            
            semantic_forms.append(SemanticForm(
                id=raw_form.id,
                action=raw_form.action,
                method=raw_form.method,
                intent=intent,
                fields=fields,
                buttons=button_labels
            ))
            
        logger.info(f"Analyzed {len(semantic_forms)} forms.")
        return semantic_forms
