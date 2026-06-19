"""Report generation service for grounded project reports."""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.prompts import REPORT_SYSTEM_PROMPT, build_report_user_prompt
from app.db.models import Document, Report, ResearchProject, User
from app.db.schemas import ReportGenerateRequest, ReportType
from app.services.chroma_service import ChromaServiceError, similarity_search
from app.services.embedding_service import embed_text
from app.services.gemini_service import GeminiServiceError, generate_answer


class ReportServiceError(Exception):
    """Raised when report generation fails unexpectedly."""


class ReportNotFoundError(ReportServiceError):
    """Raised when a report or project cannot be found for the user."""


class ReportValidationError(ReportServiceError):
    """Raised when report generation prerequisites are not met."""


_REPORT_TITLE_PREFIX = {
    ReportType.SUMMARY: "Research Summary",
    ReportType.LITERATURE_REVIEW: "Literature Review",
    ReportType.KEY_FINDINGS: "Key Findings Report",
}

_MAX_CONTEXT_CHARS = 14000
_MAX_FALLBACK_DOCUMENTS = 3


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _get_project_or_404(db: Session, project_id: int, current_user: User) -> ResearchProject:
    project = db.scalar(
        select(ResearchProject).where(
            ResearchProject.id == project_id,
            ResearchProject.user_id == current_user.id,
        )
    )
    if project is None:
        raise ReportNotFoundError("Research project not found")
    return project


def _get_report_or_404(db: Session, report_id: int, current_user: User) -> Report:
    report = db.scalar(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )
    if report is None:
        raise ReportNotFoundError("Report not found")
    return report


def _get_indexed_documents(db: Session, project_id: int, current_user: User) -> list[Document]:
    return db.scalars(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.user_id == current_user.id,
            Document.status == "indexed",
        )
        .order_by(desc(Document.created_at))
    ).all()


def _resolve_topic(project: ResearchProject, requested_topic: str | None) -> str:
    topic = (requested_topic or project.topic or project.title).strip()
    if not topic:
        raise ReportValidationError("A topic is required to generate a report")
    return topic


def _resolve_title(report_type: ReportType, topic: str) -> str:
    return f"{_REPORT_TITLE_PREFIX[report_type]} on {topic}"


def _build_sources_used(
    hits: list[dict[str, Any]],
    document_name_by_id: dict[int, str],
) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []

    for hit in hits:
        document_id = hit.get("document_id")
        document_name = document_name_by_id.get(int(document_id)) if document_id is not None else None
        page_number = hit.get("page_number")
        chunk_id = hit.get("chunk_id")
        parts = [
            part
            for part in [
                document_name,
                f"page {page_number}" if page_number is not None else None,
                str(chunk_id) if chunk_id else None,
            ]
            if part
        ]
        if not parts:
            continue
        label = " | ".join(parts)
        if label not in seen:
            seen.add(label)
            sources.append(label)

    return sources


def _build_retrieval_context(
    hits: list[dict[str, Any]],
    document_name_by_id: dict[int, str],
) -> str:
    context_parts: list[str] = []

    for index, hit in enumerate(hits, start=1):
        chunk_text = _normalize_text(str(hit.get("chunk_text") or ""))
        if not chunk_text:
            continue

        document_id = hit.get("document_id")
        document_name = document_name_by_id.get(int(document_id)) if document_id is not None else "Unknown document"
        page_number = hit.get("page_number")
        chunk_id = hit.get("chunk_id") or f"chunk_{index}"

        header = f"[Source {index} | {document_name} | {chunk_id}"
        if page_number is not None:
            header += f" | page {page_number}"
        header += "]"

        context_parts.append(f"{header}\n{chunk_text}")

    return "\n\n".join(context_parts)[:_MAX_CONTEXT_CHARS]


def _build_document_fallback(documents: list[Document]) -> tuple[str, list[str]]:
    parts: list[str] = []
    sources: list[str] = []

    for index, document in enumerate(documents[:_MAX_FALLBACK_DOCUMENTS], start=1):
        extracted_text = _normalize_text(document.extracted_text or "")
        if not extracted_text:
            continue

        excerpt = extracted_text[:2500]
        parts.append(f"[Document {index} | {document.original_filename}]\n{excerpt}")
        sources.append(document.original_filename)

    return "\n\n".join(parts)[:_MAX_CONTEXT_CHARS], sources


def _gather_project_context(
    db: Session,
    current_user: User,
    project: ResearchProject,
    topic: str,
    top_k: int,
) -> dict[str, Any]:
    indexed_documents = _get_indexed_documents(db=db, project_id=project.id, current_user=current_user)
    if not indexed_documents:
        raise ReportValidationError("No indexed documents found for this project")

    document_name_by_id = {document.id: document.original_filename for document in indexed_documents}

    try:
        query_embedding = embed_text(topic)
        hits = similarity_search(
            user_id=current_user.id,
            project_id=project.id,
            query_embedding=query_embedding,
            top_k=top_k,
            query_text=topic,
        )
    except (ValueError, ChromaServiceError) as exc:
        raise ReportServiceError(str(exc)) from exc

    context = _build_retrieval_context(hits=hits, document_name_by_id=document_name_by_id)
    sources = _build_sources_used(hits=hits, document_name_by_id=document_name_by_id)

    if context:
        return {
            "context": context,
            "sources": sources,
            "retrieved_count": len(hits),
        }

    fallback_context, fallback_sources = _build_document_fallback(indexed_documents)
    if fallback_context:
        return {
            "context": fallback_context,
            "sources": fallback_sources,
            "retrieved_count": 0,
        }

    raise ReportValidationError("No usable project context found for report generation")


def generate_project_report(
    db: Session,
    current_user: User,
    payload: ReportGenerateRequest,
) -> Report:
    project = _get_project_or_404(db=db, project_id=payload.project_id, current_user=current_user)
    topic = _resolve_topic(project=project, requested_topic=payload.topic)
    context_bundle = _gather_project_context(
        db=db,
        current_user=current_user,
        project=project,
        topic=topic,
        top_k=payload.top_k,
    )

    try:
        content = generate_answer(
            system_prompt=REPORT_SYSTEM_PROMPT,
            user_prompt=build_report_user_prompt(
                report_type=payload.report_type.value,
                project_title=project.title,
                topic=topic,
                context=context_bundle["context"],
                sources=context_bundle["sources"],
            ),
            temperature=0.2,
        )
    except GeminiServiceError as exc:
        raise ReportServiceError(str(exc)) from exc

    report = Report(
        user_id=current_user.id,
        project_id=project.id,
        title=_resolve_title(payload.report_type, topic),
        report_type=payload.report_type.value,
        topic=topic,
        content=content,
        status="completed",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_project_reports(db: Session, current_user: User, project_id: int) -> list[Report]:
    _get_project_or_404(db=db, project_id=project_id, current_user=current_user)
    return db.scalars(
        select(Report)
        .where(
            Report.project_id == project_id,
            Report.user_id == current_user.id,
        )
        .order_by(desc(Report.created_at))
    ).all()


def get_report(db: Session, current_user: User, report_id: int) -> Report:
    return _get_report_or_404(db=db, report_id=report_id, current_user=current_user)


def delete_report(db: Session, current_user: User, report_id: int) -> None:
    report = _get_report_or_404(db=db, report_id=report_id, current_user=current_user)
    db.delete(report)
    db.commit()
