import asyncio
import argparse
import os
import sys

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.browser.browser_manager import BrowserManager
from crawler.extractor.dom_extractor import DOMExtractor
from crawler.explorer.graph_manager import GraphManager
from crawler.explorer.navigator import Navigator
from crawler.embeddings.vector_store import VectorStore
from crawler.embeddings.embedder import SemanticEmbedder
from crawler.embeddings.indexer import KnowledgeIndexer
from crawler.agent.executor import ExecutionAgent

def init_directories():
    os.makedirs("crawl_data", exist_ok=True)

async def crawl_phase(url: str, depth: int):
    print(f"\n=== STARTING CRAWL PHASE ON: {url} (Max Depth: {depth}) ===")
    init_directories()
    
    browser = BrowserManager()
    await browser.start()
    
    graph_manager = GraphManager()
    navigator = Navigator(browser=browser, extractor=DOMExtractor(), graph=graph_manager)
    
    print("Crawling website and mapping structure...")
    await navigator.explore(url, max_depth=depth)
    
    print("Saving NetworkX structural navigation graph...")
    graph_manager.save("crawl_data/graph.json")
    
    print("Generating semantic vector embeddings for states...")
    vector_store = VectorStore(dimension=384)
    indexer = KnowledgeIndexer(vector_store)
    
    states_list = list(graph_manager.states.values())
    if not states_list:
        print("Error: No states crawled!")
        await browser.stop()
        return
        
    indexer.index_states(states_list)
    vector_store.save("crawl_data/faiss_index.bin", "crawl_data/metadata.json")
    
    print("\n=== CRAWL PHASE COMPLETED SUCCESSFULLY! ===")
    print(f"Crawled {len(states_list)} unique states.")
    print("Files saved to 'crawl_data/' folder.")
    await browser.stop()

async def run_phase(goal: str, start_url: str):
    print(f"\n=== STARTING RUNTIME EXECUTION ===")
    print(f"Goal: '{goal}'")
    
    if not os.path.exists("crawl_data/graph.json") or not os.path.exists("crawl_data/faiss_index.bin"):
        print("Error: Crawl data files not found in 'crawl_data/'. Please run crawl phase first.")
        return

    # 1. Load Graph and Vector Database
    print("Loading mapped site graph...")
    graph_manager = GraphManager()
    graph_manager.load("crawl_data/graph.json")
    
    print("Loading vector database...")
    vector_store = VectorStore(dimension=384)
    vector_store.load("crawl_data/faiss_index.bin", "crawl_data/metadata.json")
    
    # Identify the starting state ID by matching start_url with our known nodes
    start_state_id = None
    for node_id, node_data in graph_manager.graph.nodes(data=True):
        if node_data.get('url') == start_url:
            start_state_id = node_id
            break
            
    if not start_state_id:
        # Fallback: Just take the first node in the graph if url matching fails
        start_state_id = list(graph_manager.graph.nodes)[0]
        print(f"Warning: Starting URL '{start_url}' not explicitly found in nodes. Defaulting to node ID: {start_state_id}")
    else:
        print(f"Matched start URL to node ID: {start_state_id}")

    # 2. Spin up Browser and Agent
    browser = BrowserManager()
    await browser.start()
    
    agent = ExecutionAgent(
        vector_store=vector_store,
        embedder=SemanticEmbedder(),
        graph_manager=graph_manager,
        browser_manager=browser
    )
    
    # 3. Run the Agent
    result = await agent.run(goal, start_state_id=start_state_id)
    
    print("\n=== EXECUTION COMPLETED ===")
    print(f"Goal: {result['goal']}")
    print(f"Target Found State ID: {result['target_state_id']}")
    print(f"Path Planned: {result['execution_path']}")
    print(f"Final Execution Status: {result['status']}")
    
    await browser.stop()

def main():
    parser = argparse.ArgumentParser(description="End-to-End Live Web Automation Testing Tool")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")
    
    # Crawl parser
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a website and build knowledge database")
    crawl_parser.add_argument("url", type=str, help="Starting URL to crawl")
    crawl_parser.add_argument("--depth", type=int, default=1, help="Max depth to crawl (default: 1)")
    
    # Run parser
    run_parser = subparsers.add_parser("run", help="Run the execution agent with a natural language goal")
    run_parser.add_argument("goal", type=str, help="Goal description (e.g. 'Go to login page')")
    run_parser.add_argument("start_url", type=str, help="Starting URL of the browser")
    
    args = parser.parse_args()
    
    if args.command == "crawl":
        asyncio.run(crawl_phase(args.url, args.depth))
    elif args.command == "run":
        asyncio.run(run_phase(args.goal, args.start_url))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
