import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from shared.logger import get_logger

logger = get_logger(__name__)

class SemanticEmbedder:
    """Wraps the SentenceTransformer model to generate semantic embeddings."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        # We can fetch embedding dimension from the model
        self.embedding_dim = self.model.get_embedding_dimension()
        logger.info(f"Model loaded. Dimension: {self.embedding_dim}")

    def embed_text(self, text: str) -> np.ndarray:
        """Embeds a single string into a 1D numpy array."""
        # Convert to numpy array of float32 for FAISS compatibility
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embeds a list of strings into a 2D numpy array."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)
