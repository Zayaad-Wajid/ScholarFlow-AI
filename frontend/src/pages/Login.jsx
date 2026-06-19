import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'

import Alert from '../components/ui/Alert'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

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
    <div className="auth-page">
      <form className="auth-card stack-md" onSubmit={handleSubmit}>
        <div>
          <p className="eyebrow">ScholarFlow AI</p>
          <h1>Sign in</h1>
          <p className="muted-text">Access your research projects and grounded reports.</p>
        </div>

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
          {busy ? 'Signing in...' : 'Sign in'}
        </button>

        <p className="muted-text">
          Need an account? <Link to="/register" className="text-link">Register here</Link>
        </p>
      </form>
    </div>
  )
}
