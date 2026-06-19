export default function SectionHeader({ eyebrow, title, description, aside = null }) {
  return (
    <div className="panel-heading split-heading">
      <div>
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <h2>{title}</h2>
        {description ? <p className="muted-text">{description}</p> : null}
      </div>
      {aside}
    </div>
  )
}
