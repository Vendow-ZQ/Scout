import json
from pathlib import Path
from typing import Any

from app.core.config import settings


def _artifact_ref(task_id: str, filename: str) -> str:
    return f"runtime/artifacts/{task_id}/{filename}"


def _artifact_path(task_id: str, filename: str) -> Path:
    if Path(filename).name != filename or filename in {".", ".."}:
        raise ValueError(f"Artifact filename must be a basename: {filename}")
    path = Path(settings.artifact_dir) / task_id / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _as_dict(item: Any) -> dict[str, Any]:
    if hasattr(item, "model_dump"):
        return item.model_dump(mode="json")
    return dict(item)


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        value = ", ".join(str(v) for v in value)
    elif isinstance(value, dict):
        value = "; ".join(f"{k}: {v}" for k, v in value.items())
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _bullet_list(items: list[Any] | tuple[Any, ...] | None) -> str:
    if not items:
        return "- 信息不足"
    return "\n".join(f"- {item}" for item in items)


def _blockquote(text: Any) -> str:
    content = str(text or "").strip()
    if not content:
        return "> 信息不足"
    return "\n".join(f"> {line}" if line else ">" for line in content.splitlines())


def _write_markdown(task_id: str, filename: str, lines: list[str]) -> str:
    path = _artifact_path(task_id, filename)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return _artifact_ref(task_id, filename)


def save_markdown_artifact(task_id: str, filename: str, content: str) -> str:
    """Save a named Markdown artifact produced by an agent."""
    cleaned = (content or "").strip()
    if not cleaned:
        cleaned = "# Empty Artifact\n\n信息不足。"
    path = _artifact_path(task_id, filename)
    path.write_text(cleaned.rstrip() + "\n", encoding="utf-8")
    return _artifact_ref(task_id, filename)


def save_research_plan_markdown(
    task_id: str,
    run_id: str,
    content: str,
    *,
    schema_pack: str,
    source_count: int,
) -> str:
    prefix = [
        "# Research Plan",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- schema_pack: `{schema_pack}`",
        f"- source_count: `{source_count}`",
        "",
    ]
    return _write_markdown(task_id, "research_plan.md", prefix + [content])


def save_research_synthesis_markdown(
    task_id: str,
    run_id: str,
    content: str,
    *,
    evidence_count: int,
) -> str:
    prefix = [
        "# Research Synthesis",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- evidence_count: `{evidence_count}`",
        "",
    ]
    return _write_markdown(task_id, "research_synthesis.md", prefix + [content])


def save_analysis_plan_markdown(task_id: str, run_id: str, content: str) -> str:
    return _write_markdown(
        task_id,
        "analysis_plan.md",
        ["# Analysis Plan", "", f"- task_id: `{task_id}`", f"- run_id: `{run_id}`", "", content],
    )


def save_analysis_module_markdown(task_id: str, filename: str, title: str, content: str) -> str:
    if not content.strip().startswith("#"):
        content = f"# {title}\n\n{content}"
    return save_markdown_artifact(task_id, filename, content)


def save_analysis_synthesis_markdown(task_id: str, run_id: str, content: str) -> str:
    return _write_markdown(
        task_id,
        "analysis_synthesis.md",
        ["# Analysis Synthesis", "", f"- task_id: `{task_id}`", f"- run_id: `{run_id}`", "", content],
    )


def save_editorial_plan_markdown(task_id: str, run_id: str, content: str) -> str:
    return _write_markdown(
        task_id,
        "editorial_plan.md",
        ["# Editorial Plan", "", f"- task_id: `{task_id}`", f"- run_id: `{run_id}`", "", content],
    )


def save_editorial_notes_markdown(task_id: str, run_id: str, content: str) -> str:
    return _write_markdown(
        task_id,
        "editorial_notes.md",
        ["# Editorial Notes", "", f"- task_id: `{task_id}`", f"- run_id: `{run_id}`", "", content],
    )


def save_sources_markdown(
    task_id: str,
    run_id: str,
    sources: list[Any],
    *,
    schema_pack: str,
    data_mode: str,
    use_broken: bool,
) -> str:
    rows = [_as_dict(source) for source in sources]
    lines = [
        "# Sources Artifact",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- schema_pack: `{schema_pack}`",
        f"- data_mode: `{data_mode}`",
        f"- mock_source_mode: `{'broken_first_pass' if use_broken else 'normal_pack'}`",
        f"- source_count: `{len(rows)}`",
        "",
        "## Source Index",
        "",
        "| source_id | type | product | title | url |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item.get("source_id")),
                    _cell(item.get("source_type")),
                    _cell(item.get("product") or "market"),
                    _cell(item.get("title")),
                    _cell(item.get("url")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Raw Excerpts"])
    for item in rows:
        lines.extend(
            [
                "",
                f"### {item.get('source_id')} - {item.get('title')}",
                "",
                f"- product: `{item.get('product') or 'market'}`",
                f"- source_type: `{item.get('source_type')}`",
                f"- public_or_authorized: `{item.get('public_or_authorized')}`",
                "",
                _blockquote(item.get("raw_excerpt")),
            ]
        )
    return _write_markdown(task_id, "sources.md", lines)


def save_evidence_markdown(task_id: str, run_id: str, evidence: list[Any]) -> str:
    rows = [_as_dict(item) for item in evidence]
    lines = [
        "# Evidence Artifact",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- evidence_count: `{len(rows)}`",
        "",
        "| evidence_id | product | dimension | confidence | source_id | fact |",
        "|---|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item.get("evidence_id")),
                    _cell(item.get("product")),
                    _cell(item.get("dimension")),
                    _cell(item.get("confidence")),
                    _cell(item.get("source_id")),
                    _cell(item.get("fact")),
                ]
            )
            + " |"
        )
    return _write_markdown(task_id, "evidence.md", lines)


def save_profiles_markdown(task_id: str, run_id: str, profiles: list[Any]) -> str:
    rows = [_as_dict(item) for item in profiles]
    lines = [
        "# Product Profiles Artifact",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- profile_count: `{len(rows)}`",
    ]
    for item in rows:
        lines.extend(
            [
                "",
                f"## {item.get('name')}",
                "",
                f"- product_id: `{item.get('product_id')}`",
                f"- positioning: {item.get('positioning') or '信息不足'}",
                "",
                "### Feature Tree",
            ]
        )
        feature_tree = item.get("feature_tree") or {}
        if feature_tree:
            for group, features in feature_tree.items():
                lines.append(f"- {group}: {_cell(features)}")
        else:
            lines.append("- 信息不足")

        lines.extend(
            [
                "",
                "### Pricing Model",
                _bullet_list([f"{k}: {v}" for k, v in (item.get("pricing_model") or {}).items()]),
                "",
                "### Target Persona",
                _bullet_list(item.get("target_persona")),
                "",
                "### Strengths",
                _bullet_list(item.get("strengths")),
                "",
                "### Weaknesses",
                _bullet_list(item.get("weaknesses")),
                "",
                "### Evidence IDs",
                _bullet_list(item.get("evidence_ids")),
            ]
        )
    return _write_markdown(task_id, "profiles.md", lines)


def save_claims_markdown(task_id: str, run_id: str, claims: list[Any]) -> str:
    rows = [_as_dict(item) for item in claims]
    lines = [
        "# Claims Artifact",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- claim_count: `{len(rows)}`",
        "",
        "| claim_id | type | confidence | products | evidence_ids | text |",
        "|---|---|---|---|---|---|",
    ]
    for item in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item.get("claim_id")),
                    _cell(item.get("claim_type")),
                    _cell(item.get("confidence")),
                    _cell(item.get("product_refs")),
                    _cell(item.get("evidence_ids")),
                    _cell(item.get("text")),
                ]
            )
            + " |"
        )
    return _write_markdown(task_id, "claims.md", lines)


def save_report_markdown(task_id: str, run_id: str, report: dict[str, Any]) -> str:
    matrix = report.get("comparison_matrix") or {}
    dimensions = matrix.get("dimensions") or []
    products = matrix.get("products") or []
    lines = [
        "# Final Competitive Analysis Report",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- report_id: `{report.get('report_id')}`",
        f"- claim_count: `{report.get('claim_count', 0)}`",
        f"- evidence_coverage: `{report.get('evidence_coverage', 0)}`",
        "",
        "## Executive Summary",
        "",
        str(report.get("executive_summary") or "信息不足"),
        "",
        "## Scope",
        "",
        str(report.get("scope") or "信息不足"),
        "",
        "## Comparison Matrix",
        "",
    ]

    if dimensions and products:
        lines.append("| product | " + " | ".join(_cell(d) for d in dimensions) + " |")
        lines.append("|---|" + "|".join("---" for _ in dimensions) + "|")
        for product in products:
            lines.append(
                "| "
                + _cell(product.get("name"))
                + " | "
                + " | ".join(_cell(product.get(dim)) for dim in dimensions)
                + " |"
            )
    else:
        lines.append("信息不足")

    swot = report.get("swot") or {}
    lines.extend(["", "## SWOT"])
    for label in ("S", "W", "O", "T"):
        lines.extend(["", f"### {label}", _bullet_list(swot.get(label))])

    lines.extend(["", "## Opportunities"])
    opportunities = report.get("opportunities") or []
    if opportunities:
        for item in opportunities:
            if isinstance(item, dict):
                lines.append(f"- {item.get('text') or item}")
                if item.get("reasoning"):
                    lines.append(f"  - reasoning: {item.get('reasoning')}")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("- 信息不足")

    lines.extend(["", "## Key Claims"])
    key_claims = report.get("key_claims") or []
    if key_claims:
        for item in key_claims:
            if isinstance(item, dict):
                confidence = item.get("confidence") or item.get("confidence_label") or item.get("置信度")
                evidence_refs = item.get("evidence_refs") or item.get("evidence_ids")
                prefix = f"【置信度：{confidence}】" if confidence else ""
                lines.append(f"- {prefix}{item.get('text') or item}")
                if item.get("reasoning"):
                    lines.append(f"  - reasoning: {item.get('reasoning')}")
                if evidence_refs:
                    lines.append(f"  - evidence: {_cell(evidence_refs)}")
            else:
                lines.append(f"- {item}")
    else:
        lines.append("- 信息不足")

    lines.extend(
        [
            "",
            "## Evidence Coverage Assessment",
            "",
            str(report.get("evidence_coverage_assessment") or "信息不足"),
            "",
            "## Conclusion",
            "",
            str(report.get("conclusion") or "信息不足"),
        ]
    )
    return _write_markdown(task_id, "final_report.md", lines)


def save_review_scorecard_markdown(task_id: str, run_id: str, review: dict[str, Any]) -> str:
    issues = review.get("issues") or []
    lines = [
        "# Review Scorecard",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- review_passed: `{review.get('review_passed')}`",
        f"- retry_target: `{review.get('retry_target')}`",
        f"- retry_count: `{review.get('retry_count')}`",
        f"- open_issues: `{len([i for i in issues if i.get('status') == 'open'])}`",
        "",
        "## Overall Assessment",
        "",
        str(review.get("overall_assessment") or "信息不足"),
        "",
        "## Strengths",
        _bullet_list(review.get("strengths")),
        "",
        "## Coverage Assessment",
        "",
        "```json",
        json.dumps(review.get("coverage_assessment") or {}, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Issues",
        "",
        "| issue_id | severity | type | status | target_agent | target_object_id | message | required_fix |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in issues:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(item.get("issue_id")),
                    _cell(item.get("severity")),
                    _cell(item.get("issue_type")),
                    _cell(item.get("status")),
                    _cell(item.get("target_agent")),
                    _cell(item.get("target_object_id")),
                    _cell(item.get("message")),
                    _cell(item.get("required_fix")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Issue History"])
    for item in review.get("issue_history") or []:
        lines.append(
            f"- run_id `{item.get('run_id')}`: open={item.get('open_count')}, fixed={item.get('fixed_count')}"
        )
    if not review.get("issue_history"):
        lines.append("- 暂无历史")

    return _write_markdown(task_id, "review_scorecard.md", lines)


def save_revision_plan_markdown(task_id: str, run_id: str, review: dict[str, Any]) -> str:
    open_issues = [item for item in review.get("issues") or [] if item.get("status") == "open"]
    issues = [
        item
        for item in open_issues
        if not review.get("review_passed") or item.get("severity") in {"blocker", "major"}
    ]
    lines = [
        "# Revision Plan",
        "",
        f"- task_id: `{task_id}`",
        f"- run_id: `{run_id}`",
        f"- verdict: `{review.get('verdict') or ('pass' if review.get('review_passed') else 'revise')}`",
        f"- open_issues: `{len(issues)}`",
        "",
        "## Default Policy",
        "",
        "Reviewer does not automatically rerun the full chain. It points to the exact artifact and owner. P0 only supports Editor regeneration from existing analysis for report-layer issues.",
        "",
        "## Required Fixes",
        "",
    ]
    if not issues:
        lines.append("- No required fixes. Report can be accepted.")
    for issue in issues:
        lines.extend(
            [
                f"### {issue.get('issue_id')} - {issue.get('issue_type')}",
                "",
                f"- severity: `{issue.get('severity')}`",
                f"- target_agent: `{issue.get('target_agent')}`",
                f"- target_object_id: `{issue.get('target_object_id')}`",
                "",
                f"**Issue**: {issue.get('message')}",
                "",
                f"**Required fix**: {issue.get('required_fix')}",
                "",
            ]
        )
    if review.get("revision_plan"):
        lines.extend(["", "## Committee Notes", "", str(review.get("revision_plan"))])
    return _write_markdown(task_id, "revision_plan.md", lines)
