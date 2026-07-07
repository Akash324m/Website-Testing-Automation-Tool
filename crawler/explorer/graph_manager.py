import json
import hashlib
import networkx as nx
from typing import Dict, Any, Optional
from shared.logger import get_logger
from crawler.extractor.models import PageData
from .models import StateNode, InteractionEdge
import time

logger = get_logger(__name__)

class GraphManager:
    """Manages the website navigation graph as a State Machine using NetworkX."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.states: Dict[str, StateNode] = {}

    def _hash_state(self, page_data: PageData) -> str:
        """
        Generates a unique hash for a state based on URL and interactive components.
        This allows detecting if we've returned to a known state even in SPAs.
        """
        # We sort components by selector to ensure stable hashing
        components_str = "".join(sorted([c.css_selector for c in page_data.components]))
        base_string = f"{page_data.url.split('?')[0]}::{components_str}"
        return hashlib.md5(base_string.encode('utf-8')).hexdigest()

    def add_state(self, page_data: PageData) -> str:
        """Adds a state node if it doesn't exist. Returns the state ID."""
        state_id = self._hash_state(page_data)
        
        if state_id not in self.states:
            logger.info(f"Discovered new state: {state_id} ({page_data.url})")
            node = StateNode(
                state_id=state_id,
                url=page_data.url,
                page_data=page_data,
                hash_value=state_id
            )
            self.states[state_id] = node
            self.graph.add_node(state_id, url=page_data.url, title=page_data.title)
        else:
            logger.debug(f"State {state_id} already exists.")
            
        return state_id

    def add_interaction(self, source_id: str, target_id: str, action_type: str, selector: str, label: str):
        """Adds a directed edge representing a user action between two states."""
        edge = InteractionEdge(
            source_id=source_id,
            target_id=target_id,
            action_type=action_type,
            element_selector=selector,
            label=label,
            timestamp=time.time()
        )
        
        self.graph.add_edge(
            source_id, 
            target_id, 
            action=action_type, 
            selector=selector, 
            label=label
        )
        logger.info(f"Added edge: {source_id} -[{action_type}: {label}]-> {target_id}")

    def export_graph(self) -> Dict[str, Any]:
        """Exports the graph to a dictionary suitable for JSON serialization."""
        data = nx.node_link_data(self.graph)
        # Add detailed component info to the nodes in the export
        for node in data['nodes']:
            state_id = node['id']
            if state_id in self.states:
                # Include just basic data to keep size manageable
                node['components_count'] = len(self.states[state_id].page_data.components)
        return data

    def save(self, filepath: str):
        """Saves the graph structure to a JSON file."""
        data = self.export_graph()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved graph to {filepath}")
