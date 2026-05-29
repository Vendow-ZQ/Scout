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


def _route_after_reviewer(state: ScoutState) -> str:
    """Reviewer writes a revision plan; it does not auto-rerun the chain."""
    return "end"


def build_graph() -> StateGraph:
    """Build the Scout LangGraph workflow."""
    workflow = StateGraph(ScoutState)

    # Add nodes
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("editor", writer_node)
    workflow.add_node("reviewer", reviewer_node)

    # Define edges
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "editor")
    workflow.add_edge("editor", "reviewer")

    # Conditional edge from reviewer
    workflow.add_conditional_edges(
        "reviewer",
        _route_after_reviewer,
        {
            "end": END,
        },
    )

    return workflow.compile(checkpointer=checkpointer)


# Global compiled graph instance
scout_graph = build_graph()
