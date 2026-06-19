import { ArrowLeft, FileSearch } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'

import Alert from '../components/ui/Alert'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import { getApiError, reportApi } from '../services/api'

function formatDate(value) {
  if (!value) {
    return 'Unknown date'
  }
  return new Date(value).toLocaleString()
}

export default function ReportDetail() {
  const { reportId } = useParams()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadReport() {
      setLoading(true)
      setError('')
      try {
        const response = await reportApi.get(reportId)
        if (!cancelled) {
          setReport(response.data)
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(getApiError(loadError, 'Unable to load report.'))
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadReport()

    return () => {
      cancelled = true
    }
  }, [reportId])

  if (loading) {
    return <LoadingState message="Loading report..." />
  }

  if (error) {
    return <Alert message={error} title="Report could not be loaded" />
  }

  if (!report) {
    return (
      <EmptyState
        icon={FileSearch}
        title="No report selected"
        description="Open a saved report from a project workspace to review it here."
      />
    )
  }

  return (
    <section className="panel stack-lg report-detail-panel panel-elevated">
      <div className="stack-md">
        <Link className="text-link back-link" to={`/projects/${report.project_id}`}>
          <ArrowLeft size={16} />
          Back to workspace
        </Link>

        <div className="report-hero">
          <div className="stack-sm report-hero-copy">
            <div>
              <p className="eyebrow">Saved report</p>
              <h2>{report.title}</h2>
              <p className="muted-text">{report.topic}</p>
            </div>
          </div>

          <div className="report-hero-meta stack-sm align-end report-meta-block">
            <span className="status-pill status-pill-strong">{report.report_type.replace('_', ' ')}</span>
            <small>{formatDate(report.created_at)}</small>
          </div>
        </div>
      </div>

      <article className="markdown-body report-body report-reading-surface">
        <ReactMarkdown>{report.content}</ReactMarkdown>
      </article>
    </section>
  )
}
