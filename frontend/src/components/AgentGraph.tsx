import { useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

interface AgentGraphProps {
  nodeStatus: Record<string, string>
  reviewPassed?: boolean
  hasOpenIssues?: boolean
  retryTarget?: string | null
}

const nodeColors: Record<string, { bg: string; border: string; text: string }> = {
  pending: { bg: '#f3f4f6', border: '#d1d5db', text: '#6b7280' },
  running: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
  success: { bg: '#dcfce7', border: '#22c55e', text: '#166534' },
  failed: { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' },
}

export default function AgentGraph({
  nodeStatus,
  reviewPassed,
  hasOpenIssues,
  retryTarget,
}: AgentGraphProps) {
  const nodes: Node[] = useMemo(() => {
    const dagNodes = ['researcher', 'analyst', 'writer', 'reviewer']
    const positions = [
      { x: 0, y: 80 },
      { x: 220, y: 80 },
      { x: 440, y: 80 },
      { x: 660, y: 80 },
    ]

    return dagNodes.map((name, i) => {
      const status = nodeStatus[name] || 'pending'
      const colors = nodeColors[status] || nodeColors.pending
      return {
        id: name,
        position: positions[i],
        data: { label: name },
        style: {
          background: colors.bg,
          border: `2px solid ${colors.border}`,
          color: colors.text,
          borderRadius: 8,
          padding: '12px 20px',
          fontWeight: 600,
          fontSize: 14,
          minWidth: 100,
          textAlign: 'center' as const,
        },
      }
    })
  }, [nodeStatus])

  const edges: Edge[] = useMemo(() => {
    const base: Edge[] = [
      { id: 'e-r-a', source: 'researcher', target: 'analyst', animated: nodeStatus['researcher'] === 'running', style: { stroke: '#9ca3af', strokeWidth: 2 } },
      { id: 'e-a-w', source: 'analyst', target: 'writer', animated: nodeStatus['analyst'] === 'running', style: { stroke: '#9ca3af', strokeWidth: 2 } },
      { id: 'e-w-rv', source: 'writer', target: 'reviewer', animated: nodeStatus['writer'] === 'running', style: { stroke: '#9ca3af', strokeWidth: 2 } },
    ]

    // Add reviewer loop edge if there are open issues and a retry target
    if (hasOpenIssues && retryTarget) {
      base.push({
        id: 'e-rv-loop',
        source: 'reviewer',
        target: retryTarget,
        animated: true,
        style: { stroke: '#ef4444', strokeWidth: 2, strokeDasharray: '5 5' },
        label: '打回',
        labelStyle: { fill: '#ef4444', fontWeight: 600, fontSize: 12 },
        type: 'default',
      })
    }

    return base
  }, [nodeStatus, hasOpenIssues, retryTarget])

  return (
    <div style={{ width: '100%', height: 280, border: '1px solid #e5e7eb', borderRadius: 8 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnPinch={false}
        zoomOnDoubleClick={false}
      >
        <Background gap={16} size={1} />
        <Controls showInteractive={false} />
        <MiniMap
          style={{ height: 60, width: 100 }}
          nodeColor={(n) => {
            const s = nodeStatus[n.id] || 'pending'
            return nodeColors[s]?.border || '#d1d5db'
          }}
        />
      </ReactFlow>
    </div>
  )
}
