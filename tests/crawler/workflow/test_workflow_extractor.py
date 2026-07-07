import pytest
import networkx as nx
from crawler.explorer.graph_manager import GraphManager
from crawler.extractor.models import PageData
from crawler.workflow.extractor import WorkflowExtractor

def test_workflow_extractor():
    graph_manager = GraphManager()
    
    # Create mock pages
    page1 = PageData(url="http://test.com/home", title="Home")
    page2 = PageData(url="http://test.com/login", title="Login")
    page3 = PageData(url="http://test.com/dashboard", title="Dashboard")
    
    # Add states
    id1 = graph_manager.add_state(page1)
    id2 = graph_manager.add_state(page2)
    id3 = graph_manager.add_state(page3)
    
    # Add interactions (Path: Home -> Login -> Dashboard)
    graph_manager.add_interaction(id1, id2, "click", "a#login", "Login")
    graph_manager.add_interaction(id2, id3, "submit", "form#auth", "Sign In")
    
    # Initialize extractor
    extractor = WorkflowExtractor(graph_manager)
    workflows = extractor.extract_workflows()
    
    # Verify extraction
    assert len(workflows) == 1
    wf = workflows[0]
    
    assert wf.start_state_id == id1
    assert wf.end_state_id == id3
    assert len(wf.steps) == 2
    
    assert wf.steps[0].action_type == "click"
    assert wf.steps[0].label == "Login"
    assert wf.steps[0].target_state_id == id2
    
    assert wf.steps[1].action_type == "submit"
    assert wf.steps[1].label == "Sign In"
    assert wf.steps[1].target_state_id == id3
    
    assert wf.name == "Login -> Sign In"
