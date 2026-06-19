import { AlertCircle } from 'lucide-react'

export default function Alert({ message, title = 'Something went wrong' }) {
  if (!message) {
    return null
  }

  return (
    <div className="ui-alert" role="alert">
      <AlertCircle size={18} />
      <div>
        <strong>{title}</strong>
        <p>{message}</p>
      </div>
    </div>
  )
}
