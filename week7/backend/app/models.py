from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    comments = relationship(
        "NoteComment",
        back_populates="note",
        cascade="all, delete-orphan",
        order_by="NoteComment.created_at",
    )


class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)


class NoteComment(Base, TimestampMixin):
    __tablename__ = "note_comments"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False, index=True)
    body = Column(Text, nullable=False)

    note = relationship("Note", back_populates="comments")


