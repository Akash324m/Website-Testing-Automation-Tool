import pytest
from crawler.explorer.graph_manager import GraphManager
from crawler.extractor.models import PageData, SemanticComponent

def test_graph_manager_add_state_and_interaction():
    manager = GraphManager()
    
    # Create mock pages
    page1 = PageData(url="http://test.com/1", title="Page 1")
    page1.components.append(SemanticComponent(type="a", role="link", label="Go to 2", css_selector="a#link2", xpath=""))
    
    page2 = PageData(url="http://test.com/2", title="Page 2")
    
    # Add states
    id1 = manager.add_state(page1)
    id2 = manager.add_state(page2)
    
    assert len(manager.states) == 2
    assert manager.graph.number_of_nodes() == 2
    
    # Add interaction
    manager.add_interaction(id1, id2, "click", "a#link2", "Go to 2")
    
    assert manager.graph.number_of_edges() == 1
    
    # Test export
    data = manager.export_graph()
    assert "nodes" in data
    
    # Handle NetworkX version differences for edge key names
    edges_key = "links" if "links" in data else "edges"
    assert edges_key in data
    assert len(data["nodes"]) == 2
    assert len(data[edges_key]) == 1
