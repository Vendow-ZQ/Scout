# Scout 演示脚本（5 分钟现场演示）

## 准备

1. 启动后端：`cd backend && uvicorn app.main:app --port 8000`
2. 启动前端：`cd frontend && npm run dev`
3. 浏览器打开 http://localhost:5173
4. 确保 Mock 模式（无需外网/API Key）

---

## 演示步骤

### Step 1: 创建任务（20 秒）

**操作**: 首页选择数据包，点击启动

**解说词**:
> "这是 Scout，一个 AI 驱动的竞品分析 Agent 协作系统。我选择'通用 AI Agent'数据包，竞品包括 ChatGPT、Claude、Gemini、Genspark、Manus。点击启动分析。"

**展示点**:
- 数据包选择（体现可扩展性）
- 任务表单（行业、主品、竞品、分析目标）

---

### Step 2: 观察 DAG 执行（45 秒）

**操作**: 自动跳转到工作台，观察 DAG 标签页

**解说词**:
> "系统自动编排 4 个 Agent：Researcher 负责采集来源和提取证据，Analyst 构建产品画像和对比矩阵，Writer 生成报告草稿，Reviewer 做质量检查。这里用 React Flow 展示完整的执行流程。"

**展示点**:
- 4 个 Agent 节点依次亮起
- 节点状态变化：pending -> running -> success
- React Flow 可视化 DAG

---

### Step 3: Reviewer 打回与恢复（90 秒）【核心得分点】

**操作**: 观察 Reviewer 节点变红，DAG 展示打回路径

**解说词**:
> "Reviewer 检测到问题：Galaxy Buds 3 Pro / Manus 来源不足，缺少定价信息。这是一个真实的质量门，不是假流程。系统没有从头开始，而是从 LangGraph Checkpoint 恢复 Researcher 节点，补充来源后重跑。"

**展示点**:
- Reviewer 节点检测到 blocker/major issue
- DAG 展示条件边：reviewer -> researcher（红色返回箭头）
- 运行日志中出现 REVIEW_FAILED 和 RESUMED_FROM_CHECKPOINT
- 系统重跑 researcher -> analyst -> writer -> reviewer
- Issue 状态从 open 变为 fixed

---

### Step 4: 查看报告（45 秒）

**操作**: 切换"分析报告"标签

**解说词**:
> "Reviewer 通过后生成最终报告。包含执行摘要、竞品对比矩阵、SWOT 分析、8 条关键 Claim，100% 证据覆盖率。每条 Claim 都绑定了 evidence_ids，点击可以跳转到来源证据页。"

**展示点**:
- 竞品对比矩阵（5 产品 x 5 维度）
- SWOT 分析
- 8 条关键 Claim
- 证据覆盖率 100%
- 点击 evidence ID 链接跳转到 SourcesPage

---

### Step 5: 查看质检与溯源（45 秒）

**操作**: 切换"质检结果"标签，再打开"来源与证据"页面

**解说词**:
> "质检结果展示了 Reviewer 发现的全部问题及其修复状态。来源证据页展示了所有证据卡和来源的关联关系，支持按产品和维度筛选。"

**展示点**:
- Reviewer Issues 列表（severity、类型、状态）
- 证据卡列表（产品、维度、事实、置信度、来源）
- 来源列表（类型、摘录、URL）
- 筛选功能

---

### Step 6: 扩展性说明（15 秒）

**操作**: 返回首页，展示 AI 耳机数据包

**解说词**:
> "Scout 不绑定单一行业。通过替换 Schema Pack 和数据包，可以切换到 AI 耳机、SaaS 工具等任意垂直领域，Agent 核心逻辑不变。"

**展示点**:
- 数据包切换：ai_agent -> ai_earbuds
- 相同的 4 Agent 编排跑通不同行业

---

## 得分点对应

| 比赛评分要求 | 演示位置 | 证据 |
|---|---|---|
| 多 Agent 协作 | DAG 流程 | 4 个节点顺序执行 + React Flow |
| 结构化通信 | ScoutState / Pydantic | 节点输入输出均为 Schema 对象 |
| 真实闭环 | Reviewer 打回 + 恢复 | Issue 从 open 到 fixed，非假流程 |
| 信息溯源 | Claim -> Evidence -> Source | 证据 ID 可点击跳转 |
| 可观测性 | Run Event 日志 / Trace | JSONL 事件流 + 节点状态 |
| 日志机制 | 运行日志面板 | 15+ 事件类型完整覆盖 |
| 工程完整度 | 前后端 + 存储 + 文档 | FastAPI + React + SQLite + 全套文档 |
| 可扩展性 | AI 耳机数据包 | Schema Pack + Data Pack 切换 |
| 鲁棒性 | Mock-first 演示 | 无外网无 Key 完整跑通 |

---

## 备用方案

若现场时间不足，优先保留 **Step 3（Reviewer 打回）** 和 **Step 4（报告展示）**，这是得分权重最高的两个环节。
