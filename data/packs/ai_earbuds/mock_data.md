# Mock Data Pack: ai_earbuds

用途：为 Scout 演示“AI 耳机 / ola friend 竞品分析”提供可控摘录。该数据包只替代 Researcher 的外部采集环节，后续 Researcher 证据抽取、Analyst 分析、Writer 报告生成、Reviewer 质检均应调用真实 LLM。

## Scope

- industry: AI 耳机
- region: 全球 + 中国
- main_product: ola friend
- competitors: Nothing Ear (a), Pixel Buds Pro, AirPods Pro 2, Galaxy Buds 3 Pro
- normal source file: `sources.json`
- broken demo source file: `broken/missing_pricing_source.json`

## Normal Sources

| source_id | type | product | purpose |
|---|---|---|---|
| src_olafriend_001 | official | ola friend | 官方产品定位和 AI 能力 |
| src_olafriend_002 | review | ola friend | 第三方深度评测 |
| src_nothing_001 | official | Nothing Ear (a) | 官方产品功能 |
| src_nothing_002 | review | Nothing Ear (a) | 第三方评测和体验 |
| src_pixelbuds_001 | official | Pixel Buds Pro | Google 官方能力描述 |
| src_pixelbuds_002 | review | Pixel Buds Pro | 第三方评测 |
| src_airpods_001 | official | AirPods Pro 2 | Apple 官方产品能力 |
| src_airpods_002 | review | AirPods Pro 2 | 横向评测对比 |
| src_galaxybuds_001 | official | Galaxy Buds 3 Pro | Samsung 官方产品能力 |
| src_galaxybuds_002 | review | Galaxy Buds 3 Pro | 第三方深度评测 |
| src_market_001 | survey | market | 2025 AI 耳机市场报告 |

## Broken Case

`broken/missing_pricing_source.json` 刻意移除 `src_galaxybuds_002`，用于首轮触发 Reviewer 的来源覆盖/定价覆盖问题。LangGraph 重试 Researcher 后应切回 `sources.json`，让 Reviewer 能观察到修复链路。

## Agent Contract

- Mock data 不允许绕过 LLM：它只是“爬虫/网页采集”的本地替身。
- Agent 不应直接读取本说明文档做分析；机器输入仍以 JSON 数据包为准。
- 中间产物必须同时保存 JSON 与 Markdown：JSON 给 API/前端，Markdown 给人工 review 和开发 agent 排查。
