from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceRecord(BaseModel):
    source_id: str = Field(..., description="来源唯一标识")
    title: str = Field(..., description="来源标题")
    source_type: Literal["official", "docs", "review", "news", "interview", "survey", "manual"] = Field(
        ..., description="来源类型"
    )
    url: str | None = Field(default=None, description="来源URL")
    product: str | None = Field(default=None, description="关联产品")
    captured_at: datetime = Field(default_factory=datetime.utcnow, description="采集时间")
    raw_excerpt: str = Field(..., description="原始摘录")
    public_or_authorized: bool = Field(default=True, description="是否公开或已授权")


class EvidenceCard(BaseModel):
    evidence_id: str = Field(..., description="证据卡唯一标识")
    source_id: str = Field(..., description="来源ID")
    product: str = Field(..., description="关联产品")
    dimension: Literal["feature", "pricing", "persona", "review", "market", "risk"] = Field(
        ..., description="分析维度"
    )
    fact: str = Field(..., description="事实陈述")
    normalized_value: dict[str, Any] = Field(default_factory=dict, description="标准化值")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")


class ProductProfile(BaseModel):
    product_id: str = Field(..., description="产品唯一标识")
    name: str = Field(..., description="产品名称")
    positioning: str = Field(..., description="产品定位")
    feature_tree: dict[str, Any] = Field(default_factory=dict, description="功能树")
    pricing_model: dict[str, Any] = Field(default_factory=dict, description="定价模型")
    target_persona: list[str] = Field(default_factory=list, description="目标用户画像")
    strengths: list[str] = Field(default_factory=list, description="优势")
    weaknesses: list[str] = Field(default_factory=list, description="短板")
    evidence_ids: list[str] = Field(default_factory=list, description="支撑证据ID列表")


class Claim(BaseModel):
    claim_id: str = Field(..., description="Claim唯一标识")
    text: str = Field(..., description="Claim文本")
    claim_type: Literal["fact", "comparison", "insight", "recommendation"] = Field(..., description="Claim类型")
    product_refs: list[str] = Field(default_factory=list, description="涉及产品")
    evidence_ids: list[str] = Field(default_factory=list, description="引用证据ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    reviewer_status: Literal["pending", "failed", "approved"] = Field(default="pending", description="Reviewer状态")
