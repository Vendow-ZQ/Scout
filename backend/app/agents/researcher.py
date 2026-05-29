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
from app.storage.markdown_artifacts import save_evidence_markdown, save_sources_markdown


class ExtractedEvidenceItem(BaseModel):
    """LLM output: one extracted evidence card."""

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

    evidence_cards: list[ExtractedEvidenceItem] = Field(
        ..., description="从所有来源提取的证据卡片列表"
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
) -> list[EvidenceCard]:
    """Use Doubao LLM to intelligently extract evidence cards from sources."""
    # Prepare input for LLM
    sources_data = []
    for src in sources:
        sources_data.append({
            "source_id": src.source_id,
            "title": src.title,
            "source_type": src.source_type,
            "product": src.product,
            "raw_excerpt": src.raw_excerpt,
        })

    inputs = {"sources": sources_data}

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
        # Try to find matching source_id (LLM may reference by source_id or title)
        source_id = None
        for sid in source_map:
            if sid in item.reasoning or sid in item.fact:
                source_id = sid
                break

        # Fallback: assign to first source with matching product
        if source_id is None:
            for s in sources:
                if s.product == item.product or (item.product == "market" and s.product is None):
                    source_id = s.source_id
                    break

        # Final fallback: first source
        if source_id is None:
            source_id = sources[0].source_id if sources else "unknown"

        evidence.append(
            EvidenceCard(
                evidence_id=f"evd_{uuid.uuid4().hex[:8]}",
                source_id=source_id,
                product=item.product,
                dimension=item.dimension,  # type: ignore[arg-type]
                fact=item.fact,
                confidence=item.confidence,
            )
        )

    return evidence


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

        # Use LLM for intelligent evidence extraction
        evidence = _extract_evidence_with_llm(sources, task_id, run_id)

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

        log_artifact_saved(task_id, run_id, "sources", sources_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "sources_markdown", sources_md_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "evidence", evidence_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "evidence_markdown", evidence_md_ref, payload={"format": "markdown"})

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="researcher",
            agent_name="ResearcherAgent",
            payload={"source_count": len(sources), "evidence_count": len(evidence)},
            artifact_refs=[sources_ref, sources_md_ref, evidence_ref, evidence_md_ref],
        )

        return {
            "sources": sources_payload,
            "evidence": evidence_payload,
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
