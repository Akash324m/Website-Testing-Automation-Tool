import json
import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.extractor.models import PageData, SemanticComponent
from crawler.duplicate_detection.cluster_manager import ClusterManager
from crawler.explorer.graph_manager import GraphManager
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

def create_mock_page(url: str, title: str, button_id: str) -> PageData:
    """Creates a mock page with a predictable DOM structure but dynamic IDs."""
    return PageData(
        url=url,
        title=title,
        components=[
            SemanticComponent("div", "container", "", "div.container", "", {}),
            SemanticComponent("h1", "heading", "Product Details", "h1.title", "", {}),
            # Dynamic ID that should be ignored by the structural hasher
            SemanticComponent("button", "button", "Buy Now", f"button#buy-{button_id}.btn.btn-primary", "", {})
        ],
        forms=[]
    )

def main():
    cluster_manager = ClusterManager()
    graph_manager = GraphManager(cluster_manager=cluster_manager)

    # 1. Add three identical products with different URLs and dynamic component IDs
    pages = [
        create_mock_page("http://shop.com/product/123", "Product 123", "123"),
        create_mock_page("http://shop.com/product/456", "Product 456", "456"),
        create_mock_page("http://shop.com/product/789", "Product 789", "789"),
    ]

    for p in pages:
        logger.info(f"Adding page: {p.url}")
        state_id = graph_manager.add_state(p)
        logger.info(f" -> Assigned to state node: {state_id}")

    # 2. Add one completely different page
    contact_page = PageData(
        url="http://shop.com/contact",
        title="Contact Us",
        components=[
            SemanticComponent("form", "form", "", "form#contact-form", "", {}),
            SemanticComponent("input", "input", "Email", "input#email", "", {"type": "email"})
        ],
        forms=[]
    )
    
    logger.info(f"Adding page: {contact_page.url}")
    state_id = graph_manager.add_state(contact_page)
    logger.info(f" -> Assigned to state node: {state_id}")

    # 3. Output results
    os.makedirs("crawl_data", exist_ok=True)
    out_path = "crawl_data/duplicate_graph.json"
    graph_manager.save(out_path)

    print(f"\n--- Cluster Results ---")
    print(f"Total original pages: 4")
    print(f"Total graph nodes (states): {len(graph_manager.states)}")
    
    for tpl_id, cluster in cluster_manager.clusters_by_id.items():
        print(f"\nTemplate: {tpl_id}")
        print(f"  Normalized URL: {cluster.normalized_url}")
        print(f"  Matched URLs:   {len(cluster.example_urls)}")
        for u in cluster.example_urls:
            print(f"    - {u}")

if __name__ == "__main__":
    main()
