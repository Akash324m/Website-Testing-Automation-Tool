import pytest
from unittest.mock import AsyncMock, MagicMock
from crawler.explorer.navigator import Navigator
from crawler.explorer.graph_manager import GraphManager
from crawler.extractor.models import PageData

@pytest.mark.asyncio
async def test_navigator_explore():
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page_manager = AsyncMock()
    
    mock_browser.new_context.return_value = mock_context
    mock_browser.new_page.return_value = mock_page_manager
    
    mock_extractor = AsyncMock()
    mock_extractor.extract.return_value = PageData(url="http://test.com", title="Test")
    
    graph_manager = GraphManager()
    navigator = Navigator(mock_browser, mock_extractor, graph_manager)
    
    await navigator.explore("http://test.com", max_depth=1)
    
    # Verify it navigated to start URL
    mock_page_manager.navigate.assert_called_with("http://test.com")
    
    # Verify state was added
    assert len(graph_manager.states) == 1
