# Scout 运行日志与事件机制

## 1. 日志体系

Scout 有两类日志：

| 类型 | 用途 | 位置 |
|---|---|---|
| **Run Event** | 运行时事件流，前端展示、失败定位、演示复盘 | `runtime/logs/{task_id}.jsonl` |
| **Run Summary** | 单次运行复盘，含 git 上下文、报告统计、Issue 列表 | `runtime/runs/{task_id}/summary.md` |
| **Trace Mirror** | LangSmith 不可用时本地兜底 | Artifact JSON / SQLite |
| **AI Coding Log** | 开发过程记录 | `docs/ai_coding_log.md` |

---

## 2. Run Event 格式

统一使用 JSON Lines，每行一条事件：

```json
{
  "event_id": "evt_1fa44063",
  "task_id": "task_b6b39adc5216",
  "run_id": "run_20260528_045148",
  "level": "INFO",
  "event_type": "NODE_STARTED",
  "node_name": "researcher",
  "agent_name": "ResearcherAgent",
  "message": "Node researcher started",
  "payload": {"schema_pack": "ai_agent", "retry_count": 0},
  "artifact_refs": [],
  "trace_id": null,
  "checkpoint_id": null,
  "git_branch": "main",
  "git_commit": "463a1eb",
  "created_at": "2026-05-28T04:51:48.229194"
}
```

---

## 3. 事件类型覆盖

| 事件类型 | 触发时机 | 必需字段 |
|---|---|---|
| `TASK_CREATED` | 创建任务 | task_id, payload(配置) |
| `RUN_STARTED` | 运行开始 | run_id, git_branch, git_commit |
| `NODE_STARTED` | 节点开始 | node_name, agent_name, checkpoint_id |
| `NODE_SUCCEEDED` | 节点成功 | node_name, agent_name, artifact_refs |
| `NODE_FAILED` | 节点失败 | node_name, agent_name, message(错误) |
| `RETRY_SCHEDULED` | 重试排队 | node_name, retry_count |
| `FALLBACK_USED` | 降级使用 | payload(fallback_type, reason) |
| `ARTIFACT_SAVED` | 产物保存 | artifact_refs |
| `REVIEW_FAILED` | Reviewer 打回 | payload(issue_type, target_agent, severity) |
| `REVIEW_FIXED` | Issue 修复 | payload(issue_id) |
| `REVIEW_APPROVED` | Reviewer 通过 | payload(issue_count, open_count, fixed_count) |
| `CHECKPOINT_CREATED` | Checkpoint 创建 | checkpoint_id |
| `RESUMED_FROM_CHECKPOINT` | 从 Checkpoint 恢复 | checkpoint_id, node_name(目标节点) |
| `RUN_COMPLETED` | 运行完成 | payload(node_history, claim_count) |
| `RUN_FAILED` | 运行失败 | message(失败原因) |
| `GIT_CONTEXT_CAPTURED` | Git 上下文记录 | git_branch, git_commit |

---

## 4. 日志写入规则

1. **写入失败不阻塞主流程**：写日志异常时降级到控制台警告
2. **每个节点必须有 started + succeeded/failed**：确保可观测性完整
3. **Artifact 保存后写 ARTIFACT_SAVED**：保证产物可追溯
4. **Reviewer 结果必须写 REVIEW_FAILED 或 REVIEW_APPROVED**
5. **Run Summary 在 RUN_COMPLETED 后生成**

---

## 5. Run Summary 模板

```markdown
# Run Summary

- **task_id**: {task_id}
- **run_id**: {run_id}
- **git_branch**: {branch}
- **git_commit**: {commit}
- **data_pack**: {schema_pack}
- **schema_pack**: {schema_pack}
- **langsmith_trace**: N/A (mock mode)
- **fallback_used**: mock_llm, mock_data_pack
- **reviewer_issues**: {count}
- **final_report**: {claim_count} claims, {coverage}% evidence coverage
- **demo_notes**: End-to-end completed with Reviewer loop. Node history: {history}

## Reviewer Issues

- [severity] issue_type: message

## Node Execution History

1. researcher
2. analyst
...

## Artifacts

- runtime/artifacts/{task_id}/sources.json
- runtime/artifacts/{task_id}/evidence.json
...
```

---

## 6. 脱敏规则

写入日志前必须移除：

- API Key（任何 provider）
- `.env` 文件内容
- 邮箱地址
- 手机号
- 未脱敏的访谈原文
- 个人隐私信息

允许写入：
- source_id、evidence_id、claim_id（公开或已授权）
- 产品名称、功能描述（公开信息）
- 结构化分析结论
- 错误类型和堆栈（不含敏感参数）

---

## 7. Trace Mirror

当 LangSmith 不可用时，本地 Trace Mirror 提供：

- 节点输入快照（input_snapshot）
- 节点输出快照（output_snapshot）
- Token 使用量
- 执行耗时
- 错误信息

存储位置：`runtime/artifacts/{task_id}/trace_mirror.json`

前端 Trace 面板优先展示 LangSmith URL，不可用时展示本地 Trace Mirror。
