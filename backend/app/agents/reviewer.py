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
    log_review_approved,
    log_review_failed,
    log_review_fixed,
)
from app.core.prompt_loader import load_agent_prompt
from app.core.state import ScoutState
from app.models.review import ReviewIssue
from app.storage.artifact_store import load_artifact, save_artifact
from app.storage.markdown_artifacts import save_review_markdown


class ReviewIssueItem(BaseModel):
    """LLM output: one review issue."""

    severity: str = Field(
        ...,
        description="严重级别: blocker(阻断) / major(重要) / minor(轻微)",
    )
    issue_type: str = Field(
        ...,
        description="问题类型: MISSING_SOURCE(缺少来源) / LOW_CONFIDENCE(置信度低) / CONTRADICTION(矛盾) / REPORT_GAP(报告缺失) / SCHEMA_INVALID(格式错误) / PII_RISK(隐私风险)",
    )
    target_agent: str = Field(
        ...,
        description="应修复的 Agent: researcher / analyst / writer",
    )
    target_object_id: str = Field(
        ...,
        description="问题对象标识，如 product:ChatGPT 或 claim:clm_xxx 或 report:swot",
    )
    message: str = Field(..., description="问题描述，中文，清晰具体")
    required_fix: str = Field(..., description="要求的修复措施，中文，可操作")


class ReviewerOutput(BaseModel):
    """LLM output schema for reviewer agent."""

    review_passed: bool = Field(..., description="是否通过审查")
    overall_assessment: str = Field(..., description="整体质量评估，200字以内")
    issues: list[ReviewIssueItem] = Field(
        default_factory=list, description="发现的问题列表"
    )
    retry_target: str | None = Field(
        default=None,
        description="如果未通过，应该重试哪个 agent: researcher / analyst / writer / None",
    )
    strengths: list[str] = Field(
        default_factory=list, description="报告/分析的优点"
    )
    coverage_assessment: dict[str, Any] = Field(
        default_factory=dict,
        description="覆盖率评估: {products_covered, dimensions_covered, gaps}",
    )


def reviewer_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Reviewer Agent checks quality via LLM-as-judge."""
    task_id = state.get("task_id", "unknown")
    run_id = state.get("run_id", "unknown")
    retry_count = state.get("retry_count", 0)

    log_node_started(
        task_id=task_id,
        run_id=run_id,
        node_name="reviewer",
        agent_name="ReviewerAgent",
        payload={"retry_count": retry_count},
    )

    try:
        evidence = state.get("evidence", [])
        claims = state.get("claims", [])
        report = state.get("report")
        profiles = state.get("profiles", [])
        sources = state.get("sources", [])

        # Get task context
        from app.storage.sqlite_store import get_task
        task = get_task(task_id)
        task_config = {}
        if task and isinstance(task.get("config"), str):
            task_config = json.loads(task["config"])
        elif task:
            task_config = task.get("config", {})

        # Expected products from task config
        expected_products = task_config.get("competitors", []) + [task_config.get("main_product", "")]
        expected_products = [p for p in expected_products if p]

        inputs = {
            "task_context": {
                "industry": task_config.get("industry", "Unknown"),
                "main_product": task_config.get("main_product", "Unknown"),
                "competitors": task_config.get("competitors", []),
                "expected_products": expected_products,
            },
            "pipeline_outputs": {
                "source_count": len(sources),
                "evidence_count": len(evidence),
                "profile_count": len(profiles),
                "claim_count": len(claims),
                "report_generated": report is not None,
            },
            "sources": [
                {"source_id": s.get("source_id"), "title": s.get("title"), "product": s.get("product")}
                for s in sources[:20]  # limit context
            ],
            "evidence": [
                {
                    "evidence_id": e.get("evidence_id"),
                    "product": e.get("product"),
                    "dimension": e.get("dimension"),
                    "fact": e.get("fact", "")[:100],
                    "confidence": e.get("confidence"),
                }
                for e in evidence[:30]  # limit context
            ],
            "profiles": [
                {
                    "name": p.get("name"),
                    "positioning": p.get("positioning", "")[:100],
                    "strengths": p.get("strengths", [])[:3],
                    "weaknesses": p.get("weaknesses", [])[:3],
                }
                for p in profiles
            ],
            "claims_summary": [
                {
                    "claim_id": c.get("claim_id"),
                    "text": c.get("text", "")[:80],
                    "claim_type": c.get("claim_type"),
                    "confidence": c.get("confidence"),
                    "evidence_count": len(c.get("evidence_ids", [])),
                }
                for c in claims[:20]
            ],
            "report_summary": {
                "executive_summary": (report.get("executive_summary", "")[:200] if report else "N/A"),
                "has_comparison_matrix": bool(report and report.get("comparison_matrix")),
                "has_swot": bool(report and report.get("swot")),
                "claim_count": report.get("claim_count", 0) if report else 0,
                "evidence_coverage": report.get("evidence_coverage", 0) if report else 0,
            },
        }

        result = llm_adapter.generate_structured(
            prompt_name="quality_review",
            inputs=inputs,
            output_schema=ReviewerOutput,
            system_prompt=load_agent_prompt("reviewer"),
            metadata={"task_id": task_id, "run_id": run_id},
            temperature=0.2,
        )

        # Load previous issues for history tracking
        previous_issues: list[dict[str, Any]] = []
        try:
            prev = load_artifact(task_id, "review.json")
            if isinstance(prev, dict):
                previous_issues = prev.get("issues", [])
        except Exception:
            pass

        # Map LLM output to ReviewIssue models
        new_issues: list[ReviewIssue] = []
        for item in result.issues:
            new_issues.append(
                ReviewIssue(
                    issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                    severity=item.severity,  # type: ignore[arg-type]
                    issue_type=item.issue_type,  # type: ignore[arg-type]
                    target_agent=item.target_agent,  # type: ignore[arg-type]
                    target_object_id=item.target_object_id,
                    message=item.message,
                    required_fix=item.required_fix,
                    status="open",
                )
            )

        # Merge with previous issues: mark fixed issues
        all_issues: list[ReviewIssue] = []
        seen_keys: set[str] = set()

        for issue in new_issues:
            key = f"{issue.issue_type}:{issue.target_object_id}"
            seen_keys.add(key)
            all_issues.append(issue)

        for prev in previous_issues:
            key = f"{prev.get('issue_type')}:{prev.get('target_object_id')}"
            if key not in seen_keys:
                if prev.get("status") == "open":
                    prev["status"] = "fixed"
                    log_review_fixed(task_id, run_id, prev.get("issue_id", ""))
                all_issues.append(ReviewIssue.model_validate(prev))

        # Determine retry target
        retry_target = result.retry_target
        has_blocker = any(i.severity == "blocker" and i.status == "open" for i in all_issues)

        # If LLM says passed but we have open blockers, trust the blockers
        if has_blocker and not retry_target:
            # Pick the first blocker's target agent
            for issue in all_issues:
                if issue.severity == "blocker" and issue.status == "open":
                    retry_target = issue.target_agent
                    break

        review_passed = result.review_passed and len([i for i in all_issues if i.status == "open"]) == 0

        # Log review results
        if review_passed:
            log_review_approved(
                task_id=task_id,
                run_id=run_id,
                payload={
                    "issue_count": len(all_issues),
                    "all_fixed": True,
                    "strengths": result.strengths,
                },
            )
        else:
            for issue in all_issues:
                if issue.status == "open":
                    log_review_failed(
                        task_id=task_id,
                        run_id=run_id,
                        issue_type=issue.issue_type,
                        target_agent=issue.target_agent,
                        message=issue.message,
                        payload={
                            "severity": issue.severity,
                            "target_object_id": issue.target_object_id,
                            "required_fix": issue.required_fix,
                        },
                    )

        # Save review artifact with history.
        review_payload = {
            "review_passed": review_passed,
            "retry_target": retry_target,
            "retry_count": retry_count,
            "overall_assessment": result.overall_assessment,
            "strengths": result.strengths,
            "coverage_assessment": result.coverage_assessment,
            "issues": [i.model_dump(mode="json") for i in all_issues],
            "issue_history": [
                {
                    "run_id": run_id,
                    "open_count": len([i for i in all_issues if i.status == "open"]),
                    "fixed_count": len([i for i in all_issues if i.status == "fixed"]),
                }
            ],
        }
        review_ref = save_artifact(task_id, "review.json", review_payload)
        review_md_ref = save_review_markdown(task_id, run_id, review_payload)

        log_artifact_saved(task_id, run_id, "review", review_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "review_markdown", review_md_ref, payload={"format": "markdown"})

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="reviewer",
            agent_name="ReviewerAgent",
            payload={
                "review_passed": review_passed,
                "issue_count": len(all_issues),
                "open_issues": len([i for i in all_issues if i.status == "open"]),
                "fixed_issues": len([i for i in all_issues if i.status == "fixed"]),
                "retry_target": retry_target,
                "overall_assessment": result.overall_assessment,
            },
            artifact_refs=[review_ref, review_md_ref],
        )

        return {
            "review_issues": [i.model_dump(mode="json") for i in all_issues],
            "review_passed": review_passed,
            "retry_target": retry_target,
            "retry_count": retry_count + (1 if retry_target else 0),
            "current_node": "reviewer",
            "node_history": state.get("node_history", []) + ["reviewer"],
        }

    except Exception as e:
        log_node_failed(
            task_id=task_id,
            run_id=run_id,
            node_name="reviewer",
            agent_name="ReviewerAgent",
            error=str(e),
        )
        raise
