import json
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.llm_adapter import llm_adapter
from app.core.logging import (
    log_artifact_saved,
    log_node_failed,
    log_node_started,
    log_node_succeeded,
)
from app.core.prompt_loader import load_agent_prompt
from app.core.state import ScoutState
from app.models.evidence import EvidenceCard, SourceRecord
from app.storage.artifact_store import save_artifact
from app.storage.markdown_artifacts import (
    save_evidence_markdown,
    save_research_plan_markdown,
    save_research_synthesis_markdown,
    save_sources_markdown,
)


class ExtractedEvidenceItem(BaseModel):
    """LLM output: one extracted evidence card."""

    source_id: str = Field(
        ...,
        description="必须精确引用输入 sources 中存在的 source_id。一个 Evidence Card 只能绑定一个 source_id。",
    )
    product: str = Field(..., description="关联产品名称，市场级来源用 'market'")
    dimension: str = Field(
        ...,
        description="分析维度: feature(功能) / pricing(定价) / persona(用户画像) / review(评测) / market(市场) / risk(风险)",
    )
    fact: str = Field(..., description="精炼后的事实陈述，50-250字")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度 0-1")
    reasoning: str = Field(..., description="提取理由，说明为什么这样分类")


class EvidenceExtractionOutput(BaseModel):
    """LLM output schema for evidence extraction."""

    research_plan: str = Field(
        ...,
        description="Markdown body. 说明研究问题拆解、研究 tracks、关键词/来源策略、fallback 规则和证据标准。",
    )
    evidence_cards: list[ExtractedEvidenceItem] = Field(
        ..., description="从来源中提取的高价值证据卡片列表。优先覆盖所有产品和主要研究 tracks，数量建议 24-34 条。"
    )
    research_synthesis: str = Field(
        ...,
        description="Markdown body. 汇总已发现事实、证据覆盖、信息缺口和交给 Analyst 的重点问题。",
    )


def _load_sources(task_id: str, run_id: str, schema_pack: str, use_broken: bool = False) -> list[SourceRecord]:
    pack_dir = Path(settings.data_pack_dir) / schema_pack
    if use_broken:
        sources_path = pack_dir / "broken" / "missing_pricing_source.json"
    else:
        sources_path = pack_dir / "sources.json"

    if not sources_path.exists():
        raise FileNotFoundError(f"Data pack not found: {sources_path}")

    with open(sources_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    records = [SourceRecord.model_validate(item) for item in raw]
    return records


def _extract_evidence_with_llm(
    sources: list[SourceRecord],
    task_id: str,
    run_id: str,
    task_context: dict[str, Any],
) -> tuple[list[EvidenceCard], str, str]:
    """Use Doubao LLM to intelligently extract evidence cards from sources."""
    # Prepare input for LLM
    sources_data = []
    for src in sources:
        excerpt = src.raw_excerpt
        if len(excerpt) > 900:
            excerpt = excerpt[:900] + "..."
        sources_data.append({
            "source_id": src.source_id,
            "title": src.title,
            "source_type": src.source_type,
            "url": src.url,
            "product": src.product,
            "raw_excerpt": excerpt,
        })

    inputs = {"task_context": task_context, "sources": sources_data}

    result = llm_adapter.generate_structured(
        prompt_name="evidence_extraction",
        inputs=inputs,
        output_schema=EvidenceExtractionOutput,
        system_prompt=load_agent_prompt("researcher"),
        metadata={"task_id": task_id, "run_id": run_id},
        temperature=0.2,
    )

    # Map LLM output to EvidenceCard with proper IDs
    evidence = []
    source_map = {s.source_id: s for s in sources}

    for item in result.evidence_cards:
        source_id = item.source_id if item.source_id in source_map else None
        confidence = item.confidence
        fact = item.fact.strip()
        if fact and fact[-1] not in "。.!！?？":
            fact = f"{fact}。"

        # Fallback: assign to first source with matching product
        if source_id is None:
            for s in sources:
                if s.product == item.product or (item.product == "market" and s.product is None):
                    source_id = s.source_id
                    confidence = min(confidence, 0.55)
                    break

        # Final fallback: first source
        if source_id is None:
            source_id = sources[0].source_id if sources else "unknown"
            confidence = min(confidence, 0.4)

        evidence.append(
            EvidenceCard(
                evidence_id=f"evd_{uuid.uuid4().hex[:8]}",
                source_id=source_id,
                product=item.product,
                dimension=item.dimension,  # type: ignore[arg-type]
                fact=fact,
                confidence=confidence,
            )
        )

    return evidence, result.research_plan, result.research_synthesis


def researcher_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Researcher Agent reads sources and extracts evidence via LLM."""
    task_id = state.get("task_id", "unknown")
    run_id = state.get("run_id", "unknown")
    schema_pack = state.get("schema_pack", "ai_agent")
    retry_count = state.get("retry_count", 0)
    data_mode = state.get("data_mode", "web")

    log_node_started(
        task_id=task_id,
        run_id=run_id,
        node_name="researcher",
        agent_name="ResearcherAgent",
        payload={"schema_pack": schema_pack, "data_mode": data_mode, "retry_count": retry_count},
    )

    try:
        # Broken case demo is explicit: normal mock runs should use the full source pack.
        use_broken = data_mode == "mock_broken" and retry_count == 0

        sources = _load_sources(task_id, run_id, schema_pack, use_broken=use_broken)

        from app.storage.sqlite_store import get_task

        task = get_task(task_id)
        task_config: dict[str, Any] = {}
        if task and isinstance(task.get("config"), str):
            task_config = json.loads(task["config"])
        elif task:
            task_config = task.get("config", {})

        task_context = {
            "industry": task_config.get("industry", "Unknown"),
            "region": task_config.get("region", "Unknown"),
            "main_product": task_config.get("main_product", "Unknown"),
            "competitors": task_config.get("competitors", []),
            "analysis_goal": task_config.get("analysis_goal", ""),
        }

        # Use LLM for intelligent evidence extraction
        evidence, research_plan, research_synthesis = _extract_evidence_with_llm(
            sources,
            task_id,
            run_id,
            task_context,
        )

        # Save machine-readable JSON plus human-readable Markdown sidecars.
        sources_payload = [s.model_dump(mode="json") for s in sources]
        evidence_payload = [e.model_dump(mode="json") for e in evidence]
        sources_ref = save_artifact(task_id, "sources.json", sources_payload)
        evidence_ref = save_artifact(task_id, "evidence.json", evidence_payload)
        sources_md_ref = save_sources_markdown(
            task_id,
            run_id,
            sources,
            schema_pack=schema_pack,
            data_mode=data_mode,
            use_broken=use_broken,
        )
        evidence_md_ref = save_evidence_markdown(task_id, run_id, evidence)
        research_plan_ref = save_research_plan_markdown(
            task_id,
            run_id,
            research_plan,
            schema_pack=schema_pack,
            source_count=len(sources),
        )
        research_synthesis_ref = save_research_synthesis_markdown(
            task_id,
            run_id,
            research_synthesis,
            evidence_count=len(evidence),
        )

        log_artifact_saved(task_id, run_id, "research_plan", research_plan_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "sources", sources_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "sources_markdown", sources_md_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "evidence", evidence_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "evidence_markdown", evidence_md_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "research_synthesis", research_synthesis_ref, payload={"format": "markdown"})

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="researcher",
            agent_name="ResearcherAgent",
            payload={"source_count": len(sources), "evidence_count": len(evidence)},
            artifact_refs=[
                research_plan_ref,
                sources_ref,
                sources_md_ref,
                evidence_ref,
                evidence_md_ref,
                research_synthesis_ref,
            ],
        )

        return {
            "sources": sources_payload,
            "evidence": evidence_payload,
            "research_plan": research_plan,
            "research_synthesis": research_synthesis,
            "current_node": "researcher",
            "node_history": state.get("node_history", []) + ["researcher"],
        }

    except Exception as e:
        log_node_failed(
            task_id=task_id,
            run_id=run_id,
            node_name="researcher",
            agent_name="ResearcherAgent",
            error=str(e),
        )
        raise
