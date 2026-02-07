"""Pydantic schemas for task request/response validation.

These schemas define the API contract for task-related endpoints,
ensuring type safety and automatic validation.
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    """Schema for creating a new task.

    Attributes:
        title: Task title (required, non-empty, max 255 chars)
        description: Optional detailed description (max 5000 chars)
        status: Task status (defaults to 'todo')
        priority: Task priority (defaults to 'medium')
        tags: List of tags (defaults to empty list, duplicates removed)
    """
    title: str = Field(
        ...,
        description="Task title",
        min_length=1,
        max_length=255,
        examples=["Complete backend API implementation"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed task description",
        max_length=5000,
        examples=["Implement FastAPI endpoints with SQLModel integration"]
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current task status",
        examples=["todo"]
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level",
        examples=["medium"]
    )
    tags: list[str] = Field(
        default_factory=list,
        description="List of tags for categorization",
        examples=[["backend", "api", "phase-ii"]]
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate title is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description length and strip whitespace."""
        if v is None:
            return None
        if len(v) > 5000:
            raise ValueError("Description cannot exceed 5000 characters")
        return v.strip() if v.strip() else None

    @field_validator("tags")
    @classmethod
    def deduplicate_tags(cls, v: list[str]) -> list[str]:
        """Remove duplicate tags while preserving order."""
        if not v:
            return []
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in v:
            tag_lower = tag.lower().strip()
            if tag_lower and tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag_lower)
        return unique_tags


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (PATCH semantics).

    All fields are optional to support partial updates.
    Only provided fields will be updated.

    Attributes:
        title: Optional new task title
        description: Optional new description (null to clear)
        status: Optional new status
        priority: Optional new priority
        tags: Optional new tags list (replaces existing, not merged)
    """
    title: Optional[str] = Field(
        default=None,
        description="New task title",
        min_length=1,
        max_length=255,
        examples=["Updated task title"]
    )
    description: Optional[str] = Field(
        default=None,
        description="New task description (null to clear)",
        max_length=5000,
        examples=["Updated description"]
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="New task status",
        examples=["in-progress"]
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="New task priority",
        examples=["high"]
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="New tags list (replaces existing)",
        examples=[["backend", "urgent"]]
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate title is not empty if provided."""
        if v is None:
            return None
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate description length if provided."""
        if v is None:
            return None
        if len(v) > 5000:
            raise ValueError("Description cannot exceed 5000 characters")
        return v.strip() if v.strip() else None

    @field_validator("tags")
    @classmethod
    def deduplicate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Remove duplicate tags if provided."""
        if v is None:
            return None
        if not v:
            return []
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in v:
            tag_lower = tag.lower().strip()
            if tag_lower and tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag_lower)
        return unique_tags


class TaskResponse(BaseModel):
    """Schema for task responses.

    Represents a complete task object returned from the API.
    Includes all task fields and metadata.

    Attributes:
        id: Unique task identifier
        user_id: Owner of the task
        title: Task title
        description: Optional task description
        status: Current task status
        priority: Task priority level
        tags: List of tags
        created_at: When task was created
        updated_at: When task was last modified
    """
    id: UUID = Field(
        ...,
        description="Unique task identifier"
    )
    user_id: str = Field(
        ...,
        description="Owner of the task"
    )
    title: str = Field(
        ...,
        description="Task title"
    )
    description: Optional[str] = Field(
        default=None,
        description="Task description"
    )
    status: TaskStatus = Field(
        ...,
        description="Current task status"
    )
    priority: TaskPriority = Field(
        ...,
        description="Task priority level"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="List of tags"
    )
    created_at: datetime = Field(
        ...,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Last modification timestamp"
    )

    class Config:
        """Pydantic configuration for ORM compatibility."""
        from_attributes = True  # Enable ORM mode for SQLModel integration
        json_schema_extra = {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "user123",
                    "title": "Complete backend API",
                    "description": "Implement all FastAPI endpoints",
                    "status": "in-progress",
                    "priority": "high",
                    "tags": ["backend", "api"],
                    "created_at": "2024-01-24T10:30:00Z",
                    "updated_at": "2024-01-24T15:45:00Z"
                }
            ]
        }
