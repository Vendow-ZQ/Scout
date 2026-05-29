import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEvidence, getSources } from '../api/client'
import { scout } from '../styles/scout-theme'

interface Source {
  source_id: string
  title: string
  source_type: string
  product: string | null
  raw_excerpt: string
  url: string | null
}

interface Evidence {
  evidence_id: string
  source_id: string
  product: string
  dimension: string
  fact: string
  confidence: number
}

export default function SourcesPage() {
  const { taskId } = useParams<{ taskId: string }>()
  const [sources, setSources] = useState<Source[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!taskId) return
    Promise.all([
      getSources(taskId).catch(() => []),
      getEvidence(taskId).catch(() => []),
    ]).then(([s, e]) => {
      setSources(s as Source[])
      setEvidence(e as Evidence[])
      setLoading(false)
    })
  }, [taskId])

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: scout.bg.base,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: scout.text.tertiary,
      }}
      >
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

  return (
    <div style={{
      minHeight: '100vh',
      background: scout.bg.base,
      color: scout.text.primary,
      fontFamily: scout.font.sans,
    }}
    >
      {/* Header */}
      <header style={{
        padding: `${scout.space.lg} ${scout.space.xxl}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: `2px solid ${scout.accent.steel}`,
      }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: scout.space.lg }}>
          <Link to="/" style={{
            fontSize: scout.size.xl,
            fontWeight: scout.weight.semibold,
            color: scout.text.primary,
            textDecoration: 'none',
          }}
          >
            Scout
          </Link>
          <span style={{ color: scout.text.quaternary }}>/</span>
          <span style={{ fontSize: scout.size.base, color: scout.text.secondary }}>
            Sources
          </span>
        </div>

        <Link to={`/workbench/${taskId}`} style={{
          fontSize: scout.size.base,
          color: scout.text.secondary,
          textDecoration: 'none',
        }}
        >
          ← Back to workbench
        </Link>
      </header>

      {/* Main */}
      <main style={{
        maxWidth: 1200,
        margin: '0 auto',
        padding: scout.space.xxl,
      }}
      >
        <h1 style={{
          fontSize: scout.size.xxxl,
          fontWeight: scout.weight.medium,
          marginBottom: scout.space.xl,
        }}
        >
          Evidence & Sources
        </h1>

        {/* Stats */}
        <div style={{
          display: 'flex',
          gap: scout.space.xl,
          marginBottom: scout.space.xxl,
        }}
        >
          <div style={{
            padding: `${scout.space.lg} ${scout.space.xl}`,
            background: scout.bg.surface,
            border: `2px solid ${scout.accent.steel}`,
            borderRadius: scout.radius.lg,
            minWidth: 150,
          }}
          >
            <div style={{ fontSize: scout.size.sm, color: scout.text.tertiary, marginBottom: scout.space.xs }}>
              Evidence cards
            </div>
            <div style={{ fontSize: scout.size.xxxl, fontWeight: scout.weight.semibold }}>
              {evidence.length}
            </div>
          </div>
          <div style={{
            padding: `${scout.space.lg} ${scout.space.xl}`,
            background: scout.bg.surface,
            border: `2px solid ${scout.accent.steel}`,
            borderRadius: scout.radius.lg,
            minWidth: 150,
          }}
          >
            <div style={{ fontSize: scout.size.sm, color: scout.text.tertiary, marginBottom: scout.space.xs }}>
              Sources
            </div>
            <div style={{ fontSize: scout.size.xxxl, fontWeight: scout.weight.semibold }}>
              {sources.length}
            </div>
          </div>
        </div>

        {/* Evidence List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: scout.space.lg }}>
          {evidence.map(ev => {
            const src = sources.find(s => s.source_id === ev.source_id)
            return (
              <div key={ev.evidence_id} style={{
                padding: scout.space.xl,
                background: scout.bg.surface,
                border: `2px solid ${scout.accent.steel}`,
                borderRadius: scout.radius.lg,
              }}
              >
                <div style={{
                  display: 'flex',
                  gap: scout.space.md,
                  marginBottom: scout.space.md,
                  fontSize: scout.size.base,
                }}
                >
                  <span style={{ fontWeight: scout.weight.medium }}>{ev.product}</span>
                  <span style={{ color: scout.text.tertiary }}>/</span>
                  <span style={{ color: scout.accent.cyan }}>{ev.dimension}</span>
                  <span style={{ marginLeft: 'auto', color: scout.text.tertiary }}>
                    {Math.round(ev.confidence * 100)}%
                  </span>
                </div>
                <div style={{ fontSize: scout.size.lg, color: scout.text.secondary, marginBottom: scout.space.md, lineHeight: 1.6 }}>
                  {ev.fact}
                </div>
                <div style={{
                  fontSize: scout.size.sm,
                  color: scout.text.tertiary,
                  fontFamily: scout.font.mono,
                }}
                >
                  {ev.evidence_id} → {src?.title || ev.source_id}
                </div>
              </div>
            )
          })}
        </div>
      </main>
    </div>
  )
}
