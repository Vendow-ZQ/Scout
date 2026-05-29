import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { getSources, getEvidence, getClaims, getArtifactFile } from '../api/client'
import { scout } from '../styles/scout-theme'

interface Artifact {
  id: string
  type: string
  name: string
  agent: string
  createdAt: string
  content: string
}

function formatSourceAsMarkdown(source: any): string {
  const lines = [
    `## Source: ${source.title}`,
    '',
    `**Type:** ${source.source_type}`,
    `**Product:** ${source.product || 'Market'}`,
    `**URL:** ${source.url || 'N/A'}`,
    '',
    '### Content',
    '',
    source.raw_excerpt,
    '',
    '---',
    `*Source ID: ${source.source_id}*`,
  ]
  return lines.join('\n')
}

function formatEvidenceAsMarkdown(ev: any): string {
  const lines = [
    `## Evidence Card: ${ev.dimension}`,
    '',
    `**Product:** ${ev.product}`,
    `**Dimension:** ${ev.dimension}`,
    `**Confidence:** ${Math.round(ev.confidence * 100)}%`,
    `**Source:** ${ev.source_id}`,
    '',
    '### Fact',
    '',
    ev.fact,
    '',
    '---',
    `*Evidence ID: ${ev.evidence_id}*`,
  ]
  return lines.join('\n')
}

function formatClaimAsMarkdown(claim: any): string {
  const evidenceList = claim.evidence_ids?.map((id: string) => `- ${id}`).join('\n') || 'No evidence linked'
  const lines = [
    `## Claim: ${claim.claim_type}`,
    '',
    `**Status:** ${claim.reviewer_status || 'pending'}`,
    `**Confidence:** ${Math.round(claim.confidence * 100)}%`,
    `**Products:** ${claim.product_refs?.join(', ') || 'N/A'}`,
    '',
    '### Statement',
    '',
    claim.text,
    '',
    '### Supporting Evidence',
    '',
    evidenceList,
    '',
    '---',
    `*Claim ID: ${claim.claim_id}*`,
  ]
  return lines.join('\n')
}

// Find artifact in real data
async function findArtifact(taskId: string, artifactId: string): Promise<Artifact | null> {
  try {
    const filename = decodeURIComponent(artifactId)
    if (filename.endsWith('.md') || filename.endsWith('.json')) {
      const content = await getArtifactFile(taskId, filename)
      const agent = filename.startsWith('research_') || ['sources.md', 'evidence.md'].includes(filename)
        ? 'Researcher'
        : filename.startsWith('analysis_') || filename.includes('_analysis') || ['profiles.md', 'claims.md'].includes(filename)
          ? 'Analyst'
          : filename.startsWith('final_') || filename.startsWith('editorial_')
            ? 'Editor'
            : filename.startsWith('review_') || filename.startsWith('revision_')
              ? 'Reviewer'
              : 'Artifact'
      return {
        id: filename,
        type: filename.endsWith('.json') ? 'json' : 'markdown',
        name: filename,
        agent,
        createdAt: new Date().toISOString(),
        content,
      }
    }

    // Try sources
    const sources = await getSources(taskId)
    const source = sources.find((s: any) => s.source_id === artifactId)
    if (source) {
      return {
        id: source.source_id,
        type: 'source',
        name: source.title,
        agent: 'Researcher',
        createdAt: new Date().toISOString(),
        content: formatSourceAsMarkdown(source),
      }
    }

    // Try evidence
    const evidence = await getEvidence(taskId)
    const ev = evidence.find((e: any) => e.evidence_id === artifactId)
    if (ev) {
      return {
        id: ev.evidence_id,
        type: 'evidence',
        name: `Evidence: ${ev.dimension}`,
        agent: 'Researcher',
        createdAt: new Date().toISOString(),
        content: formatEvidenceAsMarkdown(ev),
      }
    }

    // Try claims
    const claims = await getClaims(taskId)
    const claim = claims.find((c: any) => c.claim_id === artifactId)
    if (claim) {
      return {
        id: claim.claim_id,
        type: claim.claim_type,
        name: claim.claim_type === 'comparison' ? 'Comparison Analysis' :
              claim.claim_type === 'insight' ? 'Market Insight' :
              claim.claim_type === 'recommendation' ? 'Recommendation' : 'Claim',
        agent: 'Analyst',
        createdAt: new Date().toISOString(),
        content: formatClaimAsMarkdown(claim),
      }
    }

    return null
  } catch (err) {
    console.error('Failed to find artifact:', err)
    return null
  }
}

export default function ArtifactDetail() {
  const { taskId, artifactId } = useParams<{ taskId: string; artifactId: string }>()
  const navigate = useNavigate()
  const [mounted, setMounted] = useState(false)
  const [artifact, setArtifact] = useState<Artifact | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!taskId || !artifactId) return
    setLoading(true)
    findArtifact(taskId, artifactId).then((art) => {
      setArtifact(art)
      setLoading(false)
    })
  }, [taskId, artifactId])

  if (!mounted) return null

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: scout.bg.base,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: scout.text.secondary,
      }}>
        Loading...
      </div>
    )
  }

  if (!artifact) {
    return (
      <div style={{
        minHeight: '100vh',
        background: scout.bg.base,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: scout.text.secondary,
      }}>
        Artifact not found
      </div>
    )
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: scout.bg.base,
      color: scout.text.primary,
      fontFamily: scout.font.sans,
    }}>
      <header style={{
        position: 'sticky',
        top: 0,
        padding: `${scout.space.lg} ${scout.space.xxl}`,
        background: `${scout.bg.base}ee`,
        backdropFilter: 'blur(10px)',
        borderBottom: `1px solid ${scout.accent.steel}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 100,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: scout.space.lg }}>
          <button
            onClick={() => navigate(-1)}
            style={{
              padding: `${scout.space.sm} ${scout.space.md}`,
              background: 'transparent',
              border: `1px solid ${scout.accent.steel}`,
              borderRadius: scout.radius.md,
              color: scout.text.secondary,
              fontSize: scout.size.base,
              cursor: 'pointer',
            }}
          >
            Back
          </button>
          <div>
            <div style={{
              fontSize: scout.size.xs,
              color: scout.text.tertiary,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
            }}>
              {artifact.type} / {artifact.agent}
            </div>
            <h1 style={{
              fontSize: scout.size.xl,
              fontWeight: scout.weight.medium,
              margin: 0,
            }}>
              {artifact.name}
            </h1>
          </div>
        </div>

        <div style={{ fontSize: scout.size.sm, color: scout.text.tertiary }}>
          {new Date(artifact.createdAt).toLocaleString()}
        </div>
      </header>

      <main style={{
        maxWidth: 900,
        margin: '0 auto',
        padding: `${scout.space.xxl} ${scout.space.lg}`,
      }}>
        <article style={{
          background: scout.bg.surface,
          border: `1px solid ${scout.accent.steel}`,
          borderRadius: scout.radius.lg,
          padding: `${scout.space.xxl} ${scout.space.xxxl}`,
          fontSize: scout.size.base,
          lineHeight: 1.7,
        }}>
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 style={{
                  fontSize: scout.size.xxl,
                  fontWeight: scout.weight.medium,
                  marginBottom: scout.space.lg,
                  marginTop: 0,
                  letterSpacing: '-0.02em',
                }}>{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 style={{
                  fontSize: scout.size.xl,
                  fontWeight: scout.weight.medium,
                  marginTop: scout.space.xl,
                  marginBottom: scout.space.md,
                  color: scout.text.secondary,
                  borderBottom: `1px solid ${scout.accent.steel}`,
                  paddingBottom: scout.space.sm,
                }}>{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 style={{
                  fontSize: scout.size.lg,
                  fontWeight: scout.weight.medium,
                  marginTop: scout.space.lg,
                  marginBottom: scout.space.sm,
                }}>{children}</h3>
              ),
              p: ({ children }) => (
                <p style={{
                  marginBottom: scout.space.md,
                  color: scout.text.secondary,
                }}>{children}</p>
              ),
              ul: ({ children }) => (
                <ul style={{
                  marginBottom: scout.space.md,
                  paddingLeft: scout.space.xl,
                  color: scout.text.secondary,
                }}>{children}</ul>
              ),
              li: ({ children }) => (
                <li style={{ marginBottom: scout.space.xs }}>{children}</li>
              ),
              strong: ({ children }) => (
                <strong style={{ color: scout.text.primary, fontWeight: scout.weight.semibold }}>
                  {children}
                </strong>
              ),
            }}
          >
            {artifact.content}
          </ReactMarkdown>
        </article>
      </main>
    </div>
  )
}
