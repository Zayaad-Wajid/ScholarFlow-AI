import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="empty-state stack-sm">
      <h2>Page not found</h2>
      <p className="muted-text">The page you requested does not exist in this workspace.</p>
      <Link className="primary-button link-button" to="/dashboard">
        Go to dashboard
      </Link>
    </div>
  )
}
