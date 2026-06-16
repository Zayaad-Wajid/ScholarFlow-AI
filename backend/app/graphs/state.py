"""State and workflow exceptions for the LangGraph research pipeline."""

from typing import Any, TypedDict


class ResearchPlan(TypedDict, total=False):
    objective: str
    key_topics: list[str]
    steps: list[str]


class CitationItem(TypedDict, total=False):
    document_id: int
    document_name: str
    chunk_id: str
    page_number: int | None
    similarity_score: float


class ResearchState(TypedDict, total=False):
    user_id: int
    project_id: int
    query: str
    retrieved_chunks: list[dict[str, Any]]
    research_plan: ResearchPlan
    generated_answer: str
    critique: str
    citations: list[CitationItem]
    final_response: dict[str, Any]
    metadata: dict[str, Any]


class ResearchWorkflowError(Exception):
    """Base exception for research workflow failures."""


class ResearchWorkflowNotFoundError(ResearchWorkflowError):
    """Raised when a required user-scoped resource does not exist."""


class ResearchWorkflowValidationError(ResearchWorkflowError):
    """Raised when workflow inputs or preconditions are invalid."""


class ResearchWorkflowExecutionError(ResearchWorkflowError):
    """Raised when workflow execution fails unexpectedly."""
