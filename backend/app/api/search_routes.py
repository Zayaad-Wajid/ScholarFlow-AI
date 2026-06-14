"""Semantic retrieval API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import ResearchProject, User
from app.db.schemas import RetrievalRequest, RetrievalResponse, RetrievalResult
from app.db.session import get_db
from app.services.chroma_service import similarity_search
from app.services.embedding_service import embed_text

router = APIRouter()


@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve_chunks(
    payload: RetrievalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RetrievalResponse:
    project = db.scalar(
        select(ResearchProject).where(
            ResearchProject.id == payload.project_id,
            ResearchProject.user_id == current_user.id,
        )
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research project not found",
        )

    try:
        query_embedding = embed_text(payload.query)
        hits = similarity_search(
            user_id=current_user.id,
            project_id=payload.project_id,
            query_embedding=query_embedding,
            top_k=payload.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve relevant chunks",
        ) from exc

    if not hits:
        return RetrievalResponse(query=payload.query, results=[])

    results = [
        RetrievalResult(
            document_id=int(hit["document_id"]),
            chunk_id=str(hit["chunk_id"]),
            page_number=int(hit["page_number"]) if hit.get("page_number") is not None else None,
            score=float(hit["score"] or 0.0),
            chunk_text=str(hit["chunk_text"]),
        )
        for hit in hits
        if hit.get("document_id") is not None and hit.get("chunk_id") is not None
    ]

    return RetrievalResponse(query=payload.query, results=results)
