# Scout 开发流程与工作流

## 1. 分支策略

| 工作类型 | 分支格式 | 示例 |
|---|---|---|
| Feature | `feature/<scope>` | `feature/langgraph-orchestrator` |
| Bug fix | `fix/<scope>` | `fix/reviewer-routing` |
| Docs | `docs/<scope>` | `docs/run-logging` |
| Data | `data/<scope>` | `data/ai-agent-pack` |

**必须开分支**: 运行时代码、Schema/API 变更、Agent DAG 变更、Prompt 变更、依赖变更、新数据包。

**可直接 push main**: 拼写修正、小段 Markdown 补充（<30 行）。

## 2. 合并到 main 的标准

1. 本地启动后端和前端无报错
2. 相关 P0 演示路径可跑通
3. 关键 Schema 校验通过
4. 没有真实密钥、未脱敏数据
5. Commit message 清晰说明变更目的
6. 若改动 Agent 或 Reviewer，重新跑 broken case

## 3. Review 分层

| Review 类型 | 触发条件 | 检查重点 |
|---|---|---|
| Schema Review | 修改 models/ 或 API | 兼容性、字段命名、前后端一致性 |
| Agent Review | 修改 LangGraph/Agent/Reviewer | 状态流转、打回路由、Trace、失败恢复 |
| 前端 Review | 修改工作台/报告 | 演示路径 5 分钟内可完成 |
| Demo Review | 合并前 | 端到端稳定性、Mock 模式连续 3 次无崩溃 |

## 4. 提交规范

```
feat: add run event logging
fix: route reviewer missing-source issue to researcher
data: add ai earbuds data pack
docs: update demo script
```

## 5. AI 编码协作

- 所有 Agent 修改前阅读 PRD_0528.md 和 SOP_0528.md
- 子 Agent 并行开发需明确：目标、允许修改范围、禁止修改范围、验收标准
- 并行合并顺序：Schema/API -> 后端 -> 前端 -> 数据包 -> 文档
- 每个 P0 功能完成后更新 `docs/ai_coding_log.md`
