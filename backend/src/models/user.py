"""User model for authentication and user management."""
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """User entity for authentication and task ownership.

    Security notes:
    - password_hash stores bcrypt hash (never plain password)
    - email is normalized to lowercase and indexed for fast lookup
    - All timestamps are timezone-aware UTC

    Attributes:
        id: Unique identifier (UUID v4)
        email: User's email address (normalized lowercase, unique)
        password_hash: Bcrypt-hashed password (60 chars for bcrypt)
        is_active: Account status flag (for soft disable)
        created_at: Account creation timestamp (UTC)
        updated_at: Last profile update timestamp (UTC)
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
