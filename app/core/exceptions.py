import logging
from typing import Union
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas.error import ProblemDetails, FieldError

logger = logging.getLogger(__name__)

def get_request_id(request: Request) -> str:
    """Extract request ID from request state."""
    return getattr(request.state, "request_id", "unknown")

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPException and convert to RFC 7807 Problem Details format.
    """
    request_id = get_request_id(request)
    
    # Map status codes to error types
    error_type_map = {
        400: "bad-request",
        401: "unauthorized",
        403: "forbidden",
        404: "not-found",
        409: "conflict",
        422: "validation-error",
        429: "rate-limit-exceeded",
    }
    
    error_type = error_type_map.get(exc.status_code, "error")
    base_url = str(request.base_url).rstrip("/")
    
    problem = ProblemDetails(
        type=f"{base_url}/errors/{error_type}",
        title=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url.path),
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
    )

async def validation_exception_handler(
    request: Request, 
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handle Pydantic validation errors and convert to RFC 7807 format with field details.
    """
    request_id = get_request_id(request)
    base_url = str(request.base_url).rstrip("/")
    
    # Extract field errors from Pydantic validation errors
    field_errors = []
    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        field_errors.append(
            FieldError(
                field=field_name or "unknown",
                message=error["msg"]
            )
        )
    
    problem = ProblemDetails(
        type=f"{base_url}/errors/validation-error",
        title="Validation Error",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="The request contains invalid or missing fields",
        instance=str(request.url.path),
        errors=field_errors,
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=problem.model_dump(exclude_none=True),
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions. Log the full error but return a safe response to client.
    """
    request_id = get_request_id(request)
    base_url = str(request.base_url).rstrip("/")
    
    # Log the full exception with stacktrace
    logger.error(
        f"Unhandled exception for request {request_id}: {exc}",
        exc_info=True,
        extra={"request_id": request_id, "path": request.url.path}
    )
    
    # Return safe error response (no stacktrace)
    problem = ProblemDetails(
        type=f"{base_url}/errors/internal-server-error",
        title="Internal Server Error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred. Please try again later.",
        instance=str(request.url.path),
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem.model_dump(exclude_none=True),
    )
