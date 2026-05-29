from typing import Annotated, Any

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ScoutState(TypedDict, total=False):
    """Unified state for LangGraph Scout workflow."""

    # Task identity
    task_id: str
    run_id: str
    schema_pack: str
    data_mode: str

    # Agent inputs/outputs
    sources: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    research_plan: str
    research_synthesis: str
    profiles: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    analysis_plan: str
    market_analysis: str
    user_analysis: str
    competitor_analysis: str
    analysis_synthesis: str
    report: dict[str, Any] | None
    editorial_plan: str
    editorial_notes: str

    # Reviewer feedback
    review_issues: list[dict[str, Any]]
    review_passed: bool
    retry_target: str | None  # researcher | analyst | editor; ownership only, no automatic rerun
    retry_count: int

    # Observability
    current_node: str | None
    node_history: list[str]
    trace_refs: list[str]

    # Messages (for LangGraph)
    messages: Annotated[list, add_messages]
