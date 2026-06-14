"""PDF parsing and text extraction service."""

import re
import shutil
from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import UploadFile

from app.core.config import settings


PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def validate_pdf_file(file: UploadFile) -> None:
    filename = file.filename or ""
    content_type = file.content_type or ""
    if not filename.lower().endswith(".pdf") or content_type not in PDF_CONTENT_TYPES:
        raise ValueError("Only PDF files are supported")


def save_pdf_file(file: UploadFile, user_id: int, project_id: int) -> tuple[str, str, int]:
    validate_pdf_file(file)

    upload_root = Path(settings.upload_dir).resolve()
    project_upload_dir = upload_root / f"user_{user_id}" / f"project_{project_id}"
    project_upload_dir.mkdir(parents=True, exist_ok=True)

    original_filename = file.filename or "document.pdf"
    safe_original_name = sanitize_filename(original_filename)
    stored_filename = f"{uuid4().hex}_{safe_original_name}"
    destination = project_upload_dir / stored_filename

    file.file.seek(0)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return stored_filename, str(destination), destination.stat().st_size


def extract_pdf_text(file_path: str) -> tuple[str, int]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("Stored PDF file was not found")

    text_parts: list[str] = []
    with fitz.open(path) as document:
        page_count = document.page_count
        for page in document:
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text.strip())

    extracted_text = "\n\n".join(part for part in text_parts if part)
    return extracted_text, page_count


def extract_pdf_pages_text(file_path: str) -> tuple[list[dict[str, int | str]], int]:
    """Extract text grouped by PDF page for chunk metadata."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError("Stored PDF file was not found")

    pages: list[dict[str, int | str]] = []
    with fitz.open(path) as document:
        page_count = document.page_count
        for page_index, page in enumerate(document, start=1):
            page_text = page.get_text("text")
            clean_text = page_text.strip() if page_text else ""
            if clean_text:
                pages.append({"page_number": page_index, "text": clean_text})

    return pages, page_count


def delete_pdf_file(file_path: str) -> None:
    path = Path(file_path)
    if path.exists():
        path.unlink()


def build_text_preview(text: str, limit: int = 500) -> str:
    preview = text.strip().replace("\r", " ")
    if len(preview) <= limit:
        return preview
    return f"{preview[:limit].rstrip()}..."


def sanitize_filename(filename: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return safe_name or "document.pdf"
