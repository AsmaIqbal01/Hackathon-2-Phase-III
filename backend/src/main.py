"""FastAPI application for Todo Backend API.

This is the main application entry point that configures and runs the FastAPI server
with CORS middleware, database initialization, error handling, and API routes.

Usage:
    Development: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    Production: uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

API Documentation:
    - Interactive docs (Swagger UI): http://localhost:8000/docs
    - Alternative docs (ReDoc): http://localhost:8000/redoc
    - OpenAPI schema: http://localhost:8000/openapi.json
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from src.config import settings
from src.database import create_db_and_tables
from src.api.routes import tasks, auth
from src.utils.errors import TaskError, TaskNotFoundError, UnauthorizedAccessError, AuthError
from src.schemas.error_schemas import ErrorResponse, ErrorDetail


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Initialize database tables
    - Shutdown: Clean up resources (if needed)

    Args:
        app: FastAPI application instance

    Yields:
        None: Control to the application
    """
    # Startup: Create database tables
    print("Starting up: Creating database tables...")
    create_db_and_tables()
    print("Database tables created successfully")

    yield

    # Shutdown: Clean up resources (if needed)
    print("Shutting down: Cleaning up resources...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="RESTful API for multi-user Todo management with user ownership enforcement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, PATCH, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (including X-User-ID, Authorization, etc.)
)


# Global exception handler for AuthError
@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    """Handle authentication errors.

    Converts AuthError instances into standardized JSON error responses
    with 401 Unauthorized status code.

    Args:
        request: The incoming request
        exc: The AuthError exception

    Returns:
        JSONResponse: Standardized error response with 401 status
    """
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.status_code,
            message=exc.message
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


# Global exception handler for TaskError and subclasses
@app.exception_handler(TaskError)
async def task_error_handler(request: Request, exc: TaskError) -> JSONResponse:
    """Handle custom TaskError exceptions.

    Converts TaskError instances (and subclasses like TaskNotFoundError,
    UnauthorizedAccessError) into standardized JSON error responses.

    Args:
        request: The incoming request
        exc: The TaskError exception

    Returns:
        JSONResponse: Standardized error response with appropriate status code
    """
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.status_code,
            message=exc.message
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


# Global exception handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors.

    Converts FastAPI/Pydantic validation errors into standardized
    JSON error responses.

    Args:
        request: The incoming request
        exc: The validation error exception

    Returns:
        JSONResponse: Standardized error response with 400 status
    """
    # Extract first validation error for simplicity
    first_error = exc.errors()[0] if exc.errors() else None
    if first_error:
        field = " -> ".join(str(loc) for loc in first_error["loc"])
        message = f"{field}: {first_error['msg']}"
    else:
        message = "Validation error"

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=status.HTTP_400_BAD_REQUEST,
            message=message
        )
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump()
    )


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Catches all unhandled exceptions and returns a generic 500 error
    without exposing internal details to the client.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse: Generic error response with 500 status

    Note:
        In production, this logs the full exception for debugging
        but only returns a generic message to clients.
    """
    # Log the full exception (in production, use proper logging)
    print(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")

    # Return generic error to client (don't expose internal details)
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An internal server error occurred"
        )
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


# Include API routers with /api prefix
app.include_router(
    auth.router,
    prefix="/api",
    tags=["Authentication"]
)

app.include_router(
    tasks.router,
    prefix="/api",
    tags=["Tasks"]
)


# Root endpoint (health check)
@app.get(
    "/",
    tags=["Health"],
    summary="API health check",
    description="Returns API status and version information"
)
async def root():
    """API health check endpoint.

    Returns:
        dict: API status and version information
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs"
    }


# Run the application (for development only)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
