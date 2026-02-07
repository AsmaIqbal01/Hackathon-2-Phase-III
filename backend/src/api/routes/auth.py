"""Authentication API routes for registration, login, logout, and token management."""
from fastapi import APIRouter, Depends, status, Response
from sqlmodel import Session
from src.database import get_db
from src.schemas.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    AuthResponse,
    TokenResponse,
    UserProfile,
)
from src.services.auth_service import AuthService
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """Register a new user account.

    **Request Body:**
    - `email`: User's email address (will be normalized to lowercase)
    - `password`: Plain text password (min 8 chars, at least one letter and one number)

    **Success Response (201):**
    - `user`: User profile (id, email, created_at)
    - `access_token`: JWT access token (15 min expiry)
    - `refresh_token`: Opaque refresh token (7 day expiry)
    - `token_type`: "bearer"
    - `expires_in`: Access token expiry in seconds

    **Error Responses:**
    - `400`: Invalid email format or weak password
    - `409`: Email already registered
    """
    auth_service = AuthService(db)
    return auth_service.register(
        email=request.email,
        password=request.password
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
    description="Login with email and password to receive access and refresh tokens"
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """Authenticate user and issue tokens.

    **Request Body:**
    - `email`: User's email address
    - `password`: Plain text password

    **Success Response (200):**
    - `user`: User profile
    - `access_token`: JWT access token
    - `refresh_token`: Opaque refresh token
    - `token_type`: "bearer"
    - `expires_in`: Access token expiry in seconds

    **Error Responses:**
    - `401`: Invalid credentials (generic message for security)
    - `429`: Too many login attempts (includes Retry-After header)
    """
    auth_service = AuthService(db)
    return auth_service.login(
        email=request.email,
        password=request.password
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Obtain new access token using refresh token (with rotation)"
)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Refresh access token using refresh token.

    Implements token rotation: old refresh token is revoked and a new one is issued.

    **Request Body:**
    - `refresh_token`: Opaque refresh token from previous login or refresh

    **Success Response (200):**
    - `access_token`: New JWT access token
    - `refresh_token`: New opaque refresh token (old one is revoked)
    - `token_type`: "bearer"
    - `expires_in`: Access token expiry in seconds

    **Error Responses:**
    - `401`: Invalid or expired refresh token
    """
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(refresh_token=request.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Invalidate current session tokens"
)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Response:
    """Logout user by revoking all refresh tokens.

    Requires valid JWT access token in Authorization header.

    **Success Response (204):**
    - No content (tokens revoked successfully)

    **Error Responses:**
    - `401`: Invalid or missing JWT token
    """
    auth_service = AuthService(db)
    auth_service.logout(user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Retrieve authenticated user profile"
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserProfile:
    """Get authenticated user's profile.

    Requires valid JWT access token in Authorization header.

    **Success Response (200):**
    - `id`: User's unique identifier
    - `email`: User's email address
    - `created_at`: Account creation timestamp

    **Error Responses:**
    - `401`: Invalid or missing JWT token

    **Note:** password_hash is NOT included in response.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at
    )
