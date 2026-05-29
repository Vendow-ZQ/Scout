import { Routes, Route } from 'react-router-dom'
import TaskCreate from './pages/TaskCreate'
import TaskList from './pages/TaskList'
import RunWorkbench from './pages/RunWorkbench'
import SourcesPage from './pages/SourcesPage'
import ArtifactDetail from './pages/ArtifactDetail'

function App() {
  return (
    <Routes>
      <Route path="/" element={<TaskCreate />} />
      <Route path="/tasks" element={<TaskList />} />
      <Route path="/workbench/:taskId" element={<RunWorkbench />} />
      <Route path="/workbench/:taskId/artifact/:artifactId" element={<ArtifactDetail />} />
      <Route path="/sources/:taskId" element={<SourcesPage />} />
    </Routes>
  )
}

export default App
