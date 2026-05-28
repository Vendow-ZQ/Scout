import os
from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "mock"
    doubao_api_key: str | None = None
    doubao_model: str | None = None

    # LangSmith
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "scout-competition-analysis"

    # Storage
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'runtime' / 'scout.db'}"
    log_dir: str = str(PROJECT_ROOT / "runtime" / "logs")
    artifact_dir: str = str(PROJECT_ROOT / "runtime" / "artifacts")
    run_dir: str = str(PROJECT_ROOT / "runtime" / "runs")

    # Data packs
    data_pack_dir: str = str(PROJECT_ROOT / "data" / "packs")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
