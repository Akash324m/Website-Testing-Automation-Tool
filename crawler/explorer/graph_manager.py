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

    def __init__(self, cluster_manager=None):
        self.graph = nx.DiGraph()
        self.states: Dict[str, StateNode] = {}
        # Avoid circular imports by importing here if needed, or pass from Navigator
        self.cluster_manager = cluster_manager

    def add_state(self, page_data: PageData) -> str:
        """Adds a state node if it doesn't exist. Returns the state ID (template ID)."""
        if self.cluster_manager:
            state_id = self.cluster_manager.add_page(page_data)
            url_to_use = self.cluster_manager.clusters_by_id[state_id].normalized_url
        else:
            # Fallback for simple tests
            components_str = "".join(sorted([c.css_selector for c in page_data.components]))
            base_string = f"{page_data.url.split('?')[0]}::{components_str}"
            state_id = hashlib.md5(base_string.encode('utf-8')).hexdigest()
            url_to_use = page_data.url
        
        if state_id not in self.states:
            logger.info(f"Discovered new state: {state_id} ({url_to_use})")
            node = StateNode(
                state_id=state_id,
                url=url_to_use,
                page_data=page_data,
                hash_value=state_id
            )
            self.states[state_id] = node
            self.graph.add_node(state_id, url=url_to_use, title=page_data.title)
        else:
            logger.debug(f"State {state_id} already exists.")
            # Update the graph node with the possibly newly normalized URL
            if self.cluster_manager:
                self.graph.nodes[state_id]['url'] = url_to_use
            
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

    def load(self, filepath: str):
        """Loads the graph structure from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.graph = nx.node_link_graph(data)
        logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges from {filepath}")

    def get_shortest_path(self, source_id: str, target_id: str) -> Optional[list]:
        """
        Finds the shortest path between two states in the graph and returns the 
        sequence of actions required to traverse it.
        """
        try:
            path_nodes = nx.shortest_path(self.graph, source=source_id, target=target_id)
            actions = []
            for i in range(len(path_nodes) - 1):
                u = path_nodes[i]
                v = path_nodes[i+1]
                edge_data = self.graph.get_edge_data(u, v)
                actions.append({
                    "action_type": edge_data.get("action"),
                    "selector": edge_data.get("selector"),
                    "label": edge_data.get("label")
                })
            return actions
        except nx.NetworkXNoPath:
            logger.error(f"No path found from {source_id} to {target_id}")
            return None
        except nx.NodeNotFound as e:
            logger.error(f"Node not found in graph: {e}")
            return None
