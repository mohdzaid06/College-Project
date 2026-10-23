import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { ArrowUpRight, BriefcaseBusiness, Menu, X } from 'lucide-react'

export default function Shell({ user, onLogout, children }) {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  async function logout() { await onLogout(); setOpen(false); navigate('/') }
  const close = () => setOpen(false)
  return <>
    <header className="topbar">
      <div className="topbar-inner">
        <Link className="brand" to="/" onClick={close}><span className="brand-mark"><BriefcaseBusiness size={19} /></span><span>Placi<span className="brand-dot">Fy</span><small>CAREER PREP</small></span></Link>
        <button className="mobile-toggle" aria-label="Toggle navigation" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
        <nav className={open ? 'nav-links open' : 'nav-links'} aria-label="Main navigation">
          <NavLink to="/jobs" onClick={close}>Explore roles</NavLink><NavLink to="/quiz" onClick={close}>Practice</NavLink>
          {user ? <><NavLink to="/dashboard" onClick={close}>My dashboard</NavLink>{user.role === 'admin' && <NavLink to="/admin" onClick={close}>Admin</NavLink>}<span className="nav-user">{user.name.split(' ')[0]}</span><button className="nav-logout" onClick={logout}>Log out</button></> : <><NavLink to="/login" onClick={close}>Log in</NavLink><Link className="button button-small" to="/register" onClick={close}>Get started <ArrowUpRight size={15} /></Link></>}
        </nav>
      </div>
    </header>
    <main>{children}</main>
    <footer className="footer"><div><Link className="brand footer-brand" to="/"><span className="brand-mark"><BriefcaseBusiness size={17} /></span><span>Placi<span className="brand-dot">Fy</span></span></Link><p>A practice space for your next opportunity.</p></div><span>Student Placement Preparation System · College project</span></footer>
  </>
}
