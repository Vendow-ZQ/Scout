from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.analyst import analyst_node
from app.agents.researcher import researcher_node
from app.agents.reviewer import reviewer_node
from app.agents.writer import writer_node
from app.core.state import ScoutState

# Use MemorySaver for MVP demo (supports checkpoint/resume within process)
checkpointer = MemorySaver()
MAX_RETRY_COUNT = 1


def _route_after_reviewer(state: ScoutState) -> str:
    """Conditional edge: route based on reviewer result."""
    if state.get("review_passed"):
        return "end"
    target = state.get("retry_target")
    if target and state.get("retry_count", 0) <= MAX_RETRY_COUNT:
        return target
    return "end"


def build_graph() -> StateGraph:
    """Build the Scout LangGraph workflow."""
    workflow = StateGraph(ScoutState)

    # Add nodes
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)

    # Define edges
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", "reviewer")

    # Conditional edge from reviewer
    workflow.add_conditional_edges(
        "reviewer",
        _route_after_reviewer,
        {
            "end": END,
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
        },
    )

    return workflow.compile(checkpointer=checkpointer)


# Global compiled graph instance
scout_graph = build_graph()
