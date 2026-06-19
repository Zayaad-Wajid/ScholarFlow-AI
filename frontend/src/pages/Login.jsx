import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { LockKeyhole, NotebookText, ShieldCheck, Sparkles } from 'lucide-react'

import heroImage from '../assets/hero.png'
import Alert from '../components/ui/Alert'
import { useAuth } from '../context/AuthContext'

const AUTH_POINTS = [
  'Grounded answers from indexed project documents',
  'Fast research workflows with Tavily and Gemini',
  'Saved reports and workspaces built for repeated use',
]

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (location.state?.email) {
      setEmail(location.state.email)
    }
  }, [location.state])

  const isDisabled = useMemo(() => !email.trim() || !password.trim() || busy, [email, password, busy])

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')

    const result = await login({ email, password })
    setBusy(false)

    if (!result.success) {
      setError(result.message)
      return
    }

    navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
  }

  return (
    <div className="auth-page auth-layout">
      <section className="auth-showcase" style={{ backgroundImage: `linear-gradient(180deg, rgba(3, 7, 18, 0.48), rgba(3, 7, 18, 0.7)), url(${heroImage})` }}>
        <div className="auth-showcase-inner">
          <div className="auth-brand-row">
            <span className="brand-glyph auth-brand-glyph">
              <NotebookText size={18} />
            </span>
            <div>
              <strong>ScholarFlow AI</strong>
              <p>Research orchestration for source-grounded academic work.</p>
            </div>
          </div>

          <div className="stack-md auth-copy-block">
            <p className="eyebrow auth-eyebrow">Research workspace</p>
            <h1>Sign in to continue your research workflow.</h1>
            <p>
              Move from uploaded papers to structured answers and polished reports in a focused, production-style workspace.
            </p>
          </div>

          <div className="auth-points">
            {AUTH_POINTS.map((point) => (
              <div key={point} className="auth-point-row">
                <ShieldCheck size={16} />
                <span>{point}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <form className="auth-card stack-md auth-form-panel" onSubmit={handleSubmit}>
        <div className="stack-sm">
          <div className="hero-icon-badge">
            <LockKeyhole size={18} />
          </div>
          <div>
            <p className="eyebrow">ScholarFlow AI</p>
            <h2>Sign in</h2>
            <p className="muted-text">Access your research projects, document context, and grounded reports.</p>
          </div>
        </div>

        <Alert
          message={location.state?.registered ? 'Account created successfully. Sign in to continue.' : ''}
          title="Ready to sign in"
        />

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            required
          />
        </label>

        <Alert message={error} title="Sign-in failed" />

        <button type="submit" className="primary-button" disabled={isDisabled}>
          <Sparkles size={16} />
          {busy ? 'Signing in...' : 'Sign in'}
        </button>

        <p className="muted-text auth-footer-copy">
          Need an account? <Link to="/register" className="text-link">Register here</Link>
        </p>
      </form>
    </div>
  )
}
