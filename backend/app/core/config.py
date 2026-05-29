import os
from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "doubao"
    doubao_api_key: str | None = None
    doubao_model: str | None = None
    doubao_ep: str | None = None
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"

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
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"


settings = Settings()

# Volcano Engine's OpenAI-compatible API expects the endpoint ID as model.
# Prefer DOUBAO_EP when present; DOUBAO_MODEL remains a fallback alias.
if settings.doubao_ep:
    settings.doubao_model = settings.doubao_ep
