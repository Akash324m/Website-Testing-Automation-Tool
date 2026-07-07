import os
import json
from crawler.cache.state_cache import StateCache

def test_state_cache():
    cache_file = "tests/crawler/cache/temp_cache.json"
    
    # 1. Start fresh
    if os.path.exists(cache_file):
        os.remove(cache_file)
        
    cache = StateCache(cache_file)
    assert len(cache.cache) == 0
    
    # 2. Check a new URL
    url = "http://example.com"
    hash1 = "abc"
    assert cache.is_changed(url, hash1) == True
    
    # 3. Set hash and save
    cache.set_hash(url, hash1)
    cache.save()
    assert os.path.exists(cache_file)
    
    # 4. Load from disk and check unchanged
    cache2 = StateCache(cache_file)
    assert cache2.is_changed(url, hash1) == False
    
    # 5. Check changed hash
    hash2 = "xyz"
    assert cache2.is_changed(url, hash2) == True
    
    # Cleanup
    if os.path.exists(cache_file):
        os.remove(cache_file)
