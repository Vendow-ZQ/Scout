import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.graph import scout_graph
from app.core.logging import (
    log_run_completed,
    log_run_failed,
    log_run_started,
    log_task_created,
)
from app.core.state import ScoutState
from app.models.task import TaskSpec, TaskStatus
from app.storage.sqlite_store import (
    create_task,
    get_task,
    list_tasks,
    update_task_status,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    industry: str
    region: str
    main_product: str
    competitors: list[str]
    analysis_goal: str
    data_mode: str = "mock"
    schema_pack: str = "ai_agent"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    created_at: str


@router.post("", response_model=TaskResponse)
def api_create_task(req: CreateTaskRequest) -> TaskResponse:
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    config = req.model_dump()
    config["task_id"] = task_id

    create_task(task_id, config)
    log_task_created(
        task_id=task_id,
        run_id=run_id,
        payload=config,
    )

    return TaskResponse(
        task_id=task_id,
        status="created",
        created_at=datetime.utcnow().isoformat(),
    )


@router.get("")
def api_list_tasks() -> list[dict[str, Any]]:
    return list_tasks()


@router.get("/{task_id}")
def api_get_task(task_id: str) -> dict[str, Any]:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/run")
async def api_run_task(task_id: str) -> dict[str, Any]:
    import asyncio

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    config = task.get("config", "{}")
    if isinstance(config, str):
        import json

        config = json.loads(config)

    update_task_status(
        task_id=task_id,
        status="running",
        run_id=run_id,
    )

    log_run_started(
        task_id=task_id,
        run_id=run_id,
        payload={"schema_pack": config.get("schema_pack"), "data_mode": config.get("data_mode")},
    )

    try:
        # Build initial state
        initial_state: ScoutState = {
            "task_id": task_id,
            "run_id": run_id,
            "schema_pack": config.get("schema_pack", "ai_agent"),
            "data_mode": config.get("data_mode", "mock"),
            "sources": [],
            "evidence": [],
            "profiles": [],
            "claims": [],
            "report": None,
            "review_issues": [],
            "review_passed": False,
            "retry_target": None,
            "retry_count": 0,
            "current_node": None,
            "node_history": [],
            "trace_refs": [],
            "messages": [],
        }

        # Run graph in thread pool to avoid blocking event loop
        thread_id = f"{task_id}_{run_id}"
        result = await asyncio.to_thread(
            scout_graph.invoke,
            initial_state,
            config={"configurable": {"thread_id": thread_id}},
        )

        # Update task status
        final_status = "completed" if result.get("review_passed") else "review_failed"
        update_task_status(
            task_id=task_id,
            status=final_status,
            current_node=result.get("current_node"),
            progress_percent=100 if result.get("review_passed") else 80,
        )

        if result.get("review_passed"):
            log_run_completed(
                task_id=task_id,
                run_id=run_id,
                payload={
                    "node_history": result.get("node_history", []),
                    "claim_count": result.get("report", {}).get("claim_count", 0),
                },
            )
        else:
            log_run_failed(
                task_id=task_id,
                run_id=run_id,
                reason=f"Reviewer failed with target: {result.get('retry_target')}",
                payload={
                    "issues": result.get("review_issues", []),
                    "retry_target": result.get("retry_target"),
                },
            )

        return {
            "task_id": task_id,
            "run_id": run_id,
            "status": final_status,
            "review_passed": result.get("review_passed"),
            "retry_target": result.get("retry_target"),
            "node_history": result.get("node_history", []),
        }

    except Exception as e:
        log_run_failed(task_id=task_id, run_id=run_id, reason=str(e))
        update_task_status(task_id=task_id, status="failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/events")
def api_get_events(task_id: str) -> list[dict[str, Any]]:
    """Get run events for a task from JSONL log."""
    from pathlib import Path

    from app.core.config import settings

    log_path = Path(settings.log_dir) / f"{task_id}.jsonl"
    if not log_path.exists():
        return []

    events = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                import json

                events.append(json.loads(line))

    return events
