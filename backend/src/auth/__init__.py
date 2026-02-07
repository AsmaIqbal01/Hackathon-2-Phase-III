"""
Authentication module for backend agent system.

This module provides authentication functionality following the auth.skill.md specification:
- Prompt for credentials
- Validate credentials
- Create session context
- Expose authenticated user_id
"""

from .exceptions import AuthenticationError, SessionError, ConfigurationError
from .session import is_authenticated, get_current_user, require_auth
from .authenticator import authenticate_user, prompt_for_credentials

__all__ = [
    'AuthenticationError',
    'SessionError',
    'ConfigurationError',
    'is_authenticated',
    'get_current_user',
    'require_auth',
    'authenticate_user',
    'prompt_for_credentials',
]
