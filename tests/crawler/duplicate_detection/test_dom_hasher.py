import pytest
from crawler.extractor.models import PageData, SemanticComponent
from crawler.duplicate_detection.dom_hasher import DOMHasher

def test_dom_hasher_ignores_dynamic_ids():
    # Page 1 has ID 123
    p1 = PageData(url="http://test.com/1", title="Page", components=[
        SemanticComponent("button", "button", "Submit", "button#submit-123.btn.btn-primary", "", {})
    ])
    
    # Page 2 has ID 456 but same structure
    p2 = PageData(url="http://test.com/2", title="Page", components=[
        SemanticComponent("button", "button", "Submit", "button#submit-456.btn.btn-primary", "", {})
    ])
    
    hash1 = DOMHasher.compute_structural_hash(p1)
    hash2 = DOMHasher.compute_structural_hash(p2)
    
    assert hash1 == hash2

def test_dom_hasher_differentiates_structures():
    p1 = PageData(url="http://test.com/1", title="Page", components=[
        SemanticComponent("button", "button", "Submit", "button.btn", "", {})
    ])
    
    p2 = PageData(url="http://test.com/1", title="Page", components=[
        SemanticComponent("a", "link", "Go", "a.link", "", {})
    ])
    
    assert DOMHasher.compute_structural_hash(p1) != DOMHasher.compute_structural_hash(p2)
