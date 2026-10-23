import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Shell from './components/Shell.jsx'
import Home from './pages/Home.jsx'
import Jobs from './pages/Jobs.jsx'
import Auth from './pages/Auth.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Quiz from './pages/Quiz.jsx'
import Admin from './pages/Admin.jsx'
import { api } from './services/api.js'

function Protected({ user, children, admin = false }) {
  if (!user) return <Navigate to="/login" replace />
  if (admin && user.role !== 'admin') return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  const [user, setUser] = useState(null), [ready, setReady] = useState(false)
  useEffect(() => { api('/auth/me').then(setUser).catch(() => setUser(null)).finally(() => setReady(true)) }, [])
  async function login(credentials) { const result = await api('/auth/login', { method: 'POST', body: JSON.stringify(credentials) }); setUser(result) }
  async function register(details) { const result = await api('/auth/register', { method: 'POST', body: JSON.stringify(details) }); setUser(result) }
  async function logout() { await api('/auth/logout', { method: 'POST' }); setUser(null) }
  if (!ready) return <div className="app-loading">Loading your workspace…</div>
  return <Shell user={user} onLogout={logout}><Routes><Route path="/" element={<Home />} /><Route path="/jobs" element={<Jobs user={user} />} /><Route path="/jobs/:id" element={<Jobs user={user} />} /><Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Auth mode="login" onLogin={login} />} /><Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <Auth mode="register" onRegister={register} />} /><Route path="/quiz" element={<Quiz user={user} />} /><Route path="/dashboard" element={<Protected user={user}><Dashboard user={user} /></Protected>} /><Route path="/admin" element={<Protected user={user} admin><Admin /></Protected>} /><Route path="*" element={<div className="wrap page-wrap empty-state"><h1>Page not found</h1><p>That address does not lead anywhere in this project.</p></div>} /></Routes></Shell>
}
