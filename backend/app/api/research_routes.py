
"""Research workflow API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import ResearchProject, User
from app.db.schemas import (
    DeleteResponse,
    ResearchProjectCreate,
    ResearchProjectListResponse,
    ResearchProjectResponse,
    ResearchStartRequest,
    ResearchStartResponse,
    ResearchProjectUpdate,
)
from app.db.session import get_db
from app.graphs.research_graph import run_research_workflow
from app.graphs.state import (
    ResearchWorkflowExecutionError,
    ResearchWorkflowNotFoundError,
    ResearchWorkflowValidationError,
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


@router.post(
    "/projects",
    response_model=ResearchProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ResearchProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    project = ResearchProject(
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
        topic=project_data.topic,
        status=project_data.status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=ResearchProjectListResponse)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProjectListResponse:
    projects = db.scalars(
        select(ResearchProject)
        .where(ResearchProject.user_id == current_user.id)
        .order_by(desc(ResearchProject.created_at))
    ).all()
    return ResearchProjectListResponse(projects=projects, count=len(projects))


@router.get("/projects/{project_id}", response_model=ResearchProjectResponse)
def read_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    return get_project_or_404(project_id, current_user, db)


@router.put("/projects/{project_id}", response_model=ResearchProjectResponse)
def update_project(
    project_id: int,
    project_data: ResearchProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchProject:
    project = get_project_or_404(project_id, current_user, db)
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", response_model=DeleteResponse)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeleteResponse:
    project = get_project_or_404(project_id, current_user, db)
    db.delete(project)
    db.commit()
    return DeleteResponse(message="Research project deleted successfully")


@router.post("/start", response_model=ResearchStartResponse)
def start_research(
    payload: ResearchStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchStartResponse:
    try:
        final_response = run_research_workflow(
            db=db,
            user_id=current_user.id,
            project_id=payload.project_id,
            query=payload.query,
            top_k=payload.top_k,
        )
    except ResearchWorkflowNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ResearchWorkflowValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ResearchWorkflowExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute research workflow",
        ) from exc

    return ResearchStartResponse(**final_response)
