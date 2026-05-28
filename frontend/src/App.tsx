import { Routes, Route, Link } from 'react-router-dom'
import TaskCreate from './pages/TaskCreate'
import RunWorkbench from './pages/RunWorkbench'

function App() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 1200, margin: '0 auto', padding: 20 }}>
      <header style={{ borderBottom: '1px solid #e0e0e0', paddingBottom: 16, marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>Scout</h1>
        <p style={{ margin: '4px 0 0', color: '#666' }}>AI 驱动的竞品分析 Agent 协作系统</p>
        <nav style={{ marginTop: 12 }}>
          <Link to="/" style={{ marginRight: 16 }}>新建任务</Link>
          <Link to="/tasks">任务列表</Link>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<TaskCreate />} />
        <Route path="/workbench/:taskId" element={<RunWorkbench />} />
      </Routes>
    </div>
  )
}

export default App
