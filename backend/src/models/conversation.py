"""Conversation SQLModel for database table and ORM operations."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Conversation(SQLModel, table=True):
    """Conversation database model representing a chat thread.

    Attributes:
        id: UUID primary key, auto-generated
        user_id: Owner of the conversation (indexed for multi-user queries)
        title: Optional conversation title (auto-generated from first message if None)
        created_at: Timestamp when conversation was created (auto-generated)
        updated_at: Timestamp when conversation was last modified (auto-updated)
    """
    __tablename__ = "conversations"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # User ownership (indexed for fast user-scoped queries)
    user_id: str = Field(index=True, nullable=False)

    # Conversation metadata
    title: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
