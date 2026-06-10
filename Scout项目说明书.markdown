# Scout 项目说明书
**项目名称**：Scout
**产品定位**：AI 竞品分析工作台 / Competitive Intelligence Workspace
**提交场景**：字节 CIS AI 全栈项目挑战赛最终提交
**核心一句话**：Scout 把竞品调研从“一次性 AI 报告”升级为“可运行、可追溯、可审稿、可复用的 AI 研究工作流”。
> 【图片占位 P0：项目封面图】
> 建议使用产品截图或 AIGC 生成：一个企业情报中心式工作台，用户输入调研主题后，Researcher、Analyst、Editor、Reviewer 四个节点依次流转，右侧浮现 Sources、Evidence、Claims、Final Report、Review Scorecard。画面重点是“从问题到研究资产”，不要突出某个单一样例品牌。
## 1. 项目摘要
Scout 是一个面向产品、战略、投研、增长和创业团队的 AI 竞品分析工作台。用户输入一个产品、赛道、市场机会或竞品问题后，系统会自动完成研究规划、资料读取、证据结构化、模块分析、报告编辑和质量审稿，最终生成一份可用于评审、汇报和后续协作的竞品调研报告。
它的核心价值不只是“写得更快”，而是把原本散落在搜索结果、表格、聊天记录、个人判断和临时文档里的调研过程，组织成一套可复核的研究系统。用户不仅能拿到最终报告，还能看到系统看过哪些资料、抽取了哪些证据、形成了哪些关键判断、哪些结论置信度较低、下一轮应该补充什么。
**一句话理解**：Scout 是一支可审计的 AI 竞品调研小组，帮助团队把碎片资料变成可追溯的竞争情报。
**核心流程**：Researcher 负责拆题和提证据，Analyst 负责模块分析和关键判断，Editor 负责组织最终报告，Reviewer 负责质量审稿和返修建议。
**最终产出**：竞品调研报告、来源索引、证据卡、关键 claims、分析模块、审稿评分和修订计划。
**商业化方向**：SaaS seat、Agent run 用量、企业知识库接入、行业数据包、定期竞品监控、审稿与合规模块。
Scout 的产品主张是：结论先行，证据可追溯；报告可读，过程可审计。它不是替代人的最终判断，而是让团队更快形成初版判断，更清楚地说明依据，更低成本地复用研究资产。
> 【图片占位 P1：产品摘要信息图】
> 建议用 AIGC 生成一张横向流程图：用户输入“研究一个赛道/竞品”，经过 Researcher -> Analyst -> Editor -> Reviewer，输出 Report + Evidence + Review。图中不要出现具体组织名称，强调通用企业研究场景。
## 2. 真实需求：竞品调研不是写作问题，而是决策基础设施问题
竞品调研通常发生在立项、版本规划、定价、商业化、市场进入、客户拓展、投资判断和战略复盘之前。团队真正要回答的不是“有没有一篇报告”，而是“这个机会是否真实、竞品怎么分层、我们应该怎么打、风险在哪里、结论能不能被追问”。
传统做法往往依赖人工搜索、表格整理和个人经验。它可以产出一份文档，但过程很难复用：资料散落在浏览器、群聊和本地文件里；判断和证据之间缺少稳定链接；报告被质疑时需要重新翻出处；下一次调研又要从零开始。
通用 AI 聊天工具解决了写作速度，却没有完整解决研究可信度。它可以快速生成“像报告”的文本，但团队很难知道 AI 看了什么、漏了什么、哪些结论只是猜测、哪些结论能作为行动依据。对真实业务决策来说，速度重要，证据链和可复核性同样重要。
| 典型场景 | 传统做法 | 真实痛点 | Scout 的处理 |
|---|---|---|---|
| 新产品立项 | 手动搜索、整理表格、写文档 | 时间长，结论依赖个人经验 | 自动生成研究计划、竞品分层、需求真实性判断和机会建议 |
| 版本规划 | 临时看几个竞品页面 | 容易漏掉替代方案和潜在进入者 | 先定义 Problem Space，再扩展直接竞品、相邻品类和替代方案 |
| 商业化定价 | 人工对比公开价格页 | 定价、套餐、权益和目标用户难统一比较 | 抽取 price、packaging、target users、limits，形成对比矩阵 |
| 战略/投研 | 依赖长周期深度研究 | 初筛成本高，资料和判断难复用 | 先生成可审计初版，再决定是否进入深度调研 |
| 销售/解决方案 | 为客户行业临时准备材料 | 每次从零开始，素材沉没 | 行业数据包、证据卡和报告模块可复用 |
| 管理层评审 | 看结论，但追问来源 | 证据散落，难以现场说明 | Claim -> Evidence -> Source 保留完整链路 |
Scout 的机会就在这里：把竞品研究拆成稳定的工作对象，包括研究问题、来源、证据、判断、分析模块、最终报告和审稿记录。每次运行都不只是生成一次文本，而是在积累组织自己的 competitive intelligence layer。
## 3. 目标用户与使用场景
Scout 不把产品限定在某个组织。它适合任何需要持续理解市场和竞品的团队，也能通过不同数据包和模板适配 AI、SaaS、消费电子、教育、游戏、企业服务、本地生活等行业。
| 用户类型 | 高频问题 | Scout 提供的价值 |
|---|---|---|
| 产品经理 | 需求是否真实、竞品如何设计、机会点在哪里 | 快速产出结论先行的竞品报告，并让关键判断追到证据 |
| 创业团队 | 赛道是否值得进入、如何定位、如何避开红海 | 用较低成本形成市场、用户、竞品和商业化初版判断 |
| 战略/投研团队 | 玩家如何分层、壁垒是什么、风险是什么 | 把公开资料整理成结构化机会评估，并标注进一步尽调点 |
| 增长/商业化团队 | 怎么定价、怎么包装、怎么找到切入人群 | 形成套餐、价格、目标用户、渠道和卖点对比 |
| 企业研究团队 | 如何持续跟踪竞品变化 | 将来源、证据、判断和报告模块沉淀为可复用资产 |
| 研发/平台团队 | Agent 系统是否真实可用、是否可维护 | 观察 LangGraph 流程、schema、artifact、日志和审稿机制 |
这张表用于明确“谁会用”和“为什么用”。真正的产品价值在于，Scout 可以把不同角色对同一个市场问题的理解统一到同一套证据链和报告资产上。
## 4. 产品主张与阅读模型
Scout 的默认报告要满足三种阅读深度。忙的人可以在 1 分钟内看到方向判断；负责推进的人可以用 20 分钟读完市场、用户、竞品、能力、商业和风险；质疑者可以继续追到 evidence、source、module analysis 和 review scorecard。
| 阅读层级 | 读者目标 | Scout 对应内容 |
|---|---|---|
| 1 分钟判断 | 先知道是否值得继续看 | 一页结论、Answer Map、机会、风险、可信度边界 |
| 20 分钟深读 | 理解市场、用户、竞品、能力、商业化和风险 | Final Report、Comparison Matrix、SWOT、Opportunities |
| 1 小时审计 | 追问结论来源、证据强弱和推理过程 | Sources、Evidence、Claims、Analysis Modules、Review Scorecard |
这个模型让 Scout 的输出既能做管理层摘要，也能做产品评审材料，还能成为后续研究的资料库。
> 【图片占位 P2：阅读模型图】
> 建议用 AIGC 生成一个三层阶梯图：1 分钟判断、20 分钟深读、1 小时审计。每层标出对应产物：Summary、Report、Evidence/Review。
## 5. 核心使用流程
### 5.1 创建调研任务
用户从业务问题进入，只需要输入调研主题、关注维度和地区范围。系统根据问题匹配数据包、竞品集合和研究模板。输入可以是“请分析某个 AI 产品的竞品格局”，也可以是“我想判断某个垂直赛道是否值得进入”。
| 输入项 | 说明 | 产品价值 |
|---|---|---|
| 调研主题 | 产品、赛道、竞品或市场机会 | 保持自然语言入口，降低使用门槛 |
| 关注维度 | 市场、用户、竞品、功能、技术、商业、风险 | 让输出贴近真实决策问题 |
| 地区范围 | 全球、中国、北美、欧洲或自定义区域 | 控制资料边界和结论适用范围 |
| 数据包/竞品列表 | 自动推荐，也可后续手动选择 | 平衡演示稳定性和通用扩展性 |
> 【图片占位 P3：新建调研页面截图】
> 建议使用产品截图：首页 TaskCreate，重点展示自然语言输入框、关注维度选择和地区范围选择。文案应展示通用调研问题，不必使用具体样例。
### 5.2 多 Agent 研究流程
Scout 的主流程固定为 Researcher -> Analyst -> Editor -> Reviewer。这个顺序符合真实研究工作：先定义问题和资料边界，再做分析，再写报告，最后审稿。
```text
Researcher -> Analyst -> Editor -> Reviewer
```
| Agent | 职责 | 主要产物 | 边界 |
|---|---|---|---|
| Researcher | 拆解研究问题、读取来源、抽取证据 | research_plan、sources、evidence、research_synthesis | 不直接写最终战略结论 |
| Analyst | 基于证据做模块分析和关键判断 | analysis_plan、market/user/competitor analysis、profiles、claims | 不新增无来源事实 |
| Editor | 把模块分析组织成可读报告 | editorial_plan、final_report、editorial_notes | 不编造新证据 |
| Reviewer | 检查来源覆盖、逻辑、风险和可用性 | review_scorecard、revision_plan | 不默认自动重跑全链路 |
> 【图片占位 P4：Workbench Agent Pipeline 截图】
> 建议使用产品截图：Workbench 中 Researcher、Analyst、Editor、Reviewer 的运行状态，以及右侧 Sources、Evidence、Claims 统计。用途是证明多 Agent 协作是可见流程，不只是概念。
### 5.3 查看最终报告
最终报告按“先结论、再分析、最后证据”的结构组织，适合复制到飞书、Notion、Confluence、Google Docs 或企业知识库继续协作。
| 报告章节 | 解决的问题 | 使用场景 |
|---|---|---|
| Executive Summary | 当前最重要的判断是什么 | 会前预读、管理层同步 |
| Answer Map | 每个核心问题的当前答案和可信度 | 快速对齐争议点 |
| Scope & Method | 研究范围、时间边界和资料来源 | 防止结论被误用 |
| Market & Timing | 市场阶段、增长驱动和不确定性 | 判断是否值得进入 |
| User & Demand | 用户是谁、痛点是否真实、替代方案是什么 | 判断需求优先级 |
| Competitive Landscape | 竞品分层、直接竞品、替代方案和潜在进入者 | 制定产品定位 |
| Comparison Matrix | 功能、技术、价格、商业模式和风险横向对比 | 产品和商业化评审 |
| Opportunities & Risks | 机会点、策略选项、风险和下一步验证 | 形成后续行动 |
报告不是流水账，也不是聊天记录，而是一份可以进入评审、汇报和后续协作的决策文档。
> 【图片占位 P5：Final Report 截图】
> 建议使用产品截图：Workbench 的 Final Report tab 或 final_report.md 详情页，画面中应包含 Executive Summary 和 Answer Map。
### 5.4 展开研究树和中间产物
Scout 把中间产物视为研究资产，而不是调试残留。用户可以打开每一阶段的 Markdown artifact，理解系统如何从资料走到结论。
| 阶段 | 可打开产物 | 作用 |
|---|---|---|
| Researcher | research_plan.md、sources.md、evidence.md、research_synthesis.md | 展示研究范围、来源和证据 |
| Analyst | analysis_plan.md、market_analysis.md、user_analysis.md、competitor_analysis.md、profiles.md、claims.md | 展示证据如何转化为判断 |
| Editor | editorial_plan.md、final_report.md、editorial_notes.md | 展示报告主线和编辑取舍 |
| Reviewer | review_scorecard.md、revision_plan.md | 展示质量问题和返修建议 |
> 【图片占位 P6：Artifact Tree 截图】
> 建议使用产品截图：Workbench 中 artifact 列表或 artifact 详情页，突出中间产物可打开、可阅读、可复用。
### 5.5 证据与来源追溯
每条 Evidence Card 都绑定 source、product、dimension、fact、confidence 和 evidence_id。报告中的关键 claim 可以向下追到 evidence，再追到 source。
| 字段 | 用途 |
|---|---|
| evidence_id | 作为 claim 引用的证据锚点 |
| source_id | 连接原始来源记录 |
| product | 标记证据对应的产品或竞品 |
| dimension | 标记能力、价格、用户、商业化、风险等维度 |
| fact | 保存可复核事实 |
| confidence | 表达证据强弱和判断边界 |
这种设计解决了真实评审里的核心问题：当有人问“这句话从哪里来”，Scout 不需要回到浏览器和聊天记录里翻找，而是可以直接从 claim 进入 evidence，再看到来源记录、证据维度和置信度。
> 【图片占位 P7：Evidence & Sources 截图】
> 建议使用产品截图：Sources 页面，展示 Evidence cards 数量、Sources 数量、单条 evidence 的 product/dimension/confidence/source。
### 5.6 审稿与局部返修
Reviewer 是质量门禁，不是形式化打分。它会检查来源覆盖、Claim 质量、报告完整性、逻辑一致性、风险表达和可读性，并输出精确到 artifact 的 revision plan。
| 问题类型 | 归因 | 处理方式 |
|---|---|---|
| 来源不足 | Researcher | 补充来源或标注 source gap |
| Claim 证据弱 | Analyst | 降低置信度、补充 evidence refs 或改写判断 |
| 报告结构问题 | Editor | 基于现有 analysis 重新生成 final report |
| 合规或风险表达不足 | Reviewer | 标注风险、增加限制条件和下一步验证 |
| 轻微表述问题 | Editor/Reviewer | 作为 minor issue 记录，不阻断交付 |
这套设计体现了成本控制：Reviewer 负责发现问题，返修策略需要精确控制范围，而不是一看到问题就无限重跑整条链路。
> 【图片占位 P8：Review Scorecard 截图】
> 建议使用产品截图：review_scorecard.md 或 revision_plan.md，展示 issue severity、target_agent、target_artifact 和建议动作。
## 6. 产品功能拆解
Scout 的产品模块围绕“发起调研、观察过程、阅读报告、追溯证据、控制质量”这条链路展开。下面的表格保留为功能拆解矩阵，用来同时说明已实现能力和产品价值。
| 产品模块 | 已实现能力 | 产品价值 |
|---|---|---|
| 任务创建 | 自然语言输入、关注维度、地区范围、数据包匹配 | 让用户从真实业务问题开始，而不是先填写复杂模板 |
| Workbench 工作台 | Agent pipeline、运行日志、artifact 列表、Final Report、统计卡片、Recent Events | 让 AI 研究过程可见，方便业务和研发共同验证 |
| Artifact 详情页 | Markdown 渲染、Source/Evidence/Claim 格式化、独立页面查看 | 中间产物可以被阅读、复制、复用，也可以作为异步评审材料 |
| Evidence & Sources 页面 | 来源统计、证据卡展示、source title 关联 | 支撑报告可信度，降低追问成本 |
| Reviewer 质量门禁 | review.json、review_scorecard.md、revision_plan.md、severity、issue type、target_agent | 让输出质量可度量，返修范围可控 |
| 数据包机制 | ai_coding_agent、ai_agent、ai_earbuds 等可切换数据包 | 证明 Scout 不绑定单一赛道，可扩展为行业模板和商业化数据包 |
## 7. 技术架构
### 7.1 总体架构
```text
React Workbench
  |
  | REST API
  v
FastAPI Task Service
  |
  | invoke
  v
LangGraph StateGraph
  |
  +-- Researcher
  +-- Analyst
  +-- Editor
  +-- Reviewer
  |
  +-- LLM Adapter
  +-- SQLite Task Store
  +-- Markdown Artifact Store
  +-- JSONL Run Events
```
| 层级 | 技术栈 | 说明 |
|---|---|---|
| Frontend | Vite + React + TypeScript | 任务创建、工作台、artifact、sources 页面 |
| Backend | FastAPI | 任务 API、artifact API、事件 API |
| Agent 编排 | LangGraph | 主流程状态机和节点编排 |
| LLM | OpenAI-compatible adapter，当前可接 Doubao | 真实 LLM 推理，失败时显式报错 |
| Validation | Pydantic | Source、Evidence、Claim、Review 等结构校验 |
| Storage | SQLite + Markdown artifacts + JSON | 任务状态、运行产物、机器可读索引 |
| Observability | JSONL logs + optional tracing | 运行事件、节点状态、artifact refs |
### 7.2 主流程为什么保持克制
Scout 没有把系统一开始做成复杂的全并行 Agent 网络，而是用串行主流程保证可解释性和可维护性。Researcher 必须先明确问题和证据范围，Analyst 才能基于证据做判断，Editor 才能组织报告，Reviewer 才能审查质量。
复杂度被放在节点内部的研究树里，而不是堆在主链路上。Research tracks 和 analysis modules 后续可以拆成真正的并行子 Agent，但 P0 先保留稳定、可解释、可演示的主流程。
### 7.3 Markdown-first 与结构化索引
Scout 选择 Markdown 作为主产物，因为它同时适合用户阅读、Agent 传递、Reviewer 审稿和协作文档复制。JSON 只承担索引、API response、状态缓存、前端导航和 schema 校验。
这种设计避免了两个极端：既不是把所有价值锁在一次聊天上下文里，也不是把用户可读内容塞进复杂 JSON。Markdown 负责沟通，JSON 负责机器处理，日志负责复现和审计。
### 7.4 结构化输出与错误处理
LLM 输出不是自由文本，而是通过 Pydantic schema 校验。EvidenceExtractionOutput、AnalystOutput、ReportOutput、ReviewerOutput 约束了 Agent 之间的交付物；SourceRecord、EvidenceCard、Claim、ProductProfile、ReviewIssue 统一了来源、证据、判断、产品画像和审稿问题。
常见 JSON 格式抖动会触发 repair retry；真正失败会抛出 RuntimeError，并在日志中留下 fallback 记录。这个设计让系统既能适应真实模型输出，又不会把失败伪装成成功。
### 7.5 Artifact 与日志是产品可信度的一部分
Scout 会把每次运行产生的 artifact、run events 和 summary 写入 runtime。研发团队可以定位失败节点，业务团队可以追溯产物来源，未来接入企业工作流时也具备审计基础。
```text
runtime/artifacts/{task_id}/...
runtime/logs/{task_id}.jsonl
runtime/runs/{task_id}/summary.md
```
run events 记录 event_type、node_name、agent_name 和 artifact_refs；run summary 记录 data_pack、schema_pack、LLM provider、node_history 和关键结果。这些不是隐藏 debug 信息，而是产品可信度的一部分。
## 8. 产品化与商业化空间
Scout 的商业价值不在于“卖一篇报告”，而在于让企业拥有持续运行的研究能力。每次运行都会积累来源、证据、判断和模块分析，长期形成组织自己的市场与竞品 intelligence layer。
| 产品化方向 | 形态 | 商业价值 |
|---|---|---|
| AI Research Workspace | 团队工作台、项目列表、研究树、报告库 | 按 seat subscription 收费 |
| Agent run 用量 | 按调研深度、来源数量、模型成本计量 | usage-based 增长空间 |
| 行业数据包 | AI、SaaS、消费电子、教育、游戏、企业服务等垂直包 | pack marketplace 或企业增购 |
| 企业知识库接入 | 内部文档、CRM、访谈记录、工单、会议纪要 | enterprise plan，提高粘性 |
| 定期竞品监控 | 价格变化、版本更新、舆情、招聘和客户案例监控 | scheduled monitor，形成持续收入 |
| 审稿与合规模块 | 来源授权、PII 风险、敏感结论、置信度门禁 | enterprise add-on |
| 协作文档导出 | 飞书、Notion、Confluence、Google Docs、Markdown | 降低进入现有团队流程的阻力 |
| API / Embedded Widget | 嵌入企业内部产品、售前系统和 BI 工具 | 平台化集成收入 |
可衡量的工作流增量包括：初版竞品报告从数小时/数天下降到一次 Agent run；来源追溯从翻浏览器和聊天记录变成直接查看 evidence；返修范围从靠人工经验变成 Reviewer 精确归因；报告从一次性文档变成可复用的 sources、evidence、claims 和 modules。
> 【图片占位 P9：商业化路径图】
> 建议用 AIGC 生成一张产品层级图：底层是数据源和企业知识库，中间是 Agent Research Workflow，上层是 Workspace、Monitoring、Data Packs、Review & Compliance、API。风格应像 SaaS 产品方案图。
## 9. 通用集成场景
Scout 可以作为独立 Web 工作台使用，也可以接入企业已有文档、知识库和协作工具。飞书只是其中一种适配目标；同样的 Markdown artifact 和结构化 JSON 也适合 Notion、Confluence、Google Docs、Slack、Teams、企业门户和内部 BI 系统。
| 集成入口 | Scout 能力 | 输出 |
|---|---|---|
| 文档工具 | 从当前文档上下文发起调研 | 自动生成竞品报告初稿和 evidence appendix |
| 企业知识库 | 读取内部资料和历史报告 | 结合公开资料与内部知识形成判断 |
| 多维表格/数据库 | 读取竞品库、价格表、功能表 | 更新对比矩阵和证据卡 |
| 群聊/项目空间 | 接收自然语言调研请求 | 创建任务并回填报告链接 |
| 定时任务 | 周期性监控竞品变化 | 生成变化摘要、风险提醒和机会更新 |
| 内部平台 API | 嵌入产品运营、售前、投研系统 | 让竞品研究成为可调用能力 |
这个集成设计的重点是保持 Scout 的通用性：前台可以接各种协作入口，后台仍然使用同一套 Agent 研究工作流和 artifact contract。
> 【图片占位 P10：通用集成架构图】
> 建议用 AIGC 生成一张中立的企业集成图：左侧是公开网页、企业知识库、CRM、表格、文档，中央是 Scout Agent Workflow，右侧是报告、监控、API、审稿和协作工具。
## 10. 样例验证：AI Coding Agent 赛道
验证样例只用于证明 Scout 的通用能力，不是产品定位本身。当前样例选择 AI Coding Agent 赛道，是因为这个赛道同时包含市场增长、用户需求、产品能力、技术路线、商业化和风险治理，能完整展示 Scout 的研究工作流。
| 验证项目 | 内容 |
|---|---|
| 研究主题 | AI coding agent 赛道竞品分析 |
| 主品 | Trae |
| 竞品 | Cursor、Windsurf、GitHub Copilot、Claude Code、OpenAI Codex、Devin |
| 研究 tracks | market、user、competitor、product、tech、business、risk |
| 来源数量 | 43 条公开来源记录 |
| 来源类型 | 官网、官方文档、定价说明、技术论文、行业报道、第三方评测、社区反馈 |
| 验证目标 | 证明 Scout 能处理复杂赛道、多竞品、多维度、证据链和审稿问题 |
| 样例边界 | Mock data 只替代外部采集，不替代 Agent 推理和审稿 |
这里的重点不是某个具体竞品，而是证明同一套工作流可以迁移到其他行业和产品问题。
| 产品路线 | 代表产品 | 核心竞争点 | 可迁移分析价值 |
|---|---|---|---|
| IDE-native agent | Trae、Cursor、Windsurf | 低切换成本、代码上下文、文件编辑、运行预览 | 适合分析直接竞品和用户迁移成本 |
| Workflow-native agent | GitHub Copilot | Issue、PR、Actions、企业策略和代码治理 | 适合分析生态绑定和企业流程 |
| CLI/app-native agent | Claude Code、OpenAI Codex | 跨终端、IDE、浏览器、多项目、多代理调度 | 适合分析跨场景工作流入口 |
| Delegated autonomous engineer | Devin | 云端工作区、长期任务、企业部署、审计和成本控制 | 适合分析高阶自动化和企业信任门槛 |
> 【图片占位 P11：AI Coding Agent 赛道地图】
> 建议用 AIGC 生成一张竞品路线图：IDE-native、Workflow-native、CLI/app-native、Delegated autonomous engineer 四条路线，并标出代表产品。也可以直接使用 Final Report 的 Comparison Matrix 截图。
## 11. 当前运行结果
项目已有成功跑通的 AI Coding Agent 样例 artifact。示例 run 证明主链路不是静态展示，而是 Researcher、Analyst、Editor、Reviewer 都产生了可打开产物。
| 项目 | 值 |
|---|---|
| task_id | task_421b69291a2b |
| run_id | run_20260530_094031 |
| data_pack | ai_coding_agent |
| LLM provider | doubao |
| node_history | researcher -> analyst -> editor -> reviewer |
| final_report | 8 claims，100% evidence coverage |
| reviewer behavior | 发现 Windsurf pricing source gap 和 claim 文本问题 |
| 运行意义 | 端到端跑通，且 Reviewer 没有盲目通过，而是保留真实问题 |
当前实现边界也比较清晰：Markdown artifacts、Evidence & Sources、Review Scorecard、Revision Plan 和 Editor-only regeneration API 已覆盖 P0；真实搜索、浏览器采集、报告内 evidence 跳转、前端一键返修和企业知识库接入属于后续路线图。
> 【图片占位 P12：Run Summary 或 Recent Events 截图】
> 建议使用产品截图：Workbench 的 Recent Events、System Overview，或 runtime/runs/{task_id}/summary.md 渲染结果，证明端到端运行真实发生。
## 12. 与现有方案的差异
| 方案 | 优点 | 不足 | Scout 的差异 |
|---|---|---|---|
| 手工竞品调研 | 准确、可控 | 慢、难复用、证据分散 | 自动生成初版研究资产并保留证据链 |
| ChatGPT 类聊天工具 | 快、表达强 | 过程不可审计、返修不结构化 | 多 Agent 分工、artifact tree、Reviewer 质量门禁 |
| 搜索/问答工具 | 来源多、查找快 | 很难形成产品决策报告 | 从 evidence 到 claim 到 final report 的完整链路 |
| BI/知识库工具 | 适合结构化数据 | 不擅长开放式竞品分析 | 支持开放问题、文本资料和产品判断 |
| 咨询报告 | 深度高 | 成本高、周期长、不持续 | 可低成本持续运行，沉淀组织资产 |
Scout 的独特性在于把 Agent 能力、研究方法、产品文档和工程审计放在同一个工作台里。它不是一个更长的 prompt，而是一套可扩展的研究系统。
## 13. 后续路线图
| 阶段 | 目标 | 关键交付 |
|---|---|---|
| P0：比赛 MVP，当前已覆盖 | 证明多 Agent 竞品调研链路真实可运行 | 新建调研任务、数据包机制、LangGraph 主流程、真实 LLM 推理、Markdown artifacts、Final Report、Evidence & Sources、Review Scorecard、Revision Plan、Editor-only regeneration API |
| P1：可用工作台 | 提升日常使用效率和评审闭环 | Artifact tree 树状目录、Evidence ID 报告内跳转、一键导出协作文档、Reviewer 触发 Regenerate Report 按钮、运行进度细分、数据包选择与自定义竞品列表 |
| P2：企业工作流 | 接入真实组织知识和持续监控场景 | 真实搜索和浏览器采集、企业知识库/文档/表格接入、定期竞品监控、团队协作评论、人工确认、私有数据源与权限控制 |
| P3：平台化能力 | 从单一工作台演进为可复用 Agent Research Platform | 子 Agent 物理并行化、多轮研究计划、人工 checkpoint、Agent benchmark、质量回归测试、企业审计、来源授权、PII 风险检测、API 和嵌入式组件 |
## 14. 最终提交摘要
Scout 面向的是一个通用且高频的知识工作场景：团队需要持续理解市场、竞品、用户需求和商业化机会，但现有流程往往慢、散、不可追溯、难复用。Scout 用 Researcher、Analyst、Editor、Reviewer 四段式 Agent 工作流，把这个过程变成可运行的产品系统。
它的前台交付是一份可读的竞品调研报告，后台沉淀的是来源、证据、判断、分析模块、审稿记录和修订计划。这个设计让 Scout 同时具备产品价值、商业化空间和工程可扩展性：产品上解决真实决策需求，商业上可以发展为 AI Research Workspace，工程上通过 LangGraph、Pydantic schema、Markdown artifacts、JSONL logs 和 Reviewer 质量门禁形成稳定系统。
一句话总结：
> Scout 把“AI 生成报告”变成“AI 生成可信研究资产”，让竞品分析从一次性写作走向持续可复用的智能研究工作台。
