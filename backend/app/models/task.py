from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    task_id: str = Field(..., description="任务唯一标识")
    industry: str = Field(..., description="行业方向")
    region: str = Field(..., description="分析地区")
    main_product: str = Field(..., description="待分析主品")
    competitors: list[str] = Field(..., description="竞品列表")
    analysis_goal: str = Field(..., description="分析目标")
    data_mode: Literal["mock", "mock_broken", "web", "hybrid"] = Field(default="web", description="数据模式")
    schema_pack: str = Field(default="ai_agent", description="使用的 Schema Pack")


class TaskStatus(BaseModel):
    task_id: str
    status: Literal["created", "running", "review_failed", "completed", "needs_human_fix", "failed"] = Field(
        default="created"
    )
    current_node: str | None = None
    progress_percent: int = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    run_id: str | None = None
