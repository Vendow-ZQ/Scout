import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getEvidence, getSources } from '../api/client'

interface SourceItem {
  source_id: string
  title: string
  source_type: string
  product: string | null
  raw_excerpt: string
  url: string | null
}

interface EvidenceItem {
  evidence_id: string
  source_id: string
  product: string
  dimension: string
  fact: string
  confidence: number
}

export default function SourcesPage() {
  const { taskId } = useParams<{ taskId: string }>()
  const [sources, setSources] = useState<SourceItem[]>([])
  const [evidence, setEvidence] = useState<EvidenceItem[]>([])
  const [filterProduct, setFilterProduct] = useState<string>('')
  const [filterDimension, setFilterDimension] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!taskId) return
    async function load() {
      try {
        const [s, e] = await Promise.all([
          getSources(taskId!).catch(() => []),
          getEvidence(taskId!).catch(() => []),
        ])
        setSources(s as SourceItem[])
        setEvidence(e as EvidenceItem[])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [taskId])

  if (loading) return <div>加载中...</div>

  const products = Array.from(new Set(evidence.map(e => e.product).concat(sources.map(s => s.product).filter(Boolean) as string[])))
  const dimensions = Array.from(new Set(evidence.map(e => e.dimension)))

  const filteredEvidence = evidence.filter(e => {
    return (!filterProduct || e.product === filterProduct) &&
           (!filterDimension || e.dimension === filterDimension)
  })

  return (
    <div>
      <h2>来源与证据: {taskId}</h2>

      <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
        <label>
          产品筛选
          <select value={filterProduct} onChange={e => setFilterProduct(e.target.value)} style={{ marginLeft: 8, padding: 4 }}>
            <option value="">全部</option>
            {products.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
        <label>
          维度筛选
          <select value={filterDimension} onChange={e => setFilterDimension(e.target.value)} style={{ marginLeft: 8, padding: 4 }}>
            <option value="">全部</option>
            {dimensions.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>
      </div>

      <h3>证据卡 ({filteredEvidence.length} 条)</h3>
      <div style={{ display: 'grid', gap: 12, marginBottom: 24 }}>
        {filteredEvidence.map(e => {
          const src = sources.find(s => s.source_id === e.source_id)
          return (
            <div key={e.evidence_id} style={{ padding: 16, background: '#f9fafb', borderRadius: 8, borderLeft: '4px solid #2563eb' }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
                <strong>{e.product}</strong>
                <span style={{ padding: '2px 8px', background: '#e0e7ff', borderRadius: 4, fontSize: 12 }}>{e.dimension}</span>
                <span style={{ fontSize: 12, color: '#6b7280' }}>置信度: {e.confidence * 100}%</span>
              </div>
              <div style={{ marginBottom: 8 }}>{e.fact}</div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>
                证据ID: {e.evidence_id} | 来源: {src ? src.title : e.source_id}
                {src?.url && <span> | <a href={src.url} target="_blank" rel="noopener noreferrer">链接</a></span>}
              </div>
            </div>
          )
        })}
      </div>

      <h3>来源列表 ({sources.length} 条)</h3>
      <div style={{ display: 'grid', gap: 12 }}>
        {sources.map(s => (
          <div key={s.source_id} style={{ padding: 16, background: '#f9fafb', borderRadius: 8 }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
              <strong>{s.title}</strong>
              <span style={{ padding: '2px 8px', background: '#fef3c7', borderRadius: 4, fontSize: 12 }}>{s.source_type}</span>
              {s.product && <span style={{ padding: '2px 8px', background: '#dcfce7', borderRadius: 4, fontSize: 12 }}>{s.product}</span>}
            </div>
            <div style={{ fontSize: 14, color: '#4b5563', marginBottom: 4 }}>{s.raw_excerpt}</div>
            <div style={{ fontSize: 12, color: '#6b7280' }}>
              ID: {s.source_id}
              {s.url && <span> | <a href={s.url} target="_blank" rel="noopener noreferrer">{s.url}</a></span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
