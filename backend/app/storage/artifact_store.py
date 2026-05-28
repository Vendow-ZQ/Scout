import json
from pathlib import Path
from typing import Any

from app.core.config import settings


def _artifact_path(task_id: str, filename: str) -> Path:
    path = Path(settings.artifact_dir) / task_id / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_artifact(task_id: str, filename: str, data: Any) -> str:
    path = _artifact_path(task_id, filename)
    if isinstance(data, (dict, list)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(data))
    return str(path)


def load_artifact(task_id: str, filename: str) -> Any:
    path = _artifact_path(task_id, filename)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_artifacts(task_id: str) -> list[str]:
    path = Path(settings.artifact_dir) / task_id
    if not path.exists():
        return []
    return [f.name for f in path.iterdir() if f.is_file()]
