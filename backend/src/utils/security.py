"""Security utilities for password hashing and JWT token management."""
import re
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from passlib.context import CryptContext
import jwt
from src.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt-hashed password with salt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_email(email: str) -> bool:
    """Validate email format using RFC 5322 regex pattern.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def normalize_email(email: str) -> str:
    """Normalize email address to lowercase.

    Args:
        email: Email address to normalize

    Returns:
        Lowercase email address
    """
    return email.strip().lower()


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password meets security requirements.

    Requirements:
    - At least 8 characters
    - At least one letter
    - At least one number

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Payload data (must include 'sub' for user_id)
        expires_delta: Token expiration time (default: from config)

    Returns:
        Encoded JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_expire_minutes
        )

    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid or malformed
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm]
    )
    return payload


def generate_refresh_token() -> Tuple[str, str]:
    """Generate a secure random refresh token and its hash.

    Returns:
        Tuple of (raw_token, hashed_token)
        - raw_token: URL-safe random string (give to client)
        - hashed_token: SHA-256 hash (store in database)
    """
    raw_token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, hashed_token


def verify_refresh_token_hash(raw_token: str, stored_hash: str) -> bool:
    """Verify a refresh token against its stored hash.

    Args:
        raw_token: Raw refresh token from client
        stored_hash: SHA-256 hash stored in database

    Returns:
        True if token matches hash, False otherwise
    """
    computed_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return secrets.compare_digest(computed_hash, stored_hash)
