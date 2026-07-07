from typing import List
from urllib.parse import urlparse, urlunparse

class URLNormalizer:
    """Normalizes clustered URLs by identifying dynamic segments and replacing them."""

    @staticmethod
    def normalize_url_cluster(urls: List[str]) -> str:
        """
        Given a list of URLs that belong to the same structural cluster,
        identifies varying path segments and replaces them with {id}.
        If there's only one URL, returns it unchanged.
        """
        if not urls:
            return ""
        if len(urls) == 1:
            return urls[0]
            
        parsed_urls = [urlparse(u) for u in urls]
        
        # We assume they share the same scheme and netloc for a given cluster
        base_parsed = parsed_urls[0]
        
        # Compare paths
        path_segments_list = [p.path.strip('/').split('/') for p in parsed_urls]
        
        # If paths have different lengths, normalization is harder; fallback to first URL
        length = len(path_segments_list[0])
        if any(len(segs) != length for segs in path_segments_list):
            return urls[0]
            
        normalized_segments = []
        for i in range(length):
            segment_values = set(segs[i] for segs in path_segments_list)
            if len(segment_values) > 1:
                # This segment varies across the cluster, it's a dynamic parameter
                normalized_segments.append("{id}")
            else:
                # Static segment
                normalized_segments.append(list(segment_values)[0])
                
        normalized_path = "/" + "/".join(normalized_segments)
        
        # Reconstruct URL (ignoring query parameters for now)
        return urlunparse((
            base_parsed.scheme,
            base_parsed.netloc,
            normalized_path,
            '', # params
            '', # query
            ''  # fragment
        ))
