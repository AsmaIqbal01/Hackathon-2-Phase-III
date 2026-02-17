"""Authentication service with business logic for user registration, login, logout, and token management.

Security features:
- Bcrypt password hashing with configurable work factor
- JWT access tokens with iss/aud claims
- Refresh token rotation (old token revoked on refresh)
- SHA-256 hashed token storage (never stores raw tokens)
- Rate limiting on login attempts
- Generic error messages (prevents user enumeration)
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException
from src.models.user import User
from src.models.refresh_token import RefreshToken
from src.schemas.auth_schemas import AuthResponse, TokenResponse, UserProfile
from src.utils.security import (
    hash_password,
    verify_password,
    validate_email,
    normalize_email,
    validate_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from src.utils.rate_limiter import login_rate_limiter
from src.config import settings
import logging

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class AuthService:
    """Service class for authentication operations.

    Handles user registration, login, logout, token refresh, and user profile retrieval.
    All business logic is centralized here, routes delegate to this service.
    """

    def __init__(self, db: Session):
        """Initialize auth service with database session.

        Args:
            db: SQLModel database session
        """
        self.db = db

    def register(self, email: str, password: str) -> AuthResponse:
        """Register a new user account.

        Validates email format, password strength, checks for duplicate email,
        creates user with hashed password, and returns authentication tokens.

        Args:
            email: User's email address (will be normalized)
            password: Plain text password

        Returns:
            AuthResponse with user profile and token pair

        Raises:
            HTTPException 400: Invalid email format or weak password
            HTTPException 409: Email already registered
        """
        # Validate email format
        if not validate_email(email):
            logger.warning(f"Registration failed: invalid email format - {email}")
            raise HTTPException(status_code=400, detail={
                "error": {
                    "code": 400,
                    "message": "Invalid email format"
                }
            })

        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            logger.warning(f"Registration failed: weak password for {email}")
            raise HTTPException(status_code=400, detail={
                "error": {
                    "code": 400,
                    "message": f"{error_msg} with at least one letter and one number"
                }
            })

        # Normalize email to lowercase
        normalized_email = normalize_email(email)

        # Check for duplicate email
        existing_user = self.db.exec(
            select(User).where(User.email == normalized_email)
        ).first()

        if existing_user:
            logger.warning(f"Registration failed: duplicate email - {normalized_email}")
            raise HTTPException(status_code=409, detail={
                "error": {
                    "code": 409,
                    "message": "Email already registered"
                }
            })

        # Hash password using bcrypt
        hashed = hash_password(password)

        # Create user with hashed password
        now = utc_now()
        user = User(
            email=normalized_email,
            password_hash=hashed,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User registered successfully: {user.id} ({user.email})")

        # Generate tokens
        access_token, refresh_token = self._create_token_pair(user)

        return AuthResponse(
            user=UserProfile(
                id=user.id,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_expire_minutes * 60
        )

    def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate user and issue tokens.

        Validates credentials, checks rate limiting, verifies password,
        and returns authentication tokens.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            AuthResponse with user profile and token pair

        Raises:
            HTTPException 401: Invalid credentials
            HTTPException 429: Too many login attempts (rate limited)
        """
        normalized_email = normalize_email(email)

        # Check rate limiting
        if not login_rate_limiter.is_allowed(normalized_email):
            retry_after = login_rate_limiter.get_retry_after(normalized_email)
            logger.warning(f"Login rate limited: {normalized_email}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": {
                        "code": 429,
                        "message": f"Too many login attempts. Try again in {retry_after} seconds"
                    }
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Find user by email
        user = self.db.exec(
            select(User).where(User.email == normalized_email)
        ).first()

        # Verify credentials (generic error prevents user enumeration)
        if not user or not verify_password(password, user.password_hash):
            login_rate_limiter.record_attempt(normalized_email)
            logger.warning(f"Login failed: invalid credentials for {normalized_email}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid credentials"
                }
            })

        # Check if account is disabled
        if not user.is_active:
            logger.warning(f"Login failed: account disabled for {normalized_email}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Account disabled"
                }
            })

        # Clear rate limit on successful login
        login_rate_limiter.clear_attempts(normalized_email)

        logger.info(f"User logged in successfully: {user.id} ({user.email})")

        # Generate tokens
        access_token, refresh_token = self._create_token_pair(user)

        return AuthResponse(
            user=UserProfile(
                id=user.id,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_expire_minutes * 60
        )

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token with rotation.

        Security features:
        - O(1) lookup via indexed token_hash (no linear scan)
        - Token rotation: old token revoked immediately
        - Generic error messages prevent token enumeration

        Args:
            refresh_token: Raw refresh token from client

        Returns:
            TokenResponse with new token pair

        Raises:
            HTTPException 401: Invalid or expired refresh token
        """
        # Compute hash for O(1) database lookup (token_hash is indexed)
        token_hash = hash_refresh_token(refresh_token)

        # Direct lookup by hash - O(1) instead of O(n) linear scan
        matching_token = self.db.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

        # Generic error for all failure cases (prevents enumeration)
        invalid_token_error = HTTPException(status_code=401, detail={
            "error": {
                "code": 401,
                "message": "Invalid or expired refresh token"
            }
        })

        # Validate token exists
        if not matching_token:
            logger.warning("Refresh failed: token not found")
            raise invalid_token_error

        # Check if token is revoked
        if matching_token.revoked_at is not None:
            logger.warning(f"Refresh failed: token already revoked - {matching_token.id}")
            raise invalid_token_error

        # Check if token is expired (use timezone-aware comparison)
        now = utc_now()
        # Handle both naive and aware datetimes for backwards compatibility
        expires_at = matching_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            logger.warning(f"Refresh failed: token expired - {matching_token.id}")
            raise invalid_token_error

        # Get user and verify active
        user = self.db.exec(
            select(User).where(User.id == matching_token.user_id)
        ).first()

        if not user:
            logger.error(f"Refresh failed: user not found - {matching_token.user_id}")
            raise invalid_token_error

        if not user.is_active:
            logger.warning(f"Refresh failed: user disabled - {user.id}")
            raise invalid_token_error

        # Revoke old token immediately (rotation)
        matching_token.revoked_at = now
        self.db.add(matching_token)
        self.db.commit()

        logger.info(f"Tokens refreshed for user: {user.id} ({user.email})")

        # Generate new token pair
        access_token, new_refresh_token = self._create_token_pair(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_expire_minutes * 60
        )

    def logout(self, user_id: UUID) -> None:
        """Revoke all refresh tokens for a user (logout from all devices).

        This invalidates all active sessions for the user, requiring
        re-authentication on all devices.

        Args:
            user_id: User's unique identifier from JWT

        Raises:
            HTTPException 401: User not found
        """
        # Verify user exists
        user = self.db.exec(select(User).where(User.id == user_id)).first()
        if not user:
            logger.warning(f"Logout failed: user not found - {user_id}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid token"
                }
            })

        # Revoke all active refresh tokens for user
        active_tokens = self.db.exec(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
        ).all()

        now = utc_now()
        for token in active_tokens:
            token.revoked_at = now
            self.db.add(token)

        self.db.commit()

        logger.info(f"User logged out: {user.id} ({user.email}) - {len(active_tokens)} tokens revoked")

    def get_user_profile(self, user_id: UUID) -> UserProfile:
        """Get user profile by ID.

        Args:
            user_id: User's unique identifier from JWT

        Returns:
            UserProfile without sensitive data

        Raises:
            HTTPException 404: User not found
        """
        user = self.db.exec(select(User).where(User.id == user_id)).first()

        if not user:
            logger.warning(f"Get profile failed: user not found - {user_id}")
            raise HTTPException(status_code=404, detail={
                "error": {
                    "code": 404,
                    "message": "User not found"
                }
            })

        return UserProfile(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at
        )

    def _create_token_pair(self, user: User) -> Tuple[str, str]:
        """Create access + refresh token pair for authenticated user.

        Security notes:
        - Access token: JWT with iss/aud/exp/type claims
        - Refresh token: Opaque token, stored as SHA-256 hash
        - Never logs or returns the raw refresh token hash

        Args:
            user: Authenticated user entity

        Returns:
            Tuple of (access_token, raw_refresh_token)
        """
        # Create JWT access token with security claims
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Generate opaque refresh token (raw + hash)
        raw_refresh_token, hashed_refresh_token = generate_refresh_token()

        # Store only the hash in database (never raw token)
        now = utc_now()
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh_token,
            expires_at=now + timedelta(days=settings.jwt_refresh_expire_days),
            created_at=now
        )
        self.db.add(refresh_token_record)
        self.db.commit()

        return access_token, raw_refresh_token
