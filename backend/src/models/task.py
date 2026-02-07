"""Task SQLModel for database table and ORM operations."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Index
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    """Valid task status values."""
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Valid task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(SQLModel, table=True):
    """Task database model representing a todo item.

    Attributes:
        id: UUID primary key, auto-generated
        user_id: Owner of the task (indexed for multi-user queries)
        title: Task title (required, max 255 chars)
        description: Optional detailed description (max 5000 chars)
        status: Current task status (todo, in-progress, completed)
        priority: Task priority level (low, medium, high)
        tags: List of string tags for categorization (stored as JSON)
        created_at: Timestamp when task was created (auto-generated)
        updated_at: Timestamp when task was last modified (auto-updated)
    """
    __tablename__ = "tasks"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # User ownership (indexed for fast user-scoped queries)
    user_id: str = Field(index=True, nullable=False)

    # Task content
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=5000)

    # Task metadata
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)

    # Tags stored as JSON (compatible with both SQLite and PostgreSQL)
    tags: list[str] = Field(default=[], sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Composite index for user_id + status (common query pattern)
    __table_args__ = (
        Index("idx_tasks_user_status", "user_id", "status"),
    )
