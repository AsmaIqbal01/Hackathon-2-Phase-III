"""Refresh token model for secure session management."""
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class RefreshToken(SQLModel, table=True):
    """Refresh token entity for JWT session management.

    Tokens are stored hashed (SHA-256) for security. Supports revocation
    and token rotation on refresh.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to users table
        token_hash: SHA-256 hash of raw refresh token
        expires_at: Token expiration timestamp
        created_at: Token issuance timestamp
        revoked_at: Token revocation timestamp (NULL if active)
    """
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(max_length=64, unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = Field(default=None)
