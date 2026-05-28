# Scout - AI 驱动的竞品分析 Agent 协作系统

**版本**: v0.1.0 (MVP)
**日期**: 2026-05-28

Scout 是一个面向企业产品团队的竞品分析 Agent 协作系统。用户输入行业方向、主品、竞品列表和分析目标后，系统通过多个专职 Agent 自动完成信息采集、知识结构化、竞品对比、SWOT、报告生成和质检复核，并在前端工作台展示完整 DAG、Agent Trace、证据来源和 Reviewer 打回过程。

---

## 快速启动

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 打开工作台。

---

## 核心能力

| 能力 | 状态 |
|---|---|
| 任务创建与配置 | ✅ P0 |
| LangGraph Agent 编排 (Researcher → Analyst → Writer → Reviewer) | ✅ P0 |
| Reviewer 质量门与条件路由打回 | ✅ P0 |
| Mock 数据包（ai_agent + broken case） | ✅ P0 |
| Run Event 结构化日志（JSONL） | ✅ P0 |
| 本地 Trace Mirror | ✅ P0 |
| 前端工作台（DAG / Trace / Report / Review） | ✅ P0 |
| 证据溯源（Claim → Evidence → Source） | ✅ P0 |

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vite + React + TypeScript |
| 后端 | Python + FastAPI |
| Agent 框架 | LangChain + LangGraph |
| 结构化校验 | Pydantic |
| 存储 | SQLite + JSON Artifact |
| 观测 | LangSmith（可选）+ 本地 Trace Mirror |

---

## 演示流程

1. 打开 http://localhost:5173
2. 选择"通用 AI Agent"数据包，点击"启动分析"
3. 系统自动运行 Researcher → Analyst → Writer → Reviewer
4. Reviewer 检测到 broken case（Manus 定价来源缺失），打回 Researcher
5. 系统从 checkpoint 恢复，补充来源后重跑
6. Reviewer 通过，展示最终报告（8 条 Claim，100% 证据覆盖率）
7. 在工作台查看 DAG 流程、运行日志、质检结果和证据卡

---

## 项目结构

```
scout/
├── backend/          FastAPI + LangGraph 后端
├── frontend/         React + Vite 前端
├── data/packs/       Mock 数据包
├── runtime/          运行时产物（日志、Artifact、Runs）
├── docs/             文档
└── README.md
```

---

## 文档索引

- [SOP_0528.md](SOP_0528.md) - AI 编码执行标准
- [PRD_0528.md](PRD_0528.md) - 产品需求文档
- docs/architecture.md - 系统架构
- docs/agent_protocol.md - Agent 协议
- docs/demo_script.md - 演示脚本

---

## 环境变量

复制 `.env.example` 为 `.env`（不入库）：

```bash
LLM_PROVIDER=mock
# DOUBAO_API_KEY=...
# LANGSMITH_TRACING=false
```

---

## 许可证

内部项目，用于字节 CIS AI 全栈项目挑战赛。
