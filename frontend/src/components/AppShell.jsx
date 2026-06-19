import { LogOut, LayoutDashboard, NotebookPen, Sparkles } from 'lucide-react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

function routeLabel(pathname) {
  if (pathname.startsWith('/projects/')) {
    return 'Project Workspace'
  }
  if (pathname.startsWith('/reports/')) {
    return 'Saved Report'
  }
  return 'Research Dashboard'
}

function routeDescription(pathname) {
  if (pathname.startsWith('/projects/')) {
    return 'Manage sources, ask grounded questions, and generate polished research outputs.'
  }
  if (pathname.startsWith('/reports/')) {
    return 'Review a structured report generated from indexed project evidence.'
  }
  return 'Organize active research streams, source collections, and reporting work in one place.'
}

export default function AppShell() {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/dashboard" className="brand-mark">
            <span className="brand-glyph">
              <NotebookPen size={18} />
            </span>
            <span>
              <strong>ScholarFlow AI</strong>
              <small>AI research assistant</small>
            </span>
          </Link>

          <nav className="topbar-nav" aria-label="Primary navigation">
            <NavLink to="/dashboard" className="nav-link">
              <LayoutDashboard size={16} />
              Dashboard
            </NavLink>
            <button type="button" className="ghost-button" onClick={logout}>
              <LogOut size={16} />
              Logout
            </button>
          </nav>
        </div>
      </header>

      <main className="page-shell">
        <section className="page-hero">
          <div className="page-hero-copy">
            <p className="eyebrow">{routeLabel(location.pathname)}</p>
            <h1 className="shell-title">{user?.full_name || 'ScholarFlow AI'}</h1>
            <p className="muted-text shell-subtitle">{routeDescription(location.pathname)}</p>
          </div>

          <div className="page-hero-meta">
            <div className="hero-chip">
              <Sparkles size={16} />
              <span>Grounded generation</span>
            </div>
            <div className="hero-user-card">
              <span className="hero-user-label">Signed in as</span>
              <strong>{user?.email || 'Authenticated workspace'}</strong>
            </div>
          </div>
        </section>

        <Outlet />
      </main>
    </div>
  )
}
