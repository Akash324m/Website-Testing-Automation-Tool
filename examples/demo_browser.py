import asyncio
import os
import sys

# Ensure the project root is in PYTHONPATH so crawler modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawler.browser.browser_manager import BrowserManager
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
        await page_manager.navigate("https://fctest.fssai.gov.in/")

        # Wait for page to be ready
        await page_manager.wait_for_load_state()

        # Take a screenshot
        os.makedirs("crawl_data/screenshots", exist_ok=True)
        await page_manager.take_screenshot("crawl_data/screenshots/example.png")
        logger.info("Screenshot saved successfully.")

        # Save session
        await manager.save_state(context, "crawl_data/sessions/example_state.json")
        logger.info("Session state saved successfully.")

    except Exception as e:
        logger.error(f"Error during demo: {e}")
    finally:
        await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
