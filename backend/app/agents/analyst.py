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
from app.models.evidence import Claim, EvidenceCard, ProductProfile


def _build_profiles(evidence: list[dict[str, Any]]) -> list[ProductProfile]:
    """Build product profiles from evidence cards."""
    product_evidence: dict[str, list[dict]] = {}
    for ev in evidence:
        product = ev.get("product", "unknown")
        if product not in product_evidence:
            product_evidence[product] = []
        product_evidence[product].append(ev)

    profiles = []
    for product, evs in product_evidence.items():
        if product == "market":
            continue

        # Collect evidence IDs
        ev_ids = [e["evidence_id"] for e in evs]

        # Extract features from evidence
        features = []
        strengths = []
        weaknesses = []
        pricing = {}
        persona = []

        for e in evs:
            fact = e.get("fact", "")
            dim = e.get("dimension", "feature")

            if dim == "feature":
                features.append(fact[:100])
            elif dim == "pricing":
                pricing["notes"] = fact[:150]
            elif dim == "persona":
                persona.append(fact[:100])
            elif dim == "review":
                if "优势" in fact or "strength" in fact.lower():
                    strengths.append(fact[:100])
                elif "短板" in fact or "weakness" in fact.lower():
                    weaknesses.append(fact[:100])
                else:
                    features.append(fact[:100])

        profiles.append(
            ProductProfile(
                product_id=f"prod_{uuid.uuid4().hex[:8]}",
                name=product,
                positioning=f"{product} 是 AI Agent 领域的重要产品",
                feature_tree={"核心功能": features[:5]},
                pricing_model=pricing,
                target_persona=persona or ["通用用户"],
                strengths=strengths or ["功能丰富"],
                weaknesses=weaknesses or ["待观察"],
                evidence_ids=ev_ids,
            )
        )

    return profiles


def _build_claims(profiles: list[ProductProfile], evidence: list[dict]) -> list[Claim]:
    """Build claims from profiles and evidence."""
    claims = []

    # Individual product claims
    for p in profiles:
        claims.append(
            Claim(
                claim_id=f"clm_{uuid.uuid4().hex[:8]}",
                text=f"{p.name} 定位: {p.positioning}",
                claim_type="fact",
                product_refs=[p.name],
                evidence_ids=p.evidence_ids[:2],
                confidence=0.8,
            )
        )

    # Comparison claims
    if len(profiles) >= 2:
        claims.append(
            Claim(
                claim_id=f"clm_{uuid.uuid4().hex[:8]}",
                text=f"{profiles[0].name} 和 {profiles[1].name} 在功能生态上存在明显差异",
                claim_type="comparison",
                product_refs=[profiles[0].name, profiles[1].name],
                evidence_ids=profiles[0].evidence_ids[:1] + profiles[1].evidence_ids[:1],
                confidence=0.75,
            )
        )

    # Insight claims
    claims.append(
        Claim(
            claim_id=f"clm_{uuid.uuid4().hex[:8]}",
            text="AI Agent 市场正从聊天工具向任务执行型产品演进",
            claim_type="insight",
            product_refs=[p.name for p in profiles[:3]],
            evidence_ids=[e["evidence_id"] for e in evidence if e.get("product") == "market"][:2],
            confidence=0.78,
        )
    )

    # Recommendation
    claims.append(
        Claim(
            claim_id=f"clm_{uuid.uuid4().hex[:8]}",
            text="建议关注多 Agent 协作能力和任务自主执行能力作为核心竞争力",
            claim_type="recommendation",
            product_refs=[p.name for p in profiles],
            evidence_ids=[e["evidence_id"] for e in evidence][:3],
            confidence=0.72,
        )
    )

    return claims


def analyst_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Analyst Agent builds profiles and claims."""
    task_id = state.get("task_id", "unknown")
    run_id = state.get("run_id", "unknown")

    log_node_started(
        task_id=task_id,
        run_id=run_id,
        node_name="analyst",
        agent_name="AnalystAgent",
    )

    try:
        evidence = state.get("evidence", [])
        profiles = _build_profiles(evidence)
        claims = _build_claims(profiles, evidence)

        # Save artifacts
        artifact_dir = Path(settings.artifact_dir) / task_id
        artifact_dir.mkdir(parents=True, exist_ok=True)

        profiles_ref = f"runtime/artifacts/{task_id}/profiles.json"
        claims_ref = f"runtime/artifacts/{task_id}/claims.json"

        with open(artifact_dir / "profiles.json", "w", encoding="utf-8") as f:
            json.dump([p.model_dump(mode="json") for p in profiles], f, ensure_ascii=False, indent=2)

        with open(artifact_dir / "claims.json", "w", encoding="utf-8") as f:
            json.dump([c.model_dump(mode="json") for c in claims], f, ensure_ascii=False, indent=2)

        log_artifact_saved(task_id, run_id, "profiles", profiles_ref)
        log_artifact_saved(task_id, run_id, "claims", claims_ref)

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="analyst",
            agent_name="AnalystAgent",
            payload={"profile_count": len(profiles), "claim_count": len(claims)},
            artifact_refs=[profiles_ref, claims_ref],
        )

        return {
            "profiles": [p.model_dump(mode="json") for p in profiles],
            "claims": [c.model_dump(mode="json") for c in claims],
            "current_node": "analyst",
            "node_history": state.get("node_history", []) + ["analyst"],
        }

    except Exception as e:
        log_node_failed(
            task_id=task_id,
            run_id=run_id,
            node_name="analyst",
            agent_name="AnalystAgent",
            error=str(e),
        )
        raise
