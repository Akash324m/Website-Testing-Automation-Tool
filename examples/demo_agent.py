import asyncio
import os
import sys

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.agent.executor import ExecutionAgent
from shared.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

# --- Mock Classes for Demo ---
class MockVectorStore:
    def search(self, query_emb, top_k=1):
        # Always return the license page
        return [{"state_id": "state_license", "url": "http://example.com/license", "title": "Download License"}]

class MockEmbedder:
    def embed_text(self, text):
        return [0.0] * 384

class MockGraphManager:
    def get_shortest_path(self, start, end):
        # Hardcode a path from Login -> Dashboard -> License
        return [
            {"action_type": "click", "selector": "button#login", "label": "Sign In"},
            {"action_type": "click", "selector": "a#menu-license", "label": "License Menu"},
            {"action_type": "click", "selector": "button#download", "label": "Download PDF"}
        ]

class MockPage:
    async def click(self, selector):
        logger.info(f"[PLAYWRIGHT MOCK] Clicked {selector}")
    async def wait_for_load_state(self):
        logger.info(f"[PLAYWRIGHT MOCK] Waiting for page load...")

class MockBrowserManager:
    async def new_context(self):
        return "mock_context"
    async def new_page(self, context):
        return MockPage()

async def main():
    logger.info("Initializing LangGraph Execution Agent...")
    
    agent = ExecutionAgent(
        vector_store=MockVectorStore(),
        embedder=MockEmbedder(),
        graph_manager=MockGraphManager(),
        browser_manager=MockBrowserManager()
    )
    
    goal = "I need to download my food license"
    logger.info(f"USER GOAL: '{goal}'")
    
    # Run the agent from a mock starting state
    result = await agent.run(goal, start_state_id="state_login")
    
    print("\n--- Agent Execution Summary ---")
    print(f"Goal: {result['goal']}")
    print(f"Target Found: {result['target_state_id']}")
    print(f"Steps Planned: {len(result['execution_path'])}")
    print(f"Final Status: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
