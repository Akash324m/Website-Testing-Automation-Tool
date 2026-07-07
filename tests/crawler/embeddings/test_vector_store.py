import pytest
import numpy as np
import os
from crawler.embeddings.vector_store import VectorStore

def test_vector_store():
    dim = 4
    store = VectorStore(embedding_dim=dim)
    
    docs = [
        {"id": "doc1", "text": "Hello world"},
        {"id": "doc2", "text": "Testing vector store"},
        {"id": "doc3", "text": "Goodbye"}
    ]
    
    # Create some dummy embeddings
    embeddings = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0, 0.0]
    ], dtype=np.float32)
    
    store.add_documents(docs, embeddings)
    assert store.index.ntotal == 3
    
    # Query close to doc1
    query = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float32)
    results = store.search(query, top_k=2)
    
    assert len(results) == 2
    assert results[0]["id"] == "doc1"  # Closest to [1,0,0,0]
    
    # Test save/load
    store.save("test_index")
    assert os.path.exists("test_index.index")
    assert os.path.exists("test_index.json")
    
    store2 = VectorStore(embedding_dim=dim)
    store2.load("test_index")
    assert store2.index.ntotal == 3
    assert len(store2.documents) == 3
    
    # Cleanup
    os.remove("test_index.index")
    os.remove("test_index.json")
