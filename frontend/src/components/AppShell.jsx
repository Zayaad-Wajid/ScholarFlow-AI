import { LogOut, NotebookText } from 'lucide-react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

function routeLabel(pathname) {
  if (pathname.startsWith('/projects/')) {
    return 'Workspace'
  }
  if (pathname.startsWith('/reports/')) {
    return 'Report detail'
  }
  return 'Dashboard'
}

export default function AppShell() {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <Link to="/dashboard" className="brand-mark">
            <span className="brand-glyph">
              <NotebookText size={18} />
            </span>
            <span>
              <strong>ScholarFlow AI</strong>
              <small>RAG research workspace</small>
            </span>
          </Link>
        </div>

        <nav className="topbar-nav">
          <NavLink to="/dashboard" className="nav-link">
            Dashboard
          </NavLink>
          <button type="button" className="ghost-button" onClick={logout}>
            <LogOut size={16} />
            Logout
          </button>
        </nav>
      </header>

      <main className="page-shell">
        <div className="page-shell-header app-overview-card">
          <div>
            <p className="eyebrow">{routeLabel(location.pathname)}</p>
            <h1 className="shell-title">{user?.full_name || 'ScholarFlow AI'}</h1>
            <p className="muted-text shell-subtitle">{user?.email || 'Authenticated workspace'}</p>
          </div>
        </div>
        <Outlet />
      </main>
    </div>
  )
}
