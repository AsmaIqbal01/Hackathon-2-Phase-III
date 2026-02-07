"""Message SQLModel for database table and ORM operations."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Index
from datetime import datetime
from uuid import UUID, uuid4


class Message(SQLModel, table=True):
    """Message database model representing an individual message in a conversation.

    Attributes:
        id: UUID primary key, auto-generated
        conversation_id: Foreign key to conversations table (indexed)
        role: Message role - "user", "assistant", or "system"
        content: Message text content (required)
        message_metadata: Additional metadata (tool calls, confirmations, etc.) stored as JSON
        created_at: Timestamp when message was created (auto-generated)
    """
    __tablename__ = "messages"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to conversation (indexed for fast conversation queries)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, nullable=False)

    # Message content
    role: str = Field(max_length=50, nullable=False)  # "user" | "assistant" | "system"
    content: str = Field(nullable=False)  # Message text

    # Metadata stored as JSON (tool calls, confirmations, etc.)
    # Note: field name is 'message_metadata' to avoid conflict with SQLModel's reserved 'metadata'
    message_metadata: dict = Field(default={}, sa_column=Column(JSON))

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Composite index for conversation_id + created_at (common query pattern)
    __table_args__ = (
        Index("idx_messages_conversation", "conversation_id", "created_at"),
    )
