import { ArrowLeft, FolderKanban, FileText, RefreshCw, ScrollText } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'

import ChatPanel from '../components/ChatPanel'
import DocumentPanel from '../components/DocumentPanel'
import ReportsPanel from '../components/ReportsPanel'
import Alert from '../components/ui/Alert'
import LoadingState from '../components/ui/LoadingState'
import SectionHeader from '../components/ui/SectionHeader'
import {
  chatApi,
  documentApi,
  getApiError,
  projectApi,
  reportApi,
} from '../services/api'

export default function ProjectWorkspace() {
  const { projectId } = useParams()
  const [project, setProject] = useState(null)
  const [documents, setDocuments] = useState([])
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  async function loadWorkspace(showLoading = false) {
    if (showLoading) {
      setLoading(true)
    } else {
      setRefreshing(true)
    }
    setError('')

    try {
      const [projectResponse, documentsResponse, reportsResponse] = await Promise.all([
        projectApi.get(projectId),
        documentApi.list(projectId),
        reportApi.list(projectId),
      ])

      setProject(projectResponse.data)
      setDocuments(documentsResponse.data.documents || [])
      setReports(reportsResponse.data.reports || [])
    } catch (loadError) {
      setError(getApiError(loadError, 'Unable to load project workspace.'))
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadWorkspace(true)
  }, [projectId])

  const workspaceStats = useMemo(() => ([
    { label: 'Topic', value: project?.topic || 'Not set', icon: FolderKanban },
    { label: 'Status', value: project?.status || 'Unknown', icon: ScrollText },
    { label: 'Documents', value: String(documents.length), icon: FileText },
    { label: 'Reports', value: String(reports.length), icon: ScrollText },
  ]), [project, documents.length, reports.length])

  async function handleUpload(file) {
    try {
      await documentApi.upload(projectId, file)
      await loadWorkspace()
      return { success: true }
    } catch (uploadError) {
      return { success: false, message: getApiError(uploadError, 'Upload failed.') }
    }
  }

  async function handleProcess(documentId) {
    try {
      await documentApi.process(documentId)
      await loadWorkspace()
      return { success: true }
    } catch (processError) {
      return { success: false, message: getApiError(processError, 'Processing failed.') }
    }
  }

  async function handleIndex(documentId) {
    try {
      await documentApi.index(documentId)
      await loadWorkspace()
      return { success: true }
    } catch (indexError) {
      return { success: false, message: getApiError(indexError, 'Indexing failed.') }
    }
  }

  async function handleDeleteDocument(documentId) {
    try {
      await documentApi.remove(documentId)
      await loadWorkspace()
      return { success: true }
    } catch (deleteError) {
      return { success: false, message: getApiError(deleteError, 'Delete failed.') }
    }
  }

  async function handleAsk(payload) {
    try {
      const response = await chatApi.ask(payload)
      return { success: true, data: response.data }
    } catch (askError) {
      return { success: false, message: getApiError(askError, 'Unable to ask question.') }
    }
  }

  async function handleGenerateReport(payload) {
    try {
      await reportApi.generate(payload)
      await loadWorkspace()
      return { success: true }
    } catch (reportError) {
      return {
        success: false,
        message: getApiError(reportError, 'Unable to generate report.'),
      }
    }
  }

  async function handleDeleteReport(reportId) {
    try {
      await reportApi.remove(reportId)
      await loadWorkspace()
      return { success: true }
    } catch (reportError) {
      return {
        success: false,
        message: getApiError(reportError, 'Unable to delete report.'),
      }
    }
  }

  if (loading) {
    return <LoadingState message="Loading workspace..." />
  }

  if (!project) {
    return <LoadingState message="Project not found." />
  }

  return (
    <div className="stack-lg">
      <section className="panel panel-elevated stack-md workspace-masthead">
        <div className="split-heading workspace-header">
          <div className="stack-sm workspace-heading-copy">
            <Link className="text-link back-link" to="/dashboard">
              <ArrowLeft size={16} />
              Back to dashboard
            </Link>
            <div>
              <p className="eyebrow">Project workspace</p>
              <h2>{project.title}</h2>
              <p className="muted-text">{project.description || 'No description provided.'}</p>
            </div>
          </div>

          <button type="button" className="secondary-button" onClick={() => loadWorkspace()}>
            <RefreshCw size={14} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        <Alert message={error} title="Workspace issue" />

        <div className="workspace-stats-grid">
          {workspaceStats.map(({ label, value, icon: Icon }) => (
            <div key={label} className="meta-card workspace-meta-card">
              <div className="workspace-meta-topline">
                <Icon size={15} />
                <span>{label}</span>
              </div>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      </section>

      <div className="workspace-grid polished-workspace-grid">
        <div className="stack-lg">
          <DocumentPanel
            documents={documents}
            onUpload={handleUpload}
            onProcess={handleProcess}
            onIndex={handleIndex}
            onDelete={handleDeleteDocument}
            loading={refreshing}
          />
          <ReportsPanel
            projectId={Number(projectId)}
            reports={reports}
            onGenerate={handleGenerateReport}
            onDelete={handleDeleteReport}
          />
        </div>

        <div className="stack-lg sticky-column">
          <section className="panel stack-sm workspace-summary-panel panel-tinted">
            <SectionHeader
              eyebrow="Workspace snapshot"
              title="Project context"
              description="Use indexed project documents to answer questions and generate production-ready report drafts."
            />
            <div className="source-row source-grid-row workspace-context-card">
              <FolderKanban size={16} />
              <div>
                <strong>{project.title}</strong>
                <p>{project.topic || 'Project topic will be inferred from your report or question.'}</p>
              </div>
            </div>
          </section>

          <ChatPanel projectId={Number(projectId)} onAsk={handleAsk} />
        </div>
      </div>
    </div>
  )
}
