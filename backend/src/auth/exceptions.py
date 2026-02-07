"""
Custom exception classes for authentication system.

Following auth.skill.md error specifications:
- Invalid credentials
- Authentication required
"""


class AuthenticationError(Exception):
    """
    Raised when authentication fails due to invalid credentials.

    This error occurs when:
    - Username does not match configured AUTH_USERNAME
    - Passphrase does not match configured AUTH_PASSPHRASE
    - Credentials validation fails
    """
    pass


class SessionError(Exception):
    """
    Raised when session operations fail.

    This error occurs when:
    - get_current_user() called when not authenticated
    - Session state inconsistency detected
    - Session context is invalid or corrupted
    """
    pass


class ConfigurationError(Exception):
    """
    Raised when credential configuration is missing or invalid.

    This error occurs when:
    - AUTH_USERNAME, AUTH_PASSPHRASE, or AUTH_USER_ID not found in environment
    - .env file missing and environment variables not set
    - Invalid credential format or missing required fields
    """
    pass
