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
from app.models.evidence import EvidenceCard, SourceRecord


def _load_mock_sources(task_id: str, run_id: str, schema_pack: str, use_broken: bool = False) -> list[SourceRecord]:
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


def _extract_evidence(sources: list[SourceRecord]) -> list[EvidenceCard]:
    """Extract evidence cards from sources."""
    evidence = []
    for src in sources:
        if src.product is None:
            # Market-level sources create general evidence
            evidence.append(
                EvidenceCard(
                    evidence_id=f"evd_{uuid.uuid4().hex[:8]}",
                    source_id=src.source_id,
                    product="market",
                    dimension="market",
                    fact=src.raw_excerpt[:200],
                    confidence=0.8 if src.source_type == "official" else 0.7,
                )
            )
            continue

        # Determine dimension from source type and content
        dimension = "feature"
        pricing_keywords = ["定价", "价格", "$", "元", "免费", "付费", "订阅", "月费", "年费"]
        if any(kw in src.raw_excerpt for kw in pricing_keywords):
            dimension = "pricing"
        elif "用户" in src.raw_excerpt or "persona" in src.raw_excerpt.lower() or "目标" in src.raw_excerpt:
            dimension = "persona"
        elif "评测" in src.raw_excerpt or "优势" in src.raw_excerpt or "短板" in src.raw_excerpt:
            dimension = "review"

        confidence = 0.85 if src.source_type == "official" else 0.75
        if src.source_type == "review":
            confidence = 0.7

        evidence.append(
            EvidenceCard(
                evidence_id=f"evd_{uuid.uuid4().hex[:8]}",
                source_id=src.source_id,
                product=src.product,
                dimension=dimension,
                fact=src.raw_excerpt[:250],
                confidence=confidence,
            )
        )

    return evidence


def researcher_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Researcher Agent reads sources and extracts evidence."""
    task_id = state.get("task_id", "unknown")
    run_id = state.get("run_id", "unknown")
    schema_pack = state.get("schema_pack", "ai_agent")
    retry_count = state.get("retry_count", 0)

    log_node_started(
        task_id=task_id,
        run_id=run_id,
        node_name="researcher",
        agent_name="ResearcherAgent",
        payload={"schema_pack": schema_pack, "retry_count": retry_count},
    )

    try:
        # Check if this is a retry from reviewer
        use_broken = state.get("retry_target") is None  # First run uses normal, but for demo we toggle
        # Actually: for the broken case demo, we want first run to use broken sources
        # so reviewer can detect the issue. Then on retry, we use normal sources.
        use_broken = retry_count == 0

        sources = _load_mock_sources(task_id, run_id, schema_pack, use_broken=use_broken)
        evidence = _extract_evidence(sources)

        # Save artifacts
        sources_ref = f"runtime/artifacts/{task_id}/sources.json"
        evidence_ref = f"runtime/artifacts/{task_id}/evidence.json"

        artifact_dir = Path(settings.artifact_dir) / task_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        with open(artifact_dir / "sources.json", "w", encoding="utf-8") as f:
            json.dump([s.model_dump(mode="json") for s in sources], f, ensure_ascii=False, indent=2)

        with open(artifact_dir / "evidence.json", "w", encoding="utf-8") as f:
            json.dump([e.model_dump(mode="json") for e in evidence], f, ensure_ascii=False, indent=2)

        log_artifact_saved(task_id, run_id, "sources", sources_ref)
        log_artifact_saved(task_id, run_id, "evidence", evidence_ref)

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="researcher",
            agent_name="ResearcherAgent",
            payload={"source_count": len(sources), "evidence_count": len(evidence)},
            artifact_refs=[sources_ref, evidence_ref],
        )

        return {
            "sources": [s.model_dump(mode="json") for s in sources],
            "evidence": [e.model_dump(mode="json") for e in evidence],
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
