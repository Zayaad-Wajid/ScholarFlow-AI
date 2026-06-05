"""Request and response schemas."""

from datetime import datetime
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


class ReportBase(BaseModel):
    project_id: int
    title: str
    content: str
    status: str = "draft"


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
