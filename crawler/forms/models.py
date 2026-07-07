from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class FieldValidation:
    """Represents HTML5 validation rules for a form field."""
    required: bool = False
    input_type: str = "text"
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    pattern: Optional[str] = None
    max_length: Optional[int] = None

@dataclass
class FormField:
    """Represents an enriched input field inside a form."""
    name: str
    logical_label: str
    css_selector: str
    tag_name: str
    validation: FieldValidation = field(default_factory=FieldValidation)
    options: List[Dict[str, str]] = field(default_factory=list)  # For selects: [{"value": "1", "text": "Option 1"}]

@dataclass
class SemanticForm:
    """Represents a fully parsed HTML form with semantic meaning."""
    id: str
    action: str
    method: str
    intent: str  # e.g., 'Login', 'Search', 'Registration', 'Unknown'
    fields: List[FormField] = field(default_factory=list)
    buttons: List[str] = field(default_factory=list)  # Labels of submit buttons

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "method": self.method,
            "intent": self.intent,
            "buttons": self.buttons,
            "fields": [
                {
                    "name": f.name,
                    "logical_label": f.logical_label,
                    "css_selector": f.css_selector,
                    "tag_name": f.tag_name,
                    "validation": {
                        "required": f.validation.required,
                        "input_type": f.validation.input_type,
                        "min_value": f.validation.min_value,
                        "max_value": f.validation.max_value,
                        "pattern": f.validation.pattern,
                        "max_length": f.validation.max_length,
                    },
                    "options": f.options
                } for f in self.fields
            ]
        }
