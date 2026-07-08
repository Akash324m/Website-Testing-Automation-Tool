import asyncio
import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawler.browser.browser_manager import BrowserManager
from crawler.extractor.dom_extractor import DOMExtractor
from crawler.explorer.graph_manager import GraphManager
from crawler.explorer.navigator import Navigator
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


async def main():
    browser = BrowserManager()
    extractor = DOMExtractor()
    graph = GraphManager()
    navigator = Navigator(browser, extractor, graph)

    try:
        await browser.start()

        # We use a very simple site to avoid long crawls in the demo
        start_url = "https://fctest.fssai.gov.in/"

        # Run exploration up to depth 1 to build the initial graph
        await navigator.explore(start_url, max_depth=1)

        # Save output
        os.makedirs("crawl_data", exist_ok=True)
        graph.save("crawl_data/graph.json")

        logger.info(
            f"Exploration complete. Graph nodes: {graph.graph.number_of_nodes()}, Edges: {graph.graph.number_of_edges()}"
        )

        # Extract workflows from the generated graph
        from crawler.workflow.extractor import WorkflowExtractor

        wf_extractor = WorkflowExtractor(graph)
        wf_extractor.export_workflows("crawl_data/workflows.json")

    except Exception as e:
        logger.error(f"Error during explorer demo: {e}")
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
