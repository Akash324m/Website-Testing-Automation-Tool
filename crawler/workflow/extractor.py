import json
import networkx as nx
import hashlib
from typing import List, Dict, Any
from shared.logger import get_logger
from crawler.explorer.graph_manager import GraphManager
from .models import Workflow, WorkflowStep

logger = get_logger(__name__)

class WorkflowExtractor:
    """Extracts logical workflows from the raw state graph."""

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager
        self.graph = graph_manager.graph

    def _generate_workflow_id(self, path: List[str]) -> str:
        """Generates a stable ID for a workflow based on its state sequence."""
        path_str = "->".join(path)
        return hashlib.md5(path_str.encode('utf-8')).hexdigest()

    def _identify_task_name(self, edges: List[Dict[str, Any]]) -> str:
        """Heuristically generates a task name from the edge labels."""
        if not edges:
            return "Empty Workflow"
            
        labels = []
        for edge in edges:
            label = edge.get('label', '').strip()
            if label:
                # Remove typical verb prefixes if we want to be smart, but for now just take it
                labels.append(label)
                
        if not labels:
            return "Unknown Workflow"
            
        # Example: "Login -> Dashboard -> Profile"
        return " -> ".join(labels)

    def extract_workflows(self) -> List[Workflow]:
        """
        Extracts paths from root nodes (in-degree 0 or start pages) to leaf nodes
        or nodes containing forms (which usually signify a task destination).
        """
        if not self.graph.nodes:
            return []

        # Find all possible start nodes (nodes with 0 in-degree, or just the first node added)
        start_nodes = [n for n, d in self.graph.in_degree() if d == 0]
        if not start_nodes:
            # If there's a cycle and no clear start, just pick the first node in the dict
            start_nodes = [list(self.graph.nodes)[0]]

        # Define target nodes: leaf nodes (0 out-degree) or nodes with forms
        target_nodes = []
        for node_id in self.graph.nodes:
            if self.graph.out_degree(node_id) == 0:
                target_nodes.append(node_id)
            elif node_id in self.graph_manager.states:
                # Check if this state has forms
                if len(self.graph_manager.states[node_id].page_data.forms) > 0:
                    target_nodes.append(node_id)
                    
        # Ensure target_nodes is unique and doesn't just equal start_nodes trivially
        target_nodes = list(set(target_nodes) - set(start_nodes))
        
        if not target_nodes:
            # If no clear targets, treat all nodes at max depth from start as targets
            # This is a fallback for simple sites.
            target_nodes = [n for n in self.graph.nodes if n not in start_nodes]

        workflows = []
        for start in start_nodes:
            for target in target_nodes:
                try:
                    # Find all simple paths (this can be expensive on large graphs, limit cutoff)
                    paths = nx.all_simple_paths(self.graph, start, target, cutoff=5)
                    for path in paths:
                        # Reconstruct the workflow steps from the path
                        steps = []
                        edge_data_list = []
                        
                        for i in range(len(path) - 1):
                            u, v = path[i], path[i+1]
                            edge_data = self.graph.get_edge_data(u, v)
                            edge_data_list.append(edge_data)
                            
                            target_url = self.graph.nodes[v].get('url', '')
                            
                            step = WorkflowStep(
                                step_number=i + 1,
                                action_type=edge_data.get('action', 'click'),
                                element_selector=edge_data.get('selector', ''),
                                label=edge_data.get('label', ''),
                                target_state_id=v,
                                target_url=target_url
                            )
                            steps.append(step)
                            
                        wf_id = self._generate_workflow_id(path)
                        name = self._identify_task_name(edge_data_list)
                        
                        workflow = Workflow(
                            id=wf_id,
                            name=name,
                            description=f"Path from {self.graph.nodes[start].get('url', start)} to {self.graph.nodes[target].get('url', target)}",
                            start_state_id=start,
                            end_state_id=target,
                            steps=steps
                        )
                        workflows.append(workflow)
                except nx.NetworkXNoPath:
                    continue

        logger.info(f"Extracted {len(workflows)} workflows.")
        return workflows

    def export_workflows(self, filepath: str):
        """Extracts and saves workflows to a JSON file."""
        workflows = self.extract_workflows()
        data = [wf.to_dict() for wf in workflows]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(workflows)} workflows to {filepath}")
        return workflows
