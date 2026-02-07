"""FastAPI dependency injection functions.

Dependencies for authentication, database sessions, and request validation.
"""
from fastapi import Header, Query, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlmodel import Session, select
from src.models.user import User
from src.database import get_db
from src.utils.security import verify_token
from src.utils.errors import AuthError
import jwt
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract and verify authenticated user from JWT token.

    Validates JWT access token from Authorization header and returns the
    authenticated user. This dependency replaces get_user_id for F01-S02.

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session

    Returns:
        User: Authenticated user entity

    Raises:
        AuthError: If token is missing, invalid, expired, or user not found

    Usage:
        @router.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            # user.id contains the authenticated user's ID
            ...
    """
    token = credentials.credentials

    try:
        # Verify and decode JWT token
        payload = verify_token(token)

        # Extract user_id from token subject claim
        user_id_str = payload.get("sub")
        if not user_id_str:
            logger.warning("JWT missing 'sub' claim")
            raise AuthError("Invalid token payload")

        # Convert string UUID to UUID object
        from uuid import UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.warning(f"Invalid UUID in JWT: {user_id_str}")
            raise AuthError("Invalid token payload")

        # Fetch user from database
        user = db.exec(select(User).where(User.id == user_id)).first()

        if not user:
            logger.warning(f"User not found for JWT: {user_id}")
            raise AuthError("User not found")

        return user

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise AuthError("Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise AuthError("Invalid token")
    except AuthError:
        # Re-raise AuthError as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise AuthError("Authentication failed")
