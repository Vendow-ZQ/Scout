import json
import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import (
    log_artifact_saved,
    log_node_failed,
    log_node_started,
    log_node_succeeded,
)
from app.core.state import ScoutState


def _build_report(profiles: list[dict], claims: list[dict]) -> dict[str, Any]:
    """Build structured report from profiles and claims."""
    # Filter claims: insight/recommendation must have evidence
    valid_claims = []
    for c in claims:
        if c.get("claim_type") in ("insight", "recommendation"):
            if len(c.get("evidence_ids", [])) >= 1:
                valid_claims.append(c)
            else:
                # Skip claims without evidence for critical sections
                continue
        else:
            valid_claims.append(c)

    # Build comparison matrix
    matrix = {
        "dimensions": ["功能生态", "定价", "目标用户", "优势", "短板"],
        "products": [],
    }
    for p in profiles:
        matrix["products"].append({
            "name": p.get("name", ""),
            "功能生态": ", ".join(p.get("feature_tree", {}).get("核心功能", [])[:3]),
            "定价": p.get("pricing_model", {}).get("notes", "未公开"),
            "目标用户": ", ".join(p.get("target_persona", [])[:2]),
            "优势": ", ".join(p.get("strengths", [])[:2]),
            "短板": ", ".join(p.get("weaknesses", [])[:2]),
        })

    # SWOT analysis
    swot = {"S": [], "W": [], "O": [], "T": []}
    for c in valid_claims:
        ct = c.get("claim_type", "")
        text = c.get("text", "")
        if ct == "comparison":
            swot["S"].append(text)
        elif ct == "insight":
            swot["O"].append(text)
        elif ct == "recommendation":
            swot["O"].append(text)

    # Ensure SWOT has content
    if not swot["S"]:
        swot["S"] = ["各产品功能差异化明显"]
    if not swot["W"]:
        swot["W"] = ["部分产品定价策略不明确"]
    if not swot["O"]:
        swot["O"] = ["AI Agent 向任务执行演进是重大机会"]
    if not swot["T"]:
        swot["T"] = ["竞争激烈，技术迭代快"]

    report = {
        "report_id": f"rpt_{uuid.uuid4().hex[:8]}",
        "executive_summary": "本报告对主流 AI Agent 产品进行了竞品分析，涵盖 ChatGPT、Claude、Gemini、Genspark、Manus 五款产品。",
        "scope": "分析范围包括功能生态、定价模型、目标用户画像、优劣势对比及市场机会。",
        "comparison_matrix": matrix,
        "swot": swot,
        "opportunities": [c for c in valid_claims if c.get("claim_type") == "recommendation"],
        "key_claims": valid_claims[:12],
        "claim_count": len(valid_claims),
        "evidence_coverage": _calc_coverage(valid_claims),
        "source_appendix": [],
    }

    return report


def _calc_coverage(claims: list[dict]) -> float:
    if not claims:
        return 0.0
    with_evidence = sum(1 for c in claims if len(c.get("evidence_ids", [])) > 0)
    return round(with_evidence / len(claims), 2)


def writer_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Writer Agent generates report draft."""
    task_id = state.get("task_id", "unknown")
    run_id = state.get("run_id", "unknown")

    log_node_started(
        task_id=task_id,
        run_id=run_id,
        node_name="writer",
        agent_name="WriterAgent",
    )

    try:
        profiles = state.get("profiles", [])
        claims = state.get("claims", [])
        report = _build_report(profiles, claims)

        # Save artifact
        artifact_dir = Path(settings.artifact_dir) / task_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        report_ref = f"runtime/artifacts/{task_id}/report.json"
        with open(artifact_dir / "report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        log_artifact_saved(task_id, run_id, "report", report_ref)

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="writer",
            agent_name="WriterAgent",
            payload={
                "claim_count": report["claim_count"],
                "evidence_coverage": report["evidence_coverage"],
            },
            artifact_refs=[report_ref],
        )

        return {
            "report": report,
            "current_node": "writer",
            "node_history": state.get("node_history", []) + ["writer"],
        }

    except Exception as e:
        log_node_failed(
            task_id=task_id,
            run_id=run_id,
            node_name="writer",
            agent_name="WriterAgent",
            error=str(e),
        )
        raise
