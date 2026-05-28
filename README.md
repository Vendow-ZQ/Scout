# Scout - AI 驱动的可审计竞品分析 Agent 协作系统

**版本**: v1.0.0 (MVP)  
**日期**: 2026-05-28  
**面向赛事**: 字节 CIS AI 全栈项目挑战赛

Scout 是一个面向企业产品团队的竞品分析 Agent 协作系统。用户输入行业方向、主品、竞品列表和分析目标后，系统通过多个专职 Agent 自动完成信息采集、知识结构化、竞品对比、SWOT、报告生成和质检复核，并在前端工作台展示完整 DAG、Agent Trace、证据来源和 Reviewer 打回过程。

核心不是"生成一份竞品报告"，而是把企业竞品分析流程做成一个**可审计、可追溯、可复核、可扩展**的 Agent 工作台。

---

## 快速启动

### 1. 克隆仓库

```bash
git clone https://github.com/Vendow-ZQ/Scout.git
cd Scout
```

### 2. 启动后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端服务运行在 http://localhost:8000  
API 文档: http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端工作台运行在 http://localhost:5173

---

## 核心能力

| 能力 | 状态 | 说明 |
|---|---|---|
| 任务创建与配置 | P0 | 支持行业、主品、竞品、分析目标、数据包选择 |
| LangGraph Agent 编排 | P0 | Researcher -> Analyst -> Writer -> Reviewer |
| Reviewer 质量门与条件路由打回 | P0 | 支持 MISSING_SOURCE / LOW_CONFIDENCE / REPORT_GAP 检测与打回 |
| Mock 数据包 | P0 | ai_agent（通用 AI Agent）+ ai_earbuds（AI 耳机） |
| Broken Case 演示 | P0 | 首次运行触发 Reviewer 失败，Checkpoint 恢复后通过 |
| Run Event 结构化日志 | P0 | JSONL 格式，15+ 事件类型 |
| Run Summary 生成 | P0 | 含 git branch/commit、reviewer issues、报告统计 |
| 本地 Trace Mirror | P0 | LangSmith 不可用时本地兜底 |
| 前端工作台 | P0 | DAG 可视化 / Trace / Report / Review / Sources |
| 证据溯源 | P0 | Claim -> Evidence -> Source 三级追溯 |
| 数据包可扩展 | P0 | 通过 Schema Pack + Data Pack 切换行业 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 前端 | Vite + React + TypeScript | 本地工作台 |
| 前端 UI | 内联样式（零依赖） | 优先交互密度和交付速度 |
| DAG 可视化 | @xyflow/react (React Flow) | Agent 节点状态、边、打回路径 |
| 后端 API | Python + FastAPI | 任务、报告、来源、Trace、Review API |
| Agent 框架 | LangChain + LangGraph | 状态图编排、条件路由、Checkpoint |
| 结构化校验 | Pydantic | Task / Source / Evidence / Claim / Review / Trace |
| 观测 | LangSmith（可选）+ 本地 Trace Mirror | 断网可降级 |
| 存储 | SQLite + JSON Artifact | 任务状态、产物、Trace |
| 模型接入 | Mock LLM（默认）+ Doubao 适配 | 无网络稳定演示 |

---

## 演示流程（5 分钟）

1. 打开 http://localhost:5173
2. 选择"通用 AI Agent"数据包，点击"启动分析"
3. 系统自动运行 Researcher -> Analyst -> Writer -> Reviewer
4. Reviewer 检测到 broken case（Galaxy Buds 3 Pro / Manus 来源不足），打回 Researcher
5. 系统从 Checkpoint 恢复，补充来源后重跑
6. Reviewer 通过，展示最终报告（8 条 Claim，100% 证据覆盖率）
7. 在工作台查看 React Flow DAG、运行日志、质检结果和证据卡
8. 点击 Claim 证据 ID 跳转到来源证据页
9. 切换到 AI 耳机数据包，说明系统扩展方式

完整演示脚本见 [docs/demo_script.md](docs/demo_script.md)。

---

## 项目结构

```
scout/
├── backend/
│   ├── app/
│   │   ├── api/              FastAPI 路由（tasks, artifacts, observability）
│   │   ├── agents/           4 个 Agent 节点（researcher, analyst, writer, reviewer）
│   │   ├── core/             LangGraph 编排、配置、日志、状态
│   │   ├── models/           Pydantic Schema（Task, Source, Evidence, Claim, Review, Trace）
│   │   ├── storage/          SQLite 存储、Artifact 管理
│   │   └── main.py           FastAPI 应用入口
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              API 客户端
│   │   ├── pages/            页面（TaskCreate, TaskList, RunWorkbench, SourcesPage）
│   │   ├── App.tsx           路由配置
│   │   └── main.tsx
│   └── package.json
├── data/
│   └── packs/                Mock 数据包
│       ├── ai_agent/         通用 AI Agent 竞品（5 产品，10+ 来源）
│       └── ai_earbuds/       AI 耳机竞品（5 产品，11 来源）
├── runtime/                  运行时产物（自动创建）
│   ├── artifacts/            Source / Evidence / Claim / Report JSON
│   ├── logs/                 Run Event JSONL
│   └── runs/                 Run Summary Markdown
├── docs/                     项目文档
│   ├── architecture.md       系统架构
│   ├── agent_protocol.md     Agent 职责与打回协议
│   ├── run_logging.md        运行日志与事件机制
│   ├── demo_script.md        5 分钟演示脚本
│   ├── compliance.md         合规与安全
│   ├── development_workflow.md 开发流程与分支策略
│   ├── ai_coding_log.md      AI 编码协作记录
│   └── scoring_alignment.md  比赛评分对齐
├── SOP_0528.md               AI 编码执行标准
├── PRD_0528.md               产品需求文档
└── README.md
```

---

## API 速查

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/tasks` | POST | 创建任务 |
| `/api/tasks` | GET | 任务列表 |
| `/api/tasks/{task_id}` | GET | 任务详情 |
| `/api/tasks/{task_id}/run` | POST | 运行分析 |
| `/api/tasks/{task_id}/events` | GET | 运行事件日志 |
| `/api/tasks/{task_id}/report` | GET | 分析报告 |
| `/api/tasks/{task_id}/review` | GET | 质检结果 |
| `/api/tasks/{task_id}/sources` | GET | 来源列表 |
| `/api/tasks/{task_id}/evidence` | GET | 证据卡列表 |
| `/api/tasks/{task_id}/summary` | GET | Run Summary |

---

## 环境变量

复制 `.env.example` 为 `.env`（`.env` 不入库）：

```bash
LLM_PROVIDER=mock          # mock / doubao
DOUBAO_API_KEY=            # 如需真实模型
DOUBAO_MODEL=              # 模型名称
LANGSMITH_TRACING=false    # true / false
LANGSMITH_API_KEY=         # 如需 LangSmith
```

Mock 模式无需任何外部依赖即可完整演示。

---

## 文档索引

| 文档 | 内容 |
|---|---|
| [PRD_0528.md](PRD_0528.md) | 产品需求文档（P0/P1/P2 范围、功能需求、验收标准） |
| [SOP_0528.md](SOP_0528.md) | AI 编码执行标准（分支策略、Review 规则、日志要求） |
| [docs/architecture.md](docs/architecture.md) | 系统架构、LangGraph DAG、存储设计、降级策略 |
| [docs/agent_protocol.md](docs/agent_protocol.md) | Agent 职责、输入输出 Schema、打回协议 |
| [docs/run_logging.md](docs/run_logging.md) | Run Event 机制、Trace Mirror、Run Summary、脱敏规则 |
| [docs/demo_script.md](docs/demo_script.md) | 5 分钟现场演示脚本（含得分点对应） |
| [docs/compliance.md](docs/compliance.md) | 数据来源、脱敏、密钥安全、Trace 安全 |
| [docs/development_workflow.md](docs/development_workflow.md) | 分支策略、Review 标准、子 Agent 并行规则 |
| [docs/ai_coding_log.md](docs/ai_coding_log.md) | AI 编程协作记录、关键决策、取舍说明 |
| [docs/scoring_alignment.md](docs/scoring_alignment.md) | 逐条对齐比赛评分标准 |

---

## 许可证

内部项目，用于字节 CIS AI 全栈项目挑战赛。
