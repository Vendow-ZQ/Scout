import json
import uuid
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.core.llm_adapter import llm_adapter
from app.core.logging import (
    log_artifact_saved,
    log_node_failed,
    log_node_started,
    log_node_succeeded,
)
from app.core.prompt_loader import load_agent_prompt
from app.core.state import ScoutState
from app.models.evidence import Claim, ProductProfile
from app.storage.artifact_store import save_artifact
from app.storage.markdown_artifacts import (
    save_analysis_module_markdown,
    save_analysis_plan_markdown,
    save_analysis_synthesis_markdown,
    save_claims_markdown,
    save_profiles_markdown,
)


class ProfileItem(BaseModel):
    """LLM output: one product profile."""

    name: str = Field(..., description="产品名称")
    positioning: str = Field(..., description="产品定位描述，1-2句话")
    feature_tree: dict[str, list[str]] = Field(
        default_factory=dict,
        description="功能树，按分类组织的关键功能列表",
    )
    pricing_model: dict[str, str] = Field(
        default_factory=dict,
        description="定价模型，如 {'plan': '免费版/专业版', 'notes': '详细说明'}",
    )
    target_persona: list[str] = Field(
        default_factory=list, description="目标用户画像，3-5个描述"
    )
    strengths: list[str] = Field(default_factory=list, description="核心优势，3-5条")
    weaknesses: list[str] = Field(default_factory=list, description="主要短板，2-4条")
    evidence_summary: str = Field(
        ..., description="这个产品的主要证据来源总结"
    )

    @field_validator("target_persona", "strengths", "weaknesses", mode="before")
    @classmethod
    def _coerce_string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            parts = [part.strip(" -;；,，") for part in value.replace("\n", "；").split("；")]
            return [part for part in parts if part]
        return [str(value)]

    @field_validator("feature_tree", "pricing_model", mode="before")
    @classmethod
    def _coerce_dict(cls, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if value is None:
            return {}
        return {"notes": str(value)}


class ClaimItem(BaseModel):
    """LLM output: one claim."""

    text: str = Field(..., description="Claim 文本陈述，清晰、具体、可验证")
    claim_type: str = Field(
        ...,
        description="类型: fact(事实) / comparison(对比) / insight(洞察) / recommendation(建议)",
    )
    product_refs: list[str] = Field(
        default_factory=list, description="涉及的产品名称列表"
    )
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="支撑这个 claim 的 evidence_id 列表（必须从输入 evidence 中引用）",
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度 0-1")
    reasoning: str = Field(..., description="为什么这个 claim 成立")

    @field_validator("product_refs", "evidence_refs", mode="before")
    @classmethod
    def _coerce_string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [part.strip(" -;；,，") for part in value.replace("\n", "；").split("；") if part.strip(" -;；,，")]
        return [str(value)]


class AnalystOutput(BaseModel):
    """LLM output schema for analyst agent."""

    analysis_plan: str = Field(
        ...,
        description="Markdown body. 说明模块拆分、证据现实检查、分析边界和每个模块的写作目标。",
    )
    profiles: list[ProfileItem] = Field(..., description="所有产品的画像列表")
    claims: list[ClaimItem] = Field(
        ..., description="从证据中提炼的核心主张列表，必须覆盖事实、对比、洞察、建议四类"
    )
    market_analysis: str = Field(..., description="Markdown body. 市场规模/趋势/细分市场/进入窗口分析。")
    user_analysis: str = Field(..., description="Markdown body. 用户画像、需求真实性、使用场景和购买/采用阻力分析。")
    competitor_analysis: str = Field(..., description="Markdown body. 竞品分层、直接/间接竞争关系、能力矩阵和战略含义。")
    analysis_summary: str = Field(
        ..., description="Markdown body. 汇总模块结论、共识/矛盾、交给 Editor 的组稿建议。"
    )


def analyst_node(state: ScoutState) -> dict[str, Any]:
    """LangGraph node: Analyst Agent builds profiles and claims via LLM."""
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
        sources = state.get("sources", [])

        # Get task context for richer analysis
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
            "evidence": evidence,
            "research_synthesis": state.get("research_synthesis", ""),
            "source_count": len(sources),
            "evidence_count": len(evidence),
        }

        result = llm_adapter.generate_structured(
            prompt_name="analyst_profile_claim_generation",
            inputs=inputs,
            output_schema=AnalystOutput,
            system_prompt=load_agent_prompt("analyst"),
            metadata={"task_id": task_id, "run_id": run_id},
            temperature=0.3,
        )

        # Map LLM output to domain models
        profiles = []
        for p in result.profiles:
            # Collect evidence IDs for this product
            ev_ids = [
                e["evidence_id"]
                for e in evidence
                if e.get("product") == p.name
            ]
            profiles.append(
                ProductProfile(
                    product_id=f"prod_{uuid.uuid4().hex[:8]}",
                    name=p.name,
                    positioning=p.positioning,
                    feature_tree=p.feature_tree,
                    pricing_model=p.pricing_model,
                    target_persona=p.target_persona,
                    strengths=p.strengths,
                    weaknesses=p.weaknesses,
                    evidence_ids=ev_ids[:10],  # cap at 10
                )
            )

        claims = []
        for c in result.claims:
            claims.append(
                Claim(
                    claim_id=f"clm_{uuid.uuid4().hex[:8]}",
                    text=c.text,
                    claim_type=c.claim_type,  # type: ignore[arg-type]
                    product_refs=c.product_refs,
                    evidence_ids=c.evidence_refs[:5],  # cap at 5
                    confidence=c.confidence,
                )
            )

        # Save machine-readable JSON plus human-readable Markdown sidecars.
        profiles_payload = [p.model_dump(mode="json") for p in profiles]
        claims_payload = [c.model_dump(mode="json") for c in claims]
        profiles_ref = save_artifact(task_id, "profiles.json", profiles_payload)
        claims_ref = save_artifact(task_id, "claims.json", claims_payload)
        profiles_md_ref = save_profiles_markdown(task_id, run_id, profiles)
        claims_md_ref = save_claims_markdown(task_id, run_id, claims)
        analysis_plan_ref = save_analysis_plan_markdown(task_id, run_id, result.analysis_plan)
        market_ref = save_analysis_module_markdown(
            task_id,
            "market_analysis.md",
            "Market Analysis",
            result.market_analysis,
        )
        user_ref = save_analysis_module_markdown(
            task_id,
            "user_analysis.md",
            "User Analysis",
            result.user_analysis,
        )
        competitor_ref = save_analysis_module_markdown(
            task_id,
            "competitor_analysis.md",
            "Competitor Analysis",
            result.competitor_analysis,
        )
        analysis_synthesis_ref = save_analysis_synthesis_markdown(task_id, run_id, result.analysis_summary)

        log_artifact_saved(task_id, run_id, "analysis_plan", analysis_plan_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "profiles", profiles_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "profiles_markdown", profiles_md_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "claims", claims_ref, payload={"format": "json"})
        log_artifact_saved(task_id, run_id, "claims_markdown", claims_md_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "market_analysis", market_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "user_analysis", user_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "competitor_analysis", competitor_ref, payload={"format": "markdown"})
        log_artifact_saved(task_id, run_id, "analysis_synthesis", analysis_synthesis_ref, payload={"format": "markdown"})

        log_node_succeeded(
            task_id=task_id,
            run_id=run_id,
            node_name="analyst",
            agent_name="AnalystAgent",
            payload={
                "profile_count": len(profiles),
                "claim_count": len(claims),
                "analysis_summary": result.analysis_summary,
            },
            artifact_refs=[
                analysis_plan_ref,
                profiles_ref,
                profiles_md_ref,
                claims_ref,
                claims_md_ref,
                market_ref,
                user_ref,
                competitor_ref,
                analysis_synthesis_ref,
            ],
        )

        return {
            "profiles": profiles_payload,
            "claims": claims_payload,
            "analysis_plan": result.analysis_plan,
            "market_analysis": result.market_analysis,
            "user_analysis": result.user_analysis,
            "competitor_analysis": result.competitor_analysis,
            "analysis_synthesis": result.analysis_summary,
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
