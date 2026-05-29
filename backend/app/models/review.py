from pydantic import BaseModel, Field
from typing import Literal


class ReviewIssue(BaseModel):
    issue_id: str = Field(..., description="Issue唯一标识")
    severity: Literal["blocker", "major", "minor"] = Field(..., description="严重级别")
    issue_type: Literal[
        "MISSING_SOURCE",
        "SCHEMA_INVALID",
        "LOW_CONFIDENCE",
        "CONTRADICTION",
        "PII_RISK",
        "REPORT_GAP",
    ] = Field(..., description="问题类型")
    target_agent: Literal["researcher", "analyst", "editor"] = Field(..., description="目标Agent")
    target_object_id: str = Field(..., description="目标对象ID")
    message: str = Field(..., description="问题描述")
    required_fix: str = Field(..., description="要求的修复")
    status: Literal["open", "fixed", "accepted_risk"] = Field(default="open", description="Issue状态")
