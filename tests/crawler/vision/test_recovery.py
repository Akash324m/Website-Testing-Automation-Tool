import pytest
import os
from unittest.mock import MagicMock
from crawler.vision.recovery_agent import VisionRecoveryAgent
from crawler.vision.screenshotter import ScreenshotManager
from crawler.vision.llm_client import MockVisionLLMClient

def test_vision_recovery():
    # Setup mocks
    mock_page = MagicMock()
    # Ensure the screenshot method just creates a dummy file so os.path.abspath works
    def mock_screenshot(path, full_page):
        with open(path, "w") as f:
            f.write("dummy")
            
    mock_page.screenshot.side_effect = mock_screenshot
    
    screenshotter = ScreenshotManager(output_dir="tests/crawler/vision/temp_screenshots")
    mock_llm = MockVisionLLMClient(mock_response="Click the hidden button")
    
    agent = VisionRecoveryAgent(llm_client=mock_llm, screenshot_manager=screenshotter)
    
    # Run recovery
    advice = agent.attempt_recovery(mock_page)
    
    assert advice == "Click the hidden button"
    assert mock_page.screenshot.called
    
    # Cleanup dummy files
    for f in os.listdir("tests/crawler/vision/temp_screenshots"):
        os.remove(os.path.join("tests/crawler/vision/temp_screenshots", f))
    os.rmdir("tests/crawler/vision/temp_screenshots")
