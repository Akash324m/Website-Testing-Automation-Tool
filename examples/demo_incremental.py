import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.cache.state_cache import StateCache
from crawler.extractor.models import PageData, SemanticComponent
from crawler.duplicate_detection.dom_hasher import DOMHasher
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

def main():
    logger.info("Initializing Incremental Cache...")
    cache_file = "crawl_data/demo_cache.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        
    cache = StateCache(cache_file)
    
    url = "https://shop.com/products/123"
    
    # 1. First Crawl (New Page)
    logger.info("--- 1. First Crawl ---")
    page_v1 = PageData(
        url=url,
        title="Product",
        components=[
            SemanticComponent("button", "submit", "Buy", "button.buy", "", {})
        ],
        forms=[]
    )
    
    hash_v1 = DOMHasher.compute_structural_hash(page_v1)
    
    if cache.is_changed(url, hash_v1):
        logger.info(f"Page changed (new hash: {hash_v1}). Extracting...")
        cache.set_hash(url, hash_v1)
        cache.save()
    else:
        logger.info("Page unchanged, skipping.")
        
    # 2. Second Crawl (Unchanged Page)
    logger.info("--- 2. Second Crawl (Unchanged) ---")
    # Simulate a dynamic session ID change which shouldn't affect the structural hash
    page_v2 = PageData(
        url=url,
        title="Product",
        components=[
            SemanticComponent("button", "submit", "Buy", "button.buy#session-999", "", {})
        ],
        forms=[]
    )
    
    hash_v2 = DOMHasher.compute_structural_hash(page_v2)
    
    if cache.is_changed(url, hash_v2):
        logger.info(f"Page changed (new hash: {hash_v2}). Extracting...")
        cache.set_hash(url, hash_v2)
        cache.save()
    else:
        logger.info("Page unchanged, skipping extraction.")
        
    # 3. Third Crawl (Changed Page)
    logger.info("--- 3. Third Crawl (Changed UI) ---")
    # Simulate a structural change (e.g. out of stock)
    page_v3 = PageData(
        url=url,
        title="Product - Out of Stock",
        components=[
            SemanticComponent("div", "alert", "Out of Stock", "div.alert", "", {})
        ],
        forms=[]
    )
    
    hash_v3 = DOMHasher.compute_structural_hash(page_v3)
    
    if cache.is_changed(url, hash_v3):
        logger.info(f"Page changed (new hash: {hash_v3}). Extracting...")
        cache.set_hash(url, hash_v3)
        cache.save()
    else:
        logger.info("Page unchanged, skipping extraction.")

if __name__ == "__main__":
    main()
