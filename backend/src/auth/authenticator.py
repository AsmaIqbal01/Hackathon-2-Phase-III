"""
Authenticator module for backend agent system.

Implements auth.skill.md core functionality:
- authenticate_user() - Prompt for credentials, validate, create session
"""

import sys
import getpass
from .credential_loader import load_credentials
from .session import _get_session
from .exceptions import AuthenticationError, ConfigurationError


def authenticate_user(username: str, passphrase: str) -> bool:
    """
    Authenticate user with provided credentials.

    Following auth.skill.md specification: authenticate_user() function.

    Validates credentials against configuration (AUTH_USERNAME, AUTH_PASSPHRASE)
    and creates session on success.

    Args:
        username: User-provided username
        passphrase: User-provided passphrase

    Returns:
        True if authentication successful

    Raises:
        AuthenticationError: If credentials are invalid
        ConfigurationError: If credentials not configured in environment

    Side Effects:
        - Creates session context on success
        - Sets session.user_id, session.username, session.authenticated

    Example:
        >>> try:
        ...     authenticate_user("admin", "secret123")
        ...     print("Authentication successful")
        ... except AuthenticationError as e:
        ...     print(f"Failed: {e}")
    """
    # Load configured credentials from .env or environment
    try:
        creds = load_credentials()
    except ConfigurationError as e:
        # Re-raise configuration error (credentials not found)
        raise

    # Validate username and passphrase
    if username != creds['username'] or passphrase != creds['passphrase']:
        raise AuthenticationError("Invalid username or passphrase")

    # Create session on successful authentication
    session = _get_session()
    session.login(username=username, user_id=creds['user_id'])

    return True


def prompt_for_credentials(max_retries: int = 3) -> None:
    """
    Prompt user for credentials with retry/exit options.

    Following auth.skill.md specification: prompt for credentials at app start.

    Args:
        max_retries: Maximum authentication attempts (default 3)

    Returns:
        None (exits application if authentication fails)

    Raises:
        SystemExit: On authentication failure after max retries or user exit

    Side Effects:
        - Prompts user for input via stdin
        - Calls authenticate_user() internally
        - Exits application on failure

    Example:
        >>> # On application startup
        >>> prompt_for_credentials()
        Username: admin
        Passphrase: (hidden input)
        Authentication successful!
        Welcome, admin
    """
    attempt = 0

    while attempt < max_retries:
        try:
            # Prompt for username
            username = input("Username: ")

            # Prompt for passphrase (hidden input)
            passphrase = getpass.getpass("Passphrase: ")

            # Attempt authentication
            authenticate_user(username, passphrase)

            # Success - print welcome message and return
            print(f"\nAuthentication successful!")
            print(f"Welcome, {username}\n")
            return

        except AuthenticationError as e:
            # Authentication failed - increment attempt counter
            attempt += 1
            remaining = max_retries - attempt

            # Display error message
            print(f"\nError: {e}")

            # Check if retries remaining
            if remaining > 0:
                # Offer retry or exit
                retry_choice = input(f"Retry? (y/n): ").lower().strip()

                if retry_choice != 'y':
                    # User chose to exit
                    print("Exiting application.")
                    sys.exit(0)
            else:
                # Max retries exceeded
                print("Max retries exceeded. Exiting application.")
                sys.exit(1)

        except ConfigurationError as e:
            # Configuration error - cannot proceed
            print(f"\nConfiguration error: {e}")
            print("Please check your .env file or environment variables.")
            sys.exit(1)

    # Should never reach here, but handle edge case
    print("Authentication failed. Exiting application.")
    sys.exit(1)
