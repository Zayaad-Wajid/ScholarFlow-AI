"""Chat API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models import User
from app.db.schemas import ChatAskRequest, ChatAskResponse
from app.db.session import get_db
from app.services.rag_service import (
	RagNotFoundError,
	RagServiceError,
	RagValidationError,
	answer_question,
)


router = APIRouter()


@router.post("/ask", response_model=ChatAskResponse)
def ask_question(
	payload: ChatAskRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> ChatAskResponse:
	try:
		result = answer_question(
			db=db,
			current_user=current_user,
			project_id=payload.project_id,
			question=payload.question,
			top_k=payload.top_k,
		)
	except RagNotFoundError as exc:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=str(exc),
		) from exc
	except RagValidationError as exc:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(exc),
		) from exc
	except RagServiceError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=str(exc),
		) from exc
	except Exception as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to generate grounded answer",
		) from exc

	return ChatAskResponse(**result)
