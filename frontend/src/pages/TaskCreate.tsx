import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createTask, runTask } from '../api/client'

const DEFAULT_COMPETITORS = ['ChatGPT', 'Claude', 'Gemini', 'Genspark', 'Manus']

export default function TaskCreate() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    industry: '通用 AI Agent',
    region: '全球 + 中国',
    main_product: 'Scout',
    competitors: DEFAULT_COMPETITORS.join('\n'),
    analysis_goal: '判断 AI Agent 产品能力差异、目标用户、机会点和风险',
    data_mode: 'mock',
    schema_pack: 'ai_agent',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = {
        ...form,
        competitors: form.competitors.split('\n').map(s => s.trim()).filter(Boolean),
      }
      const task = await createTask(payload)
      const result = await runTask(task.task_id)

      if (result.status === 'completed' || result.status === 'review_failed') {
        navigate(`/workbench/${task.task_id}`)
      } else {
        setError(`运行异常: ${JSON.stringify(result)}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>创建竞品分析任务</h2>
      {error && (
        <div style={{ background: '#fee', color: '#c00', padding: 12, borderRadius: 4, marginBottom: 16 }}>
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gap: 16, maxWidth: 600 }}>
          <label>
            行业方向
            <input
              value={form.industry}
              onChange={e => setForm(f => ({ ...f, industry: e.target.value }))}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>
          <label>
            地区
            <input
              value={form.region}
              onChange={e => setForm(f => ({ ...f, region: e.target.value }))}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>
          <label>
            主品
            <input
              value={form.main_product}
              onChange={e => setForm(f => ({ ...f, main_product: e.target.value }))}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>
          <label>
            竞品列表（每行一个）
            <textarea
              value={form.competitors}
              onChange={e => setForm(f => ({ ...f, competitors: e.target.value }))}
              rows={5}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>
          <label>
            分析目标
            <textarea
              value={form.analysis_goal}
              onChange={e => setForm(f => ({ ...f, analysis_goal: e.target.value }))}
              rows={2}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>
          <label>
            数据包
            <select
              value={form.schema_pack}
              onChange={e => setForm(f => ({ ...f, schema_pack: e.target.value }))}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            >
              <option value="ai_agent">通用 AI Agent</option>
              <option value="ai_earbuds">AI 耳机 (示例)</option>
            </select>
          </label>
          <label>
            数据模式
            <select
              value={form.data_mode}
              onChange={e => setForm(f => ({ ...f, data_mode: e.target.value }))}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            >
              <option value="mock">Mock 数据（演示）</option>
            </select>
          </label>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 24px',
              background: loading ? '#999' : '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: 4,
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: 16,
            }}
          >
            {loading ? '运行中...' : '启动分析'}
          </button>
        </div>
      </form>
    </div>
  )
}
