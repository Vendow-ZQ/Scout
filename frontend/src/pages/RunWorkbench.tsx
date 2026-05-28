import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getTask, getEvents, getReport, getReview, getEvidence } from '../api/client'

interface LogEvent {
  event_id: string
  event_type: string
  node_name?: string
  agent_name?: string
  message: string
  created_at: string
  payload?: Record<string, unknown>
}

interface ReviewIssue {
  issue_id: string
  severity: string
  issue_type: string
  target_agent: string
  message: string
  required_fix: string
  status: string
}

interface EvidenceItem {
  evidence_id: string
  source_id: string
  product: string
  dimension: string
  fact: string
  confidence: number
}

interface Claim {
  claim_id: string
  text: string
  claim_type: string
  confidence: number
  evidence_ids?: string[]
}

interface MatrixProduct {
  name: string
  [key: string]: string
}

interface ComparisonMatrix {
  dimensions: string[]
  products: MatrixProduct[]
}

interface ReportData {
  executive_summary?: string
  scope?: string
  comparison_matrix?: ComparisonMatrix
  swot?: Record<string, string[]>
  claim_count?: number
  evidence_coverage?: number
  key_claims?: Claim[]
}

export default function RunWorkbench() {
  const { taskId } = useParams<{ taskId: string }>()
  const [task, setTask] = useState<Record<string, unknown> | null>(null)
  const [events, setEvents] = useState<LogEvent[]>([])
  const [report, setReport] = useState<ReportData | null>(null)
  const [review, setReview] = useState<Record<string, unknown> | null>(null)
  const [evidence, setEvidence] = useState<EvidenceItem[]>([])
  const [activeTab, setActiveTab] = useState<'dag' | 'trace' | 'report' | 'review'>('dag')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!taskId) return
    let cancelled = false

    async function load() {
      try {
        const [t, ev, r, rv, evd] = await Promise.all([
          getTask(taskId!),
          getEvents(taskId!),
          getReport(taskId!).catch(() => null),
          getReview(taskId!).catch(() => null),
          getEvidence(taskId!).catch(() => []),
        ])
        if (cancelled) return
        setTask(t as Record<string, unknown>)
        setEvents(ev as LogEvent[])
        setReport(r as ReportData | null)
        setReview(rv as Record<string, unknown> | null)
        setEvidence((evd as EvidenceItem[]) || [])
      } catch (e) {
        console.error(e)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [taskId])

  if (loading) return <div>加载中...</div>
  if (!task) return <div>任务不存在</div>

  const nodeEvents = events.filter(e =>
    ['NODE_STARTED', 'NODE_SUCCEEDED', 'NODE_FAILED'].includes(e.event_type)
  )

  const dagNodes = ['researcher', 'analyst', 'writer', 'reviewer']
  const nodeStatus: Record<string, string> = {}
  nodeEvents.forEach(e => {
    if (e.event_type === 'NODE_STARTED') nodeStatus[e.node_name || ''] = 'running'
    if (e.event_type === 'NODE_SUCCEEDED') nodeStatus[e.node_name || ''] = 'success'
    if (e.event_type === 'NODE_FAILED') nodeStatus[e.node_name || ''] = 'failed'
  })

  const reviewIssues = ((review?.issues as unknown[]) || []) as ReviewIssue[]
  const reviewPassed = review?.review_passed as boolean | undefined

  return (
    <div>
      <h2>运行工作台: {taskId}</h2>
      <div style={{ marginBottom: 16, color: '#666' }}>
        状态: <strong>{task.status as string}</strong>
        {!!task.current_node && <span> | 当前节点: {task.current_node as string}</span>}
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16, borderBottom: '1px solid #e0e0e0' }}>
        {(['dag', 'trace', 'report', 'review'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #2563eb' : '2px solid transparent',
              background: 'transparent',
              cursor: 'pointer',
              fontWeight: activeTab === tab ? 600 : 400,
            }}
          >
            {tab === 'dag' && 'DAG 流程'}
            {tab === 'trace' && '运行日志'}
            {tab === 'report' && '分析报告'}
            {tab === 'review' && '质检结果'}
          </button>
        ))}
      </div>

      {activeTab === 'dag' && (
        <div>
          <h3>Agent 执行流程</h3>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginTop: 16 }}>
            {dagNodes.map((node, i) => {
              const status = nodeStatus[node]
              const colors: Record<string, string> = {
                running: '#f59e0b',
                success: '#22c55e',
                failed: '#ef4444',
                pending: '#e5e7eb',
              }
              const bg = colors[status || 'pending']
              const textColor = status ? '#fff' : '#374151'
              return (
                <div key={node} style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div
                    style={{
                      padding: '16px 24px',
                      background: bg,
                      color: textColor,
                      borderRadius: 8,
                      fontWeight: 600,
                      minWidth: 100,
                      textAlign: 'center',
                    }}
                  >
                    {node}
                  </div>
                  {i < dagNodes.length - 1 && (
                    <span style={{ fontSize: 20, color: '#9ca3af' }}>→</span>
                  )}
                </div>
              )
            })}
          </div>
          {!reviewPassed && reviewIssues.length > 0 && (
            <div style={{ marginTop: 24, padding: 16, background: '#fef3c7', borderRadius: 8 }}>
              <strong>Reviewer 打回路径</strong>
              <div style={{ marginTop: 8 }}>
                {reviewIssues.filter(i => i.status === 'open').map((issue, idx) => (
                  <div key={idx} style={{ marginTop: 8 }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '2px 8px',
                      background: issue.severity === 'blocker' ? '#ef4444' : '#f59e0b',
                      color: '#fff',
                      borderRadius: 4,
                      fontSize: 12,
                    }}>
                      {issue.severity}
                    </span>
                    {' '}
                    {issue.issue_type} → 打回 {issue.target_agent}
                    <div style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
                      {issue.message}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {reviewPassed && (
            <div style={{ marginTop: 24, padding: 16, background: '#dcfce7', borderRadius: 8, color: '#166534' }}>
              Reviewer 已通过，报告已生成
            </div>
          )}
        </div>
      )}

      {activeTab === 'trace' && (
        <div>
          <h3>运行日志</h3>
          <div style={{ marginTop: 16 }}>
            {events.map(e => (
              <div
                key={e.event_id}
                style={{
                  padding: '8px 12px',
                  borderBottom: '1px solid #f0f0f0',
                  fontSize: 14,
                }}
              >
                <span style={{ color: '#9ca3af', fontSize: 12 }}>
                  [{e.created_at.slice(11, 19)}]
                </span>
                {' '}
                <span style={{
                  fontWeight: 600,
                  color: e.event_type.includes('FAILED') ? '#ef4444'
                    : e.event_type.includes('SUCCEEDED') ? '#22c55e'
                    : '#374151',
                }}>
                  {e.event_type}
                </span>
                {e.node_name && (
                  <span style={{ color: '#6b7280', marginLeft: 8 }}>
                    ({e.node_name})
                  </span>
                )}
                <div style={{ color: '#4b5563', marginTop: 2 }}>{e.message}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'report' && report && (
        <div>
          <h3>分析报告</h3>
          <div style={{ marginTop: 16 }}>
            <div style={{ background: '#f9fafb', padding: 16, borderRadius: 8, marginBottom: 16 }}>
              <h4 style={{ marginTop: 0 }}>执行摘要</h4>
              <p>{report.executive_summary || ''}</p>
            </div>

            <div style={{ background: '#f9fafb', padding: 16, borderRadius: 8, marginBottom: 16 }}>
              <h4 style={{ marginTop: 0 }}>分析范围</h4>
              <p>{report.scope || ''}</p>
            </div>

            {report.comparison_matrix && (
              <div style={{ background: '#f9fafb', padding: 16, borderRadius: 8, marginBottom: 16 }}>
                <h4 style={{ marginTop: 0 }}>竞品对比矩阵</h4>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                      <th style={{ textAlign: 'left', padding: 8 }}>产品</th>
                      {report.comparison_matrix.dimensions.map(d => (
                        <th key={d} style={{ textAlign: 'left', padding: 8 }}>{d}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {report.comparison_matrix.products.map((p, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
                        <td style={{ padding: 8, fontWeight: 600 }}>{p.name}</td>
                        {report.comparison_matrix!.dimensions.map(d => (
                          <td key={d} style={{ padding: 8 }}>{p[d] || '-'}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {report.swot && (
              <div style={{ background: '#f9fafb', padding: 16, borderRadius: 8, marginBottom: 16 }}>
                <h4 style={{ marginTop: 0 }}>SWOT 分析</h4>
                {Object.entries(report.swot).map(([key, items]) => (
                  <div key={key} style={{ marginTop: 8 }}>
                    <strong>{key === 'S' ? '优势' : key === 'W' ? '劣势' : key === 'O' ? '机会' : '威胁'}:</strong>
                    <ul style={{ margin: '4px 0', paddingLeft: 20 }}>
                      {items.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}

            <div style={{ background: '#f9fafb', padding: 16, borderRadius: 8 }}>
              <h4 style={{ marginTop: 0 }}>关键 Claim ({report.claim_count || 0} 条)</h4>
              <p>证据覆盖率: {(report.evidence_coverage || 0) * 100}%</p>
              <div style={{ marginTop: 8 }}>
                {(report.key_claims || []).map((c, i) => (
                  <div key={i} style={{
                    padding: 12,
                    marginTop: 8,
                    background: '#fff',
                    borderRadius: 4,
                    border: '1px solid #e5e7eb',
                  }}>
                    <div style={{ fontWeight: 500 }}>{c.text}</div>
                    <div style={{ fontSize: 12, color: '#6b7280', marginTop: 4 }}>
                      类型: {c.claim_type} | 置信度: {c.confidence * 100}%
                      {(c.evidence_ids || []).length > 0 && (
                        <span> | 证据: {c.evidence_ids!.join(', ')}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'review' && (
        <div>
          <h3>质检结果</h3>
          {reviewPassed !== undefined && (
            <div style={{
              padding: 16,
              background: reviewPassed ? '#dcfce7' : '#fef3c7',
              borderRadius: 8,
              marginBottom: 16,
              color: reviewPassed ? '#166534' : '#92400e',
            }}>
              {reviewPassed ? 'Reviewer 已通过' : 'Reviewer 发现以下问题'}
            </div>
          )}
          <div style={{ marginTop: 16 }}>
            {reviewIssues.map((issue, i) => (
              <div key={i} style={{
                padding: 16,
                marginTop: 12,
                background: issue.status === 'open' ? '#fef2f2' : '#f0fdf4',
                borderRadius: 8,
                borderLeft: `4px solid ${issue.status === 'open' ? '#ef4444' : '#22c55e'}`,
              }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span style={{
                    padding: '2px 8px',
                    background: issue.severity === 'blocker' ? '#ef4444' : '#f59e0b',
                    color: '#fff',
                    borderRadius: 4,
                    fontSize: 12,
                  }}>
                    {issue.severity}
                  </span>
                  <span style={{ fontWeight: 600 }}>{issue.issue_type}</span>
                  <span style={{ color: '#6b7280', fontSize: 14 }}>→ {issue.target_agent}</span>
                </div>
                <div style={{ marginTop: 8 }}>{issue.message}</div>
                <div style={{ marginTop: 4, fontSize: 14, color: '#6b7280' }}>
                  修复要求: {issue.required_fix}
                </div>
                <div style={{ marginTop: 4, fontSize: 12, color: '#9ca3af' }}>
                  状态: {issue.status}
                </div>
              </div>
            ))}
          </div>
          {evidence.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <h4>证据卡 ({evidence.length} 条)</h4>
              {evidence.map((e, i) => (
                <div key={i} style={{
                  padding: 12,
                  marginTop: 8,
                  background: '#f9fafb',
                  borderRadius: 4,
                  fontSize: 14,
                }}>
                  <strong>{e.product}</strong> [{e.dimension}]
                  <div style={{ marginTop: 4 }}>{e.fact}</div>
                  <div style={{ color: '#6b7280', fontSize: 12, marginTop: 4 }}>
                    置信度: {e.confidence * 100}% | 来源: {e.source_id}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
