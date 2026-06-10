# AI Coding Agent Mock Crawl Plan

**Pack**: `ai_coding_agent`  
**Main product**: Trae  
**Captured at**: 2026-05-28  
**Purpose**: Provide high-quality pre-crawled public material for Scout's Researcher node. This data pack replaces live crawling only; downstream evidence extraction, analysis, report editing and review should still use the configured LLM.

---

## 1. Research Intent

Demo query:

> Trae 是字节旗下 AI IDE。请分析 Trae 在 AI coding agent 赛道中的竞品格局、用户需求、能力差异、商业化机会和风险。

Researcher should not search one keyword only. It should first map the problem space:

- IDE-native AI coding tools: Trae, Cursor, Windsurf.
- Workflow-native coding agents: GitHub Copilot cloud agent.
- CLI / desktop / web coding agents: Claude Code, OpenAI Codex.
- Autonomous delegated software engineer: Devin.
- Market/user/risk context: developer AI adoption, trust gap, PR-level agent adoption, code churn, industrial benchmark gap.

---

## 2. Track Design

| Track | Goal | Included source types |
|---|---|---|
| market | Determine whether AI coding agents are a real and growing category | Stack Overflow survey, arXiv adoption studies, benchmark/news sources |
| user | Understand developer needs and trust barriers | Stack Overflow trust gap, product docs around review/rollback/test loops |
| competitor | Build player map and product taxonomy | Official pages and docs for Trae, Cursor, Windsurf, GitHub Copilot, Claude Code, Codex, Devin |
| product | Compare interaction model and feature surface | Builder/SOLO, Background Agents, Cascade, Copilot cloud agent, Claude Code, Codex app, Devin workspace |
| tech | Compare agent architecture and execution surface | tool calling, terminal/browser/editor, worktrees, Devbox, MCP, sandboxing, checkpoints |
| business | Compare pricing and cost control | Trae token tiers, Cursor API-cost usage, GitHub usage billing, Codex token-rate card, Devin self-serve plans |
| risk | Surface privacy/security/quality concerns | Trae telemetry reporting, Cursor remote-agent risk, Stack Overflow trust gap, arXiv churn studies |

---

## 3. Search Playbook

### 3.1 Trae

Search queries:

- `Trae AI IDE official Builder docs`
- `Trae SOLO responsive coding agent official`
- `Trae membership token based pricing 2026`
- `Trae IDE telemetry privacy risk report`

Priority domains:

- `trae.ai`
- `traeide.com`
- `theregister.com`
- selected third-party reviews only as sentiment/risk support

### 3.2 Cursor

Search queries:

- `Cursor official coding agent product page`
- `Cursor background agents docs`
- `Cursor pricing agent usage API cost privacy mode`
- `Cursor 2026 multi agent review`

Priority domains:

- `cursor.com`
- `docs.cursor.com`
- reputable review/news pages for market sentiment

### 3.3 Windsurf

Search queries:

- `Windsurf Cascade docs tool calling checkpoints MCP`
- `Windsurf models docs SWE pricing availability`
- `Windsurf usage plans quota credits`
- `Windsurf pricing official plans Pro Teams Enterprise`
- `Cognition acquires Windsurf`

Priority domains:

- `docs.windsurf.com`
- `windsurf.com`
- `techcrunch.com`
- `cnbc.com`

### 3.4 GitHub Copilot

Search queries:

- `GitHub Copilot cloud agent docs`
- `GitHub Copilot agents GitHub Issues Jira Slack Teams`
- `GitHub Copilot plans premium requests usage based billing 2026`
- `GitHub Copilot cloud agent risks prompt injection mitigation`
- `GitHub Copilot pull request user backlash product tips`
- `GitHub Copilot security concerns online discussions`

Priority domains:

- `docs.github.com`
- `github.com/features/copilot`
- `github.blog`

### 3.5 Claude Code

Search queries:

- `Claude Code overview docs agentic coding tool`
- `Claude Code models usage limits Sonnet Opus Haiku`
- `Claude Code data usage commercial terms`
- `Claude Code agents MCP CLAUDE.md hooks skills`
- `Claude Code user feedback rate limit drain`
- `Claude Code power user complaints quality regression`
- `Claude Code review AI coding agent 2026`

Priority domains:

- `code.claude.com`
- `docs.anthropic.com`
- `support.claude.com`

### 3.6 OpenAI Codex

Search queries:

- `OpenAI Codex app command center agents`
- `OpenAI Codex rate card token based pricing 2026`
- `OpenAI Codex system card coding agent`
- `Codex app worktrees sandboxing skills automations`
- `OpenAI Codex app review developer feedback`
- `OpenAI Codex PR acceptance rate coding agents`
- `OpenAI Codex user feedback reliability agent workflows`

Priority domains:

- `openai.com`
- `help.openai.com`
- `cdn.openai.com`
- `developers.openai.com`
- reputable tech media and review pages for product-direction / hands-on evaluation
- community discussions only as low-confidence user sentiment

### 3.7 Devin

Search queries:

- `Devin enterprise deployment docs Brain Devbox`
- `Cognition new self serve plans Devin 2026`
- `Devin release notes 2026 governance ACU session caps`
- `Devin 2.0 price drop cloud IDE parallel sessions`

Priority domains:

- `docs.devin.ai`
- `cognition.ai`
- reputable tech/business news for market narrative

---

## 4. Coverage Rules

Researcher should produce at least:

- 2+ product/feature evidence cards for Trae.
- 1+ pricing/business evidence card for each major competitor where available.
- 1+ risk/security evidence card for Trae and remote/cloud-agent category.
- 1+ non-official review/news/user-feedback evidence card for each major competitor where available; if missing, mark the gap.
- 3+ market/user evidence cards.
- A competitor taxonomy separating IDE-native, workflow-native, CLI/app-native, and delegated autonomous software engineer tools.

---

## 5. Broken Case

`broken/missing_pricing_source.json` intentionally removes:

- Trae pricing source.
- several long-tail market and review sources.

Expected reviewer behavior:

- It may flag Trae pricing/business model coverage as incomplete.
- It may ask Researcher to add pricing/business evidence.
- On the next run, normal `sources.json` restores the missing source.

This broken file exists only because the current runtime expects a `broken/missing_pricing_source.json` file on first pass.
