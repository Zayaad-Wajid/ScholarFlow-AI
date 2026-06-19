import { MessageSquareQuote, Send } from 'lucide-react'
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

import Alert from './ui/Alert'
import EmptyState from './ui/EmptyState'
import SectionHeader from './ui/SectionHeader'

export default function ChatPanel({ projectId, onAsk }) {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [submittedQuestion, setSubmittedQuestion] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    const nextQuestion = question.trim()
    if (!nextQuestion) {
      setError('Enter a question before asking the assistant.')
      return
    }

    setLoading(true)
    setSubmittedQuestion(nextQuestion)
    const response = await onAsk({
      project_id: projectId,
      question: nextQuestion,
      top_k: 5,
    })
    setLoading(false)

    if (!response?.success) {
      setResult(null)
      setError(response?.message || 'Unable to get answer.')
      return
    }

    setResult(response.data)
  }

  return (
    <section className="panel stack-md">
      <SectionHeader
        eyebrow="RAG Q&A"
        title="Ask grounded questions"
        description="Answers are generated only from indexed project material."
      />

      <form className="stack-sm" onSubmit={handleSubmit}>
        <label className="field">
          <span>Question</span>
          <textarea
            rows="4"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What do the uploaded papers say about transformer-based phishing detection?"
          />
        </label>
        <Alert message={error} title="Question could not be answered" />
        <button type="submit" className="primary-button" disabled={loading}>
          <Send size={16} />
          {loading ? 'Generating answer...' : 'Ask question'}
        </button>
      </form>

      {loading ? (
        <div className="response-card stack-sm question-answer-shell">
          <p className="eyebrow">Working question</p>
          <p className="question-chip">{submittedQuestion}</p>
          <p className="muted-text">Searching indexed chunks and generating a grounded response...</p>
        </div>
      ) : null}

      {!loading && !result ? (
        <EmptyState
          icon={MessageSquareQuote}
          title="No answer yet"
          description="Process and index at least one document, then ask a specific project question here."
          compact
        />
      ) : null}

      {result ? (
        <div className="response-card stack-md question-answer-shell">
          <div className="stack-sm">
            <p className="eyebrow">Question</p>
            <p className="question-chip">{submittedQuestion}</p>
          </div>

          <div className="stack-sm">
            <p className="eyebrow">Answer</p>
            <div className="markdown-body">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
          </div>

          <div className="stack-sm">
            <h3>Supporting sources</h3>
            {result.sources?.length ? (
              result.sources.map((source) => (
                <div key={`${source.document_id}-${source.chunk_id}`} className="source-row source-grid-row">
                  <MessageSquareQuote size={16} />
                  <div>
                    <strong>{source.document_name || `Document ${source.document_id}`}</strong>
                    <p>
                      {source.chunk_id}
                      {source.page_number ? ` | page ${source.page_number}` : ''}
                      {source.similarity_score ? ` | score ${source.similarity_score.toFixed(2)}` : ''}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="muted-text">No source metadata returned.</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  )
}
