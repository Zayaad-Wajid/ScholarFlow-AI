"""RAG orchestration service for grounded question answering."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.prompts import RAG_SYSTEM_PROMPT, build_rag_user_prompt
from app.db.models import Document, ResearchProject, User
from app.services.chroma_service import ChromaServiceError, similarity_search
from app.services.embedding_service import embed_text
from app.services.gemini_service import GeminiServiceError, generate_answer


class RagServiceError(Exception):
    """Raised when the RAG pipeline cannot complete."""


class RagNotFoundError(RagServiceError):
    """Raised when user-scoped project or required records are missing."""


class RagValidationError(RagServiceError):
    """Raised when request or pipeline preconditions are invalid."""


def _get_project_or_404(db: Session, project_id: int, current_user: User) -> ResearchProject:
    project = db.scalar(
        select(ResearchProject).where(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id,
        )
    )
    if project is None:
        raise RagNotFoundError("Research project not found")
    return project


def _get_indexed_documents(db: Session, project_id: int, current_user: User) -> list[Document]:
    return db.scalars(
        select(Document).where(
            Document.project_id == project_id,
            Document.user_id == current_user.id,
            Document.status == "indexed",
        )
    ).all()


def _build_context(hits: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for index, hit in enumerate(hits, start=1):
        chunk_id = str(hit.get("chunk_id") or f"chunk_{index}")
        page_number = hit.get("page_number")
        page_text = f"page {page_number}" if page_number is not None else "page unknown"
        chunk_text = str(hit.get("chunk_text") or "").strip()
        if not chunk_text:
            continue
        parts.append(f"[Source {index} | {chunk_id} | {page_text}]\n{chunk_text}")
    return "\n\n".join(parts)


def answer_question(
    db: Session,
    current_user: User,
    project_id: int,
    question: str,
    top_k: int = 5,
) -> dict[str, Any]:
    _get_project_or_404(db=db, project_id=project_id, current_user=current_user)

    indexed_documents = _get_indexed_documents(db=db, project_id=project_id, current_user=current_user)
    if not indexed_documents:
        raise RagValidationError("No indexed documents found for this project")

    normalized_question = question.strip()
    if not normalized_question:
        raise RagValidationError("Question cannot be empty")

    try:
        query_embedding = embed_text(normalized_question)
        hits = similarity_search(
            user_id=current_user.id,
            project_id=project_id,
            query_embedding=query_embedding,
            top_k=top_k,
            query_text=normalized_question,
        )
    except (ValueError, ChromaServiceError) as exc:
        raise RagServiceError(str(exc)) from exc

    if not hits:
        raise RagValidationError("No relevant chunks found for this question")

    context = _build_context(hits)
    if not context:
        raise RagValidationError("No usable retrieval context found")

    try:
        answer = generate_answer(
            system_prompt=RAG_SYSTEM_PROMPT,
            user_prompt=build_rag_user_prompt(context=context, question=normalized_question),
        )
    except GeminiServiceError as exc:
        raise RagServiceError(str(exc)) from exc

    doc_name_by_id = {document.id: document.original_filename for document in indexed_documents}
    sources: list[dict[str, Any]] = []
    for hit in hits:
        document_id = hit.get("document_id")
        chunk_id = hit.get("chunk_id")
        if document_id is None or chunk_id is None:
            continue

        source_item = {
            "document_id": int(document_id),
            "chunk_id": str(chunk_id),
            "page_number": int(hit["page_number"]) if hit.get("page_number") is not None else None,
            "similarity_score": float(hit.get("score") or 0.0),
        }
        document_name = doc_name_by_id.get(int(document_id))
        if document_name:
            source_item["document_name"] = document_name
        sources.append(source_item)

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_metadata": {
            "top_k": top_k,
            "retrieved_count": len(sources),
            "project_id": project_id,
        },
    }
