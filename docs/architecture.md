# Scout 架构文档

## 1. 总体架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│  React 工作台 │────▶│  FastAPI    │────▶│  Task Service   │
│  (Vite+TS)  │     │  (Port 8000)│     │                 │
└─────────────┘     └─────────────┘     └────────┬────────┘
                                                  │
                                                  ▼
                                       ┌────────────────────┐
                                       │ LangGraph          │
                                       │ Orchestrator       │
                                       │ (StateGraph)       │
                                       └────────┬───────────┘
                                                │
              ┌──────────┬──────────┬──────────┼──────────┬──────────┐
              ▼          ▼          ▼          ▼          ▼          ▼
         Researcher   Analyst     Writer   Reviewer  Checkpoint  Trace
              │          │          │          │          │
              ▼          ▼          ▼          │          ▼
         Data Source   Product    Report     │       MemorySaver
         Adapter     Profile    Builder      │       (SQLite P1)
              │          │          │          │
              └──────────┴──────────┴──────────┘
                         │
                         ▼
                    LLM Adapter
                    (Mock / Doubao)
```

---

## 2. LangGraph DAG

### 2.1 节点定义

```
                    ┌─────────────┐
         Entry ────▶│  researcher │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   analyst   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   writer    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  reviewer   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           review      retry      retry
           passed      researcher  analyst
              │            │            │
              ▼            ▼            ▼
             END     researcher    analyst
                         │            │
                         └──────┬─────┘
                                │
                          (continue flow)
```

### 2.2 条件边路由逻辑

```python
def _route_after_reviewer(state: ScoutState) -> str:
    if state.get("review_passed"):
        return "end"
    target = state.get("retry_target")
    if target:
        return target
    return "end"
```

| 条件 | 路由目标 | 说明 |
|---|---|---|
| `review_passed == True` | END | 质检通过，流程结束 |
| `retry_target == "researcher"` | researcher | 补充来源 |
| `retry_target == "analyst"` | analyst | 重新结构化 |
| `retry_target == "writer"` | writer | 补齐报告 |

### 2.3 Checkpoint 机制

使用 LangGraph `MemorySaver` 作为 checkpointer：

- 每个节点执行前自动保存 checkpoint
- Reviewer 打回后，从目标节点的 checkpoint 恢复状态
- 已成功节点的结果（Artifact）保留，不重新执行
- 支持同一会话内多次恢复

---

## 3. 状态管理

统一 `ScoutState`（TypedDict）管理任务全生命周期状态：

```python
class ScoutState(TypedDict, total=False):
    # 任务身份
    task_id: str
    run_id: str
    schema_pack: str      # ai_agent / ai_earbuds
    data_mode: str        # mock / web / hybrid

    # Agent 输入/输出
    sources: list[dict]      # SourceRecord[]
    evidence: list[dict]     # EvidenceCard[]
    profiles: list[dict]     # ProductProfile[]
    claims: list[dict]       # Claim[]
    report: dict | None      # Report

    # Reviewer 反馈
    review_issues: list[dict]
    review_passed: bool
    retry_target: str | None   # researcher / analyst / writer
    retry_count: int

    # 可观测性
    current_node: str | None
    node_history: list[str]
    trace_refs: list[str]

    # LangGraph 消息机制
    messages: Annotated[list, add_messages]
```

---

## 4. 存储设计

| 数据 | 存储方式 | 路径/表 | 说明 |
|---|---|---|---|
| Task | SQLite | `tasks` 表 | 任务配置、状态、进度 |
| Run Event | JSONL + SQLite | `runtime/logs/{task_id}.jsonl` | 结构化事件流 |
| Source Artifact | JSON | `runtime/artifacts/{task_id}/sources.json` | 来源记录 |
| Evidence Artifact | JSON | `runtime/artifacts/{task_id}/evidence.json` | 证据卡 |
| Profile Artifact | JSON | `runtime/artifacts/{task_id}/profiles.json` | 产品画像 |
| Claim Artifact | JSON | `runtime/artifacts/{task_id}/claims.json` | 关键结论 |
| Report Artifact | JSON | `runtime/artifacts/{task_id}/report.json` | 分析报告 |
| Review Artifact | JSON | `runtime/artifacts/{task_id}/review.json` | 质检结果 |
| Run Summary | Markdown | `runtime/runs/{task_id}/summary.md` | 运行复盘 |
| Checkpoint | MemorySaver | 内存（MVP） | 进程内状态恢复 |

---

## 5. 降级策略

| 失败场景 | 系统行为 | 日志 |
|---|---|---|
| LangSmith 不可用 | 继续运行，使用本地 Trace Mirror | `FALLBACK_USED` |
| LLM 调用失败 | Mock LLM 兜底 | `FALLBACK_USED` |
| Web 采集失败 | Mock Pack 兜底 | `NODE_FAILED` + `FALLBACK_USED` |
| 结构化输出校验失败 | 重试一次，仍失败则生成 ReviewIssue | `NODE_FAILED` |
| Reviewer 打回 | 从 checkpoint 恢复目标节点 | `RESUMED_FROM_CHECKPOINT` |
| Artifact 写入失败 | 标记 run 失败，不覆盖上一次成功产物 | `RUN_FAILED` |

---

## 6. 数据流

```
1. 用户创建任务 -> Task 存入 SQLite
2. 用户启动运行 -> Run Event: RUN_STARTED
3. researcher 节点:
   - 读取 Data Pack -> SourceRecord[]
   - 提取 Evidence -> EvidenceCard[]
   - 保存 Artifact -> sources.json, evidence.json
   - Run Event: NODE_STARTED / NODE_SUCCEEDED / ARTIFACT_SAVED
4. analyst 节点:
   - 读取 Evidence -> ProductProfile[]
   - 构建 Claim -> Claim[]
   - 保存 Artifact -> profiles.json, claims.json
5. writer 节点:
   - 读取 Profile + Claim -> Report
   - 过滤无证据 Claim
   - 保存 Artifact -> report.json
6. reviewer 节点:
   - 校验 Schema 完整性
   - 校验引用覆盖率
   - 校验置信度
   - 校验报告完整性
   - 生成 ReviewIssue[]
   - 保存 Artifact -> review.json
   - 若通过: REVIEW_APPROVED -> END
   - 若失败: REVIEW_FAILED -> 条件边路由 -> RESUMED_FROM_CHECKPOINT
7. 重跑后 reviewer 再次检查
8. 通过 -> RUN_COMPLETED -> 生成 Run Summary
```

---

## 7. 可扩展性设计

### 7.1 行业扩展

新行业只需提供：
1. `data/packs/{industry}/manifest.json` — 产品列表、描述
2. `data/packs/{industry}/sources.json` — 来源数据
3. （可选）`data/packs/{industry}/broken/*.json` — 演示用 broken case

Agent 核心逻辑不变，通过 `schema_pack` 字段切换数据包。

### 7.2 数据源扩展

Researcher 通过 Data Source Adapter 读取：
- Mock Pack（当前）
- Web Source（P1）
- Manual Source（P1）

新增来源类型不改 Analyst/Writer 主逻辑。

### 7.3 Agent 复用

所有 Agent 输入输出只依赖核心 Schema：
- 替换 LLM：改 `llm_adapter.py`
- 替换数据包：改 `schema_pack` 配置
- 不影响 DAG 结构
