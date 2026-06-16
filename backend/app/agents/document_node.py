"""Retrieval node for fetching relevant chunks from project documents."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document, ResearchProject
from app.graphs.state import (
	ResearchState,
	ResearchWorkflowNotFoundError,
	ResearchWorkflowValidationError,
)
from app.services.chroma_service import ChromaServiceError, similarity_search
from app.services.embedding_service import embed_text


def retrieval_node(state: ResearchState, db: Session) -> dict[str, object]:
	user_id = int(state.get("user_id", 0))
	project_id = int(state.get("project_id", 0))
	query = str(state.get("query", "")).strip()
	metadata = dict(state.get("metadata") or {})
	top_k = int(metadata.get("top_k", 5))

	if user_id <= 0 or project_id <= 0:
		raise ResearchWorkflowValidationError("Invalid user or project for retrieval")
	if not query:
		raise ResearchWorkflowValidationError("Query cannot be empty")

	project = db.scalar(
		select(ResearchProject).where(
			ResearchProject.id == project_id,
			ResearchProject.user_id == user_id,
		)
	)
	if project is None:
		raise ResearchWorkflowNotFoundError("Research project not found")

	indexed_documents = db.scalars(
		select(Document).where(
			Document.project_id == project_id,
			Document.user_id == user_id,
			Document.status == "indexed",
		)
	).all()
	if not indexed_documents:
		raise ResearchWorkflowValidationError("No indexed documents found for this project")

	try:
		query_embedding = embed_text(query)
		hits = similarity_search(
			user_id=user_id,
			project_id=project_id,
			query_embedding=query_embedding,
			top_k=top_k,
			query_text=query,
		)
	except (ValueError, ChromaServiceError) as exc:
		raise ResearchWorkflowValidationError(str(exc)) from exc

	if not hits:
		raise ResearchWorkflowValidationError("No relevant chunks found for this query")

	metadata["document_name_by_id"] = {
		document.id: document.original_filename for document in indexed_documents
	}
	metadata["retrieved_count"] = len(hits)

	return {
		"retrieved_chunks": hits,
		"metadata": metadata,
	}

