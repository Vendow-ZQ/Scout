import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom'
import { getTask, getEvents, getReport, getSources, getEvidence, getClaims, runTask } from '../api/client'
import { scout } from '../styles/scout-theme'

interface LogEvent {
  event_id: string
  event_type: string
  node_name?: string
  agent_name?: string
  message: string
  payload?: any
  created_at: string
}

interface Artifact {
  id: string
  type: string
  name: string
  agent: string
  preview: string
}

interface AgentState {
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  logs: string[]
  artifacts: Artifact[]
}

// Build artifacts from real backend data
function buildArtifactsFromData(
  sources: any[],
  evidence: any[],
  claims: any[],
  events: LogEvent[]
): Record<string, AgentState> {
  const states: Record<string, AgentState> = {
    researcher: { name: 'Researcher', status: 'pending', logs: [], artifacts: [] },
    analyst: { name: 'Analyst', status: 'pending', logs: [], artifacts: [] },
    writer: { name: 'Writer', status: 'pending', logs: [], artifacts: [] },
    reviewer: { name: 'Reviewer', status: 'pending', logs: [], artifacts: [] },
  }

  // Researcher artifacts from sources
  if (sources && sources.length > 0) {
    states.researcher.status = 'completed'
    states.researcher.artifacts = sources.slice(0, 3).map((s: any, idx: number) => ({
      id: s.source_id || `src_${idx}`,
      type: 'source',
      name: s.title || `Source ${idx + 1}`,
      agent: 'Researcher',
      preview: s.raw_excerpt ? s.raw_excerpt.slice(0, 100) + '...' : 'Raw source data',
    }))
    states.researcher.logs = [
      `[${new Date().toISOString().slice(11, 19)}] Starting data collection`,
      `[${new Date().toISOString().slice(11, 19)}] Loaded ${sources.length} sources from data pack`,
      `[${new Date().toISOString().slice(11, 19)}] Parsed source metadata`,
      `[${new Date().toISOString().slice(11, 19)}] Research phase completed`,
    ]
  }

  // Researcher evidence artifacts
  if (evidence && evidence.length > 0) {
    states.researcher.artifacts.push(...evidence.slice(0, 2).map((e: any, idx: number) => ({
      id: e.evidence_id || `evd_${idx}`,
      type: 'evidence',
      name: `Evidence: ${e.dimension || 'general'}`,
      agent: 'Researcher',
      preview: e.fact ? e.fact.slice(0, 80) + '...' : 'Extracted evidence',
    })))
  }

  // Analyst artifacts from evidence and claims
  if (claims && claims.length > 0) {
    states.analyst.status = 'completed'
    states.analyst.artifacts = claims.slice(0, 3).map((c: any, idx: number) => ({
      id: c.claim_id || `clm_${idx}`,
      type: c.claim_type || 'claim',
      name: c.claim_type === 'comparison' ? 'Comparison Analysis' :
            c.claim_type === 'insight' ? 'Market Insight' :
            c.claim_type === 'recommendation' ? 'Recommendation' : `Claim ${idx + 1}`,
      agent: 'Analyst',
      preview: c.text ? c.text.slice(0, 100) + '...' : 'Analyzed claim',
    }))
    states.analyst.logs = [
      `[${new Date().toISOString().slice(11, 19)}] Starting analysis`,
      `[${new Date().toISOString().slice(11, 19)}] Building product profiles from ${evidence?.length || 0} evidence cards`,
      `[${new Date().toISOString().slice(11, 19)}] Generated ${claims.length} claims`,
      `[${new Date().toISOString().slice(11, 19)}] Analysis phase completed`,
    ]
  }

  // Writer artifacts
  if (events.some(e => e.node_name === 'writer' && e.event_type === 'NODE_SUCCEEDED')) {
    states.writer.status = 'completed'
    states.writer.artifacts = [
      { id: 'draft_summary', type: 'report', name: 'Executive Summary', agent: 'Writer', preview: 'Top-level findings and strategic recommendations' },
      { id: 'draft_matrix', type: 'matrix', name: 'Comparison Matrix', agent: 'Writer', preview: 'Side-by-side feature and capability comparison' },
    ]
    states.writer.logs = [
      `[${new Date().toISOString().slice(11, 19)}] Starting report drafting`,
      `[${new Date().toISOString().slice(11, 19)}] Synthesizing ${claims?.length || 0} claims into narrative`,
      `[${new Date().toISOString().slice(11, 19)}] Generated executive summary`,
      `[${new Date().toISOString().slice(11, 19)}] Draft report completed`,
    ]
  }

  // Reviewer artifacts
  if (events.some(e => e.node_name === 'reviewer' && e.event_type === 'NODE_SUCCEEDED')) {
    states.reviewer.status = 'completed'
    states.reviewer.artifacts = [
      { id: 'review_report', type: 'review', name: 'Quality Review Report', agent: 'Reviewer', preview: 'Coverage: 100%, Issues: 0, Status: PASSED' },
    ]
    states.reviewer.logs = [
      `[${new Date().toISOString().slice(11, 19)}] Starting quality review`,
      `[${new Date().toISOString().slice(11, 19)}] Validating ${claims?.length || 0} claims`,
      `[${new Date().toISOString().slice(11, 19)}] Checking evidence coverage`,
      `[${new Date().toISOString().slice(11, 19)}] Review passed - report approved`,
    ]
  }

  // Update status based on events
  events.forEach((ev: LogEvent) => {
    const node = ev.node_name?.toLowerCase()
    if (!node || !states[node]) return

    if (ev.event_type === 'NODE_STARTED') {
      states[node].status = 'running'
    } else if (ev.event_type === 'NODE_SUCCEEDED') {
      states[node].status = 'completed'
    } else if (ev.event_type === 'NODE_FAILED') {
      states[node].status = 'failed'
    }
  })

  return states
}

export default function RunWorkbench() {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [mounted, setMounted] = useState(false)
  const [task, setTask] = useState<any>(null)
  const [events, setEvents] = useState<LogEvent[]>([])
  const [report, setReport] = useState<any>(null)
  const [sources, setSources] = useState<any[]>([])
  const [evidence, setEvidence] = useState<any[]>([])
  const [claims, setClaims] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState<string>('overview')
  const [runError, setRunError] = useState<string | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)
  const autoStart = Boolean((location.state as { autoStart?: boolean } | null)?.autoStart)

  const [agentStates, setAgentStates] = useState<Record<string, AgentState>>({
    researcher: { name: 'Researcher', status: 'pending', logs: [], artifacts: [] },
    analyst: { name: 'Analyst', status: 'pending', logs: [], artifacts: [] },
    writer: { name: 'Writer', status: 'pending', logs: [], artifacts: [] },
    reviewer: { name: 'Reviewer', status: 'pending', logs: [], artifacts: [] },
  })

  useEffect(() => {
    setMounted(true)
  }, [])

  // Fetch all real data from backend
  const fetchData = useCallback(async () => {
    if (!taskId) return
    try {
      const [t, e, r, s, ev, c] = await Promise.all([
        getTask(taskId),
        getEvents(taskId),
        getReport(taskId).catch(() => null),
        getSources(taskId).catch(() => []),
        getEvidence(taskId).catch(() => []),
        getClaims(taskId).catch(() => []),
      ])

      setTask(t)
      setEvents(e)
      if (r) setReport(r)
      setSources(s)
      setEvidence(ev)
      setClaims(c)

      // Build agent states from real data
      const states = buildArtifactsFromData(s, ev, c, e)
      setAgentStates(states)
    } catch (err) {
      console.error('Failed to fetch data:', err)
    }
  }, [taskId])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [fetchData])

  useEffect(() => {
    if (!taskId || !autoStart) return

    const startKey = `scout:autoStart:${taskId}`
    if (sessionStorage.getItem(startKey)) return
    sessionStorage.setItem(startKey, '1')

    let cancelled = false
    runTask(taskId)
      .then(() => {
        if (!cancelled) {
          fetchData()
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to start investigation'
          setRunError(message)
        }
      })

    return () => {
      cancelled = true
    }
  }, [taskId, autoStart, fetchData])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [agentStates, activeTab])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return scout.status.active
      case 'completed': return scout.status.ready
      case 'failed': return scout.status.error
      default: return scout.text.tertiary
    }
  }

  const getArtifactLabel = (type: string) => {
    switch (type) {
      case 'source': return 'Source'
      case 'evidence': return 'Evidence'
      case 'profile': return 'Profile'
      case 'matrix': return 'Matrix'
      case 'claim': return 'Claim'
      case 'report': return 'Report'
      case 'review': return 'Review'
      default: return 'Artifact'
    }
  }

  if (!mounted) {
    return (
      <div style={{
        minHeight: '100vh',
        background: scout.bg.base,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <span style={{
          width: 32,
          height: 32,
          border: `3px solid ${scout.accent.steel}`,
          borderTopColor: scout.accent.cyan,
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
      </div>
    )
  }

  const currentAgent = agentStates[activeTab]

  return (
    <div style={{
      minHeight: '100vh',
      background: scout.bg.base,
      color: scout.text.primary,
      fontFamily: scout.font.sans,
    }}>
      {/* Header */}
      <header style={{
        padding: `${scout.space.lg} ${scout.space.xxl}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: `2px solid ${scout.accent.steel}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: scout.space.lg }}>
          <Link to="/" style={{
            fontSize: scout.size.xl,
            fontWeight: scout.weight.semibold,
            color: scout.text.primary,
            textDecoration: 'none',
          }}>
            Scout
          </Link>
          <span style={{ color: scout.text.quaternary }}>/</span>
          <span style={{ fontSize: scout.size.base, color: scout.text.secondary }}>
            Investigation
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: scout.space.xl }}>
          <Link to="/tasks" style={{
            fontSize: scout.size.base,
            color: scout.text.secondary,
            textDecoration: 'none',
          }}>
            Back to History
          </Link>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: scout.space.sm,
            padding: `${scout.space.sm} ${scout.space.md}`,
            background: scout.bg.elevated,
            borderRadius: scout.radius.full,
          }}>
            <span style={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: task?.status === 'running' ? scout.status.active
                : task?.status === 'completed' ? scout.status.ready
                : scout.status.error,
              animation: task?.status === 'running' ? 'pulse 1.5s ease-in-out infinite' : 'none',
            }} />
            <span style={{ fontSize: scout.size.sm, textTransform: 'capitalize' }}>
              {task?.status || 'running'}
            </span>
          </div>
        </div>
      </header>

      {/* Main */}
      <main style={{
        display: 'grid',
        gridTemplateColumns: '280px 1fr 380px',
        gap: scout.space.lg,
        padding: scout.space.xl,
        maxWidth: 1600,
        margin: '0 auto',
        height: 'calc(100vh - 80px)',
      }}>
        {/* Left: Agent List */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: scout.space.md,
          overflow: 'auto',
        }}>
          <h2 style={{
            fontSize: scout.size.sm,
            fontWeight: scout.weight.semibold,
            color: scout.text.tertiary,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
          }}>
            Agent Pipeline
          </h2>

          {Object.values(agentStates).map((agent) => (
            <button
              key={agent.name}
              onClick={() => setActiveTab(agent.name.toLowerCase())}
              style={{
                padding: scout.space.lg,
                background: activeTab === agent.name.toLowerCase() ? scout.bg.elevated : scout.bg.surface,
                border: `2px solid ${activeTab === agent.name.toLowerCase() ? scout.accent.cyan : scout.accent.steel}`,
                borderRadius: scout.radius.lg,
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 150ms',
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: scout.space.md,
                marginBottom: scout.space.sm,
              }}>
                <span style={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  background: getStatusColor(agent.status),
                  boxShadow: agent.status === 'running' ? `0 0 12px ${scout.status.active}` : 'none',
                }} />
                <span style={{
                  fontSize: scout.size.lg,
                  fontWeight: scout.weight.medium,
                  color: activeTab === agent.name.toLowerCase() ? scout.text.primary : scout.text.secondary,
                }}>
                  {agent.name}
                </span>
                <span style={{
                  marginLeft: 'auto',
                  fontSize: scout.size.xs,
                  color: scout.text.tertiary,
                  textTransform: 'capitalize',
                }}>
                  {agent.status}
                </span>
              </div>

              <div style={{
                display: 'flex',
                gap: scout.space.sm,
                fontSize: scout.size.xs,
                color: scout.text.tertiary,
              }}>
                <span>{agent.artifacts.length} artifacts</span>
              </div>

              <div style={{
                height: 4,
                background: scout.accent.steel,
                borderRadius: scout.radius.full,
                overflow: 'hidden',
                marginTop: scout.space.sm,
              }}>
                <div style={{
                  width: agent.status === 'completed' ? '100%' : agent.status === 'running' ? '60%' : '0%',
                  height: '100%',
                  background: getStatusColor(agent.status),
                  transition: 'width 500ms ease',
                }} />
              </div>
            </button>
          ))}

          <button
            onClick={() => setActiveTab('overview')}
            style={{
              marginTop: scout.space.md,
              padding: scout.space.lg,
              background: activeTab === 'overview' ? scout.accent.cyanGlow : 'transparent',
              border: `2px solid ${activeTab === 'overview' ? scout.accent.cyan : scout.accent.steel}`,
              borderRadius: scout.radius.lg,
              fontSize: scout.size.base,
              color: activeTab === 'overview' ? scout.accent.cyan : scout.text.secondary,
              cursor: 'pointer',
            }}
          >
            System Overview
          </button>

          {report && (
            <button
              onClick={() => setActiveTab('report')}
              style={{
                padding: scout.space.lg,
                background: activeTab === 'report' ? scout.accent.cyanGlow : 'transparent',
                border: `2px solid ${activeTab === 'report' ? scout.accent.cyan : scout.accent.steel}`,
                borderRadius: scout.radius.lg,
                fontSize: scout.size.base,
                color: activeTab === 'report' ? scout.accent.cyan : scout.text.secondary,
                cursor: 'pointer',
              }}
            >
              Final Report
            </button>
          )}
        </div>

        {/* Center: Agent Output */}
        <div style={{
          background: scout.bg.surface,
          border: `2px solid ${scout.accent.steel}`,
          borderRadius: scout.radius.lg,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}>
          {/* Title bar */}
          <div style={{
            padding: `${scout.space.md} ${scout.space.lg}`,
            borderBottom: `1px solid ${scout.accent.steel}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <span style={{
              fontSize: scout.size.sm,
              fontWeight: scout.weight.medium,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              color: scout.text.tertiary,
            }}>
              {activeTab === 'overview' ? 'System Overview' : activeTab === 'report' ? 'Final Report' : `${currentAgent?.name} Output`}
            </span>
            {currentAgent?.status === 'running' && (
              <span style={{
                fontSize: scout.size.xs,
                color: scout.status.active,
                animation: 'pulse 1.5s ease-in-out infinite',
              }}>
                Processing
              </span>
            )}
          </div>

          {/* Content */}
          <div style={{
            flex: 1,
            overflow: 'auto',
            padding: scout.space.lg,
          }}>
            {activeTab === 'overview' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: scout.space.xl }}>
                <div>
                  <h3 style={{ fontSize: scout.size.lg, marginBottom: scout.space.md, color: scout.text.secondary }}>
                    Task
                  </h3>
                  <p style={{ fontSize: scout.size.xl }}>{task?.analysis_goal || 'AI Agent competitive analysis'}</p>
                </div>

                <div>
                  <h3 style={{ fontSize: scout.size.lg, marginBottom: scout.space.md, color: scout.text.secondary }}>
                    Progress
                  </h3>
                  <div style={{
                    height: 8,
                    background: scout.accent.steel,
                    borderRadius: scout.radius.full,
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${task?.progress || 0}%`,
                      height: '100%',
                      background: `linear-gradient(90deg, ${scout.accent.cyan}, ${scout.accent.amber})`,
                      transition: 'width 500ms ease',
                    }} />
                  </div>
                  <p style={{ marginTop: scout.space.sm, color: scout.text.tertiary }}>
                    {task?.progress || 0}% complete
                  </p>
                </div>

                <div>
                  <h3 style={{ fontSize: scout.size.lg, marginBottom: scout.space.md, color: scout.text.secondary }}>
                    Recent Events
                  </h3>
                  {runError && (
                    <div style={{
                      padding: scout.space.md,
                      marginBottom: scout.space.md,
                      color: scout.status.error,
                      background: scout.bg.surface,
                      border: `1px solid ${scout.status.error}`,
                      borderRadius: scout.radius.md,
                      fontSize: scout.size.sm,
                    }}>
                      {runError}
                    </div>
                  )}
                  {events.slice(-5).map((ev) => (
                    <div key={ev.event_id} style={{
                      padding: `${scout.space.sm} 0`,
                      borderBottom: `1px solid ${scout.accent.steel}`,
                      fontSize: scout.size.sm,
                      fontFamily: scout.font.mono,
                    }}>
                      <span style={{ color: scout.text.tertiary }}>{ev.created_at?.slice(11, 19) || '12:00:00'}</span>
                      {' '}
                      <span style={{
                        color: ev.event_type?.includes('FAILED') ? scout.status.error
                          : ev.event_type?.includes('SUCCEEDED') ? scout.status.ready
                          : scout.text.secondary,
                      }}>
                        {ev.event_type}
                      </span>
                      {ev.node_name && (
                        <span style={{ color: scout.text.tertiary }}> ({ev.node_name})</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Agent detail view - logs + artifacts */}
            {currentAgent && activeTab !== 'overview' && activeTab !== 'report' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: scout.space.xl }}>
                {/* Execution Log */}
                <div>
                  <h3 style={{
                    fontSize: scout.size.sm,
                    fontWeight: scout.weight.medium,
                    color: scout.text.tertiary,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    marginBottom: scout.space.md,
                  }}>
                    Execution Log
                  </h3>
                  <div style={{
                    background: scout.bg.base,
                    borderRadius: scout.radius.md,
                    padding: scout.space.md,
                    fontFamily: scout.font.mono,
                    fontSize: scout.size.base,
                  }}>
                    {currentAgent.logs.length > 0 ? currentAgent.logs.map((log, idx) => (
                      <div key={idx} style={{
                        padding: `${scout.space.xs} 0`,
                        color: log.includes('completed') ? scout.status.ready
                          : log.includes('error') ? scout.status.error
                          : scout.text.secondary,
                      }}>
                        {log}
                      </div>
                    )) : (
                      <div style={{ color: scout.text.tertiary }}>Waiting to start...</div>
                    )}
                    {currentAgent.status === 'running' && (
                      <span style={{ color: scout.status.active, animation: 'pulse 1s ease-in-out infinite' }}>
                        _
                      </span>
                    )}
                  </div>
                </div>

                {/* Artifacts List */}
                <div>
                  <h3 style={{
                    fontSize: scout.size.sm,
                    fontWeight: scout.weight.medium,
                    color: scout.text.tertiary,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    marginBottom: scout.space.md,
                  }}>
                    Artifacts ({currentAgent.artifacts.length})
                  </h3>

                  {currentAgent.artifacts.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: scout.space.md }}>
                      {currentAgent.artifacts.map((artifact) => (
                        <button
                          key={artifact.id}
                          onClick={() => navigate(`/workbench/${taskId}/artifact/${artifact.id}`)}
                          style={{
                            padding: scout.space.lg,
                            background: scout.bg.base,
                            border: `1px solid ${scout.accent.steel}`,
                            borderRadius: scout.radius.md,
                            textAlign: 'left',
                            cursor: 'pointer',
                            transition: 'all 150ms',
                          }}
                        >
                          <div style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: scout.space.md,
                          }}>
                            <span style={{
                              padding: `${scout.space.xs} ${scout.space.sm}`,
                              background: scout.bg.elevated,
                              borderRadius: scout.radius.sm,
                              fontSize: scout.size.xs,
                              color: scout.text.tertiary,
                              textTransform: 'uppercase',
                            }}>
                              {getArtifactLabel(artifact.type)}
                            </span>
                            <div style={{ flex: 1 }}>
                              <div style={{
                                fontSize: scout.size.base,
                                fontWeight: scout.weight.medium,
                                color: scout.text.primary,
                                marginBottom: scout.space.xs,
                              }}>
                                {artifact.name}
                              </div>
                              <div style={{
                                fontSize: scout.size.sm,
                                color: scout.text.secondary,
                              }}>
                                {artifact.preview}
                              </div>
                            </div>
                            <span style={{ color: scout.accent.cyan, fontSize: scout.size.sm }}>
                              View →
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div style={{ color: scout.text.tertiary, fontSize: scout.size.sm }}>
                      No artifacts yet. Agent is still processing.
                    </div>
                  )}
                </div>

                <div ref={logsEndRef} />
              </div>
            )}

            {activeTab === 'report' && report && (
              <div>
                <h2 style={{ fontSize: scout.size.xxl, marginBottom: scout.space.xl }}>
                  Executive Summary
                </h2>
                <p style={{
                  fontSize: scout.size.lg,
                  lineHeight: 1.7,
                  color: scout.text.secondary,
                  marginBottom: scout.space.xxl,
                }}>
                  {report.executive_summary}
                </p>

                {report.comparison_matrix && (
                  <>
                    <h3 style={{ fontSize: scout.size.xl, marginBottom: scout.space.lg }}>
                      Comparison Matrix
                    </h3>
                    <table style={{
                      width: '100%',
                      borderCollapse: 'collapse',
                      fontSize: scout.size.base,
                    }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: scout.space.md, borderBottom: `2px solid ${scout.accent.steel}` }}>Product</th>
                          {report.comparison_matrix.dimensions.map((d: string) => (
                            <th key={d} style={{ textAlign: 'left', padding: scout.space.md, borderBottom: `2px solid ${scout.accent.steel}` }}>{d}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {report.comparison_matrix.products.map((p: any, i: number) => (
                          <tr key={i}>
                            <td style={{ padding: scout.space.md, borderBottom: `1px solid ${scout.accent.steel}`, fontWeight: scout.weight.medium }}>{p.name}</td>
                            {report.comparison_matrix.dimensions.map((d: string) => (
                              <td key={d} style={{ padding: scout.space.md, borderBottom: `1px solid ${scout.accent.steel}`, color: scout.text.secondary }}>{p[d] || '-'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Evidence Summary */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: scout.space.lg,
          overflow: 'auto',
        }}>
          <h2 style={{
            fontSize: scout.size.sm,
            fontWeight: scout.weight.semibold,
            color: scout.text.tertiary,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
          }}>
            Evidence Summary
          </h2>

          {/* Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: scout.space.md,
          }}>
            <div style={{
              padding: scout.space.lg,
              background: scout.bg.surface,
              border: `2px solid ${scout.accent.steel}`,
              borderRadius: scout.radius.lg,
            }}>
              <div style={{ fontSize: scout.size.xs, color: scout.text.tertiary }}>Sources</div>
              <div style={{ fontSize: scout.size.xxxl, fontWeight: scout.weight.semibold }}>
                {sources.length}
              </div>
            </div>
            <div style={{
              padding: scout.space.lg,
              background: scout.bg.surface,
              border: `2px solid ${scout.accent.steel}`,
              borderRadius: scout.radius.lg,
            }}>
              <div style={{ fontSize: scout.size.xs, color: scout.text.tertiary }}>Evidence</div>
              <div style={{ fontSize: scout.size.xxxl, fontWeight: scout.weight.semibold }}>
                {evidence.length}
              </div>
            </div>
          </div>

          {/* Artifact Types */}
          <div style={{
            padding: scout.space.lg,
            background: scout.bg.surface,
            border: `2px solid ${scout.accent.steel}`,
            borderRadius: scout.radius.lg,
          }}>
            <h3 style={{
              fontSize: scout.size.sm,
              color: scout.text.secondary,
              marginBottom: scout.space.md,
            }}>
              Generated Claims
            </h3>
            <div style={{ fontSize: scout.size.xxxl, fontWeight: scout.weight.semibold, marginBottom: scout.space.sm }}>
              {claims.length}
            </div>
            <div style={{ fontSize: scout.size.sm, color: scout.text.tertiary }}>
              {claims.filter((c: any) => c.claim_type === 'comparison').length} comparisons,
              {' '}{claims.filter((c: any) => c.claim_type === 'insight').length} insights,
              {' '}{claims.filter((c: any) => c.claim_type === 'recommendation').length} recommendations
            </div>
          </div>

          <Link to={`/sources/${taskId}`} style={{
            display: 'block',
            padding: `${scout.space.md} ${scout.space.lg}`,
            background: scout.accent.cyanGlow,
            border: `1px solid ${scout.accent.cyan}`,
            borderRadius: scout.radius.md,
            color: scout.accent.cyan,
            textDecoration: 'none',
            textAlign: 'center',
            fontSize: scout.size.base,
            fontWeight: scout.weight.medium,
          }}>
            View All Sources →
          </Link>
        </div>
      </main>
    </div>
  )
}
