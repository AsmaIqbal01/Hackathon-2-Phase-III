"""MCP Server for task management operations.

This server exposes task CRUD operations as MCP tools that can be called
by AI agents. All tools delegate to TaskService for business logic.
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from uuid import UUID
from typing import Optional
from src.services.task_service import TaskService
from src.schemas.task_schemas import TaskCreate, TaskUpdate
from src.models.task import TaskStatus, TaskPriority
from src.mcp.context import get_context_user_id, get_db_session
from src.utils.errors import TaskNotFoundError, UnauthorizedAccessError, ValidationError


# Initialize MCP Server
app = Server("task-management-mcp")


# ============================================================================
# MCP Tools (T021-T025)
# ============================================================================


@app.tool()
async def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: list[str] = None
) -> dict:
    """Create a new task.

    Args:
        title: Task title (required)
        description: Task description (optional, default: "")
        priority: Task priority - "low", "medium", or "high" (default: "medium")
        tags: List of tags for categorization (optional, default: [])

    Returns:
        dict: {"success": bool, "task_id": str, "message": str}
    """
    try:
        # Get user context and database session
        user_id = get_context_user_id()
        db = next(get_db_session())

        # Create TaskService instance
        service = TaskService(db, user_id)

        # Parse priority
        try:
            task_priority = TaskPriority(priority)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'."
            }

        # Create task
        task_data = TaskCreate(
            title=title,
            description=description if description else None,
            status=TaskStatus.TODO,
            priority=task_priority,
            tags=tags or []
        )

        task = service.create_task(task_data)

        return {
            "success": True,
            "task_id": str(task.id),
            "message": f"Created task: {task.title}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
async def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    sort_by: Optional[str] = None
) -> dict:
    """List tasks with optional filters.

    Args:
        status: Filter by status - "todo", "in-progress", or "completed" (optional)
        priority: Filter by priority - "low", "medium", or "high" (optional)
        tags: Filter by tags - tasks must contain ALL specified tags (optional)
        sort_by: Sort field - "created_at", "updated_at", "priority", "status" (optional)

    Returns:
        dict: {"success": bool, "tasks": list[dict], "count": int}
    """
    try:
        # Get user context and database session
        user_id = get_context_user_id()
        db = next(get_db_session())

        # Create TaskService instance
        service = TaskService(db, user_id)

        # Parse status and priority if provided
        task_status = TaskStatus(status) if status else None
        task_priority = TaskPriority(priority) if priority else None

        # List tasks
        tasks = service.list_tasks(
            status=task_status,
            priority=task_priority,
            tags=tags,
            sort_by=sort_by
        )

        # Convert tasks to dict
        tasks_data = [
            {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "tags": task.tags,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]

        return {
            "success": True,
            "tasks": tasks_data,
            "count": len(tasks_data)
        }

    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid parameter: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
async def complete_task(task_id: str) -> dict:
    """Mark a task as completed.

    Args:
        task_id: UUID of the task to complete

    Returns:
        dict: {"success": bool, "task": dict}
    """
    try:
        # Get user context and database session
        user_id = get_context_user_id()
        db = next(get_db_session())

        # Create TaskService instance
        service = TaskService(db, user_id)

        # Update task status to completed
        task_update = TaskUpdate(status=TaskStatus.COMPLETED)
        task = service.update_task(UUID(task_id), task_update)

        return {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.title,
                "status": task.status.value,
                "updated_at": task.updated_at.isoformat()
            }
        }

    except (TaskNotFoundError, UnauthorizedAccessError) as e:
        return {
            "success": False,
            "error": str(e)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid task_id format: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> dict:
    """Update task fields.

    Args:
        task_id: UUID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status - "todo", "in-progress", or "completed" (optional)
        priority: New priority - "low", "medium", or "high" (optional)
        tags: New tags list (optional)

    Returns:
        dict: {"success": bool, "task": dict}
    """
    try:
        # Get user context and database session
        user_id = get_context_user_id()
        db = next(get_db_session())

        # Create TaskService instance
        service = TaskService(db, user_id)

        # Build update data (only include provided fields)
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = TaskStatus(status)
        if priority is not None:
            update_data["priority"] = TaskPriority(priority)
        if tags is not None:
            update_data["tags"] = tags

        # Update task
        task_update = TaskUpdate(**update_data)
        task = service.update_task(UUID(task_id), task_update)

        return {
            "success": True,
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "tags": task.tags,
                "updated_at": task.updated_at.isoformat()
            }
        }

    except (TaskNotFoundError, UnauthorizedAccessError) as e:
        return {
            "success": False,
            "error": str(e)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid parameter: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
async def delete_task(task_id: str) -> dict:
    """Delete a task.

    Note: This operation requires confirmation from the user via the agent layer.

    Args:
        task_id: UUID of the task to delete

    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        # Get user context and database session
        user_id = get_context_user_id()
        db = next(get_db_session())

        # Create TaskService instance
        service = TaskService(db, user_id)

        # Delete task
        service.delete_task(UUID(task_id))

        return {
            "success": True,
            "message": "Task deleted successfully"
        }

    except (TaskNotFoundError, UnauthorizedAccessError) as e:
        return {
            "success": False,
            "error": str(e)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid task_id format: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def main():
    """Main entry point for MCP server.

    Runs the MCP server with stdio transport, listening for tool calls
    from the Master Agent.
    """
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
