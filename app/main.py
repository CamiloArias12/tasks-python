from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from app.core.config import settings
from app.api.v1.routes import auth_route, tasks_route
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.schemas.response import Envelope, Meta

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API for managing Tasks with JWT Authentication",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENABLE_DOCS else None,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
)

# Add Middleware
app.add_middleware(RequestIDMiddleware)

# Register Exception Handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include Routers
app.include_router(auth_route.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(tasks_route.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])

@app.get("/", response_model=Envelope[dict])
def root(request: Request):
    return Envelope(
        data={"message": "Welcome to the Technical Test API"},
        meta=Meta(request_id=getattr(request.state, "request_id", None))
    )
