"""
Session context management for authentication system.

Implements auth.skill.md session requirements:
- Create session context
- Expose authenticated user_id
- Session valid for runtime duration
- Session destroyed on exit

Session Lifecycle (T037):
--------------------

1. Created:
   - Session object instantiated as module-level singleton (_session)
   - Initial state: user_id=None, username=None, authenticated=False
   - Created on module import (before authentication)

2. Active (Authenticated):
   - Triggered by: authenticate_user() calling session.login()
   - State: user_id=<value>, username=<value>, authenticated=True
   - Duration: Throughout application lifetime (process runtime)
   - Persistence: In-memory only, not saved to disk/database
   - Access: get_current_user() returns user_id without re-authentication
   - Validation: is_authenticated() checks state consistency

3. Destroyed:
   - Triggered by: Application exit (process termination)
   - State: Session data cleared from memory
   - No explicit cleanup required (handled by process exit)
   - Note: logout() method available for explicit session clearing if needed

Session Persistence Guarantee:
------------------------------
Once authenticated via authenticate_user(), the session context persists
across ALL subsequent function calls within the same process lifetime.
No re-authentication is required for task CRUD operations after initial login.

Example:
    >>> # Application startup
    >>> prompt_for_credentials()  # Authenticates once
    >>>
    >>> # Session persists across multiple operations
    >>> task1 = create_task("First task")   # Uses session, no re-auth
    >>> task2 = create_task("Second task")  # Uses session, no re-auth
    >>> tasks = list_tasks()                # Uses session, no re-auth
    >>>
    >>> # All operations use same user_id from initial authentication
"""

from functools import wraps
from .exceptions import SessionError, AuthenticationError


class SessionContext:
    """
    Active authenticated session in backend agent.

    Attributes:
        user_id: Authenticated user's identifier (from AUTH_USER_ID)
        username: Authenticated user's username (for display/logging)
        authenticated: Whether user is currently authenticated

    Lifecycle:
        - Created: On successful authentication
        - Active: Throughout application lifetime while process runs
        - Destroyed: On application exit (no persistence)
    """

    def __init__(self):
        """Initialize empty session context."""
        self.user_id = None
        self.username = None
        self.authenticated = False

    def login(self, username: str, user_id: str):
        """
        Create authenticated session.

        Args:
            username: Authenticated username
            user_id: Authenticated user_id

        Side Effects:
            Sets authenticated=True, assigns username and user_id
        """
        self.username = username
        self.user_id = user_id
        self.authenticated = True

    def logout(self):
        """
        Destroy session context.

        Side Effects:
            Clears username, user_id, sets authenticated=False
        """
        self.username = None
        self.user_id = None
        self.authenticated = False


# Global session instance (module-level singleton)
# Session persists for application runtime, cleared on exit
_session = SessionContext()


def is_authenticated() -> bool:
    """
    Check if user is currently authenticated with session state validation.

    Following auth.skill.md specification: is_authenticated() function.

    Validates session consistency:
    - If authenticated=True, username and user_id must be set
    - If authenticated=False, username and user_id must be None

    Returns:
        True if authenticated, False otherwise

    Example:
        >>> if is_authenticated():
        ...     print("User is logged in")
        ... else:
        ...     print("Please authenticate first")
    """
    # Validate session state consistency (T036)
    if _session.authenticated:
        # If authenticated, username and user_id must be present
        if not _session.username or not _session.user_id:
            # Inconsistent state - authenticated but missing credentials
            _session.authenticated = False
            return False
    else:
        # If not authenticated, username and user_id should be None
        if _session.username is not None or _session.user_id is not None:
            # Inconsistent state - not authenticated but has credentials
            _session.username = None
            _session.user_id = None

    return _session.authenticated


def get_current_user() -> str:
    """
    Get the current authenticated user's user_id.

    Following auth.skill.md specification: get_current_user() function.

    Returns:
        user_id string

    Raises:
        SessionError: If not authenticated

    Example:
        >>> try:
        ...     user_id = get_current_user()
        ...     print(f"Current user: {user_id}")
        ... except SessionError:
        ...     print("Not authenticated")
    """
    if not _session.authenticated:
        raise SessionError("No authenticated session - authentication required")
    return _session.user_id


def require_auth(func):
    """
    Decorator to enforce authentication before function execution.

    Following auth.skill.md rule: "Authentication must occur before any task operation"

    Args:
        func: Function to wrap with authentication check

    Returns:
        Wrapped function that checks authentication first

    Raises:
        AuthenticationError: If not authenticated when function called

    Example:
        >>> @require_auth
        ... def create_task(title: str) -> dict:
        ...     user_id = get_current_user()
        ...     return {"id": "task-1", "user_id": user_id, "title": title}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            raise AuthenticationError("Authentication required - please authenticate first")
        return func(*args, **kwargs)
    return wrapper


# Internal access to session for authenticator module
def _get_session() -> SessionContext:
    """
    Internal function to access session for login/logout operations.

    Note: This is for internal use by authenticator module only.
    External code should use is_authenticated() and get_current_user().
    """
    return _session
