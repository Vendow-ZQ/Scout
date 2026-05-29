# Scout

**AI 竞品分析工作台 / Competitive Analysis Workbench**  
**Version**: v2.0 architecture refresh  
**Date**: 2026-05-28  
**Competition**: 字节 CIS AI 全栈项目挑战赛

Scout 面向产品经理、创业团队、战略/投研团队，帮助用户围绕一个赛道、产品或机会完成全链路竞品调研。它的前台交付是一份可复制到飞书继续使用的中文 **竞品调研报告 / Competitive Analysis Report**；后台能力是一套可审计的多 Agent 研究系统。

一句话：

> 结论先行，证据可追溯；报告可读，过程可审计。

---

## 1. What Scout Produces

一次完整运行会生成：

- `researcher/research_plan.md`
- 多条 Research tracks，例如市场、用户、竞品、技术、商业模式、风险
- `researcher/research_synthesis.md`
- `analyst/analysis_plan.md`
- 多篇 Analyst module analysis
- `analyst/analysis_synthesis.md`
- `editor/final_report.md`
- `editor/editorial_notes.md`
- `reviewer/review_scorecard.md`
- `reviewer/revision_plan.md`
- JSON indexes, run events, traces, and source/evidence records

最终报告满足三层阅读深度：

1. **1 分钟判断**：一页结论、Answer Map、风险和建议。
2. **20 分钟深读**：市场、用户、竞品、能力、商业、风险分析。
3. **1 小时审计**：追溯 evidence、source、module analysis、review scorecard。

---

## 2. Architecture at a Glance

主流程固定串行：

```text
Researcher -> Analyst -> Editor -> Reviewer
```

节点内部可以树状展开：

```text
Researcher
  plan -> tracks -> synthesis

Analyst
  plan -> modules -> synthesis

Editor
  editorial plan -> final report -> editorial notes

Reviewer
  scorecard -> revision plan
```

关键设计：

- Researcher 先 planning，再 ReAct-style 搜索/读取/降级/提证据。
- Analyst 不搜索竞品，而是基于研究产物写模块级分析文章。
- Editor 是主编，不是简单 writer。它负责把模块文章组织成完整报告。
- Reviewer 是虚拟审稿委员会，默认只给 scorecard 和 revision plan，不自动重跑整条链路。
- Markdown 是主要产物；JSON 只做索引、API、状态和校验。

---

## 3. Quick Start

### 3.1 Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend:

- App: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

### 3.2 Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5003
```

Frontend:

- Workbench: `http://127.0.0.1:5003`

---

## 4. Environment

Copy `env.example` to `.env`. Do not commit `.env`.

```bash
LLM_PROVIDER=doubao
DOUBAO_API_KEY=
DOUBAO_MODEL=
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
```

Mock data only replaces the external crawler/source collection layer. Agent reasoning should call the configured real LLM. If the model is unavailable, the run should fail clearly and write logs; it should not silently switch to fake reasoning.

---

## 5. Project Structure

```text
Scout/
  PRODUCT_DEFINITION.md       Product philosophy and agent boundaries
  PRD_0528.md                 Product requirements and acceptance criteria
  SOP_0528.md                 AI coding and runtime execution standard
  README.md                   This file
  env.example                 Environment template

  backend/
    app/
      api/                    FastAPI routes
      agents/                 Researcher, Analyst, Editor/legacy writer, Reviewer runtime code
      core/                   LangGraph, config, state, logging, LLM adapter
      models/                 Pydantic models
      prompts/agents/         System prompts in Markdown
      storage/                SQLite and artifact storage

  frontend/
    src/
      api/                    API client
      components/             Graph and shared components
      pages/                  Task creation, workbench, artifacts, sources
      styles/                 Visual system

  data/
    packs/
      ai_coding_agent/        Main demo pack: Trae and AI coding agents
      ai_agent/               Legacy demo mock data pack
      ai_earbuds/             Secondary demo data pack

  docs/
    architecture.md           Runtime architecture
    demo_script.md            Competition demo script

  runtime/                    Local generated outputs, ignored unless explicitly needed
    artifacts/
    logs/
    runs/
```

Note: some current code paths may still use the filename `writer.py`; product language and next architecture target use **Editor**. Rename code only as part of an explicit implementation slice.

---

## 6. API Quick Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/tasks` | POST | Create task |
| `/api/tasks` | GET | List tasks |
| `/api/tasks/{task_id}` | GET | Task detail |
| `/api/tasks/{task_id}/run` | POST | Start or rerun task |
| `/api/tasks/{task_id}/regenerate-report` | POST | Regenerate final report from existing analysis |
| `/api/tasks/{task_id}/artifacts` | GET | Artifact tree/index |
| `/api/tasks/{task_id}/artifacts/{artifact_id}` | GET | Artifact detail |
| `/api/tasks/{task_id}/report` | GET | Final report |
| `/api/tasks/{task_id}/review` | GET | Review scorecard/revision plan |
| `/api/tasks/{task_id}/events` | GET | Run event stream |
| `/api/tasks/{task_id}/summary` | GET | Run summary |
| `/api/tasks/{task_id}/traces` | GET | LangSmith/local trace refs |

---

## 7. Demo Flow

1. Open `http://127.0.0.1:5003`.
2. Create a new research task.
3. Enter: `Trae 是字节旗下 AI IDE，请分析 AI coding agent 赛道`.
4. The app uses the `ai_coding_agent` mock crawler pack: Trae, Cursor, Windsurf, GitHub Copilot, Claude Code, OpenAI Codex, Devin.
5. Run the main flow: `Researcher -> Analyst -> Editor -> Reviewer`.
6. Open the final report first.
7. Expand Research Tree to inspect every Markdown artifact.
8. Open Evidence/Source records to verify claims.
9. Open Reviewer Scorecard and Revision Plan.
10. If the issue is report-level, trigger Editor regeneration from existing analysis.

---

## 8. Documentation Index

| Document | Purpose |
|---|---|
| `PRODUCT_DEFINITION.md` | Product definition, philosophy, report model, agent boundaries |
| `PRD_0528.md` | Requirements, P0 scope, acceptance criteria |
| `SOP_0528.md` | Coding, logging, Git, failure, sub-agent, smoke test rules |
| `docs/architecture.md` | LangGraph, artifact tree, state, storage, recovery model |
| `docs/demo_script.md` | 5-minute competition demo script |

---

## 9. License

Internal project for the ByteDance CIS AI full-stack project challenge.
