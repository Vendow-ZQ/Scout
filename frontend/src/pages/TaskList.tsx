import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { scout } from '../styles/scout-theme'

interface Task {
  task_id: string
  status: string
  query: string
  progress: number
  created_at: string
  source_count: number
  evidence_count: number
}

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/tasks')
      .then(r => r.json())
      .then((data: Task[]) => {
        setTasks(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return scout.status.active
      case 'completed': return scout.status.ready
      case 'failed':
      case 'review_failed': return scout.status.error
      default: return scout.text.tertiary
    }
  }

  const formatDate = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

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
        <Link to="/" style={{
          fontSize: scout.size.xl,
          fontWeight: scout.weight.semibold,
          color: scout.text.primary,
          textDecoration: 'none',
        }}>
          Scout
        </Link>

        <Link to="/" style={{
          padding: `${scout.space.md} ${scout.space.xl}`,
          background: scout.text.primary,
          borderRadius: scout.radius.full,
          color: scout.bg.base,
          fontSize: scout.size.base,
          fontWeight: scout.weight.medium,
          textDecoration: 'none',
        }}>
          + New Investigation
        </Link>
      </header>

      {/* Main */}
      <main style={{
        maxWidth: 1200,
        margin: '0 auto',
        padding: `${scout.space.xxl} ${scout.space.lg}`,
      }}>
        <h1 style={{
          fontSize: scout.size.xxxl,
          fontWeight: scout.weight.medium,
          marginBottom: scout.space.xxl,
          letterSpacing: '-0.02em',
        }}>
          Investigations
        </h1>

        {loading ? (
          <div style={{ color: scout.text.tertiary, fontSize: scout.size.lg }}>
            Loading...
          </div>
        ) : tasks.length === 0 ? (
          <div style={{
            padding: `${scout.space.xxxl} ${scout.space.xl}`,
            textAlign: 'center',
            border: `2px dashed ${scout.accent.steel}`,
            borderRadius: scout.radius.xl,
          }}>
            <p style={{ fontSize: scout.size.lg, color: scout.text.secondary, marginBottom: scout.space.lg }}>
              No investigations yet.
            </p>
            <Link to="/" style={{
              color: scout.accent.cyan,
              fontSize: scout.size.xl,
              textDecoration: 'none',
            }}>
              Start your first →
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: scout.space.md }}>
            {tasks.map((task) => (
              <Link
                key={task.task_id}
                to={`/workbench/${task.task_id}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: `${scout.space.xl} ${scout.space.xxl}`,
                  background: scout.bg.surface,
                  border: `2px solid ${scout.accent.steel}`,
                  borderRadius: scout.radius.lg,
                  textDecoration: 'none',
                  color: scout.text.primary,
                  transition: 'all 150ms',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = scout.accent.steelLight
                  e.currentTarget.style.background = scout.bg.elevated
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = scout.accent.steel
                  e.currentTarget.style.background = scout.bg.surface
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: scout.space.lg }}>
                  <span style={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: getStatusColor(task.status),
                    boxShadow: task.status === 'running' ? `0 0 12px ${scout.status.active}` : 'none',
                    animation: task.status === 'running' ? 'pulse 1.5s ease-in-out infinite' : 'none',
                  }} />

                  <div>
                    <div style={{
                      fontSize: scout.size.lg,
                      fontWeight: scout.weight.medium,
                      marginBottom: scout.space.xs,
                    }}>
                      {task.query || 'Untitled investigation'}
                    </div>
                    <div style={{
                      fontSize: scout.size.sm,
                      color: scout.text.tertiary,
                    }}>
                      {formatDate(task.created_at)} · {task.source_count || 0} sources · {task.evidence_count || 0} evidence
                    </div>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: scout.space.xl,
                }}>
                  {/* 进度 */}
                  <div style={{
                    width: 120,
                    height: 6,
                    background: scout.accent.steel,
                    borderRadius: scout.radius.full,
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${task.progress || 0}%`,
                      height: '100%',
                      background: getStatusColor(task.status),
                      transition: 'width 500ms ease',
                    }} />
                  </div>

                  <span style={{
                    fontSize: scout.size.sm,
                    color: scout.text.tertiary,
                    textTransform: 'capitalize',
                    minWidth: 100,
                    textAlign: 'right',
                  }}>
                    {task.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
