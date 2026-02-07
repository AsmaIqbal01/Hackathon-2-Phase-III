"""User model for authentication and user management."""
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """User entity for authentication and task ownership.

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (normalized lowercase, unique)
        password_hash: Bcrypt-hashed password
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
