const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

export async function api(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`)
  return body.data
}

export const query = (params) => `?${new URLSearchParams(params).toString()}`
