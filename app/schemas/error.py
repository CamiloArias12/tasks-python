from typing import Optional, List, Any
from pydantic import BaseModel, Field

class FieldError(BaseModel):
    """Individual field validation error."""
    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Error message for this field")

class ProblemDetails(BaseModel):
    """
    RFC 7807 Problem Details for HTTP APIs.
    Provides a standardized format for error responses.
    """
    type: str = Field(
        ..., 
        description="URI reference identifying the problem type",
        example="https://api.example.com/errors/validation"
    )
    title: str = Field(
        ..., 
        description="Short, human-readable summary of the problem",
        example="Validation Error"
    )
    status: int = Field(
        ..., 
        description="HTTP status code",
        ge=400,
        le=599,
        example=422
    )
    detail: str = Field(
        ..., 
        description="Human-readable explanation specific to this occurrence",
        example="The request body contains invalid data"
    )
    instance: str = Field(
        ..., 
        description="URI reference identifying the specific occurrence",
        example="/api/v1/tasks"
    )
    errors: Optional[List[FieldError]] = Field(
        None, 
        description="List of field-level validation errors"
    )
    request_id: Optional[str] = Field(
        None, 
        description="Unique request identifier for tracing"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "https://api.example.com/errors/validation",
                "title": "Validation Error",
                "status": 422,
                "detail": "Invalid request payload",
                "instance": "/api/v1/tasks",
                "errors": [
                    {"field": "title", "message": "Field required"}
                ],
                "request_id": "req_abc123"
            }
        }
