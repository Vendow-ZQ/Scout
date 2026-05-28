# Scout AI 编码协作记录

## 2026-05-28 - 项目骨架与核心链路

- **Agent/tool**: Claude Code (Opus 4.7)
- **Branch**: main
- **Goal**: 初始化 Scout 项目，完成 LangGraph 编排、4 Agent 实现、前端工作台、Run Event 日志
- **Files changed**: 全部骨架文件
- **Decisions**:
  - 使用 MemorySaver 而非 SqliteSaver（LangGraph 1.2 API 变更导致 SqliteSaver 不兼容）
  - Mock-first 策略：无需外部 LLM/API 即可完整演示
  - 使用内联样式而非 Tailwind（减少依赖，加速交付）
  - Pydantic BaseModel 用于所有 Schema，前后端类型一致
- **Verification**:
  - Smoke test通过：8 节点（Reviewer 打回 -> 恢复 -> 通过）
  - 8 Claims, 100% evidence coverage
  - Run Event JSONL 完整，Run Summary 生成

## 2026-05-28 - Reviewer Issue 历史保存 + Run Summary + ai_earbuds 数据包

- **Agent/tool**: Claude Code (Opus 4.7)
- **Branch**: main
- **Goal**: Reviewer 跨轮次 Issue 状态跟踪、Run Summary 生成、第二数据包
- **Files changed**:
  - `backend/app/agents/reviewer.py` — 读取前一轮 review.json，合并新 issue，标记旧 open issue 为 fixed
  - `backend/app/api/tasks.py` — `_generate_run_summary()` 含 git branch/commit 捕获
  - `data/packs/ai_earbuds/` — 新增 AI 耳机数据包（5 产品，11 来源）
  - `frontend/src/pages/SourcesPage.tsx` — 来源证据页（产品/维度筛选）
  - `frontend/src/pages/TaskList.tsx` — 任务列表页
  - `frontend/src/App.tsx` — 路由配置
  - `frontend/src/api/client.ts` — getSources API
  - `frontend/src/pages/RunWorkbench.tsx` — 证据 ID 可点击链接
- **Decisions**:
  - Issue key = `issue_type:target_object_id`，用于去重和状态跟踪
  - Run Summary 包含 git context，方便复现 Demo
  - ai_earbuds broken case 缺少 Galaxy Buds 3 Pro review 来源
- **Verification**:
  - ai_agent smoke test: task_b6b39adc5216, 8 节点, review_passed=true, 8 claims, 100% coverage
  - ai_earbuds smoke test: task_d33841c9abaf, 8 节点, review_passed=true, 8 claims, 100% coverage

## 2026-05-28 - 文档补齐与 React Flow DAG

- **Agent/tool**: Claude Code (Opus 4.7)
- **Branch**: main
- **Goal**: 补齐 PRD 要求的全套文档，实现 React Flow DAG 可视化
- **Files changed**:
  - `README.md` — 完整更新
  - `docs/architecture.md` — 系统架构、DAG、存储、降级策略
  - `docs/agent_protocol.md` — Agent 职责、Schema、打回协议
  - `docs/run_logging.md` — Run Event 机制、脱敏规则
  - `docs/demo_script.md` — 5 分钟演示脚本
  - `docs/compliance.md` — 合规与安全
  - `docs/development_workflow.md` — 分支策略、Review 规则
  - `docs/ai_coding_log.md` — 本文件
  - `docs/scoring_alignment.md` — 比赛评分对齐
  - `frontend/src/components/AgentGraph.tsx` — React Flow DAG
  - `frontend/src/pages/RunWorkbench.tsx` — 集成 AgentGraph
- **Known risks**:
  - React Flow 节点布局需要手动调整坐标
  - 中文显示在 React Flow 中可能需要字体适配
