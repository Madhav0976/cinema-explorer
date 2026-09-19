from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated container for catalog discovery."""
    items: list[T]
    total: int = Field(..., description="Total number of items matching filters")
    page: int = Field(..., description="Current 1-based page number")
    page_size: int = Field(..., description="Number of items requested per page")
    total_pages: int = Field(..., description="Total available pages")
    has_next: bool = Field(False, description="Whether a subsequent page exists")
    has_previous: bool = Field(False, description="Whether a preceding page exists")

