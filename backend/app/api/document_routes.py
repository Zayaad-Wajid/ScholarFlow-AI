"""Document upload and management API routes."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import Document, ResearchProject, User
from app.db.schemas import (
    DeleteResponse,
    DocumentIndexResponse,
    DocumentListResponse,
    DocumentProcessResponse,
    DocumentResponse,
)
from app.db.session import get_db
from app.services.pdf_service import (
    build_text_preview,
    delete_pdf_file,
    extract_pdf_pages_text,
    extract_pdf_text,
    save_pdf_file,
)

router = APIRouter()


def get_project_or_404(
    project_id: int,
    current_user: User,
    db: Session,
) -> ResearchProject:
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


def get_document_or_404(
    document_id: int,
    current_user: User,
    db: Session,
) -> Document:
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    get_project_or_404(project_id, current_user, db)

    try:
        filename, file_path, file_size = save_pdf_file(
            file=file,
            user_id=current_user.id,
            project_id=project_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save PDF file",
        ) from exc

    document = Document(
        user_id=current_user.id,
        project_id=project_id,
        filename=filename,
        original_filename=file.filename or filename,
        file_path=file_path,
        file_type=file.content_type or "application/pdf",
        content_type=file.content_type,
        file_size=file_size,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/project/{project_id}", response_model=DocumentListResponse)
def list_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    get_project_or_404(project_id, current_user, db)
    documents = db.scalars(
        select(Document)
        .where(
            Document.project_id == project_id,
            Document.user_id == current_user.id,
        )
        .order_by(desc(Document.created_at))
    ).all()
    return DocumentListResponse(documents=documents, count=len(documents))


@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    return get_document_or_404(document_id, current_user, db)


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
def process_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentProcessResponse:
    document = get_document_or_404(document_id, current_user, db)

    try:
        extracted_text, page_count = extract_pdf_text(document.file_path)
    except Exception as exc:
        document.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process PDF",
        ) from exc

    document.extracted_text = extracted_text
    document.page_count = page_count
    document.status = "processed"
    db.commit()
    db.refresh(document)

    return DocumentProcessResponse(
        document_id=document.id,
        status=document.status,
        page_count=document.page_count,
        extracted_text_preview=build_text_preview(document.extracted_text or ""),
    )


@router.post("/{document_id}/index", response_model=DocumentIndexResponse)
def index_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentIndexResponse:
    from app.services.chroma_service import (
        ChromaServiceError,
        add_documents,
        has_document_vectors,
    )
    from app.services.embedding_service import build_document_chunks, embed_texts

    document = get_document_or_404(document_id, current_user, db)

    if document.status not in {"processed", "indexed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document must be processed before indexing",
        )

    try:
        if has_document_vectors(current_user.id, document.project_id, document.id):
            document.status = "indexed"
            db.commit()
            return DocumentIndexResponse(
                document_id=document.id,
                indexed_chunks=0,
                collection_name=f"user_{current_user.id}_project_{document.project_id}",
                status=document.status,
            )

        pages, _ = extract_pdf_pages_text(document.file_path)
        chunks = build_document_chunks(pages=pages, document_id=document.id)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chunks available for indexing",
            )

        chunk_texts = [str(chunk["chunk_text"]) for chunk in chunks]
        embeddings = embed_texts(chunk_texts)
        if not embeddings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing embeddings for indexing",
            )
        if len(embeddings) != len(chunks):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing embeddings for one or more chunks",
            )

        indexed_chunks = add_documents(
            user_id=current_user.id,
            project_id=document.project_id,
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings,
        )
    except ChromaServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to index document in ChromaDB",
        ) from exc

    document.status = "indexed"
    db.commit()
    return DocumentIndexResponse(
        document_id=document.id,
        indexed_chunks=indexed_chunks,
        collection_name=f"user_{current_user.id}_project_{document.project_id}",
        status=document.status,
    )


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeleteResponse:
    from app.services.chroma_service import ChromaServiceError, delete_document_vectors

    document = get_document_or_404(document_id, current_user, db)

    try:
        delete_document_vectors(current_user.id, document.project_id, document.id)
        delete_pdf_file(document.file_path)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete PDF file",
        ) from exc
    except ChromaServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document vectors",
        ) from exc

    db.delete(document)
    db.commit()
    return DeleteResponse(message="Document deleted successfully")
