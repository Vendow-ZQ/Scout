from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import artifacts, tasks
from app.storage.sqlite_store import init_db

app = FastAPI(
    title="Scout API",
    description="AI 驱动的竞品分析 Agent 协作系统",
    version="0.1.0",
)

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5003", "http://127.0.0.1:5003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB on startup
@app.on_event("startup")
def startup() -> None:
    init_db()

# Include routers
app.include_router(tasks.router)
app.include_router(artifacts.router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "scout"}
