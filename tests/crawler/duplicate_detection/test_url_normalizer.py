import pytest
from crawler.duplicate_detection.url_normalizer import URLNormalizer

def test_url_normalizer():
    urls = [
        "http://test.com/product/123/view",
        "http://test.com/product/456/view",
        "http://test.com/product/789/view"
    ]
    
    normalized = URLNormalizer.normalize_url_cluster(urls)
    assert normalized == "http://test.com/product/{id}/view"

def test_url_normalizer_single_url():
    urls = ["http://test.com/product/123/view"]
    normalized = URLNormalizer.normalize_url_cluster(urls)
    assert normalized == "http://test.com/product/123/view"

def test_url_normalizer_different_lengths():
    urls = [
        "http://test.com/product/123",
        "http://test.com/product/456/view"
    ]
    normalized = URLNormalizer.normalize_url_cluster(urls)
    # Should fallback to first URL if lengths differ
    assert normalized == "http://test.com/product/123"
