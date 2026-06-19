import { FileSearch, Sparkles, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'

import Alert from './ui/Alert'
import ConfirmDialog from './ui/ConfirmDialog'
import EmptyState from './ui/EmptyState'
import SectionHeader from './ui/SectionHeader'

function formatDate(value) {
  if (!value) {
    return 'Unknown date'
  }
  return new Date(value).toLocaleString()
}

export default function ReportsPanel({ projectId, reports, onGenerate, onDelete }) {
  const [topic, setTopic] = useState('')
  const [reportType, setReportType] = useState('summary')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    const result = await onGenerate({
      project_id: projectId,
      report_type: reportType,
      topic: topic.trim() || undefined,
      top_k: 8,
    })

    setLoading(false)
    if (!result?.success) {
      setError(result?.message || 'Unable to generate report.')
      return
    }

    setTopic('')
  }

  async function handleDelete(reportId) {
    setDeletingId(String(reportId))
    const result = await onDelete(reportId)
    setDeletingId('')
    if (!result?.success) {
      setError(result?.message || 'Unable to delete report.')
    }
  }

  return (
    <section className="panel stack-md">
      <SectionHeader
        eyebrow="Reports"
        title="Generate and review outputs"
        description="Create project summaries, literature reviews, and key findings from indexed context."
      />

      <form className="report-form report-form-grid" onSubmit={handleSubmit}>
        <label className="field">
          <span>Report type</span>
          <select value={reportType} onChange={(event) => setReportType(event.target.value)}>
            <option value="summary">Summary</option>
            <option value="literature_review">Literature Review</option>
            <option value="key_findings">Key Findings</option>
          </select>
        </label>

        <label className="field grow-field">
          <span>Topic override</span>
          <input
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            placeholder="Optional: refine the report topic"
          />
        </label>

        <button type="submit" className="primary-button" disabled={loading}>
          <Sparkles size={16} />
          {loading ? 'Generating...' : 'Generate report'}
        </button>
      </form>

      <Alert message={error} title="Report action failed" />

      <div className="stack-sm">
        {reports.length === 0 ? (
          <EmptyState
            icon={FileSearch}
            title="No reports generated yet"
            description="Generate a summary, literature review, or key findings report for this project."
            compact
          />
        ) : (
          reports.map((report) => (
            <article key={report.id} className="report-row report-card-row">
              <div className="stack-xs report-copy">
                <Link className="text-link report-title-link" to={`/reports/${report.id}`}>
                  {report.title}
                </Link>
                <p>
                  {report.report_type.replace('_', ' ')} | {report.topic}
                </p>
                <small>{formatDate(report.created_at)}</small>
              </div>

              <div className="inline-actions action-wrap">
                <Link className="secondary-button link-button subtle-link-button" to={`/reports/${report.id}`}>
                  Open
                </Link>
                <button
                  type="button"
                  className="danger-button"
                  disabled={deletingId === String(report.id)}
                  onClick={() => setPendingDelete(report)}
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete report?"
        description={pendingDelete ? `This will permanently remove ${pendingDelete.title}.` : ''}
        confirmLabel="Delete report"
        busy={pendingDelete ? deletingId === String(pendingDelete.id) : false}
        onCancel={() => setPendingDelete(null)}
        onConfirm={async () => {
          if (!pendingDelete) {
            return
          }
          await handleDelete(pendingDelete.id)
          setPendingDelete(null)
        }}
      />
    </section>
  )
}
