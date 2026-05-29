# Scout Product Definition

**Version**: v1.0  
**Date**: 2026-05-28  
**Product name**: Scout  
**Primary output**: 竞品调研报告 / Competitive Analysis Report  
**Primary audience**: 产品经理、创业团队、战略/投研团队；比赛评委是重要评审人，但不是唯一叙事对象。

---

## 1. Product Positioning

Scout 是一个 **AI 竞品分析工作台**。它帮助产品和战略团队围绕一个赛道、产品或机会，完成从研究规划、资料采集、模块分析、报告编辑到审稿质检的全链路竞品调研。

Scout 的前台形态是一份可交付的竞品调研报告；底层差异是一个 **可审计的多 Agent 研究系统**。系统不只生成结果，还保留研究计划、研究线、分析模块、编辑说明、审稿评分和证据链。

一句话定义：

> Scout 是一支可审计的 AI 竞品调研小组，把碎片资料组织成一份能被产品和战略团队用于决策的竞品调研报告。

Scout 不做“漂亮但不可追溯的 AI 报告”。Scout 要让用户知道：系统看到了什么、没有看到什么、为什么这样判断、哪些判断可信、哪些只是弱信号。

---

## 2. Product Philosophy

### 2.1 结论先行，但必须带可信度

Scout 的报告不采用学术论文式的“先堆资料再等读者自己推理”。面向产品决策时，用户需要先看到判断，再看判断是否可靠。

默认表达顺序：

1. 结论
2. 可信度
3. 关键依据
4. 详细证据
5. 信息缺口
6. 下一步动作

### 2.2 只能看到一部分世界，所以必须显式表达边界

公开资料、搜索结果、Mock data 和网页采集都只能覆盖部分现实。系统必须标注：

- 哪些资料覆盖充分。
- 哪些竞品或维度信息不足。
- 哪些结论是强判断。
- 哪些结论只是弱信号或假设。
- 哪些问题需要下一轮调研验证。

### 2.3 竞品分析从用户任务出发，而不是从产品外形出发

Scout 先定义 Problem Space，再定义竞品集合。

例如研究“AI 穿戴式运动健身设备”，Researcher 不应只搜“AI wearable fitness device”，而要先拆：

- 用户任务：提升运动表现、健身指导、动作纠正、健康监测、训练计划。
- 广义替代：传统运动设备、健身 App、私教、课程、健康监测工具。
- 相邻品类：智能手表、智能耳机、智能戒指、运动传感器。
- 垂类竞品：AI 健身 App、AI 私教、动作识别产品。
- 直接竞品：AI 穿戴式健身设备。
- 潜在进入者：Apple、Garmin、WHOOP、Keep、Strava、大模型公司、硬件品牌。

### 2.4 中间产物不是调试残留，而是研究资产

所有 Agent 产物都要沉淀为 Markdown artifacts。用户默认看最终报告，但可以随时展开研究树查看：

- Research plan
- Research track
- Evidence card
- Analysis module
- Analysis synthesis
- Editorial notes
- Review scorecard
- Revision plan

### 2.5 不盲目自动重跑

Reviewer 默认不自动回退整条链路。它生成精确修订计划，指出问题在哪个 artifact、哪个模块、是否需要新研究、是否可接受为 limitation。

第一版仅支持轻量返修：

> Regenerate Final Report from Existing Analysis

也就是报告层问题可重跑 Editor，不重跑 Researcher/Analyst，避免 token 燃烧。

---

## 3. Reading Model of the Final Report

Scout 报告需要满足三层阅读深度：

1. **1 分钟判断**：忙的人看一页结论、Answer Map、风险和建议。
2. **20 分钟深读**：产品/战略同学读完整市场、用户、竞品、能力、商业、风险分析。
3. **1 小时审计**：质疑者可以追溯全部 evidence、source、module analysis 和 review scorecard。

最终报告不是浅 memo，而是：

> 有 memo 第一屏的深度竞品调研报告。

---

## 4. Final Report Structure

展示名：

- 中文：竞品调研报告
- 英文：Competitive Analysis Report

默认语言策略：

- 用户输入可以是中文或英文。
- 来源可以是中文或英文。
- 分析正文和最终报告默认中文。
- 产品名、专有名词、英文原文标题可以保留英文。
- 前端中文主导、英文辅助。

推荐目录：

```markdown
# {Topic} 竞品调研报告
Competitive Analysis Report

## 0. 一页结论
- 当前判断
- 可信度
- 推荐动作
- 最大风险

## 1. 核心问题与当前答案 / Answer Map
| 核心问题 | 当前判断 | 可信度 | 关键依据 | 行动含义 |
|---|---|---|---|---|

## 2. 研究范围与方法
- 研究对象
- Problem Space
- 竞品分层逻辑
- 数据来源
- 信息缺口

## 3. 市场与时机
- 市场规模
- 增长驱动
- 赛道阶段
- 关键不确定性

## 4. 用户与需求真实性
- 目标用户
- 场景
- 痛点
- 替代方案
- 真需求/弱需求/伪需求判断

## 5. 竞争格局与玩家分层
- 广义替代
- 相邻品类
- 垂类竞品
- 直接竞品
- 潜在进入者

## 6. 核心竞品深拆
- 定位
- 核心能力
- 用户
- 商业模式
- 护城河
- 短板

## 7. 能力/技术/商业模式对比矩阵
| 维度 | 产品 A | 产品 B | 产品 C |
|---|---|---|---|

## 8. 机会点与战略选项
| 选项 | 做法 | 优点 | 风险 | 前置条件 | 建议程度 |
|---|---|---|---|---|---|

## 9. 风险、未知数与下一步验证
- 结论风险
- 数据缺口
- 下一步调研

## 10. 附录
- Evidence Index
- Source Index
- Analyst Module Links
- Reviewer Scorecard
```

---

## 5. Main Architecture Philosophy

Scout 使用 **串行主流程 + 树状并行研究结构**。

主流程固定串行：

```text
Researcher -> Analyst -> Editor -> Reviewer
```

主节点内部可以树状并行：

```text
Researcher
  research_plan.md
  tracks/
    market_research.md
    user_research.md
    competitor_research.md
    product_research.md
    tech_research.md
    business_research.md
    risk_research.md
  research_synthesis.md

Analyst
  analysis_plan.md
  modules/
    market_analysis.md
    user_analysis.md
    competitor_landscape.md
    product_feature_analysis.md
    tech_analysis.md
    business_model_analysis.md
    risk_analysis.md
  analysis_synthesis.md

Editor
  editorial_plan.md
  final_report.md
  editorial_notes.md

Reviewer
  review_scorecard.md
  revision_plan.md
```

第一版不一定物理实现所有子 Agent 并行，但产品定义和 artifact tree 必须按这个方向设计。

---

## 6. Artifact Protocol

Scout 采用：

> Structured Markdown First + Artifact Tree + JSON Index

### 6.1 Markdown 是主产物

Markdown 是用户、Agent 和 Reviewer 共同阅读的工作文档。所有关键中间产物都必须以 Markdown 保存。

### 6.2 JSON 是索引和校验缓存

JSON 不承担产品叙事。它用于：

- 前端树状导航。
- API 返回。
- 状态、依赖、路径、置信度索引。
- Pydantic 校验。
- 回归测试。

### 6.3 并行产物不能写同一个文件

每个子 Agent 写自己的 Markdown。父节点或 orchestrator 负责生成 synthesis 和 index，避免并发写冲突。

---

## 7. Agent Boundaries

### 7.1 Researcher

Researcher 是 **研究规划 + 信息采集 + 证据结构化 Agent**。

它负责：

- 生成 `research_plan.md`。
- 定义 Problem Space。
- 规划 Research Tracks。
- 分配子 Research Agent。
- 设计 Search Playbook。
- 执行搜索、采集或读取 Mock data。
- 在搜索失败、网页被拦截、来源不足时降级并记录。
- 输出 tracks Markdown。
- 输出 sources/evidence/coverage map。
- 输出 `research_synthesis.md`。

它不能：

- 做战略建议。
- 做谁赢谁输的判断。
- 编造缺失资料。
- 把“搜不到”包装成“没有问题”。

### 7.2 Analyst

Analyst 是 **分析编排者 + 模块分析作者**。

它负责：

- 生成 `analysis_plan.md`。
- 对 Researcher 结果做 Evidence Reality Check。
- 判断哪些模块应该写、哪些只适合附录。
- 分配子 Analyst 模块。
- 写包含 Claim Pack 的模块分析文章。
- 输出核心判断集合。
- 输出 `analysis_synthesis.md`。

它不负责：

- 搜索资料。
- 扩展竞品集合。
- 写最终报告。
- 为证据不足的方向强行下结论。

### 7.3 Editor

Editor 是 **主编 / Report Editor-in-Chief**，不是 Writer。

它负责：

- 读取 Analyst 模块和 synthesis。
- 理解原材料精髓。
- 生成 `editorial_plan.md`。
- 组织报告主线。
- 写一页结论、Answer Map、章节过渡和最终报告。
- 合并、重排、降级或删去弱观点。
- 形成跨模块综合观点。
- 输出 `final_report.md`。
- 输出 `editorial_notes.md`，记录编辑决策。

它不能：

- 新增没有 Analyst 支撑的实质判断。
- 把弱信号包装成强结论。
- 删除关键风险或信息缺口。
- 为了可读性牺牲可追溯性。

### 7.4 Reviewer

Reviewer 是 **虚拟审稿委员会 / Editorial Review Committee**。

物理上第一版可以是单节点；逻辑上必须模拟多个审稿视角：

- Evidence Reviewer
- Product Reviewer
- Strategy Reviewer
- Editorial Reviewer
- Risk Reviewer
- Originality Reviewer

它负责：

- 生成 `review_scorecard.md`。
- 生成 `revision_plan.md`。
- 对报告质量打分。
- 精确指出问题 artifact。
- 判断是否通过、是否接受 limitation、是否建议局部返修。

它默认不自动触发重跑。

---

## 8. Reviewer Scorecard

质量维度：

1. **可信度 / Credibility**
2. **深度 / Depth**
3. **可读性 / Readability**
4. **独创洞察 / Original Insight**
5. **行动性 / Actionability**
6. **可追溯 / Traceability**
7. **边界感 / Uncertainty Awareness**

Reviewer 的结论类型：

- `pass`
- `revise`
- `accept_with_limitation`

---

## 9. Frontend Product Expression

前端默认中文主导、英文辅助：

- 新建调研 / New Research
- 研究树 / Research Tree
- 研究线 / Research Tracks
- 分析模块 / Analysis Modules
- 最终报告 / Final Report
- 证据库 / Evidence
- 审稿评分 / Review Scorecard
- 返修计划 / Revision Plan

Workbench 不再只展示线性四卡片，而要展示 research tree：

- 主节点状态。
- 子节点状态。
- Markdown artifacts。
- Reviewer issues。
- report/evidence 跳转。

---

## 10. First Implementation Target

第一版实现优先级：

1. 保持四个主节点串行：Researcher -> Analyst -> Editor -> Reviewer。
2. 文档和数据结构按 artifact tree 设计。
3. Editor 替换 Writer 命名和产品语义。
4. Reviewer 默认生成 scorecard/revision plan，不自动回退。
5. 先支持 Editor-level regeneration。
6. 子 Agent 可以先由单节点内部模拟，后续再物理拆分并行。

