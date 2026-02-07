"""Business logic layer for task operations.

TaskService encapsulates all task-related business logic and database operations,
enforcing user ownership and data integrity rules.
"""
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from src.models.task import Task, TaskStatus, TaskPriority
from src.schemas.task_schemas import TaskCreate, TaskUpdate
from src.utils.errors import TaskNotFoundError, UnauthorizedAccessError


class TaskService:
    """Service layer for task CRUD operations with user ownership enforcement.

    This service ensures:
    - All operations are scoped to the authenticated user
    - Cross-user access attempts return 403 Forbidden
    - Database transactions are properly managed
    - Business logic is enforced (validation, ownership, integrity)

    Attributes:
        db: Database session for queries
        user_id: Authenticated user's ID (all operations scoped to this user)
    """

    def __init__(self, db: Session, user_id: str):
        """Initialize TaskService with database session and user context.

        Args:
            db: SQLModel database session
            user_id: Authenticated user's ID (from JWT or dependency)
        """
        self.db = db
        self.user_id = user_id

    def create_task(self, data: TaskCreate) -> Task:
        """Create a new task for the authenticated user.

        Args:
            data: Task creation data (title, description, status, priority, tags)

        Returns:
            Task: Created task with auto-generated ID and timestamps

        Raises:
            ValidationError: If data violates validation rules
        """
        # Create task with user ownership
        task = Task(
            user_id=self.user_id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            tags=data.tags,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Persist to database
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        tags: Optional[List[str]] = None,
        sort_by: Optional[str] = None
    ) -> List[Task]:
        """List all tasks for the authenticated user with optional filters.

        Args:
            status: Filter by task status (optional)
            priority: Filter by task priority (optional)
            tags: Filter by tags (task must contain ALL specified tags) (optional)
            sort_by: Sort field (created_at, updated_at, priority, status) (optional)

        Returns:
            List[Task]: List of tasks matching filters, sorted as specified

        Note:
            Results are ALWAYS filtered by user_id (enforces user ownership).
        """
        # Start with base query filtered by user_id (CRITICAL for security)
        query = select(Task).where(Task.user_id == self.user_id)

        # Apply status filter
        if status is not None:
            query = query.where(Task.status == status)

        # Apply priority filter
        if priority is not None:
            query = query.where(Task.priority == priority)

        # Apply tags filter (task must contain ALL specified tags)
        if tags:
            for tag in tags:
                query = query.where(Task.tags.contains([tag]))

        # Apply sorting
        if sort_by == "created_at":
            query = query.order_by(Task.created_at.desc())
        elif sort_by == "updated_at":
            query = query.order_by(Task.updated_at.desc())
        elif sort_by == "priority":
            # Sort by priority: high > medium > low
            priority_order = {
                TaskPriority.HIGH: 3,
                TaskPriority.MEDIUM: 2,
                TaskPriority.LOW: 1
            }
            query = query.order_by(Task.priority.desc())
        elif sort_by == "status":
            # Sort by status: todo > in-progress > completed
            query = query.order_by(Task.status)
        else:
            # Default: sort by created_at descending (newest first)
            query = query.order_by(Task.created_at.desc())

        # Execute query
        tasks = self.db.exec(query).all()
        return list(tasks)

    def get_task_by_id(self, task_id: UUID) -> Task:
        """Get a single task by ID.

        Args:
            task_id: UUID of the task to retrieve

        Returns:
            Task: The requested task

        Raises:
            TaskNotFoundError: If task doesn't exist for this user
            UnauthorizedAccessError: If task belongs to another user (403)

        Security:
            MUST filter by user_id to prevent cross-user access.
            Returns 403 (not 404) for other users' tasks to avoid info disclosure.
        """
        # Query with user_id filter (CRITICAL for security)
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == self.user_id
        )
        task = self.db.exec(statement).first()

        if not task:
            # Check if task exists for another user (to return 403 instead of 404)
            other_user_statement = select(Task).where(Task.id == task_id)
            other_user_task = self.db.exec(other_user_statement).first()

            if other_user_task:
                # Task exists but belongs to another user - return 403
                raise UnauthorizedAccessError(
                    "Access denied: task belongs to another user"
                )
            else:
                # Task doesn't exist at all - return 404
                raise TaskNotFoundError(task_id=str(task_id))

        return task

    def update_task(self, task_id: UUID, data: TaskUpdate) -> Task:
        """Update an existing task with partial data (PATCH semantics).

        Args:
            task_id: UUID of the task to update
            data: Partial task data (only provided fields are updated)

        Returns:
            Task: Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist for this user
            UnauthorizedAccessError: If task belongs to another user (403)
            ValidationError: If update data violates validation rules

        Note:
            Only fields present in data (non-None) are updated.
            This implements PATCH semantics (partial update).
        """
        # Retrieve task (enforces ownership)
        task = self.get_task_by_id(task_id)

        # Update only fields that are provided (PATCH semantics)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(task, field, value)

        # Update timestamp
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def delete_task(self, task_id: UUID) -> None:
        """Delete a task by ID.

        Args:
            task_id: UUID of the task to delete

        Raises:
            TaskNotFoundError: If task doesn't exist for this user
            UnauthorizedAccessError: If task belongs to another user (403)

        Note:
            This is a hard delete (removes from database).
            Consider soft delete (status flag) for production systems.
        """
        # Retrieve task (enforces ownership)
        task = self.get_task_by_id(task_id)

        # Delete from database
        self.db.delete(task)
        self.db.commit()
