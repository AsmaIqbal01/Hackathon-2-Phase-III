"""Database connection and session management using SQLModel."""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from src.config import settings
from src.models import User, RefreshToken, Task, Conversation, Message  # Import models for table creation


def _get_database_url() -> str:
    """Normalize DATABASE_URL for SQLAlchemy compatibility.

    Converts postgresql:// to postgresql+psycopg:// so SQLAlchemy uses
    psycopg v3 driver (which is what we have installed) instead of
    defaulting to psycopg2.
    """
    url = settings.database_url
    if url.startswith("postgres://"):
        # Render/Heroku use postgres:// which is deprecated
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


db_url = _get_database_url()

# Create engine with appropriate settings based on database type
if db_url.startswith("sqlite"):
    # SQLite configuration (for local development/testing)
    engine = create_engine(
        db_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
    )
else:
    # PostgreSQL configuration (for production with Neon Serverless)
    engine = create_engine(
        db_url,
        echo=settings.debug,  # Log SQL queries in debug mode
        pool_pre_ping=True,   # Verify connections before using (important for serverless)
        pool_recycle=3600,    # Recycle connections after 1 hour
    )


def create_db_and_tables() -> None:
    """Create all database tables defined in SQLModel models.

    This is called during application startup to ensure tables exist.
    For production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection function for FastAPI.

    Yields a database session that is automatically closed after the request.

    Usage in FastAPI:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    with Session(engine) as session:
        yield session
