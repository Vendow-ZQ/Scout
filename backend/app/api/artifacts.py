from typing import Any

from fastapi import APIRouter, HTTPException

from app.storage.artifact_store import list_artifacts, load_artifact

router = APIRouter(prefix="/api/tasks/{task_id}", tags=["artifacts"])


@router.get("/sources")
def api_get_sources(task_id: str) -> Any:
    data = load_artifact(task_id, "sources.json")
    if data is None:
        raise HTTPException(status_code=404, detail="Sources not found")
    return data


@router.get("/evidence")
def api_get_evidence(task_id: str) -> Any:
    data = load_artifact(task_id, "evidence.json")
    if data is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return data


@router.get("/claims")
def api_get_claims(task_id: str) -> Any:
    data = load_artifact(task_id, "claims.json")
    if data is None:
        raise HTTPException(status_code=404, detail="Claims not found")
    return data


@router.get("/report")
def api_get_report(task_id: str) -> Any:
    data = load_artifact(task_id, "report.json")
    if data is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return data


@router.get("/review")
def api_get_review(task_id: str) -> Any:
    data = load_artifact(task_id, "review.json")
    if data is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return data
