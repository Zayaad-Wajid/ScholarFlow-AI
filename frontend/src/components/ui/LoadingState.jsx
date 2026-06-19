import { LoaderCircle } from 'lucide-react'

export default function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="empty-state loading-state">
      <LoaderCircle size={22} className="spin" />
      <span>{message}</span>
    </div>
  )
}
