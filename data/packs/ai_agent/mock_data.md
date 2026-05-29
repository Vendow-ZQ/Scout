# Mock Data Pack: ai_agent

用途：为 Scout 演示“通用 AI Agent 竞品分析”提供可控的一手/二手摘录。该数据包只替代 Researcher 的外部采集环节，后续 Researcher 证据抽取、Analyst 分析、Writer 报告生成、Reviewer 质检均应调用真实 LLM。

## Scope

- industry: 通用 AI Agent
- region: 全球 + 中国
- main_product: ChatGPT
- competitors: ChatGPT, Claude, Gemini, Genspark, Manus
- normal source file: `sources.json`
- broken demo source file: `broken/missing_pricing_source.json`

## Normal Sources

| source_id | type | product | purpose |
|---|---|---|---|
| src_chatgpt_001 | official | ChatGPT | 官方能力与产品定位 |
| src_chatgpt_002 | review | ChatGPT | 第三方评测和优缺点 |
| src_claude_001 | official | Claude | 官方能力与产品定位 |
| src_claude_002 | review | Claude | 与 ChatGPT 的深度对比 |
| src_gemini_001 | official | Gemini | Google 官方能力描述 |
| src_gemini_002 | review | Gemini | 第三方评测和落地反馈 |
| src_genspark_001 | official | Genspark | 官方产品页与功能能力 |
| src_genspark_002 | news | Genspark | 中国 AI Agent 市场叙事 |
| src_manus_001 | official | Manus | 官方 Agent 能力描述 |
| src_manus_002 | review | Manus | 第三方评测和可信度讨论 |
| src_market_001 | survey | market | 2025 AI Agent 市场趋势 |
| src_market_002 | survey | market | AI Agent 用户需求调研 |

## Broken Case

`broken/missing_pricing_source.json` 刻意移除 `src_manus_002`，用于首轮触发 Reviewer 的来源覆盖/定价覆盖问题。LangGraph 重试 Researcher 后应切回 `sources.json`，让 Reviewer 能观察到修复链路。

## Agent Contract

- Mock data 不允许绕过 LLM：它只是“爬虫/网页采集”的本地替身。
- Agent 不应直接读取本说明文档做分析；机器输入仍以 JSON 数据包为准。
- 中间产物必须同时保存 JSON 与 Markdown：JSON 给 API/前端，Markdown 给人工 review 和开发 agent 排查。
