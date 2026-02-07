"""Authentication service with business logic for user registration, login, logout, and token management."""
from datetime import datetime, timedelta
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
    verify_token,
    generate_refresh_token,
    verify_refresh_token_hash,
)
from src.utils.rate_limiter import login_rate_limiter
from src.config import settings
import logging

logger = logging.getLogger(__name__)


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

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = User(
            email=normalized_email,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
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

        # Verify credentials (generic error for security)
        if not user or not verify_password(password, user.password_hash):
            login_rate_limiter.record_attempt(normalized_email)
            logger.warning(f"Login failed: invalid credentials for {normalized_email}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid credentials"
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
                created_at=user.created_at
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.jwt_access_expire_minutes * 60
        )

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token with rotation.

        Validates refresh token, revokes old token, creates new token pair.

        Args:
            refresh_token: Raw refresh token from client

        Returns:
            TokenResponse with new token pair

        Raises:
            HTTPException 401: Invalid or expired refresh token
        """
        # Find active refresh token
        token_records = self.db.exec(select(RefreshToken)).all()

        matching_token = None
        for token_record in token_records:
            if verify_refresh_token_hash(refresh_token, token_record.token_hash):
                matching_token = token_record
                break

        # Validate token exists and is active
        if not matching_token:
            logger.warning("Refresh failed: token not found")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid or expired refresh token"
                }
            })

        # Check if token is revoked
        if matching_token.revoked_at is not None:
            logger.warning(f"Refresh failed: token already revoked - {matching_token.id}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid or expired refresh token"
                }
            })

        # Check if token is expired
        if matching_token.expires_at < datetime.utcnow():
            logger.warning(f"Refresh failed: token expired - {matching_token.id}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid or expired refresh token"
                }
            })

        # Get user
        user = self.db.exec(
            select(User).where(User.id == matching_token.user_id)
        ).first()

        if not user:
            logger.error(f"Refresh failed: user not found - {matching_token.user_id}")
            raise HTTPException(status_code=401, detail={
                "error": {
                    "code": 401,
                    "message": "Invalid or expired refresh token"
                }
            })

        # Revoke old token (rotation)
        matching_token.revoked_at = datetime.utcnow()
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
        """Revoke all refresh tokens for a user (logout).

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

        now = datetime.utcnow()
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
            created_at=user.created_at
        )

    def _create_token_pair(self, user: User) -> Tuple[str, str]:
        """Internal method to create access + refresh token pair.

        Args:
            user: User entity

        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Create access token (JWT)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Generate refresh token (opaque)
        raw_refresh_token, hashed_refresh_token = generate_refresh_token()

        # Store refresh token in database
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.jwt_refresh_expire_days),
            created_at=datetime.utcnow()
        )
        self.db.add(refresh_token_record)
        self.db.commit()

        return access_token, raw_refresh_token
