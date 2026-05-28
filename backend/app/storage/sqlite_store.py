import json
import sqlite3
from pathlib import Path
from typing import Any

from app.core.config import settings

DB_PATH = Path(settings.database_url.replace("sqlite:///", ""))


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite tables for tasks and run events."""
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            config TEXT NOT NULL,
            status TEXT DEFAULT 'created',
            current_node TEXT,
            progress_percent INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            run_id TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS run_events (
            event_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            request_id TEXT,
            level TEXT,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            node_name TEXT,
            agent_name TEXT,
            payload TEXT,
            artifact_refs TEXT,
            trace_id TEXT,
            checkpoint_id TEXT,
            git_branch TEXT,
            git_commit TEXT,
            created_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_run_events_task_run
        ON run_events(task_id, run_id)
        """
    )

    conn.commit()
    conn.close()


def create_task(task_id: str, config: dict[str, Any]) -> None:
    from datetime import datetime

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (task_id, config, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            task_id,
            json.dumps(config, ensure_ascii=False),
            "created",
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_task(task_id: str) -> dict[str, Any] | None:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def list_tasks() -> list[dict[str, Any]]:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_task_status(
    task_id: str,
    status: str,
    current_node: str | None = None,
    progress_percent: int | None = None,
    run_id: str | None = None,
) -> None:
    from datetime import datetime

    conn = _get_conn()
    cursor = conn.cursor()
    updates = ["status = ?", "updated_at = ?"]
    params = [status, datetime.utcnow().isoformat()]

    if current_node is not None:
        updates.append("current_node = ?")
        params.append(current_node)
    if progress_percent is not None:
        updates.append("progress_percent = ?")
        params.append(progress_percent)
    if run_id is not None:
        updates.append("run_id = ?")
        params.append(run_id)

    params.append(task_id)
    cursor.execute(
        f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?",
        tuple(params),
    )
    conn.commit()
    conn.close()
