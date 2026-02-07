"""Error response schemas for standardized API error formatting.

All API errors follow the format:
{
    "error": {
        "code": <http_status_code>,
        "message": "<human_readable_message>"
    }
}
"""
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail containing status code and message.

    Attributes:
        code: HTTP status code (400, 401, 403, 404, 422, 500)
        message: Human-readable error message
    """
    code: int = Field(
        ...,
        description="HTTP status code",
        ge=100,
        le=599,
        examples=[400, 404, 500]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        min_length=1,
        examples=["Task not found", "Validation failed"]
    )


class ErrorResponse(BaseModel):
    """Standardized error response wrapper.

    All API errors are wrapped in this structure for consistency.

    Attributes:
        error: Error details containing code and message
    """
    error: ErrorDetail = Field(
        ...,
        description="Error details"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "error": {
                        "code": 404,
                        "message": "Task not found"
                    }
                },
                {
                    "error": {
                        "code": 400,
                        "message": "user_id is required"
                    }
                }
            ]
        }
