"""API router registration."""

from fastapi import APIRouter

from app.api import (
    auth_routes,
    chat_routes,
    document_routes,
    report_routes,
    research_routes,
    search_routes,
)
from app.core.config import settings


api_router = APIRouter()


@api_router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }


api_router.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(research_routes.router, prefix="/research", tags=["research"])
api_router.include_router(document_routes.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
api_router.include_router(report_routes.router, prefix="/reports", tags=["reports"])
api_router.include_router(search_routes.router, prefix="/search", tags=["search"])
