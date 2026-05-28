# Scout Agent 协议

## Agent 职责

### Researcher
- 输入：task_id, schema_pack, retry_count
- 输出：SourceRecord[], EvidenceCard[]
- 职责：读取数据包，提取证据卡，标记来源类型和可信度

### Analyst
- 输入：EvidenceCard[]
- 输出：ProductProfile[], Claim[]
- 职责：构建产品画像，生成对比矩阵，创建可溯源 Claim

### Writer
- 输入：ProductProfile[], Claim[]
- 输出：Report（摘要/矩阵/SWOT/建议/附录）
- 职责：生成结构化报告，无来源 Claim 不进关键建议

### Reviewer
- 输入：EvidenceCard[], Claim[], Report
- 输出：ReviewIssue[], review_passed
- 职责：Schema 校验、引用覆盖、置信度、报告完整性检查

## 打回协议

| Issue 类型 | 打回节点 | 修复动作 |
|---|---|---|
| MISSING_SOURCE | Researcher | 补充来源或移除无证据 Claim |
| SCHEMA_INVALID | Analyst | 重新结构化输出 |
| LOW_CONFIDENCE | Researcher | 补充 Evidence |
| REPORT_GAP | Writer | 补齐报告章节 |

## 状态传递

Agent 间通过 `ScoutState` 传递结构化数据，所有输出经过 Pydantic 校验。
