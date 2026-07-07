from playwright.sync_api import Page
from .screenshotter import ScreenshotManager
from .llm_client import VisionLLMClient
from shared.logger import get_logger
import uuid

logger = get_logger(__name__)

class VisionRecoveryAgent:
    """Orchestrates recovery by taking screenshots and querying the Vision LLM."""
    
    def __init__(self, llm_client: VisionLLMClient, screenshot_manager: ScreenshotManager):
        self.llm_client = llm_client
        self.screenshot_manager = screenshot_manager
        
    def attempt_recovery(self, page: Page) -> str:
        """
        Takes a screenshot of the current page state and asks the LLM for advice.
        
        Args:
            page: The Playwright Page object that is currently "stuck".
            
        Returns:
            A string containing the LLM's actionable advice.
        """
        logger.warning("Crawler is stuck. Initiating Vision Fallback recovery...")
        
        # 1. Take a screenshot
        filename = f"recovery_{uuid.uuid4().hex[:8]}.png"
        image_path = self.screenshot_manager.take_screenshot(page, filename)
        
        # 2. Build the prompt
        prompt = (
            "I am an automated web crawler and I am currently stuck on this page. "
            "I cannot find the next interactive element to proceed. "
            "Please analyze this screenshot and tell me if there is a hidden menu, "
            "a collapsed sidebar, an overlay modal, or any specific element I should click."
        )
        
        # 3. Ask the LLM
        advice = self.llm_client.analyze_ui(image_path, prompt)
        
        logger.info(f"Vision LLM Advice received: {advice}")
        return advice
