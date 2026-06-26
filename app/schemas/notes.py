import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str | None = Field(max_length=255)
    content: str


class CreateSuccess(BaseModel):
    doc_id: str | None


class NoteOut(BaseModel):
    doc_id: str
    title: str
    content: str
    summary: str | None
    tags: list | None
    created_at: datetime.datetime


class NotePreAiDTO(BaseModel):
    doc_id: str
    title: str | None
    content: str
    created_at: datetime.datetime


class SummaryResponse(BaseModel):
    summary: str


class NotePostAiDTO(BaseModel):
    doc_id: str
    title: str
    content: str
    summary: str | None = None
    tags: list | None = None
    embedding: list | None = None
    created_at: datetime.datetime


class NoteUpdatePayload(BaseModel):
    note_id: str
    title: str | None = None
    content: str | None = None


class NoteListResponse(BaseModel):
    count: int
    notes: list[NotePostAiDTO]
