const API_BASE = '/api'

export async function createTask(data: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function runTask(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/run`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getTask(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getEvents(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/events`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getReport(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/report`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getReview(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/review`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getEvidence(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/evidence`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
