"""Request and response schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    email: str
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    topic: str | None = Field(default=None, max_length=255)
    status: str = Field(default="active", max_length=50)


class ResearchProjectCreate(ResearchProjectBase):
    status: str = Field(default="active", max_length=50)


class ResearchProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    topic: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=50)


class ResearchProjectResponse(ResearchProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


ResearchProjectRead = ResearchProjectResponse


class ResearchProjectListResponse(BaseModel):
    projects: list[ResearchProjectResponse]
    count: int


class ResearchStartRequest(BaseModel):
    project_id: int
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ResearchStartResponse(BaseModel):
    research_plan: dict[str, Any]
    answer: str
    critique: str
    citations: list[dict[str, Any]]
    sources_used: int


class DeleteResponse(BaseModel):
    message: str


class DocumentBase(BaseModel):
    user_id: int
    project_id: int
    filename: str
    original_filename: str
    file_path: str
    file_type: str
    file_size: int | None = None
    status: str = "uploaded"
    page_count: int | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


DocumentRead = DocumentResponse


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    count: int


class DocumentProcessResponse(BaseModel):
    document_id: int
    status: str
    page_count: int | None
    extracted_text_preview: str


class DocumentIndexResponse(BaseModel):
    document_id: int
    indexed_chunks: int
    collection_name: str
    status: str


class RetrievalRequest(BaseModel):
    project_id: int
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievalResult(BaseModel):
    document_id: int
    chunk_id: str
    page_number: int | None = None
    score: float
    chunk_text: str


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]


class WebSearchRequest(BaseModel):
    project_id: int
    query: str = Field(min_length=1)
    max_results: int = Field(default=5, ge=1, le=10)
    search_depth: str = Field(default="advanced", pattern="^(basic|advanced)$")


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str | None = None
    score: float | None = None
    source_name: str | None = None
    published_date: str | None = None


class WebSearchResponse(BaseModel):
    query: str
    results: list[WebSearchResult]


class SourceBase(BaseModel):
    project_id: int
    document_id: int | None = None
    title: str
    url: str | None = None
    source_type: str
    metadata_json: dict[str, Any] | None = None


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageBase(BaseModel):
    project_id: int
    role: str
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageRead(ChatMessageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatAskRequest(BaseModel):
    project_id: int
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatSource(BaseModel):
    document_id: int
    chunk_id: str
    page_number: int | None = None
    similarity_score: float
    document_name: str | None = None


class ChatAskResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    retrieval_metadata: dict[str, Any]


class ReportType(str, Enum):
    SUMMARY = "summary"
    LITERATURE_REVIEW = "literature_review"
    KEY_FINDINGS = "key_findings"


class ReportBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    report_type: ReportType
    topic: str = Field(min_length=1, max_length=255)
    content: str
    status: str = Field(default="completed", max_length=50)


class ReportCreate(ReportBase):
    project_id: int


class ReportGenerateRequest(BaseModel):
    project_id: int
    report_type: ReportType
    topic: str | None = Field(default=None, min_length=1, max_length=255)
    top_k: int = Field(default=8, ge=1, le=20)


class ReportCreateRequest(ReportGenerateRequest):
    pass


class ReportResponse(ReportBase):
    id: int
    user_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


ReportRead = ReportResponse


class ReportListResponse(BaseModel):
    reports: list[ReportResponse]
    count: int
