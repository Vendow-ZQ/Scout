# Scout 演示脚本 - 5 分钟现场演示

**Version**: v2.0  
**Date**: 2026-05-28  
**Demo URL**: `http://127.0.0.1:5003`

---

## 0. 准备

1. 启动后端：

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. 启动前端：

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5003
```

3. 浏览器打开 `http://127.0.0.1:5003`。
4. 使用 `ai_coding_agent` 数据包。前端输入 Trae / AI coding agent 相关问题时会自动选择该包。
5. 确认 LLM 环境变量已配置。Mock data 只替代外部采集，不替代 Agent 推理。

---

## 1. 演示主线

这次演示不要把 Scout 讲成“自动生成报告的小工具”。讲法应该是：

> Scout 是一个 AI 竞品分析工作台。它的前台输出是一份能给产品、战略、投研团队看的竞品调研报告；后台是一套可审计的多 Agent 研究树。我们不仅能看到结论，还能看到每一步怎么规划、怎么研究、怎么分析、怎么编辑、怎么审稿。

---

## 2. Step 1: 创建调研任务（30 秒）

**操作**

- 打开首页。
- 点击新建调研 / New Research。
- 选择或触发 `ai_coding_agent` 数据包。
- 保持或输入：
  - 主品：Trae
  - 竞品：Cursor, Windsurf, GitHub Copilot, Claude Code, OpenAI Codex, Devin
  - 分析目标：Trae 是字节旗下 AI IDE，请分析 AI coding agent 赛道的竞品格局、用户需求、能力差异、商业化机会和风险
- 点击启动分析。

**解说词**

> 我们先创建一个 AI coding agent 赛道的竞品调研任务，主品是字节旗下 Trae。这里的重点不是填一个长问卷，而是把调研主题、目标产品、竞品和决策问题给到系统。Scout 会先规划研究方向，再从提前采集的高质量公开资料包里读取证据；mock data 只替代外部爬虫，不替代后续 Agent 推理。

**展示点**

- 中文主导、英文辅助的任务创建界面。
- 输入负担尽量低。
- 用户把问题交给系统，系统负责拆解。

---

## 3. Step 2: 观察主流程和研究树（60 秒）

**操作**

- 进入 Workbench。
- 展示主流程：Researcher -> Analyst -> Editor -> Reviewer。
- 展开 Research Tree。
- 打开 `research_plan.md`。

**解说词**

> Scout 的四个大 Agent 是串行的：Researcher、Analyst、Editor、Reviewer。但每个 Agent 里面不是单点黑盒，而是一棵研究树。Researcher 会先做 Research Plan，拆出市场、用户、竞品、产品、技术、商业模式和风险等研究线，然后再进入搜索、读取、降级和证据提取的 ReAct 循环。

**展示点**

- LangGraph 主流程。
- 研究树，而不是平铺的四张卡片。
- `research_plan.md` 能看到 Problem Space、Search Playbook、Sub-agent Assignment。

---

## 4. Step 3: 查看 Analyst 模块文章（60 秒）

**操作**

- 展开 Analyst。
- 打开 `analysis_plan.md`。
- 打开一个模块，例如 `competitor_landscape.md` 或 `market_analysis.md`。

**解说词**

> Analyst 不是把资料简单整理成 JSON。它会先检查 Researcher 找到的证据质量，再决定哪些分析模块值得写。每个模块是一篇小的分析文章，里面有 Claim Pack：结论、可信度、证据引用、不确定性和决策含义。

**展示点**

- Analyst 不搜索竞品，只基于 Researcher 产物分析。
- 模块文章有完整文字分析。
- Claim Pack 支持下游 Editor 和 Reviewer 使用。

---

## 5. Step 4: 展示最终报告（90 秒）

**操作**

- 打开 Final Report。
- 展示一页结论。
- 展示 Answer Map。
- 展示竞品对比矩阵。
- 展示机会点、风险和下一步验证。

**解说词**

> 最终交付不是流水账，而是一份竞品调研报告。它先给结论和可信度，再给证据。忙的人可以 1 分钟看判断，产品和战略同学可以 20 分钟看完整分析，质疑的人可以继续追到 evidence、source 和每个分析模块。

**展示点**

- 一页结论。
- 核心问题与当前答案 / Answer Map。
- 市场、用户、竞品、矩阵、机会、风险。
- 中文正文，英文术语保留。
- 可复制到飞书继续编辑。

---

## 6. Step 5: 展示审稿机制（60 秒）

**操作**

- 打开 Reviewer。
- 展示 `review_scorecard.md`。
- 展示 `revision_plan.md`。
- 如果 verdict 是 `revise`，展示修订建议。
- 如果是报告层问题，展示 Regenerate Final Report from Existing Analysis。

**解说词**

> Reviewer 不是简单打分，它像一个虚拟审稿委员会：证据审稿人、产品审稿人、战略审稿人、编辑审稿人、风险审稿人、原创性审稿人都会提出意见。但它默认不会自动重跑整条链路，因为那会变成 token 燃烧机。它会精确指出要改哪个 artifact，P0 只支持报告层重生成，也就是只让 Editor 基于已有分析重写报告。

**展示点**

- Scorecard 的 7 个维度：可信度、深度、可读性、独创洞察、行动性、可追溯、边界感。
- Revision Plan 精确到目标 artifact。
- 无默认全链路自动回退。
- 局部返修思路符合工程成本控制。

---

## 7. Step 6: 展示溯源与可观测性（40 秒）

**操作**

- 打开 Evidence/Source。
- 点击一个 evidence 或 source。
- 打开 Run Events 或 Trace。

**解说词**

> 每条关键结论都应该能追到证据和来源。系统还会记录运行事件：哪个节点开始、哪个 artifact 保存、哪里用了 fallback、Reviewer 做了什么判断。这个不是隐藏 debug 信息，而是产品的一部分。

**展示点**

- Claim -> Evidence -> Source。
- Artifact tree。
- JSONL run events。
- LangSmith 或 local trace mirror。

---

## 8. 得分点对应

| 评委关心点 | 演示位置 | 证据 |
|---|---|---|
| 产品理解 | Final Report | 结论先行、Answer Map、机会/风险/行动建议 |
| 竞品分析深度 | Analyst modules + report | 市场、用户、竞品、矩阵、战略选项 |
| 多 Agent 协作 | Workbench 主流程 | Researcher -> Analyst -> Editor -> Reviewer |
| Agent 不 toy | Research Tree | plan、tracks、modules、synthesis、review artifacts |
| LangGraph 架构 | Workbench / architecture | 串行主节点 + 节点内部树状 fan-out/fan-in |
| 可审计性 | Artifact detail | Markdown artifacts 全部可打开 |
| 证据链 | Evidence/Source | Claim -> Evidence -> Source |
| 鲁棒性 | Revision Plan | 不自动全链路重跑，支持局部返修 |
| 可观测性 | Run Events / Trace | JSONL events + LangSmith/local trace |
| 工程完整度 | README/SOP/API | 前后端、存储、日志、artifact、文档齐全 |

---

## 9. 备用讲法

如果现场时间不够，优先讲三件事：

1. **Final Report**：Scout 最终交付一份能给产品/战略团队看的竞品调研报告。
2. **Research Tree**：每一步的中间 Markdown 产物都可追溯。
3. **Reviewer**：审稿委员会保证质量，但默认不自动烧 token 重跑全链路。

一句收尾：

> Scout 的价值不是“AI 帮我写一篇报告”，而是“AI 组建了一支可审计的竞品调研小组，并把研究过程和最终判断都沉淀下来”。
