import { useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { scout } from '../styles/scout-theme'

interface AgentGraphProps {
  nodeStatus: Record<string, 'pending' | 'running' | 'success' | 'failed'>
}

export default function AgentGraph({ nodeStatus }: AgentGraphProps) {
  const nodes: Node[] = useMemo(() => {
    const agents = [
      { id: 'researcher', label: 'Researcher', desc: 'Collect sources' },
      { id: 'analyst', label: 'Analyst', desc: 'Structure evidence' },
      { id: 'editor', label: 'Editor', desc: 'Edit final report' },
      { id: 'reviewer', label: 'Reviewer', desc: 'Quality check' },
    ]

    return agents.map((agent, i) => {
      const status = nodeStatus[agent.id] || 'pending'
      const isActive = status === 'running'
      const isSuccess = status === 'success'

      return {
        id: agent.id,
        position: { x: i * 200, y: 100 },
        data: { label: agent.label, desc: agent.desc },
        style: {
          background: isActive ? scout.accent.cyanGlow
            : isSuccess ? 'rgba(124, 175, 106, 0.1)'
            : scout.bg.elevated,
          border: `1px solid ${isActive ? scout.accent.cyan
            : isSuccess ? scout.status.ready
            : scout.accent.steel}`,
          borderRadius: scout.radius.md,
          padding: '16px 24px',
          color: isActive ? scout.accent.cyan
            : isSuccess ? scout.status.ready
            : scout.text.secondary,
          fontSize: '14px',
          fontWeight: 500,
          minWidth: 140,
          textAlign: 'center' as const,
          boxShadow: isActive ? `0 0 16px ${scout.accent.cyanGlow}` : 'none',
          transition: 'all 250ms ease',
        },
      }
    })
  }, [nodeStatus])

  const edges: Edge[] = useMemo(() => [
    { id: 'e1-2', source: 'researcher', target: 'analyst', style: { stroke: scout.accent.steel } },
    { id: 'e2-3', source: 'analyst', target: 'editor', style: { stroke: scout.accent.steel } },
    { id: 'e3-4', source: 'editor', target: 'reviewer', style: { stroke: scout.accent.steel } },
  ], [])

  return (
    <div style={{ height: 300, background: scout.bg.elevated, borderRadius: scout.radius.md }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
      >
        <Background gap={20} size={1} color={scout.accent.steel} />
        <Controls style={{ background: scout.bg.surface }} />
      </ReactFlow>
    </div>
  )
}
