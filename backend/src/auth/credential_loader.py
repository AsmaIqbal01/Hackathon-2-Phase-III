"""
Credential loader for authentication system.

Loads user credentials from .env file or environment variables.
"""

import os
from dotenv import load_dotenv
from .exceptions import ConfigurationError


def load_credentials() -> dict[str, str]:
    """
    Load user credentials from configuration.

    Loads from .env file (if present) or environment variables.
    Requires: AUTH_USERNAME, AUTH_PASSPHRASE, AUTH_USER_ID

    Returns:
        Dictionary with keys: 'username', 'passphrase', 'user_id'

    Raises:
        ConfigurationError: If any required credential is missing

    Example:
        >>> creds = load_credentials()
        >>> print(f"Loaded credentials for user: {creds['username']}")
        Loaded credentials for user: admin
    """
    # Load from .env file if present (searches in current dir and parents)
    load_dotenv()

    # Extract credentials from environment
    username = os.getenv('AUTH_USERNAME')
    passphrase = os.getenv('AUTH_PASSPHRASE')
    user_id = os.getenv('AUTH_USER_ID')

    # Validate all required fields are present
    missing_fields = []
    if not username:
        missing_fields.append('AUTH_USERNAME')
    if not passphrase:
        missing_fields.append('AUTH_PASSPHRASE')
    if not user_id:
        missing_fields.append('AUTH_USER_ID')

    if missing_fields:
        raise ConfigurationError(
            f"Missing required credential configuration: {', '.join(missing_fields)}. "
            f"Please ensure .env file exists with these variables or set them in environment."
        )

    return {
        'username': username,
        'passphrase': passphrase,
        'user_id': user_id
    }
