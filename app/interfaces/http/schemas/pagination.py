"""Pagination models for BizOS list endpoints.

Provides a consistent paginated response wrapper used by all
list endpoints across the API. Every endpoint that returns a
collection uses this structure.
"""

from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse[T](BaseModel):
    """A generic paginated response wrapper.

    Attributes:
        items: The page of results.
        total: Total number of matching records across all pages.
        limit: Maximum items per page (as requested).
        offset: Number of items skipped from the beginning.
        has_more: Whether more items exist beyond this page.

    Example response:
        {
            "items": [...],
            "total": 42,
            "limit": 20,
            "offset": 0,
            "has_more": true
        }
    """

    items: list[T] = Field(description="The page of results.")
    total: int = Field(ge=0, description="Total number of matching records.")
    limit: int = Field(ge=1, description="Maximum items per page.")
    offset: int = Field(ge=0, description="Number of items skipped.")
    has_more: bool = Field(description="Whether more items exist beyond this page.")
