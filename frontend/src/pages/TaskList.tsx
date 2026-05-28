import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface TaskItem {
  task_id: string
  status: string
  current_node: string | null
  progress_percent: number
  created_at: string
}

export default function TaskList() {
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/tasks')
      .then(r => r.json())
      .then((data: TaskItem[]) => {
        setTasks(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>加载中...</div>

  return (
    <div>
      <h2>任务列表</h2>
      {tasks.length === 0 ? (
        <p style={{ color: '#666' }}>暂无任务，<Link to="/">创建一个</Link></p>
      ) : (
        <div style={{ display: 'grid', gap: 12, marginTop: 16 }}>
          {tasks.map(t => (
            <div key={t.task_id} style={{ padding: 16, background: '#f9fafb', borderRadius: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong>{t.task_id}</strong>
                <span style={{
                  padding: '2px 8px',
                  borderRadius: 4,
                  fontSize: 12,
                  background: t.status === 'completed' ? '#dcfce7'
                    : t.status === 'failed' ? '#fef2f2'
                    : t.status === 'running' ? '#fef3c7'
                    : '#e5e7eb',
                  color: t.status === 'completed' ? '#166534'
                    : t.status === 'failed' ? '#991b1b'
                    : t.status === 'running' ? '#92400e'
                    : '#374151',
                }}>
                  {t.status}
                </span>
              </div>
              <div style={{ fontSize: 14, color: '#6b7280', marginTop: 4 }}>
                {t.current_node && <span>节点: {t.current_node} | </span>}
                进度: {t.progress_percent}% | 创建于: {t.created_at.slice(0, 19).replace('T', ' ')}
              </div>
              <div style={{ marginTop: 8 }}>
                <Link to={`/workbench/${t.task_id}`} style={{ marginRight: 16 }}>工作台</Link>
                <Link to={`/sources/${t.task_id}`}>来源与证据</Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
