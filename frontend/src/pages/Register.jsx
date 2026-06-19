import { Link, useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'

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

    navigate('/dashboard', { replace: true })
  }

  return (
    <div className="auth-page">
      <form className="auth-card stack-md" onSubmit={handleSubmit}>
        <div>
          <p className="eyebrow">ScholarFlow AI</p>
          <h1>Create account</h1>
          <p className="muted-text">Set up your workspace for PDF research and grounded reporting.</p>
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
          {busy ? 'Creating account...' : 'Create account'}
        </button>

        <p className="muted-text">
          Already registered? <Link to="/login" className="text-link">Sign in</Link>
        </p>
      </form>
    </div>
  )
}
