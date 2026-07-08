import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from crawler.agent.executor import ExecutionAgent

@pytest.mark.asyncio
async def test_execution_agent():
    # Mock VectorStore
    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = [{"state_id": "state_b", "url": "http://test/b"}]
    
    # Mock Embedder
    mock_embedder = MagicMock()
    mock_embedder.embed_text.return_value = [0.1, 0.2]
    
    # Mock GraphManager
    mock_graph_manager = MagicMock()
    mock_graph_manager.get_shortest_path.return_value = [
        {"action_type": "click", "selector": "button#next", "label": "Next"}
    ]
    
    # Mock BrowserManager and Page
    mock_page = AsyncMock()
    mock_context = AsyncMock()
    mock_browser_manager = AsyncMock()
    mock_browser_manager.new_context.return_value = mock_context
    mock_browser_manager.new_page.return_value = mock_page
    
    # Init Agent
    agent = ExecutionAgent(mock_vector_store, mock_embedder, mock_graph_manager, mock_browser_manager)
    
    # Run
    final_state = await agent.run("Go to next page", "state_a")
    
    assert final_state["status"] == "success"
    assert final_state["target_state_id"] == "state_b"
    assert len(final_state["execution_path"]) == 1
    
    # Verify Playwright was called
    mock_page.click.assert_called_with("button#next")
