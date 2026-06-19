export default function EmptyState({ icon: Icon, title, description, compact = false, action = null }) {
  return (
    <div className={`empty-state ${compact ? 'compact-empty' : ''} stack-sm`}>
      {Icon ? <Icon size={18} /> : null}
      <strong>{title}</strong>
      {description ? <p className="muted-text">{description}</p> : null}
      {action}
    </div>
  )
}
