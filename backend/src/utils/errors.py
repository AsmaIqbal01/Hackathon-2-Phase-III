"""Custom exception classes for task-related and authentication errors."""


class AuthError(Exception):
    """Exception for authentication failures.

    Raised when JWT token is missing, invalid, or expired.
    Returns 401 Unauthorized status code.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (always 401)
    """

    def __init__(self, message: str = "Authentication required"):
        self.message = message
        self.status_code = 401
        super().__init__(self.message)


class TaskError(Exception):
    """Base exception for task-related errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code for the error response
    """

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class TaskNotFoundError(TaskError):
    """Exception raised when a task is not found.

    Used when a task with the given ID does not exist for the authenticated user.
    Returns 404 Not Found status code.
    """

    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task with id '{task_id}' not found",
            status_code=404
        )
        self.task_id = task_id


class UnauthorizedAccessError(TaskError):
    """Exception raised for unauthorized access attempts.

    Used when a user attempts to access, modify, or delete a task they don't own.
    Returns 403 Forbidden status code (not 404) to prevent information disclosure.
    """

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=403
        )


class ValidationError(TaskError):
    """Exception raised for validation errors.

    Used when input data fails validation rules.
    Returns 400 Bad Request status code.
    """

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        if field:
            message = f"{field}: {message}"
        super().__init__(message=message, status_code=400)
