import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pathlib import Path

from app.core.config import settings
from app.core.graph import scout_graph
from app.core.logging import (
    log_run_completed,
    log_run_failed,
    log_run_started,
    log_task_created,
)
from app.core.state import ScoutState
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

        # Generate Run Summary
        _generate_run_summary(
            task_id=task_id,
            run_id=run_id,
            config=config,
            result=result,
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


@router.get("/{task_id}/summary")
def api_get_summary(task_id: str) -> dict[str, Any]:
    """Get Run Summary markdown for a task."""
    summary_path = Path(settings.run_dir) / task_id / "summary.md"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found")
    with open(summary_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"task_id": task_id, "content": content}


def _generate_run_summary(
    task_id: str,
    run_id: str,
    config: dict[str, Any],
    result: dict[str, Any],
) -> None:
    """Generate Run Summary markdown after a run completes."""
    import subprocess

    report = result.get("report", {})
    issues = result.get("review_issues", [])
    node_history = result.get("node_history", [])

    # Get git context
    try:
        git_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=Path(__file__).parent.parent.parent.parent,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        git_branch = "unknown"

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).parent.parent.parent.parent,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        git_commit = "unknown"

    # Build summary
    summary = f"""# Run Summary

- **task_id**: {task_id}
- **run_id**: {run_id}
- **git_branch**: {git_branch}
- **git_commit**: {git_commit}
- **data_pack**: {config.get("schema_pack", "ai_agent")}
- **schema_pack**: {config.get("schema_pack", "ai_agent")}
- **langsmith_trace**: N/A (mock mode)
- **fallback_used**: mock_llm, mock_data_pack
- **reviewer_issues**: {len(issues)}
- **final_report**: {report.get("claim_count", 0)} claims, {(report.get("evidence_coverage", 0) * 100):.0f}% evidence coverage
- **demo_notes**: End-to-end completed with Reviewer loop. Node history: {' -> '.join(node_history)}

## Reviewer Issues

"""
    if issues:
        for issue in issues:
            status_icon = "✅" if issue.get("status") in ("fixed", "accepted_risk") else "❌"
            summary += f"- {status_icon} [{issue.get('severity', '')}] {issue.get('issue_type', '')}: {issue.get('message', '')[:100]}\\n"
    else:
        summary += "- No issues found.\\n"

    summary += f"""
## Node Execution History

"""
    for i, node in enumerate(node_history, 1):
        summary += f"{i}. {node}\\n"

    summary += f"""
## Artifacts

- `runtime/artifacts/{task_id}/sources.json`
- `runtime/artifacts/{task_id}/evidence.json`
- `runtime/artifacts/{task_id}/profiles.json`
- `runtime/artifacts/{task_id}/claims.json`
- `runtime/artifacts/{task_id}/report.json`
- `runtime/artifacts/{task_id}/review.json`
- `runtime/logs/{task_id}.jsonl`

Generated at: {datetime.utcnow().isoformat()} UTC
"""

    # Write to file
    summary_dir = Path(settings.run_dir) / task_id
    summary_dir.mkdir(parents=True, exist_ok=True)
    with open(summary_dir / "summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
