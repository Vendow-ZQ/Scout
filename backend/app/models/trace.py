from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentTraceMirror(BaseModel):
    trace_id: str = Field(..., description="Trace唯一标识")
    task_id: str = Field(..., description="任务ID")
    langsmith_url: str | None = Field(default=None, description="LangSmith URL")
    agent_name: str = Field(..., description="Agent名称")
    node_name: str = Field(..., description="节点名称")
    input_snapshot: dict[str, Any] = Field(default_factory=dict, description="输入快照")
    output_snapshot: dict[str, Any] = Field(default_factory=dict, description="输出快照")
    token_usage: dict[str, int] = Field(default_factory=dict, description="Token消耗")
    latency_ms: int = Field(..., description="耗时毫秒")
    status: Literal["success", "failed", "retried", "skipped"] = Field(..., description="状态")
    error_message: str | None = Field(default=None, description="错误信息")


class RunLogEvent(BaseModel):
    event_id: str = Field(..., description="事件唯一标识")
    task_id: str = Field(..., description="任务ID")
    run_id: str = Field(..., description="运行ID")
    request_id: str | None = Field(default=None, description="请求ID")
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = Field(default="INFO", description="日志级别")
    event_type: Literal[
        "TASK_CREATED",
        "RUN_STARTED",
        "RUN_COMPLETED",
        "RUN_FAILED",
        "NODE_STARTED",
        "NODE_SUCCEEDED",
        "NODE_FAILED",
        "RETRY_SCHEDULED",
        "FALLBACK_USED",
        "ARTIFACT_SAVED",
        "REVIEW_FAILED",
        "REVIEW_FIXED",
        "REVIEW_APPROVED",
        "CHECKPOINT_CREATED",
        "RESUMED_FROM_CHECKPOINT",
        "HUMAN_EDIT_APPLIED",
        "GIT_CONTEXT_CAPTURED",
    ] = Field(..., description="事件类型")
    message: str = Field(..., description="事件消息")
    node_name: str | None = Field(default=None, description="节点名称")
    agent_name: str | None = Field(default=None, description="Agent名称")
    payload: dict[str, Any] = Field(default_factory=dict, description="附加数据")
    artifact_refs: list[str] = Field(default_factory=list, description="产物引用")
    trace_id: str | None = Field(default=None, description="Trace ID")
    checkpoint_id: str | None = Field(default=None, description="Checkpoint ID")
    git_branch: str | None = Field(default=None, description="Git分支")
    git_commit: str | None = Field(default=None, description="Git提交")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
