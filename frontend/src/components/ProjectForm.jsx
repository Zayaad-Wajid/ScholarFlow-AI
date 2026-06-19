import { useState } from 'react'

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
    <form className="panel stack-sm" onSubmit={handleSubmit}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">New project</p>
          <h2>Create research project</h2>
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
          rows="4"
          value={form.description}
          onChange={handleChange}
          placeholder="Capture the scope, intended papers, or expected questions."
        />
      </label>

      {error ? <p className="form-error">{error}</p> : null}

      <button type="submit" className="primary-button" disabled={busy}>
        {busy ? 'Creating...' : 'Create project'}
      </button>
    </form>
  )
}
