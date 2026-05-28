# Scout 比赛评分对齐

本文件逐条对齐字节 CIS AI 全栈项目挑战赛的评分标准，说明 Scout 在每个得分点上的实现方式。

---

## 评分维度对照

### 1. 多 Agent 协作与编排

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| 至少 4 个 Agent | Researcher、Analyst、Writer、Reviewer | DAG 展示 4 个节点 |
| Agent 间有真实协作 | 通过 ScoutState 传递结构化数据 | 节点输入输出可查 |
| 有 DAG 可视化 | React Flow 展示节点、边、状态、打回路径 | 前端 DAG 标签页 |
| 支持条件路由 | Reviewer 根据 issue 类型路由到不同节点 | 条件边代码 + 演示 |

**演示证据**: 打开工作台 DAG 标签页，展示 researcher -> analyst -> writer -> reviewer 流程，以及 reviewer 打回路径。

---

### 2. 结构化消息与通信

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| 节点输入输出结构化 | ScoutState TypedDict + Pydantic Schema | 代码审查 |
| 不纯文本拼接 | SourceRecord、EvidenceCard、Claim、ReviewIssue 均为结构化对象 | Schema 定义 |
| Schema 校验 | Pydantic model_validate | 运行时校验 |

**演示证据**: 展示 `backend/app/models/` 下的 Pydantic Schema，或展示 API 返回的 JSON 结构。

---

### 3. 真实反馈闭环

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| Reviewer 能检测问题 | _check_source_coverage、_check_claim_evidence、_check_confidence、_check_report_completeness | 代码 + 演示 |
| 能触发打回 | broken case 故意让某产品来源不足 | 首次运行必触发 |
| 能从 checkpoint 恢复 | LangGraph MemorySaver | 重跑时不重复执行成功节点 |
| 修复后能通过 | retry_count > 0 时读取完整数据包 | 第二次 Reviewer 通过 |
| 前后差异可视化 | Issue 状态从 open -> fixed | Review 标签页展示 |

**演示证据**: 运行任务，展示 Reviewer 打回 -> 恢复 -> 通过的全过程。

---

### 4. 信息溯源

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| 关键结论有来源 | 每条 Claim 绑定 evidence_ids | Report 展示 |
| 可追溯到 Evidence | EvidenceCard 包含 source_id | Evidence 面板 |
| 可追溯到 Source | SourceRecord 包含 url、raw_excerpt | SourcesPage |
| 引用可点击 | Report 中 evidence_ids 为 Link 到 SourcesPage | 点击跳转 |

**演示证据**: 报告标签页点击 Claim 的证据 ID，跳转到来源证据页。

---

### 5. 可观测性

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| Agent Trace | LangSmith（可选）+ 本地 Trace Mirror | 配置可切换 |
| 节点输入输出 | ScoutState 快照 + Artifact JSON | Artifact 文件 |
| Token/耗时 | Trace Mirror 记录 | trace_mirror.json |
| 错误捕获 | NODE_FAILED 事件 + 错误信息 | Run Event 日志 |
| Trace 可查看 | 前端 Trace 面板 | 工作台标签页 |

**演示证据**: 展示 Run Event 日志中的 NODE_STARTED/SUCCEEDED 事件，或展示 Artifact 文件内容。

---

### 6. 日志机制

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| 结构化日志 | JSONL 格式，15+ 事件类型 | runtime/logs/*.jsonl |
| 覆盖关键事件 | TASK_CREATED 到 RUN_COMPLETED 全生命周期 | 事件列表 |
| 可解释成功/失败 | Run Summary 含统计和 Issue 列表 | summary.md |
| 可解释重试/降级 | RETRY_SCHEDULED、FALLBACK_USED、RESUMED_FROM_CHECKPOINT | 日志内容 |

**演示证据**: 打开 JSONL 日志文件，展示完整事件流。

---

### 7. 工程完整度

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| 后端 | FastAPI + Python，完整 REST API | /docs 可访问 |
| 前端 | Vite + React + TypeScript | localhost:5173 |
| 存储 | SQLite + JSON Artifact | 文件系统 |
| 文档 | README + 9 份技术文档 | docs/ 目录 |
| 演示脚本 | 5 分钟脚本含得分点对应 | docs/demo_script.md |
| 代码质量 | Pydantic 校验、类型注解、错误处理 | 代码审查 |

---

### 8. 可扩展性

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| 第二数据包 | ai_earbuds（AI 耳机） | data/packs/ai_earbuds/ |
| Schema Pack 切换 | schema_pack 字段控制数据包选择 | 创建任务时选择 |
| 行业扩展方式 | 新增 manifest.json + sources.json 即可 | 文档说明 |

**演示证据**: 创建 ai_earbuds 任务并运行，展示相同 Agent 编排处理不同行业。

---

### 9. 鲁棒性

| 评分要求 | Scout 实现 | 验证方式 |
|---|---|---|
| LLM 失败降级 | Mock LLM 兜底 | 无 Key 可运行 |
| Web 采集失败 | Mock Pack 兜底 | 无网络可运行 |
| LangSmith 失败 | 本地 Trace Mirror 兜底 | 断网可运行 |
| 明确失败状态 | NODE_FAILED / RUN_FAILED 事件 | 日志记录 |

**演示证据**: 在无任何外部网络/API 的环境下完整跑通 Demo。

---

## 总结

| 评分维度 | 覆盖状态 |
|---|---|
| 多 Agent 协作与编排 | ✅ 完全覆盖 |
| 结构化消息与通信 | ✅ 完全覆盖 |
| 真实反馈闭环 | ✅ 完全覆盖 |
| 信息溯源 | ✅ 完全覆盖 |
| 可观测性 | ✅ 完全覆盖 |
| 日志机制 | ✅ 完全覆盖 |
| 工程完整度 | ✅ 完全覆盖 |
| 可扩展性 | ✅ 完全覆盖 |
| 鲁棒性 | ✅ 完全覆盖 |
