import { useState } from 'react'
import { BriefcaseBusiness, Sparkles } from 'lucide-react'

const INITIAL_FORM = {
  title: '',
  topic: '',
  description: '',
}

export default function ProjectForm({ onSubmit, busy }) {
  const [form, setForm] = useState(INITIAL_FORM)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!form.title.trim()) {
      setError('Project title is required')
      return
    }

    const result = await onSubmit({
      title: form.title.trim(),
      topic: form.topic.trim(),
      description: form.description.trim(),
      status: 'active',
    })

    if (result?.success) {
      setForm(INITIAL_FORM)
      return
    }

    setError(result?.message || 'Unable to create project')
  }

  return (
    <form className="panel stack-md panel-tinted" onSubmit={handleSubmit}>
      <div className="panel-heading form-hero-heading">
        <div className="hero-icon-badge">
          <BriefcaseBusiness size={18} />
        </div>
        <div>
          <p className="eyebrow">New project</p>
          <h2>Create research workspace</h2>
          <p className="muted-text">Start a focused workspace for papers, questions, and polished deliverables.</p>
        </div>
      </div>

      <label className="field">
        <span>Title</span>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          placeholder="Phishing detection literature scan"
        />
      </label>

      <label className="field">
        <span>Topic</span>
        <input
          name="topic"
          value={form.topic}
          onChange={handleChange}
          placeholder="Transformer-based phishing detection"
        />
      </label>

      <label className="field">
        <span>Description</span>
        <textarea
          name="description"
          rows="5"
          value={form.description}
          onChange={handleChange}
          placeholder="Capture the scope, intended source set, or the questions this workspace should answer."
        />
      </label>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="form-footer-note">
        <Sparkles size={15} />
        <span>Projects become the anchor for uploads, grounded Q&A, Tavily research, and report generation.</span>
      </div>

      <button type="submit" className="primary-button" disabled={busy}>
        {busy ? 'Creating...' : 'Create project'}
      </button>
    </form>
  )
}
