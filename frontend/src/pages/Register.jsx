import { Link, useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'
import { NotebookPen, Sparkles, UserRoundPlus, Waypoints } from 'lucide-react'

import heroImage from '../assets/hero.png'
import Alert from '../components/ui/Alert'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const isDisabled = useMemo(
    () => !form.email.trim() || !form.password.trim() || form.password.trim().length < 8 || busy,
    [form, busy],
  )

  function handleChange(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')

    if (form.password.trim().length < 8) {
      setBusy(false)
      setError('Password must be at least 8 characters long.')
      return
    }

    const result = await register(form)
    setBusy(false)

    if (!result.success) {
      setError(result.message)
      return
    }

    navigate('/login', {
      replace: true,
      state: {
        registered: true,
        email: form.email.trim(),
      },
    })
  }

  return (
    <div className="auth-page auth-layout">
      <section className="auth-showcase" style={{ backgroundImage: `linear-gradient(180deg, rgba(3, 7, 18, 0.42), rgba(3, 7, 18, 0.72)), url(${heroImage})` }}>
        <div className="auth-showcase-inner">
          <div className="auth-brand-row">
            <span className="brand-glyph auth-brand-glyph">
              <NotebookPen size={18} />
            </span>
            <div>
              <strong>ScholarFlow AI</strong>
              <p>Production-style research workspace for document-grounded analysis.</p>
            </div>
          </div>

          <div className="stack-md auth-copy-block">
            <p className="eyebrow auth-eyebrow">Create workspace</p>
            <h1>Set up an account for structured research work.</h1>
            <p>
              Build projects, upload papers, ask grounded questions, and generate publication-style outputs from one clean environment.
            </p>
          </div>

          <div className="auth-points">
            <div className="auth-point-row">
              <Waypoints size={16} />
              <span>Project-based organization for repeated research workflows</span>
            </div>
            <div className="auth-point-row">
              <Sparkles size={16} />
              <span>RAG answers, Tavily research, and Gemini-powered synthesis</span>
            </div>
            <div className="auth-point-row">
              <UserRoundPlus size={16} />
              <span>Personal workspace that persists reports, documents, and context</span>
            </div>
          </div>
        </div>
      </section>

      <form className="auth-card stack-md auth-form-panel" onSubmit={handleSubmit}>
        <div className="stack-sm">
          <div className="hero-icon-badge">
            <UserRoundPlus size={18} />
          </div>
          <div>
            <p className="eyebrow">ScholarFlow AI</p>
            <h2>Create account</h2>
            <p className="muted-text">Set up your workspace for PDF research and grounded reporting.</p>
          </div>
        </div>

        <label className="field">
          <span>Full name</span>
          <input
            name="full_name"
            value={form.full_name}
            onChange={handleChange}
            placeholder="Zayad Wajid"
          />
        </label>

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder="you@example.com"
            required
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder="At least 8 characters"
            required
          />
        </label>

        <Alert message={error} title="Registration failed" />

        <button type="submit" className="primary-button" disabled={isDisabled}>
          <Sparkles size={16} />
          {busy ? 'Creating account...' : 'Create account'}
        </button>

        <p className="muted-text auth-footer-copy">
          Already registered? <Link to="/login" className="text-link">Sign in</Link>
        </p>
      </form>
    </div>
  )
}
