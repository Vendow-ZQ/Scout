import json
import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.core.llm_adapter import llm_adapter
from app.core.logging import (
    log_artifact_saved,
    log_node_failed,
    log_node_started,
    log_node_succeeded,
)
from app.core.prompt_loader import load_agent_prompt
from app.core.state import ScoutState
from app.storage.artifact_store import save_artifact
from app.storage.markdown_artifacts import (
    save_editorial_notes_markdown,
    save_editorial_plan_markdown,
    save_report_markdown,
)


class ComparisonMatrixItem(BaseModel):
    """One product row in comparison matrix."""

    name: str = Field(..., description="产品名称")
    dimensions: dict[str, str] = Field(
        ..., description="各维度对比值，如 {'功能生态': '...', '定价': '...'}"
    )


class SWOT(BaseModel):
    """SWOT analysis."""

    S: list[str] = Field(..., description="优势 Strengths")
    W: list[str] = Field(..., description="劣势 Weaknesses")
    O: list[str] = Field(..., description="机会 Opportunities")
    T: list[str] = Field(..., description="威胁 Threats")


class ReportOutput(BaseModel):
    """LLM output schema for editor agent."""

    editorial_plan: str = Field(..., description="Markdown body. 说明如何把 Analyst modules 编成一份完整报告。")
    executive_summary: str = Field(..., description="执行摘要，200-400字，概括分析核心发现")
    scope: str = Field(..., description="分析范围说明")
    comparison_matrix: list[ComparisonMatrixItem] = Field(
        ..., description="竞品对比矩阵，每个产品一行"
    )
    swot: SWOT = Field(..., description="SWOT 分析")
    opportunities: list[dict[str, Any]] = Field(
        ..., description="市场机会列表，每项包含 text 和 reasoning"
    )
    key_claims: list[dict[str, Any]] = Field(
        ..., description="关键主张列表（从前序节点 claims 中筛选并润色）"
    )
    conclusion: str = Field(..., description="结论与行动建议")
    evidence_coverage_assessment: str = Field(
        ..., description="对证据覆盖率的评估：哪些 claim 证据充分，哪些不足"
    )
    editorial_notes: str = Field(..., description="Markdown body. 编者说明：重组了哪些观点、哪些不确定性被保留、哪些内容不应过度解读。")


def writer_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Editor Agent generates the final report via LLM."""
    task_id = state.get("task_id", "unknown")
    run_id = state.get("run_id", "unknown")

    log_node_started(
        task_id=task_id,
        run_id=run_id,
        node_name="editor",
        agent_name="EditorAgent",
    )

    try:
        profiles = state.get("profiles", [])
        claims = state.get("claims", [])
        evidence = state.get("evidence", [])
        analysis_modules = {
            "market_analysis": state.get("market_analysis", ""),
            "user_analysis": state.get("user_analysis", ""),
            "competitor_analysis": state.get("competitor_analysis", ""),
            "analysis_synthesis": state.get("analysis_synthesis", ""),
        }

        # Get task context
        from app.storage.sqlite_store import get_task
        task = get_task(task_id)
        task_config = {}
        if task and isinstance(task.get("config"), str):
            task_config = json.loads(task["config"])
        elif task:
            task_config = task.get("config", {})

        inputs = {
            "task_context": {
                "industry": task_config.get("industry", "Unknown"),
                "main_product": task_config.get("main_product", "Unknown"),
                "competitors": task_config.get("competitors", []),
                "analysis_goal": task_config.get("analysis_goal", ""),
            },
            "profiles": profiles,
            "claims": claims,
            "analysis_modules": analysis_modules,
            "evidence_summary": {
                "total_evidence": len(evidence),
                "products_covered": list(set(e.get("product", "") for e in evidence)),
                "dimensions_covered": list(set(e.get("dimension", "") for e in evidence)),
            },
        }

        result = llm_adapter.generate_structured(
            prompt_name="report_generation",
            inputs=inputs,
            output_schema=ReportOutput,
            system_prompt=load_agent_prompt("editor"),
            metadata={"task_id": task_id, "run_id": run_id},
            temperature=0.4,
        )

        # Calculate evidence coverage
        claim_count = len(claims)
        claims_with_evidence = sum(
            1 for c in claims if len(c.get("evidence_ids", [])) > 0
        )
        coverage = round(claims_with_evidence / claim_count, 2) if claim_count > 0 else 0.0

        # Build final report
        report = {
            "report_id": f"rpt_{uuid.uuid4().hex[:8]}",
            "executive_summary": result.executive_summary,
            "scope": result.scope,
            "comparison_matrix": {
                "dimensions": list(result.comparison_matrix[0].dimensions.keys()) if result.comparison_matrix else [],
                "products": [
                    {
                        "name": item.name,
                        **item.dimensions,
                    }
                    for item in result.comparison_matrix
                ],
            },
            "swot": {
                "S": result.swot.S,
                "W": result.swot.W,
                "O": result.swot.O,
                "T": result.swot.T,
            },
            "opportunities": result.opportunities,
            "key_claims": result.key_claims,
            "conclusion": result.conclusion,
            "claim_count": claim_count,
            "evidence_coverage": coverage,
            "evidence_coverage_assessment": result.evidence_coverage_assessment,
            "editorial_plan": result.editorial_plan,
            "editorial_notes": result.editorial_notes,
            "source_appendix": [],
        }

        # Save machine-readable JSON plus human-readable Markdown sidecar.
        report_ref = save_artifact(task_id, "report.json", report)
        report_md_ref = save_report_markdown(task_id, run_id, report)
        editorial_plan_ref = save_editorial_plan_markdown(task_id, run_id, result.editorial_plan)
        editorial_notes_ref = save_editorial_notes_markdown(task_id, run_id, result.editorial_notes)

        log_artifact_saved(task_id, run_id, "report", report_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "final_report", report_md_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "editorial_plan", editorial_plan_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "editorial_notes", editorial_notes_ref, payload={"format": "markdown"})

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="editor",
            agent_name="EditorAgent",
            payload={
                "claim_count": claim_count,
                "evidence_coverage": coverage,
            },
            artifact_refs=[editorial_plan_ref, report_ref, report_md_ref, editorial_notes_ref],
        )

        return {
            "report": report,
            "editorial_plan": result.editorial_plan,
            "editorial_notes": result.editorial_notes,
            "current_node": "editor",
            "node_history": state.get("node_history", []) + ["editor"],
        }

    except Exception as e:
        log_node_failed(
            task_id=task_id,
            run_id=run_id,
            node_name="editor",
            agent_name="EditorAgent",
            error=str(e),
        )
        raise
