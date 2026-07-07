import asyncio
import os
import sys
import json

# Ensure the project root is in PYTHONPATH so crawler modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawler.browser.browser_manager import BrowserManager
from crawler.extractor.dom_extractor import DOMExtractor
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


async def main():
    manager = BrowserManager()
    try:
        await manager.start()

        # Create a new context
        context = await manager.new_context()

        # Create a new page wrapper
        page_manager = await manager.new_page(context)

        # Navigate
        url = "https://epaas-uat.fssai.gov.in/"
        await page_manager.navigate(url)

        # Wait for page to be ready
        await page_manager.wait_for_load_state()

        # Initialize extractor
        extractor = DOMExtractor()

        # Extract page data using the raw playwright page
        page_data = await extractor.extract(page_manager.page)

        # Save output
        os.makedirs("crawl_data", exist_ok=True)
        output_file = "crawl_data/pages.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([page_data.to_dict()], f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully extracted DOM structure and saved to {output_file}")

    except Exception as e:
        logger.error(f"Error during extractor demo: {e}")
    finally:
        await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
