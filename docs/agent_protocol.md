# Scout Agent 协议

## 1. Agent 职责

### 1.1 Researcher Agent

- **节点名**: `researcher`
- **输入**: `task_id`, `run_id`, `schema_pack`, `retry_count`
- **输出**: `SourceRecord[]`, `EvidenceCard[]`
- **职责**:
  - 读取 Mock 数据包或 Web 来源
  - 为每个产品生成至少 2 条 EvidenceCard
  - 标记来源类型（official / review / news / survey）
  - 识别定价维度（pricing keywords: `$`, `定价`, `价格`, `元`, `免费`, `付费`, `订阅`, `月费`, `年费`）
- **Broken Case 行为**:
  - `retry_count == 0` 时读取 `broken/missing_pricing_source.json`（更少来源）
  - `retry_count > 0` 时读取完整 `sources.json`
  - 使 Reviewer 能在首次运行时检测到 MISSING_SOURCE

### 1.2 Analyst Agent

- **节点名**: `analyst`
- **输入**: `EvidenceCard[]`
- **输出**: `ProductProfile[]`, `Claim[]`
- **职责**:
  - 从 Evidence 构建产品结构化画像（定位、功能树、定价、用户画像、优劣势）
  - 生成竞品对比矩阵（功能、定价、目标用户、优势、短板）
  - 创建可溯源 Claim，绑定 `evidence_ids`
  - 关键 Claim 类型：fact / comparison / insight / recommendation

### 1.3 Writer Agent

- **节点名**: `writer`
- **输入**: `ProductProfile[]`, `Claim[]`
- **输出**: `Report`
- **职责**:
  - 生成结构化报告：执行摘要、分析范围、竞品矩阵、SWOT、机会建议、关键 Claim
  - **关键规则**: insight/recommendation 类型 Claim 无 evidence 时不进入关键建议
  - 计算 evidence_coverage（有 evidence 的 Claim 比例）

### 1.4 Reviewer Agent

- **节点名**: `reviewer`
- **输入**: `EvidenceCard[]`, `Claim[]`, `Report`
- **输出**: `ReviewIssue[]`, `review_passed`, `retry_target`
- **职责**:
  - Schema 完整性检查
  - 引用覆盖率检查（insight/recommendation 必须有 evidence）
  - 来源覆盖度检查（每产品 >= 2 条 evidence）
  - 定价信息检查（每产品 pricing 维度 evidence）
  - 置信度检查（Claim confidence < 0.6 报 major）
  - 报告完整性检查（executive_summary, comparison_matrix, swot, key_claims）
  - Issue 历史 preservation（旧 open issue 未复现则标记为 fixed）

---

## 2. 核心 Schema

### 2.1 SourceRecord

```python
class SourceRecord(BaseModel):
    source_id: str
    title: str
    source_type: Literal["official", "docs", "review", "news", "interview", "survey", "manual"]
    url: str | None
    product: str | None
    raw_excerpt: str
    public_or_authorized: bool
```

### 2.2 EvidenceCard

```python
class EvidenceCard(BaseModel):
    evidence_id: str
    source_id: str
    product: str
    dimension: Literal["feature", "pricing", "persona", "review", "market", "risk"]
    fact: str
    normalized_value: dict[str, Any]
    confidence: float
```

### 2.3 Claim

```python
class Claim(BaseModel):
    claim_id: str
    text: str
    claim_type: Literal["fact", "comparison", "insight", "recommendation"]
    product_refs: list[str]
    evidence_ids: list[str]
    confidence: float
    reviewer_status: Literal["pending", "failed", "approved"]
```

### 2.4 ReviewIssue

```python
class ReviewIssue(BaseModel):
    issue_id: str
    severity: Literal["blocker", "major", "minor"]
    issue_type: Literal["MISSING_SOURCE", "SCHEMA_INVALID", "LOW_CONFIDENCE", "CONTRADICTION", "PII_RISK", "REPORT_GAP"]
    target_agent: Literal["researcher", "analyst", "writer"]
    target_object_id: str
    message: str
    required_fix: str
    status: Literal["open", "fixed", "accepted_risk"]
```

---

## 3. 打回协议

### 3.1 Issue 类型与路由

| Issue 类型 | 打回节点 | 修复动作 | 严重级别 |
|---|---|---|---|
| `MISSING_SOURCE` | researcher | 补充来源或移除无证据 Claim | blocker / major |
| `SCHEMA_INVALID` | analyst | 重新结构化输出 | blocker |
| `LOW_CONFIDENCE` | researcher | 补充更多 Evidence 或降低结论强度 | major |
| `CONTRADICTION` | analyst | 输出冲突解释和最终采用依据 | major |
| `PII_RISK` | researcher | 脱敏后重写 Evidence | blocker |
| `REPORT_GAP` | writer | 补齐报告章节 | major |

### 3.2 打回流程

```
1. Reviewer 检测问题 -> 生成 ReviewIssue
2. Reviewer 根据最高 severity issue 确定 retry_target
3. 条件边将流程路由到 retry_target 节点
4. LangGraph 从 checkpoint 恢复该节点状态
5. 目标节点重新执行，保留上游节点结果
6. Reviewer 再次检查
7. 旧 open issue 未复现 -> 标记为 fixed
8. 新 issue 可能产生（若修复不彻底）
9. 无 open issue -> review_passed = True -> END
```

### 3.3 Issue 状态流转

```
open (首次发现)
  │
  ├──▶ fixed (重跑后未复现)
  │
  └──▶ accepted_risk (人工确认接受，P1)
```

---

## 4. 状态传递契约

Agent 间通过 `ScoutState` 传递结构化数据，约束：

1. 每个节点只读取自己需要的字段，不依赖其他节点的内部实现
2. 所有输出经过 Pydantic 校验
3. 节点失败时抛出异常，由 LangGraph 捕获并记录 `NODE_FAILED`
4. Artifact 文件保存与 State 返回同步
5. Run Event 写入失败不阻塞主流程（降级到控制台警告）
