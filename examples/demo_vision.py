import os
import sys
from playwright.sync_api import sync_playwright

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.vision.screenshotter import ScreenshotManager
from crawler.vision.llm_client import MockVisionLLMClient
from crawler.vision.recovery_agent import VisionRecoveryAgent
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

def main():
    logger.info("Initializing Vision Fallback modules...")
    screenshotter = ScreenshotManager()
    llm_client = MockVisionLLMClient(mock_response="The main content is inside an iframe. Switch to the iframe to interact with the form.")
    agent = VisionRecoveryAgent(llm_client, screenshotter)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to a page that might be tricky
        logger.info("Navigating to example.com...")
        page.goto("https://example.com")
        
        # Simulate being stuck and invoking the recovery agent
        logger.info("Simulating being stuck. Invoking VisionRecoveryAgent...")
        advice = agent.attempt_recovery(page)
        
        print("\n--- Vision Recovery Result ---")
        print(f"Actionable Advice: {advice}")
        print("------------------------------\n")
        
        browser.close()

if __name__ == "__main__":
    main()
