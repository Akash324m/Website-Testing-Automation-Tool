import hashlib
from typing import List
from crawler.extractor.models import PageData, SemanticComponent

class DOMHasher:
    """Calculates a structural hash of the DOM that is invariant to content and dynamic IDs."""

    @staticmethod
    def _clean_selector(selector: str) -> str:
        """Strips likely dynamic IDs or numeric classes from a CSS selector."""
        parts = selector.split('.')
        cleaned_parts = []
        for part in parts:
            if '#' in part:
                # Strip ID completely for structural hashing
                part = part.split('#')[0]
            if not part:
                continue
            # Keep class if it doesn't look numeric/random (heuristic)
            if not any(char.isdigit() for char in part) and len(part) < 30:
                cleaned_parts.append(part)
        
        return ".".join(cleaned_parts)

    @classmethod
    def compute_structural_hash(cls, page_data: PageData) -> str:
        """
        Creates a hash based on the sequence of semantic roles and normalized CSS selectors.
        """
        # Sort components to ensure stable hashing regardless of extraction order quirks
        sorted_components = sorted(page_data.components, key=lambda c: c.css_selector)
        
        signature_parts = []
        for comp in sorted_components:
            cleaned = cls._clean_selector(comp.css_selector)
            signature_parts.append(f"{comp.type}:{comp.role}:{cleaned}")
            
        base_string = "|".join(signature_parts)
        return hashlib.md5(base_string.encode('utf-8')).hexdigest()
