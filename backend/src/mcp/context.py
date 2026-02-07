"""MCP context management for user_id and database session injection."""
import os
from typing import Generator
from sqlmodel import Session
from src.database import engine


def get_context_user_id() -> str:
    """Get user_id from MCP context (environment variable).

    The MCP server receives user_id via environment variable when launched
    by the Master Agent with stdio_client.

    Returns:
        str: User ID from MCP context

    Raises:
        ValueError: If USER_ID environment variable is not set
    """
    user_id = os.environ.get("USER_ID")
    if not user_id:
        raise ValueError("USER_ID not found in MCP context")
    return user_id


def get_db_session() -> Generator[Session, None, None]:
    """Get database session for MCP tool operations.

    Yields a database session that is automatically closed after use.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session
