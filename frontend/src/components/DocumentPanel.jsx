import { FileText, RefreshCcw, Upload, WandSparkles, Trash2 } from 'lucide-react'
import { useState } from 'react'

import ConfirmDialog from './ui/ConfirmDialog'
import Alert from './ui/Alert'
import EmptyState from './ui/EmptyState'
import SectionHeader from './ui/SectionHeader'

function formatDate(value) {
  if (!value) {
    return 'Unknown date'
  }
  return new Date(value).toLocaleString()
}

export default function DocumentPanel({
  documents,
  onUpload,
  onProcess,
  onIndex,
  onDelete,
  loading,
}) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [actionError, setActionError] = useState('')
  const [actionId, setActionId] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)

  async function handleUpload(event) {
    event.preventDefault()
    setActionError('')
    if (!selectedFile) {
      setActionError('Select a PDF file before uploading.')
      return
    }

    setActionId('upload')
    const result = await onUpload(selectedFile)
    setActionId('')

    if (!result?.success) {
      setActionError(result?.message || 'Upload failed.')
      return
    }

    setSelectedFile(null)
    event.target.reset()
  }

  async function runAction(documentId, action) {
    setActionError('')
    setActionId(`${action}:${documentId}`)

    const handlers = {
      process: onProcess,
      index: onIndex,
      delete: onDelete,
    }

    const result = await handlers[action](documentId)
    setActionId('')

    if (!result?.success) {
      setActionError(result?.message || `Unable to ${action} document.`)
    }
  }

  return (
    <section className="panel stack-md">
      <SectionHeader
        eyebrow="Documents"
        title="Upload, process, and index PDFs"
        description="Move each paper from upload to indexed state before asking grounded questions."
        aside={loading ? <span className="status-pill muted">Refreshing</span> : null}
      />

      <form className="upload-form" onSubmit={handleUpload}>
        <label className="file-picker">
          <Upload size={16} />
          <span>{selectedFile ? selectedFile.name : 'Choose PDF'}</span>
          <input
            type="file"
            accept="application/pdf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />
        </label>
        <button type="submit" className="primary-button" disabled={actionId === 'upload'}>
          {actionId === 'upload' ? 'Uploading...' : 'Upload PDF'}
        </button>
      </form>

      <Alert message={actionError} title="Document action failed" />

      <div className="document-list stack-sm">
        {documents.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No documents yet"
            description="Upload a PDF to start extracting, indexing, and grounding your project context."
            compact
          />
        ) : (
          documents.map((document) => {
            const processBusy = actionId === `process:${document.id}`
            const indexBusy = actionId === `index:${document.id}`
            const deleteBusy = actionId === `delete:${document.id}`

            return (
              <article key={document.id} className="document-row document-card-row">
                <div className="stack-xs document-copy">
                  <h3>{document.original_filename}</h3>
                  <p>
                    Status: <strong>{document.status}</strong>
                    {document.page_count ? ` | ${document.page_count} pages` : ''}
                  </p>
                  <small>Added {formatDate(document.created_at)}</small>
                </div>

                <div className="inline-actions action-wrap">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => runAction(document.id, 'process')}
                    disabled={processBusy || deleteBusy}
                  >
                    <RefreshCcw size={14} />
                    {processBusy ? 'Processing...' : 'Process'}
                  </button>
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => runAction(document.id, 'index')}
                    disabled={indexBusy || deleteBusy}
                  >
                    <WandSparkles size={14} />
                    {indexBusy ? 'Indexing...' : 'Index'}
                  </button>
                  <button
                    type="button"
                    className="danger-button"
                    onClick={() => setPendingDelete(document)}
                    disabled={deleteBusy}
                  >
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
              </article>
            )
          })
        )}
      </div>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete document?"
        description={pendingDelete ? `This will remove ${pendingDelete.original_filename} and its indexed vectors.` : ''}
        confirmLabel="Delete document"
        busy={pendingDelete ? actionId === `delete:${pendingDelete.id}` : false}
        onCancel={() => setPendingDelete(null)}
        onConfirm={async () => {
          if (!pendingDelete) {
            return
          }
          await runAction(pendingDelete.id, 'delete')
          setPendingDelete(null)
        }}
      />
    </section>
  )
}
