"""Refresh token model for secure session management."""
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class RefreshToken(SQLModel, table=True):
    """Refresh token entity for JWT session management.

    Security notes:
    - Tokens are stored as SHA-256 hash (never raw token)
    - token_hash is indexed for O(1) lookup during refresh
    - Supports revocation via revoked_at timestamp
    - Token rotation: old token revoked when new one issued

    Attributes:
        id: Unique identifier (UUID v4)
        user_id: Foreign key to users table (indexed)
        token_hash: SHA-256 hash of raw refresh token (indexed for lookup)
        expires_at: Token expiration timestamp (UTC)
        created_at: Token issuance timestamp (UTC)
        revoked_at: Token revocation timestamp (NULL if active)
    """
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(max_length=64, unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=utc_now)
    revoked_at: Optional[datetime] = Field(default=None)
