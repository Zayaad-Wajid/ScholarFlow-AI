"""Semantic retrieval API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import ResearchProject, User
from app.db.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievalResult,
    WebSearchRequest,
    WebSearchResponse,
    WebSearchResult,
)
from app.db.session import get_db

router = APIRouter()


def _get_project_or_404(db: Session, project_id: int, current_user: User) -> ResearchProject:
    project = db.scalar(
        select(ResearchProject).where(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id,
        )
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research project not found",
        )
    return project


@router.post("/retrieve", response_model=RetrievalResponse)
def retrieve_chunks(
    payload: RetrievalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RetrievalResponse:
    from app.services.chroma_service import ChromaServiceError, similarity_search
    from app.services.embedding_service import embed_text

    _get_project_or_404(db, payload.project_id, current_user)

    query_text = payload.query.strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )

    try:
        query_embedding = embed_text(query_text)
        hits = similarity_search(
            user_id=current_user.id,
            project_id=payload.project_id,
            query_embedding=query_embedding,
            top_k=payload.top_k,
            query_text=query_text,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ChromaServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve relevant chunks",
        ) from exc

    if not hits:
        return RetrievalResponse(query=query_text, results=[])

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

    return RetrievalResponse(query=query_text, results=results)


@router.post("/web", response_model=WebSearchResponse)
def web_search(
    payload: WebSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WebSearchResponse:
    from app.services.search_service import ExternalSearchError, tavily_search

    _get_project_or_404(db, payload.project_id, current_user)

    query_text = payload.query.strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )

    try:
        hits = tavily_search(
            query_text,
            max_results=payload.max_results,
            search_depth=payload.search_depth,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ExternalSearchError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run web search",
        ) from exc

    results = [
        WebSearchResult(
            title=result["title"],
            url=result["url"],
            snippet=result.get("snippet"),
            score=result.get("score"),
            source_name=result.get("source_name"),
            published_date=result.get("published_date"),
        )
        for result in hits
    ]

    return WebSearchResponse(query=query_text, results=results)
