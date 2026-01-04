from typing import Generic, TypeVar, Optional
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")

class Meta(BaseModel):
    """Metadata for API responses."""
    request_id: Optional[str] = Field(None, description="Unique request identifier for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp in UTC")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }

class Envelope(BaseModel, Generic[T]):
    """Generic response envelope wrapping data with metadata."""
    data: T = Field(..., description="Response payload")
    meta: Meta = Field(default_factory=Meta, description="Response metadata")

class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")

class PaginatedData(BaseModel, Generic[T]):
    """Paginated data container."""
    items: list[T] = Field(..., description="List of items for current page")
    pagination: PaginationMeta = Field(..., description="Pagination information")

class PaginatedEnvelope(BaseModel, Generic[T]):
    """Response envelope for paginated lists."""
    data: PaginatedData[T] = Field(..., description="Paginated response data")
    meta: Meta = Field(default_factory=Meta, description="Response metadata")
