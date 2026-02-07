"""Pydantic schemas for authentication request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


# Request Schemas

class RegisterRequest(BaseModel):
    """User registration request payload.

    Attributes:
        email: User's email address (validated format)
        password: Plain text password (min 8 chars, will be hashed)
    """
    email: EmailStr = Field(..., max_length=255, description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, at least one letter and one number)"
    )


class LoginRequest(BaseModel):
    """User login request payload.

    Attributes:
        email: User's email address
        password: Plain text password
    """
    email: EmailStr = Field(..., max_length=255, description="User's email address")
    password: str = Field(..., max_length=128, description="User's password")


class RefreshRequest(BaseModel):
    """Token refresh request payload.

    Attributes:
        refresh_token: Opaque refresh token from previous login/refresh
    """
    refresh_token: str = Field(..., description="Refresh token from previous login or refresh")


# Response Schemas

class UserProfile(BaseModel):
    """User profile information (no sensitive data).

    Attributes:
        id: User's unique identifier
        email: User's email address
        created_at: Account creation timestamp
    """
    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token pair response (for refresh endpoint).

    Attributes:
        access_token: New JWT access token
        refresh_token: New refresh token (rotated)
        token_type: Token type (always "bearer")
        expires_in: Access token expiry in seconds
    """
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New refresh token (rotation)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds", example=900)


class AuthResponse(BaseModel):
    """Authentication response with user profile and tokens.

    Returned on successful registration and login.

    Attributes:
        user: User profile information
        access_token: JWT access token (15 min expiry)
        refresh_token: Opaque refresh token (7 day expiry)
        token_type: Token type (always "bearer")
        expires_in: Access token expiry in seconds
    """
    user: UserProfile = Field(..., description="User profile information")
    access_token: str = Field(..., description="JWT access token (15 min expiry)")
    refresh_token: str = Field(..., description="Opaque refresh token (7 day expiry)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds", example=900)
