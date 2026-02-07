"""Task management API endpoints.

RESTful API routes for task CRUD operations with user ownership enforcement.
All endpoints require JWT authentication via Authorization header.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from uuid import UUID
from typing import List, Optional
from src.database import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.services.task_service import TaskService
from src.schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse
from src.schemas.error_schemas import ErrorResponse
from src.models.task import TaskStatus, TaskPriority
from src.utils.errors import TaskError, TaskNotFoundError, UnauthorizedAccessError


# Create router with /tasks prefix
router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user. Returns 201 with created task.",
    responses={
        201: {
            "description": "Task created successfully",
            "model": TaskResponse
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized - missing or invalid JWT token",
            "model": ErrorResponse
        }
    }
)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title, description, status, priority, tags)
        current_user: Authenticated user (from JWT token)
        db: Database session (from dependency)

    Returns:
        TaskResponse: Created task with ID and timestamps

    Raises:
        HTTPException 400: If validation fails
        HTTPException 401: If JWT token is missing or invalid
    """
    service = TaskService(db=db, user_id=str(current_user.id))
    task = service.create_task(data=task_data)
    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
    description="Retrieve all tasks for the authenticated user with optional filtering and sorting.",
    responses={
        200: {
            "description": "List of tasks (may be empty)",
            "model": List[TaskResponse]
        },
        400: {
            "description": "Invalid filters",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized - missing or invalid JWT token",
            "model": ErrorResponse
        }
    }
)
def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: Optional[TaskStatus] = Query(
        default=None,
        alias="status",
        description="Filter by task status (todo, in-progress, completed)"
    ),
    priority_filter: Optional[TaskPriority] = Query(
        default=None,
        alias="priority",
        description="Filter by priority (low, medium, high)"
    ),
    tags_filter: Optional[str] = Query(
        default=None,
        alias="tags",
        description="Filter by tags (comma-separated, task must contain ALL)"
    ),
    sort_by: Optional[str] = Query(
        default="created_at",
        description="Sort by field (created_at, updated_at, priority, status)",
        pattern="^(created_at|updated_at|priority|status)$"
    )
) -> List[TaskResponse]:
    """List all tasks for the authenticated user with filters.

    Args:
        current_user: Authenticated user (from JWT token)
        db: Database session (from dependency)
        status_filter: Filter by task status (optional)
        priority_filter: Filter by task priority (optional)
        tags_filter: Comma-separated tags (task must contain ALL) (optional)
        sort_by: Sort field (default: created_at)

    Returns:
        List[TaskResponse]: List of tasks matching criteria (may be empty)

    Raises:
        HTTPException 400: If filters are invalid
        HTTPException 401: If JWT token is missing or invalid
    """
    # Parse tags filter
    tags_list = None
    if tags_filter:
        tags_list = [tag.strip().lower() for tag in tags_filter.split(",") if tag.strip()]

    service = TaskService(db=db, user_id=str(current_user.id))
    tasks = service.list_tasks(
        status=status_filter,
        priority=priority_filter,
        tags=tags_list,
        sort_by=sort_by
    )

    return [TaskResponse.model_validate(task) for task in tasks]


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single task",
    description="Retrieve a specific task by ID. Returns 403 if task belongs to another user.",
    responses={
        200: {
            "description": "Task retrieved successfully",
            "model": TaskResponse
        },
        400: {
            "description": "Invalid task_id format",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized - missing or invalid JWT token",
            "model": ErrorResponse
        },
        403: {
            "description": "Task belongs to another user (cross-user access denied)",
            "model": ErrorResponse
        },
        404: {
            "description": "Task not found",
            "model": ErrorResponse
        }
    }
)
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Get a single task by ID.

    Args:
        task_id: UUID of the task to retrieve
        current_user: Authenticated user (from JWT token)
        db: Database session (from dependency)

    Returns:
        TaskResponse: The requested task

    Raises:
        HTTPException 401: If JWT token is missing or invalid
        HTTPException 403: If task belongs to another user
        HTTPException 404: If task doesn't exist
    """
    service = TaskService(db=db, user_id=str(current_user.id))
    task = service.get_task_by_id(task_id=task_id)
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Partially update a task (PATCH semantics). Only provided fields are updated.",
    responses={
        200: {
            "description": "Task updated successfully",
            "model": TaskResponse
        },
        400: {
            "description": "Invalid update data",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized - missing or invalid JWT token",
            "model": ErrorResponse
        },
        403: {
            "description": "Task belongs to another user (cross-user access denied)",
            "model": ErrorResponse
        },
        404: {
            "description": "Task not found",
            "model": ErrorResponse
        }
    }
)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Update an existing task with partial data (PATCH semantics).

    Args:
        task_id: UUID of the task to update
        task_data: Partial task data (only provided fields are updated)
        current_user: Authenticated user (from JWT token)
        db: Database session (from dependency)

    Returns:
        TaskResponse: Updated task

    Raises:
        HTTPException 400: If validation fails
        HTTPException 401: If JWT token is missing or invalid
        HTTPException 403: If task belongs to another user
        HTTPException 404: If task doesn't exist
    """
    service = TaskService(db=db, user_id=str(current_user.id))
    task = service.update_task(task_id=task_id, data=task_data)
    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task. Returns 204 No Content on success.",
    responses={
        204: {
            "description": "Task deleted successfully (no content returned)"
        },
        401: {
            "description": "Unauthorized - missing or invalid JWT token",
            "model": ErrorResponse
        },
        403: {
            "description": "Task belongs to another user (cross-user access denied)",
            "model": ErrorResponse
        },
        404: {
            "description": "Task not found",
            "model": ErrorResponse
        }
    }
)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Delete a task by ID.

    Args:
        task_id: UUID of the task to delete
        current_user: Authenticated user (from JWT token)
        db: Database session (from dependency)

    Returns:
        None: 204 No Content (no response body)

    Raises:
        HTTPException 401: If JWT token is missing or invalid
        HTTPException 403: If task belongs to another user
        HTTPException 404: If task doesn't exist
    """
    service = TaskService(db=db, user_id=str(current_user.id))
    service.delete_task(task_id=task_id)
    # FastAPI automatically returns 204 No Content with no response body
