const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}

export { API_BASE }

export async function listWorkshops() {
  const res = await fetch(`${API_BASE}/api/workshops`)
  if (!res.ok) throw new Error('Failed to load workshops')
  return res.json()
}

export async function registerWorkshop(workshopId, payload) {
  const isFormData = typeof FormData !== 'undefined' && payload instanceof FormData
  const options = { method: 'POST' }
  if (isFormData) {
    options.body = payload
  } else {
    options.headers = { 'Content-Type': 'application/json' }
    options.body = JSON.stringify(payload)
  }
  const res = await fetch(`${API_BASE}/api/workshops/${workshopId}/register`, options)
  if (!res.ok) throw new Error('Registration failed')
  return res.json()
}


