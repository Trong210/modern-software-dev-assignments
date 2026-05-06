from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _normalize_non_empty_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return value

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


class NoteCreate(BaseModel):
    title: str = Field(max_length=200)
    content: str

    @field_validator("title", "content")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        normalized = _normalize_non_empty_string(value, "Note field")
        assert normalized is not None
        return normalized


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    comments: list["NoteCommentRead"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None

    @field_validator("title", "content")
    @classmethod
    def validate_text_fields(cls, value: str | None) -> str | None:
        return _normalize_non_empty_string(value, "Note field")


class ActionItemCreate(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        normalized = _normalize_non_empty_string(value, "description")
        assert normalized is not None
        return normalized


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return _normalize_non_empty_string(value, "description")


class NoteCommentCreate(BaseModel):
    body: str

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        normalized = _normalize_non_empty_string(value, "body")
        assert normalized is not None
        return normalized


class NoteCommentRead(BaseModel):
    id: int
    note_id: int
    body: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


