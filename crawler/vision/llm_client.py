from abc import ABC, abstractmethod
from shared.logger import get_logger
import time

logger = get_logger(__name__)

class VisionLLMClient(ABC):
    """Abstract base class for a Vision LLM Client."""
    
    @abstractmethod
    def analyze_ui(self, image_path: str, prompt: str) -> str:
        """
        Analyzes a screenshot and returns actionable advice.
        """
        pass


class MockVisionLLMClient(VisionLLMClient):
    """A mocked LLM client for testing and development without API keys."""
    
    def __init__(self, mock_response: str = "I see a collapsed sidebar menu in the top left corner. Click the hamburger icon to expand it."):
        self.mock_response = mock_response

    def analyze_ui(self, image_path: str, prompt: str) -> str:
        logger.info(f"MockVisionLLMClient analyzing {image_path} with prompt: '{prompt}'")
        # Simulate network delay
        time.sleep(1.5)
        logger.info("MockVisionLLMClient generated a response.")
        return self.mock_response
