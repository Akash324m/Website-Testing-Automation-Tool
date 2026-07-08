from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from shared.logger import get_logger

logger = get_logger(__name__)

class AgentState(TypedDict):
    """The state of the Execution Agent workflow."""
    goal: str
    current_state_id: Optional[str]
    target_state_id: Optional[str]
    execution_path: List[Dict[str, Any]]
    status: str

def create_agent_graph(vector_store, embedder, graph_manager, browser_manager):
    """
    Creates a LangGraph workflow that executes a goal deterministically.
    
    Args:
        vector_store: VectorStore instance for semantic search.
        embedder: SemanticEmbedder instance.
        graph_manager: GraphManager instance for pathfinding.
        browser_manager: BrowserManager instance for execution.
    """
    
    def retrieve_target(state: AgentState) -> AgentState:
        """Queries the vector store to find the target state."""
        logger.info(f"Retrieving target for goal: '{state['goal']}'")
        emb = embedder.embed_text(state["goal"])
        results = vector_store.search(emb, top_k=1)
        
        if not results:
            logger.error("No semantic match found for the goal.")
            state["status"] = "failed"
            return state
            
        target = results[0]
        logger.info(f"Found target match: {target.get('title')} (URL: {target.get('url')})")
        
        state["target_state_id"] = target.get("state_id")
        return state

    def plan_path(state: AgentState) -> AgentState:
        """Finds the shortest path from the current state to the target state."""
        if state["status"] == "failed":
            return state
            
        logger.info(f"Planning path from {state['current_state_id']} to {state['target_state_id']}")
        path_actions = graph_manager.get_shortest_path(state["current_state_id"], state["target_state_id"])
        
        if path_actions is None:
            logger.error("No path found between current state and target state.")
            state["status"] = "failed"
            return state
            
        logger.info(f"Planned path with {len(path_actions)} steps.")
        state["execution_path"] = path_actions
        return state

    async def execute_path(state: AgentState) -> AgentState:
        """Executes the planned path using Playwright."""
        if state["status"] == "failed" or not state["execution_path"]:
            return state
            
        logger.info("Executing path...")
        context = await browser_manager.new_context()
        page_manager = await browser_manager.new_page(context)
        
        try:
            # First, navigate to the starting page
            start_url = graph_manager.graph.nodes[state["current_state_id"]].get("url")
            if start_url:
                await page_manager.navigate(start_url)
            else:
                logger.warning(f"No URL found for starting state {state['current_state_id']}")
            
            for step in state["execution_path"]:
                logger.info(f"Executing step: {step['action_type']} on '{step['label']}'")
                if step["action_type"] == "click":
                    await page_manager.click(step["selector"])
                    await page_manager.wait_for_load_state()
                # Additional action types (type, hover, etc.) would be handled here
                
            state["status"] = "success"
            logger.info("Execution complete!")
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            state["status"] = "failed"
        
        return state
        
    def should_continue(state: AgentState) -> str:
        if state["status"] == "failed":
            return END
        return "continue"

    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("retrieve", retrieve_target)
    workflow.add_node("plan", plan_path)
    workflow.add_node("execute", execute_path)
    
    workflow.set_entry_point("retrieve")
    
    workflow.add_conditional_edges(
        "retrieve",
        should_continue,
        {
            "continue": "plan",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "plan",
        should_continue,
        {
            "continue": "execute",
            END: END
        }
    )
    
    workflow.add_edge("execute", END)
    
    return workflow.compile()
