import os
from playwright.sync_api import Page
from shared.logger import get_logger

logger = get_logger(__name__)

class ScreenshotManager:
    """Manages capturing and saving screenshots via Playwright."""
    
    def __init__(self, output_dir: str = "crawl_data/screenshots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def take_screenshot(self, page: Page, filename: str, full_page: bool = True) -> str:
        """
        Takes a screenshot of the current page.
        
        Args:
            page: Playwright Page object.
            filename: Name of the output file (e.g., 'stuck_state.png').
            full_page: Whether to capture the full scrolling page.
            
        Returns:
            The absolute path to the saved screenshot.
        """
        filepath = os.path.join(self.output_dir, filename)
        try:
            page.screenshot(path=filepath, full_page=full_page)
            logger.info(f"Screenshot saved to {filepath}")
            return os.path.abspath(filepath)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise
