"""Security utilities for password hashing and JWT token management.

Security best practices implemented:
- Bcrypt password hashing with configurable work factor
- JWT tokens with iss/aud/type claims
- Constant-time comparison for token verification
- Secure refresh token generation with SHA-256 hashing
"""
import re
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from passlib.context import CryptContext
import jwt
from src.config import settings


# Password hashing context using bcrypt
# Work factor (rounds) is configurable via BCRYPT_ROUNDS env var
# Default: 12 for production security, use 4 for development speed
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.bcrypt_rounds
)


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

    Requirements (OWASP compliant):
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        return False, "Password must contain at least one special character"

    return True, None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with security claims.

    Implements RFC 7519 recommended claims:
    - iss (issuer): Identifies the principal that issued the JWT
    - aud (audience): Identifies the recipients the JWT is intended for
    - exp (expiration): Token expiration timestamp
    - iat (issued at): Token issuance timestamp
    - sub (subject): User identifier (passed in data)
    - type: Custom claim to distinguish access vs refresh tokens

    Args:
        data: Payload data (must include 'sub' for user_id)
        expires_delta: Token expiration time (default: from config)

    Returns:
        Encoded JWT access token
    """
    now = datetime.now(timezone.utc)
    to_encode = data.copy()

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.jwt_access_expire_minutes)

    to_encode.update({
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "exp": expire,
        "iat": now,
        "type": "access",
    })

    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """Verify and decode a JWT token with full claim validation.

    Validates:
    - Signature using HS256 and JWT_SECRET
    - Expiration (exp claim)
    - Issuer (iss claim)
    - Audience (aud claim)
    - Token type (access vs refresh)

    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid, malformed, or wrong type
        jwt.InvalidIssuerError: If issuer doesn't match
        jwt.InvalidAudienceError: If audience doesn't match
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": ["exp", "iat", "sub", "iss", "aud", "type"]}
    )

    # Validate token type
    token_type = payload.get("type")
    if token_type != expected_type:
        raise jwt.InvalidTokenError(
            f"Invalid token type: expected {expected_type}, got {token_type}"
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


def hash_refresh_token(raw_token: str) -> str:
    """Compute SHA-256 hash of a refresh token.

    Used for database lookup and storage. The hash is computed
    deterministically so we can query by hash directly.

    Args:
        raw_token: Raw refresh token from client

    Returns:
        SHA-256 hex digest of the token
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()


def verify_refresh_token_hash(raw_token: str, stored_hash: str) -> bool:
    """Verify a refresh token against its stored hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        raw_token: Raw refresh token from client
        stored_hash: SHA-256 hash stored in database

    Returns:
        True if token matches hash, False otherwise
    """
    computed_hash = hash_refresh_token(raw_token)
    return secrets.compare_digest(computed_hash, stored_hash)
