import json
import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import (
    log_node_failed,
    log_node_started,
    log_node_succeeded,
    log_review_approved,
    log_review_failed,
    log_review_fixed,
)
from app.core.state import ScoutState
from app.models.review import ReviewIssue


def _check_source_coverage(evidence: list[dict], products: list[str]) -> list[ReviewIssue]:
    """Check each product has at least 2 evidence items."""
    issues = []
    product_evidence: dict[str, list[dict]] = {}
    for ev in evidence:
        p = ev.get("product", "unknown")
        if p not in product_evidence:
            product_evidence[p] = []
        product_evidence[p].append(ev)

    for product in products:
        count = len(product_evidence.get(product, []))
        if count < 2:
            issues.append(
                ReviewIssue(
                    issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                    severity="blocker" if count == 0 else "major",
                    issue_type="MISSING_SOURCE",
                    target_agent="researcher",
                    target_object_id=f"product:{product}",
                    message=f"产品 '{product}' 只有 {count} 条 evidence，要求至少 2 条",
                    required_fix=f"补充 {product} 的来源和 evidence，确保每产品不少于 2 条",
                )
            )

    # Check pricing dimension specifically
    for product in products:
        pricing_evidence = [e for e in product_evidence.get(product, []) if e.get("dimension") == "pricing"]
        if not pricing_evidence:
            # Check if the product has any source with pricing info
            pricing_keywords = ["$", "定价", "价格", "元", "免费", "付费", "订阅", "月费", "年费"]
            has_pricing_info = any(
                any(kw in (e.get("fact", "")) for kw in pricing_keywords)
                for e in product_evidence.get(product, [])
            )
            if not has_pricing_info:
                issues.append(
                    ReviewIssue(
                        issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                        severity="blocker",
                        issue_type="MISSING_SOURCE",
                        target_agent="researcher",
                        target_object_id=f"product:{product}:pricing",
                        message=f"产品 '{product}' 缺少定价信息来源",
                        required_fix=f"补充 {product} 的定价来源，或将对应 Claim 从最终报告中移除",
                    )
                )

    return issues


def _check_claim_evidence(claims: list[dict]) -> list[ReviewIssue]:
    """Check insight/recommendation claims have evidence."""
    issues = []
    for c in claims:
        if c.get("claim_type") in ("insight", "recommendation"):
            if len(c.get("evidence_ids", [])) == 0:
                issues.append(
                    ReviewIssue(
                        issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                        severity="blocker",
                        issue_type="MISSING_SOURCE",
                        target_agent="analyst",
                        target_object_id=c.get("claim_id", "unknown"),
                        message=f"Claim '{c.get('text', '')[:50]}...' 无 evidence 支撑",
                        required_fix="为 Claim 补充 evidence_ids 或降低 claim 类型",
                    )
                )
    return issues


def _check_confidence(claims: list[dict]) -> list[ReviewIssue]:
    """Check confidence threshold."""
    issues = []
    for c in claims:
        conf = c.get("confidence", 0.0)
        if conf < 0.6:
            issues.append(
                ReviewIssue(
                    issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                    severity="major",
                    issue_type="LOW_CONFIDENCE",
                    target_agent="researcher",
                    target_object_id=c.get("claim_id", "unknown"),
                    message=f"Claim confidence {conf} < 0.6",
                    required_fix="补充更多 evidence 或降低结论强度",
                )
            )
    return issues


def _check_report_completeness(report: dict | None) -> list[ReviewIssue]:
    """Check report has all required sections."""
    issues = []
    if report is None:
        issues.append(
            ReviewIssue(
                issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                severity="blocker",
                issue_type="REPORT_GAP",
                target_agent="writer",
                target_object_id="report",
                message="报告为空",
                required_fix="生成完整报告",
            )
        )
        return issues

    required_keys = ["executive_summary", "comparison_matrix", "swot", "key_claims"]
    for key in required_keys:
        if key not in report or not report[key]:
            issues.append(
                ReviewIssue(
                    issue_id=f"iss_{uuid.uuid4().hex[:8]}",
                    severity="major",
                    issue_type="REPORT_GAP",
                    target_agent="writer",
                    target_object_id=f"report:{key}",
                    message=f"报告缺少 {key} 章节",
                    required_fix=f"补齐报告的 {key} 章节",
                )
            )

    return issues


def reviewer_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Reviewer Agent checks quality and routes issues."""
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

        # Determine product list from profiles or manifest
        products = [p.get("name", "") for p in profiles if p.get("name")]
        if not products:
            products = ["ChatGPT", "Claude", "Gemini", "Genspark", "Manus"]

        all_issues: list[ReviewIssue] = []
        all_issues.extend(_check_source_coverage(evidence, products))
        all_issues.extend(_check_claim_evidence(claims))
        all_issues.extend(_check_confidence(claims))
        all_issues.extend(_check_report_completeness(report))

        # Determine retry target from highest severity issue
        retry_target = None
        has_blocker = False

        for issue in all_issues:
            if issue.status == "open":
                if issue.severity == "blocker":
                    has_blocker = True
                    if retry_target is None:
                        retry_target = issue.target_agent
                elif issue.severity == "major" and retry_target is None:
                    retry_target = issue.target_agent

        review_passed = len([i for i in all_issues if i.status == "open"]) == 0

        # Log review results
        if review_passed:
            log_review_approved(
                task_id=task_id,
                run_id=run_id,
                payload={"issue_count": len(all_issues), "all_fixed": True},
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

        # Save review artifact
        artifact_dir = Path(settings.artifact_dir) / task_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        review_ref = f"runtime/artifacts/{task_id}/review.json"
        with open(artifact_dir / "review.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "review_passed": review_passed,
                    "retry_target": retry_target,
                    "retry_count": retry_count,
                    "issues": [i.model_dump(mode="json") for i in all_issues],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="reviewer",
            agent_name="ReviewerAgent",
            payload={
                "review_passed": review_passed,
                "issue_count": len(all_issues),
                "open_issues": len([i for i in all_issues if i.status == "open"]),
                "retry_target": retry_target,
            },
        )

        # If on retry and issues are fixed, mark them as fixed
        if retry_count > 0 and not has_blocker:
            for issue in all_issues:
                if issue.status == "open" and issue.severity != "blocker":
                    issue.status = "fixed"
                    log_review_fixed(task_id, run_id, issue.issue_id)

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
