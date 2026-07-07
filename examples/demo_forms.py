import asyncio
import os
import sys
import json

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawler.browser.browser_manager import BrowserManager
from crawler.extractor.dom_extractor import DOMExtractor
from crawler.forms.analyzer import FormAnalyzer
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


async def main():
    browser = BrowserManager()
    extractor = DOMExtractor()

    try:
        await browser.start()
        context = await browser.new_context()
        page_manager = await browser.new_page(context)

        # Wikipedia login page is a good example of a form
        target_url = "https://fctest.fssai.gov.in/"
        logger.info(f"Navigating to {target_url}")

        await page_manager.navigate(target_url)
        await page_manager.wait_for_load_state()

        # Extract basic DOM
        page_data = await extractor.extract(page_manager.page)

        # Analyze forms
        form_analyzer = FormAnalyzer(page_data)
        semantic_forms = form_analyzer.analyze_forms()

        # Output
        os.makedirs("crawl_data", exist_ok=True)
        out_path = "crawl_data/forms.json"

        data = [sf.to_dict() for sf in semantic_forms]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(semantic_forms)} enriched forms to {out_path}")

        # Print a quick summary
        for sf in semantic_forms:
            print(f"\nForm ID: {sf.id} | Intent: {sf.intent}")
            print(f"Action: {sf.action} | Method: {sf.method}")
            print(f"Buttons: {sf.buttons}")
            for field in sf.fields:
                req = "*" if field.validation.required else ""
                print(
                    f"  - [{field.tag_name}] {field.logical_label} (name={field.name}) {req}"
                )
                if field.validation.max_length:
                    print(f"      maxlen: {field.validation.max_length}")
                if field.options:
                    print(f"      options: {len(field.options)}")

    except Exception as e:
        logger.error(f"Error during form demo: {e}")
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
