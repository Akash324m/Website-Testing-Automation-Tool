from shared.logger import get_logger
from crawler.agent.graph import create_agent_graph


logger = get_logger(__name__)


class ExecutionAgent:
    """Wraps the LangGraph workflow to execute goals on the website."""

    def __init__(self, vector_store, embedder, graph_manager, browser_manager):
        self.workflow = create_agent_graph(
            vector_store, embedder, graph_manager, browser_manager
        )

    async def run(self, goal: str, start_state_id: str):
        """
        Executes the given goal starting from start_state_id.
        """
        logger.info(
            f"Starting ExecutionAgent with goal: '{goal}' from state: '{start_state_id}'"
        )

        initial_state = {
            "goal": goal,
            "current_state_id": start_state_id,
            "target_state_id": None,
            "execution_path": [],
            "status": "pending",
        }

        final_state = await self.workflow.ainvoke(initial_state)

        if final_state["status"] == "success":
            logger.info("Goal successfully executed!")
        else:
            logger.error("Goal execution failed.")

        return final_state
