from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from crawler.extractor.models import PageData

@dataclass
class StateNode:
    """Represents a unique state (node) in the navigation graph."""
    state_id: str
    url: str
    page_data: PageData
    hash_value: str
    is_terminal: bool = False

@dataclass
class InteractionEdge:
    """Represents an interaction (edge) between two states."""
    source_id: str
    target_id: str
    action_type: str  # e.g., 'click', 'submit'
    element_selector: str
    label: str
    timestamp: float
