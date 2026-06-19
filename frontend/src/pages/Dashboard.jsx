import { FolderOpen, Plus, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'

import ProjectForm from '../components/ProjectForm'
import Alert from '../components/ui/Alert'
import ConfirmDialog from '../components/ui/ConfirmDialog'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import SectionHeader from '../components/ui/SectionHeader'
import { getApiError, projectApi } from '../services/api'

function formatDate(value) {
  if (!value) {
    return 'Unknown date'
  }
  return new Date(value).toLocaleDateString()
}

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deletingId, setDeletingId] = useState('')

  async function loadProjects() {
    setLoading(true)
    setError('')

    try {
      const response = await projectApi.list()
      setProjects(response.data.projects || [])
    } catch (loadError) {
      setError(getApiError(loadError, 'Unable to load projects.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  async function handleCreateProject(payload) {
    setBusy(true)
    try {
      const response = await projectApi.create(payload)
      setProjects((current) => [response.data, ...current])
      return { success: true }
    } catch (createError) {
      return {
        success: false,
        message: getApiError(createError, 'Unable to create project.'),
      }
    } finally {
      setBusy(false)
    }
  }

  async function handleDeleteProject(projectId) {
    setDeletingId(String(projectId))
    try {
      await projectApi.delete(projectId)
      setProjects((current) => current.filter((project) => project.id !== projectId))
      setPendingDelete(null)
    } catch (deleteError) {
      setError(getApiError(deleteError, 'Unable to delete project.'))
    } finally {
      setDeletingId('')
    }
  }

  return (
    <div className="dashboard-grid">
      <ProjectForm onSubmit={handleCreateProject} busy={busy} />

      <section className="panel stack-md">
        <SectionHeader
          eyebrow="Projects"
          title="Research dashboard"
          description="Create and manage project workspaces for papers, RAG Q&A, and reports."
          aside={<span className="status-pill">{projects.length} total</span>}
        />

        <Alert message={error} title="Dashboard issue" />

        {loading ? (
          <LoadingState message="Loading projects..." />
        ) : projects.length === 0 ? (
          <EmptyState
            icon={Plus}
            title="No research projects yet"
            description="Create your first project to start uploading papers and generating grounded outputs."
          />
        ) : (
          <div className="card-grid">
            {projects.map((project) => (
              <article key={project.id} className="project-card stack-sm">
                <div className="card-header-row">
                  <div>
                    <h3>{project.title}</h3>
                    <p>{project.topic || 'No topic set'}</p>
                  </div>
                  <span className="status-pill">{project.status}</span>
                </div>

                <p className="muted-text">
                  {project.description || 'No project description yet.'}
                </p>

                <div className="meta-row">
                  <small>Created {formatDate(project.created_at)}</small>
                </div>

                <div className="inline-actions action-wrap">
                  <Link className="primary-button link-button" to={`/projects/${project.id}`}>
                    <FolderOpen size={16} />
                    Open workspace
                  </Link>
                  <button
                    type="button"
                    className="danger-button"
                    onClick={() => setPendingDelete(project)}
                  >
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete project?"
        description={pendingDelete ? `This will remove ${pendingDelete.title} and its related records.` : ''}
        confirmLabel="Delete project"
        busy={pendingDelete ? deletingId === String(pendingDelete.id) : false}
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && handleDeleteProject(pendingDelete.id)}
      />
    </div>
  )
}
