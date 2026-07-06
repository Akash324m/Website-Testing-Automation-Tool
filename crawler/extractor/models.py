from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class DOMNode:
    """Represents a node in the DOM tree."""
    tag: str
    attributes: Dict[str, str] = field(default_factory=dict)
    text: str = ""
    is_visible: bool = True
    bounding_box: Optional[Dict[str, float]] = None
    children: List['DOMNode'] = field(default_factory=list)

@dataclass
class SemanticComponent:
    """Represents a semantic, interactive component on the page."""
    type: str  # e.g., 'button', 'link', 'input', 'heading'
    role: str
    label: str
    css_selector: str
    xpath: str
    attributes: Dict[str, str] = field(default_factory=dict)

@dataclass
class Form:
    """Represents an HTML form."""
    id: str
    action: str
    method: str
    inputs: List[SemanticComponent] = field(default_factory=list)
    buttons: List[SemanticComponent] = field(default_factory=list)

@dataclass
class PageData:
    """Contains all structured data extracted from a single webpage."""
    url: str
    title: str
    metadata: Dict[str, str] = field(default_factory=dict)
    headings: List[str] = field(default_factory=list)
    components: List[SemanticComponent] = field(default_factory=list)
    forms: List[Form] = field(default_factory=list)
    raw_html: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the page data to a JSON-serializable dictionary (excluding raw HTML)."""
        return {
            "url": self.url,
            "title": self.title,
            "metadata": self.metadata,
            "headings": self.headings,
            "components": [
                {
                    "type": c.type,
                    "role": c.role,
                    "label": c.label,
                    "css_selector": c.css_selector,
                    "xpath": c.xpath,
                    "attributes": c.attributes
                } for c in self.components
            ],
            "forms": [
                {
                    "id": f.id,
                    "action": f.action,
                    "method": f.method,
                    "inputs": [{"label": i.label, "type": i.type} for i in f.inputs],
                    "buttons": [{"label": b.label, "type": b.type} for b in f.buttons]
                } for f in self.forms
            ]
        }
