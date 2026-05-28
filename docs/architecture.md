# Scout 架构文档

## 总体架构

```
React 工作台 → FastAPI API → Task Service → LangGraph Orchestrator
                                              ↓
                    ┌──────────┬──────────┬──────────┬──────────┐
                    ↓          ↓          ↓          ↓          ↓
               Researcher   Analyst     Writer    Reviewer  Checkpoint
                    ↓          ↓          ↓          ↓
               Data Source Adapter      LLM Adapter (Mock / Doubao)
```

## LangGraph DAG

```
researcher → analyst → writer → reviewer
                ↑                    ↓
                └──── researcher ────┘ (conditional edge on MISSING_SOURCE)
                └──── analyst ───────┘ (conditional edge on SCHEMA_INVALID)
                └──── writer ────────┘ (conditional edge on REPORT_GAP)
```

## 状态管理

统一 `ScoutState`（TypedDict）管理任务状态：
- task_id, run_id, schema_pack
- sources, evidence, profiles, claims, report
- review_issues, review_passed, retry_target, retry_count
- current_node, node_history, trace_refs

## 存储

| 数据 | 存储方式 |
|---|---|
| Task | SQLite |
| Artifact | JSON 文件 |
| Checkpoint | MemorySaver（MVP）|
| Run Event | JSONL + SQLite |
| Trace Mirror | JSON Artifact |

## 降级策略

| 场景 | 行为 |
|---|---|
| LangSmith 不可用 | 本地 Trace Mirror 兜底 |
| LLM 不可用 | Mock LLM 兜底 |
| Web 采集失败 | Mock Pack 兜底 |
