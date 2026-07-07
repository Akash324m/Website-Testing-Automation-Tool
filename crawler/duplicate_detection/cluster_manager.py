from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid
from shared.logger import get_logger
from crawler.extractor.models import PageData
from .dom_hasher import DOMHasher
from .url_normalizer import URLNormalizer

logger = get_logger(__name__)

@dataclass
class TemplateCluster:
    """Represents a cluster of identical or highly similar pages."""
    template_id: str
    structural_hash: str
    normalized_url: str
    example_urls: List[str] = field(default_factory=list)

class ClusterManager:
    """Manages template clustering and dynamic URL resolution."""

    def __init__(self):
        self.clusters_by_hash: Dict[str, TemplateCluster] = {}
        self.clusters_by_id: Dict[str, TemplateCluster] = {}

    def add_page(self, page_data: PageData) -> str:
        """
        Computes structural hash, clusters the page, normalizes URL, 
        and returns the template_id.
        """
        structural_hash = DOMHasher.compute_structural_hash(page_data)
        
        if structural_hash in self.clusters_by_hash:
            # Match found
            cluster = self.clusters_by_hash[structural_hash]
            
            # If URL is new, add it and recalculate the normalized URL
            clean_url = page_data.url.split('?')[0]
            if clean_url not in cluster.example_urls:
                cluster.example_urls.append(clean_url)
                cluster.normalized_url = URLNormalizer.normalize_url_cluster(cluster.example_urls)
                logger.info(f"Updated cluster {cluster.template_id} normalized URL to: {cluster.normalized_url}")
                
            return cluster.template_id
            
        else:
            # New template discovered
            template_id = f"tpl_{uuid.uuid4().hex[:8]}"
            clean_url = page_data.url.split('?')[0]
            
            cluster = TemplateCluster(
                template_id=template_id,
                structural_hash=structural_hash,
                normalized_url=clean_url,
                example_urls=[clean_url]
            )
            
            self.clusters_by_hash[structural_hash] = cluster
            self.clusters_by_id[template_id] = cluster
            
            logger.info(f"Created new template cluster: {template_id} ({clean_url})")
            return template_id
