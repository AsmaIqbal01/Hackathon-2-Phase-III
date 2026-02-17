"""FastAPI dependency injection functions.

Dependencies for authentication, database sessions, and request validation.
Security: All authentication flows use constant-time comparisons and
generic error messages to prevent timing attacks and user enumeration.
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from uuid import UUID
from src.models.user import User
from src.database import get_db
from src.utils.security import verify_token
from src.utils.errors import AuthError
import jwt
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme for Swagger UI integration
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter JWT access token from /auth/login response"
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract and verify authenticated user from JWT access token.

    Security validations:
    - Verifies JWT signature (HS256)
    - Validates iss/aud claims match config
    - Validates token type is "access"
    - Validates token is not expired
    - Verifies user exists and is active

    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session

    Returns:
        User: Authenticated and active user entity

    Raises:
        AuthError: Generic error for all auth failures (prevents enumeration)

    Usage:
        @router.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            # user.id contains the authenticated user's ID
            ...
    """
    token = credentials.credentials

    try:
        # Verify JWT with full claim validation (iss, aud, exp, type)
        payload = verify_token(token, expected_type="access")

        # Extract user_id from subject claim
        user_id_str = payload.get("sub")
        if not user_id_str:
            logger.warning("JWT missing 'sub' claim")
            raise AuthError("Invalid token")

        # Parse UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.warning(f"Invalid UUID in JWT: {user_id_str}")
            raise AuthError("Invalid token")

        # Fetch user from database
        user = db.exec(select(User).where(User.id == user_id)).first()

        if not user:
            logger.warning(f"User not found for JWT: {user_id}")
            raise AuthError("Invalid token")

        # Check if user account is active
        if not user.is_active:
            logger.warning(f"Disabled user attempted access: {user_id}")
            raise AuthError("Account disabled")

        return user

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise AuthError("Token expired")
    except jwt.InvalidIssuerError:
        logger.warning("JWT issuer mismatch")
        raise AuthError("Invalid token")
    except jwt.InvalidAudienceError:
        logger.warning("JWT audience mismatch")
        raise AuthError("Invalid token")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise AuthError("Invalid token")
    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise AuthError("Authentication failed")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Alias for get_current_user that explicitly documents the active check.

    Use this dependency when you want to be explicit that the endpoint
    requires an active user account.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User: Same user (is_active already verified)
    """
    return current_user
