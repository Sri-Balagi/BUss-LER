import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import Field

from app.models.schemas import DomainBaseModel
from app.models.enums import MemoryCategory


class MemorySearchQuery(DomainBaseModel):
    """Encapsulates parameters for searching memories."""
    twin_id: uuid.UUID
    query_text: str = Field(..., description="The semantic search string.")
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    category: Optional[MemoryCategory] = None
    min_importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_deleted: bool = Field(default=False)
