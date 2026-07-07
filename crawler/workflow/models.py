from dataclasses import dataclass, field
from typing import List, Dict, Any
from crawler.explorer.models import InteractionEdge

@dataclass
class WorkflowStep:
    """Represents a single step (interaction + next state) in a workflow."""
    step_number: int
    action_type: str
    element_selector: str
    label: str
    target_state_id: str
    target_url: str

@dataclass
class Workflow:
    """Represents an end-to-end user workflow extracted from the state graph."""
    id: str
    name: str
    description: str
    start_state_id: str
    end_state_id: str
    steps: List[WorkflowStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_state_id": self.start_state_id,
            "end_state_id": self.end_state_id,
            "steps": [
                {
                    "step_number": s.step_number,
                    "action_type": s.action_type,
                    "element_selector": s.element_selector,
                    "label": s.label,
                    "target_state_id": s.target_state_id,
                    "target_url": s.target_url
                } for s in self.steps
            ]
        }
