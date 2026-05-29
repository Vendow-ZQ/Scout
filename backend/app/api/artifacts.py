from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.storage.artifact_store import list_artifacts, load_artifact, load_text_artifact

router = APIRouter(prefix="/api/tasks/{task_id}", tags=["artifacts"])


@router.get("/artifacts")
def api_list_artifacts(task_id: str) -> dict[str, Any]:
    return {"task_id": task_id, "artifacts": list_artifacts(task_id)}


@router.get("/artifacts/{filename}", response_class=PlainTextResponse)
def api_get_artifact_file(task_id: str, filename: str) -> str:
    try:
        content = load_text_artifact(task_id, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if content is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return content


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
