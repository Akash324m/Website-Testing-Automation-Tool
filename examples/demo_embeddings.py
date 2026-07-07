import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawler.extractor.models import PageData, SemanticComponent
from crawler.embeddings.embedder import SemanticEmbedder
from crawler.embeddings.vector_store import VectorStore
from crawler.embeddings.indexer import KnowledgeIndexer
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


def main():
    logger.info("Initializing Embedder (this may take a moment to load the model)...")
    embedder = SemanticEmbedder("all-MiniLM-L6-v2")
    vector_store = VectorStore(embedding_dim=embedder.embedding_dim)
    indexer = KnowledgeIndexer(embedder, vector_store)

    # 1. Create a mock login page
    login_page = PageData(
        url="http://shop.com/login",
        title="Sign In to Your Account",
        components=[
            SemanticComponent("input", "input", "Username", "input#user", "", {}),
            SemanticComponent("input", "input", "Password", "input#pass", "", {}),
            SemanticComponent("button", "submit", "Sign In", "button#login", "", {}),
        ],
        forms=[],
    )

    # 2. Create a mock checkout page
    checkout_page = PageData(
        url="http://shop.com/checkout",
        title="Secure Checkout",
        components=[
            SemanticComponent("input", "input", "Credit Card", "input#cc", "", {}),
            SemanticComponent("button", "submit", "Pay Now", "button#pay", "", {}),
        ],
        forms=[],
    )

    logger.info("Indexing pages...")
    indexer.index_page(login_page, "state_login")
    indexer.index_page(checkout_page, "state_checkout")

    os.makedirs("crawl_data", exist_ok=True)
    vector_store.save("crawl_data/knowledge")

    # 3. Perform a semantic search
    query_text = "I need to access my account"
    logger.info(f"Querying for: '{query_text}'")

    query_emb = embedder.embed_text(query_text)
    results = vector_store.search(query_emb, top_k=1)

    print("\n--- Semantic Search Results ---")
    print(f"Query: {query_text}")
    for res in results:
        print(f"\nMatch (Distance: {res['_distance']:.4f}):")
        print(f"  URL: {res.get('url')}")
        print(f"  Title: {res.get('title')}")
        print(f"  Text: {res.get('text')}")


if __name__ == "__main__":
    main()
