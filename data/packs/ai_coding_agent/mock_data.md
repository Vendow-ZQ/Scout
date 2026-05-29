# Mock Data Pack: ai_coding_agent

This pack contains pre-crawled public data for an AI coding agent competitive analysis demo.

It is designed for the following live demo:

> User enters: `Trae`  
> System interprets: Trae is ByteDance's AI IDE / AI coding agent.  
> Researcher reads this pack instead of doing live web crawling.  
> Researcher, Analyst, Editor and Reviewer still use the real configured LLM.

---

## 1. Scope

| Field | Value |
|---|---|
| pack_id | `ai_coding_agent` |
| main_product | Trae |
| category | AI Coding Agent |
| region | Global + China |
| products | Trae, Cursor, Windsurf, GitHub Copilot, Claude Code, OpenAI Codex, Devin |
| normal source file | `sources.json` |
| broken demo source file | `broken/missing_pricing_source.json` |
| crawler plan | `crawler_plan.md` |

---

## 2. Product Taxonomy

| Segment | Products | Why it matters |
|---|---|---|
| IDE-native agent | Trae, Cursor, Windsurf | Best for daily coding inside an editor; strong context and low switching cost. |
| Workflow-native agent | GitHub Copilot | Best for teams already living in GitHub Issues, PRs, Actions and enterprise policy. |
| CLI/app-native agent | Claude Code, OpenAI Codex | Best for agentic work across terminal, desktop, web, IDE, and automation surfaces. |
| Delegated autonomous engineer | Devin | Best for assigning a larger task to a cloud workspace with shell/browser/editor and enterprise controls. |

---

## 3. Research Track Coverage

### Market

Included sources:

- `src_market_stackoverflow_001`
- `src_market_trust_gap_002`
- `src_market_agent_adoption_003`
- `src_market_agent_prs_004`
- `src_market_mobile_benchmark_005`
- `src_market_swe_bench_006`

Core material:

- AI coding tool adoption is high, but trust is declining.
- Coding agents are now visible in GitHub traces and PR workflows.
- Benchmarks are improving quickly, but industrial mobile tasks and long-term maintainability remain hard.

### User

Included sources:

- `src_market_stackoverflow_001`
- `src_market_trust_gap_002`
- product docs showing rollback, review, testing, PR and governance workflows

Core material:

- Developers want speed, but they need reviewability and production safety.
- Enterprise buyers care about data handling, policy control, cost predictability and auditability.
- The winning product is not only the one with the strongest model; it is the one that can fit into a team workflow without creating hidden risk.

### Competitor

Included product groups:

- Trae: `src_trae_*`
- Cursor: `src_cursor_*`
- Windsurf: `src_windsurf_*`
- GitHub Copilot: `src_github_*`
- Claude Code: `src_claude_*`
- OpenAI Codex: `src_codex_*`
- Devin: `src_devin_*`

Core material:

- Trae competes directly with Cursor and Windsurf in AI IDE experience.
- Trae also competes indirectly with Claude Code and Codex for agentic coding workflows.
- GitHub Copilot and Devin define enterprise workflow and delegated-agent reference points.

### Product / Feature

Important feature dimensions:

- Planning before execution.
- Multi-file editing.
- Terminal/command execution.
- Browser/app preview.
- Rollback/checkpoint/revert.
- Parallel agents.
- Context management.
- PR/code review workflow.
- MCP/tool integrations.

### Technology

Important technology dimensions:

- Local IDE agent vs remote/cloud agent.
- Tool calling and command execution.
- Worktree or branch isolation.
- Devbox/cloud workspace.
- MCP and external tool connectors.
- Sandbox and permission model.
- Context window and codebase indexing.

### Business

Important business dimensions:

- Free/low-cost acquisition.
- Token/usage-based pricing.
- Team/enterprise admin controls.
- Additional credits/usage purchase.
- Compute-heavy workflows such as autonomous agents, review and automations.

### Risk

Important risk dimensions:

- Data privacy and telemetry.
- Prompt injection / data exfiltration for remote agents.
- Code churn and maintainability.
- Over-trust in generated code.
- Cost unpredictability under agentic loops.
- Enterprise compliance and audit needs.

---

## 4. Source Quality Notes

Priority order:

1. Official product pages and docs.
2. Official pricing/help-center pages.
3. Technical papers / survey sources.
4. Reputable tech/business/security media.
5. Third-party reviews only for sentiment and framing, never as sole source for hard facts.

The `raw_excerpt` fields are concise human-readable source notes, not full copied articles.

---

## 5. Expected Researcher Behavior

Researcher should:

- Generate a `research_plan.md` with the taxonomy above.
- Treat Trae as the main product.
- Use the product taxonomy to define direct, adjacent and indirect competitors.
- Extract evidence cards from every major track.
- Mark privacy/telemetry items as allegations or third-party reports, not official admissions.
- Mark pricing as time-sensitive because pricing changed across products in 2026.
- Keep source gaps explicit.

Researcher should not:

- Conclude Trae is best merely because it is the main product.
- Treat all products as the same type of tool.
- Ignore that Cursor/Windsurf are IDE-native, Copilot is GitHub-workflow-native, Claude/Codex are multi-surface agent tools, and Devin is a delegated autonomous engineer.
- Use market benchmarks as direct proof of any specific product's product-market fit.

---

## 6. Broken Case

The broken file intentionally removes Trae pricing coverage. This should create a visible gap:

> Trae's product capability is covered, but its current pricing/business model is under-supported.

On a second pass, normal `sources.json` restores:

- `src_trae_pricing_004`
- broader market and review sources

The broken case is for demo robustness only. It should not be used as the default source of truth.
