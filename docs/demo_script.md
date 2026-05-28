# Scout 演示脚本（5 分钟）

## 准备

1. 启动后端：`cd backend && uvicorn app.main:app --port 8000`
2. 启动前端：`cd frontend && npm run dev`
3. 打开 http://localhost:5173

## 演示步骤

### 1. 创建任务（30 秒）

- 首页选择"通用 AI Agent"数据包
- 竞品：ChatGPT, Claude, Gemini, Genspark, Manus
- 点击"启动分析"

### 2. 观察 DAG 执行（1 分钟）

- 自动跳转到工作台
- DAG 标签页展示节点状态变化
- Researcher → Analyst → Writer → Reviewer

### 3. 观察 Reviewer 打回（1 分钟）

- Reviewer 节点变红/黄
- DAG 展示打回路径：reviewer → researcher
- 系统从 checkpoint 恢复，重跑 researcher
- 查看运行日志中的 REVIEW_FAILED 和 REVIEW_FIXED 事件

### 4. 查看报告（1 分钟）

- 切换"分析报告"标签
- 查看竞品对比矩阵、SWOT、关键 Claim
- 点击 Claim 查看证据引用
- 确认 8 条 Claim，100% 证据覆盖率

### 5. 查看质检结果（1 分钟）

- 切换"质检结果"标签
- 查看证据卡列表
- 确认 Reviewer 已通过

### 6. 扩展性说明（30 秒）

- 展示 `data/packs/ai_agent/` 结构
- 说明可替换 Schema Pack 和数据包
- 提及 AI 耳机扩展示例

## 得分点对应

| 评分要求 | 展示位置 |
|---|---|
| 多 Agent 协作 | DAG 流程 |
| 结构化通信 | ScoutState / Pydantic Schema |
| 真实闭环 | Reviewer 打回 + 恢复 |
| 信息溯源 | Claim → Evidence → Source |
| 可观测性 | Run Event 日志 / Trace |
| 工程完整度 | 前后端 + 存储 + 文档 |
| 鲁棒性 | Mock-first + 降级策略 |
