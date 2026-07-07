import json
import os
from typing import Dict, Optional
from shared.logger import get_logger

logger = get_logger(__name__)

class StateCache:
    """Caches DOM hashes for URLs to enable incremental crawling."""
    
    def __init__(self, cache_file: str = "crawl_data/cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, str] = {}
        self._load_cache()
        
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded cache with {len(self.cache)} entries.")
            except Exception as e:
                logger.error(f"Failed to load cache from {self.cache_file}: {e}")
                self.cache = {}
        else:
            logger.info("No existing cache found. Starting fresh.")
            
    def save(self):
        """Persists the cache to disk."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"Saved cache to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            
    def get_hash(self, url: str) -> Optional[str]:
        """Returns the cached hash for a URL, if any."""
        return self.cache.get(url)
        
    def set_hash(self, url: str, dom_hash: str):
        """Updates the hash for a URL."""
        self.cache[url] = dom_hash
        
    def is_changed(self, url: str, new_hash: str) -> bool:
        """
        Checks if the new hash is different from the cached hash.
        If the URL is not in the cache, it is considered changed (new).
        """
        cached_hash = self.get_hash(url)
        if not cached_hash:
            return True
        return cached_hash != new_hash
