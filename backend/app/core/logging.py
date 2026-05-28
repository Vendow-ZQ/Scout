import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.models.trace import RunLogEvent


def _ensure_log_dir(task_id: str) -> Path:
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{task_id}.jsonl"


def write_event(event: RunLogEvent) -> None:
    log_path = _ensure_log_dir(event.task_id)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
    except Exception as e:
        print(f"[LOGGING WARNING] Failed to write event {event.event_id}: {e}")


def log_task_created(
    task_id: str,
    run_id: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="TASK_CREATED",
        message=f"Task {task_id} created",
        payload=payload or {},
    )
    write_event(event)
    return event


def log_run_started(
    task_id: str,
    run_id: str,
    payload: dict[str, Any] | None = None,
    git_branch: str | None = None,
    git_commit: str | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="RUN_STARTED",
        message=f"Run {run_id} started for task {task_id}",
        payload=payload or {},
        git_branch=git_branch,
        git_commit=git_commit,
    )
    write_event(event)
    return event


def log_node_started(
    task_id: str,
    run_id: str,
    node_name: str,
    agent_name: str,
    payload: dict[str, Any] | None = None,
    checkpoint_id: str | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="NODE_STARTED",
        message=f"Node {node_name} started",
        node_name=node_name,
        agent_name=agent_name,
        payload=payload or {},
        checkpoint_id=checkpoint_id,
    )
    write_event(event)
    return event


def log_node_succeeded(
    task_id: str,
    run_id: str,
    node_name: str,
    agent_name: str,
    payload: dict[str, Any] | None = None,
    artifact_refs: list[str] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="NODE_SUCCEEDED",
        message=f"Node {node_name} succeeded",
        node_name=node_name,
        agent_name=agent_name,
        payload=payload or {},
        artifact_refs=artifact_refs or [],
    )
    write_event(event)
    return event


def log_node_failed(
    task_id: str,
    run_id: str,
    node_name: str,
    agent_name: str,
    error: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="NODE_FAILED",
        message=f"Node {node_name} failed: {error}",
        node_name=node_name,
        agent_name=agent_name,
        payload=payload or {},
    )
    write_event(event)
    return event


def log_retry_scheduled(
    task_id: str,
    run_id: str,
    node_name: str,
    retry_count: int,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="RETRY_SCHEDULED",
        message=f"Retry {retry_count} scheduled for {node_name}",
        node_name=node_name,
        payload=payload or {},
    )
    write_event(event)
    return event


def log_fallback_used(
    task_id: str,
    run_id: str,
    fallback_type: str,
    reason: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="FALLBACK_USED",
        message=f"Fallback used: {fallback_type} - {reason}",
        payload={"fallback_type": fallback_type, "reason": reason, **(payload or {})},
    )
    write_event(event)
    return event


def log_artifact_saved(
    task_id: str,
    run_id: str,
    artifact_type: str,
    artifact_ref: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="ARTIFACT_SAVED",
        message=f"Artifact saved: {artifact_type} at {artifact_ref}",
        artifact_refs=[artifact_ref],
        payload={"artifact_type": artifact_type, **(payload or {})},
    )
    write_event(event)
    return event


def log_review_failed(
    task_id: str,
    run_id: str,
    issue_type: str,
    target_agent: str,
    message: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="REVIEW_FAILED",
        message=message,
        payload={"issue_type": issue_type, "target_agent": target_agent, **(payload or {})},
    )
    write_event(event)
    return event


def log_review_fixed(
    task_id: str,
    run_id: str,
    issue_id: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="REVIEW_FIXED",
        message=f"Issue {issue_id} fixed",
        payload={"issue_id": issue_id, **(payload or {})},
    )
    write_event(event)
    return event


def log_review_approved(
    task_id: str,
    run_id: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="REVIEW_APPROVED",
        message="Reviewer approved",
        payload=payload or {},
    )
    write_event(event)
    return event


def log_checkpoint_created(
    task_id: str,
    run_id: str,
    checkpoint_id: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="CHECKPOINT_CREATED",
        message=f"Checkpoint {checkpoint_id} created",
        checkpoint_id=checkpoint_id,
        payload=payload or {},
    )
    write_event(event)
    return event


def log_resumed_from_checkpoint(
    task_id: str,
    run_id: str,
    checkpoint_id: str,
    target_node: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="RESUMED_FROM_CHECKPOINT",
        message=f"Resumed from checkpoint {checkpoint_id} targeting {target_node}",
        checkpoint_id=checkpoint_id,
        node_name=target_node,
        payload=payload or {},
    )
    write_event(event)
    return event


def log_run_completed(
    task_id: str,
    run_id: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="RUN_COMPLETED",
        message=f"Run {run_id} completed",
        payload=payload or {},
    )
    write_event(event)
    return event


def log_run_failed(
    task_id: str,
    run_id: str,
    reason: str,
    payload: dict[str, Any] | None = None,
) -> RunLogEvent:
    event = RunLogEvent(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        run_id=run_id,
        event_type="RUN_FAILED",
        message=f"Run {run_id} failed: {reason}",
        payload=payload or {},
    )
    write_event(event)
    return event
