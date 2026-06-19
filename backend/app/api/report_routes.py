"""Report generation and retrieval API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User
from app.db.schemas import (
    DeleteResponse,
    ReportGenerateRequest,
    ReportListResponse,
    ReportResponse,
)
from app.db.session import get_db
from app.services.report_service import (
    ReportNotFoundError,
    ReportServiceError,
    ReportValidationError,
    delete_report,
    generate_project_report,
    get_report,
    list_project_reports,
)

router = APIRouter()


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(
    payload: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    try:
        report = generate_project_report(db=db, current_user=current_user, payload=payload)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ReportValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ReportServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report",
        ) from exc

    return ReportResponse.model_validate(report)


@router.get("/project/{project_id}", response_model=ReportListResponse)
def read_project_reports(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportListResponse:
    try:
        reports = list_project_reports(db=db, current_user=current_user, project_id=project_id)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ReportListResponse(
        reports=[ReportResponse.model_validate(report) for report in reports],
        count=len(reports),
    )


@router.get("/{report_id}", response_model=ReportResponse)
def read_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    try:
        report = get_report(db=db, current_user=current_user, report_id=report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ReportResponse.model_validate(report)


@router.delete("/{report_id}", response_model=DeleteResponse)
def remove_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeleteResponse:
    try:
        delete_report(db=db, current_user=current_user, report_id=report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return DeleteResponse(message="Report deleted successfully")
