import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any
from shared.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    """Manages the FAISS index and the associated metadata (documents)."""

    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim
        # IndexFlatL2 measures L2 (Euclidean) distance
        self.index = faiss.IndexFlatL2(embedding_dim)
        # Store metadata mapping index ID -> document data
        self.documents: Dict[int, Dict[str, Any]] = {}

    def add_documents(self, docs: List[Dict[str, Any]], embeddings: np.ndarray):
        """Adds documents and their corresponding vector embeddings."""
        if len(docs) != embeddings.shape[0]:
            raise ValueError("Number of docs must match number of embeddings.")
        
        start_id = self.index.ntotal
        self.index.add(embeddings)
        
        for i, doc in enumerate(docs):
            self.documents[start_id + i] = doc
            
        logger.info(f"Added {len(docs)} documents to vector store. Total: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches for the closest vectors and returns their metadata."""
        if self.index.ntotal == 0:
            return []
            
        # FAISS expects a 2D array, even for a single query
        if len(query_embedding.shape) == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)
            
        # Ensure it's float32
        query_embedding = query_embedding.astype(np.float32)
        
        # Search returns distances and indices
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.documents: # -1 means not enough results found
                doc = self.documents[idx].copy()
                doc['_distance'] = float(distances[0][i])
                results.append(doc)
                
        return results

    def save(self, filepath_prefix: str):
        """Saves the FAISS index and the documents JSON to disk."""
        faiss.write_index(self.index, f"{filepath_prefix}.index")
        with open(f"{filepath_prefix}.json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved vector store to {filepath_prefix}.index and .json")

    def load(self, filepath_prefix: str):
        """Loads the FAISS index and the documents JSON from disk."""
        if os.path.exists(f"{filepath_prefix}.index") and os.path.exists(f"{filepath_prefix}.json"):
            self.index = faiss.read_index(f"{filepath_prefix}.index")
            with open(f"{filepath_prefix}.json", "r", encoding="utf-8") as f:
                docs_str_keys = json.load(f)
                # Convert string keys back to int
                self.documents = {int(k): v for k, v in docs_str_keys.items()}
            logger.info(f"Loaded vector store with {self.index.ntotal} items.")
        else:
            logger.warning(f"Could not find index/json at {filepath_prefix}")
