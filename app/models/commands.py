import uuid
from typing import Dict, Any, Optional
from pydantic import Field

from app.models.schemas import DomainBaseModel
from app.models.enums import MemoryCategory, MemorySource


class CreateMemoryCommand(DomainBaseModel):
    """Command to create a new memory."""
    twin_id: uuid.UUID
    content: str
    title: str = "Untitled"
    source: MemorySource = MemorySource.USER_INPUT
    memory_category: MemoryCategory = MemoryCategory.OBSERVATION
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class DeleteMemoryCommand(DomainBaseModel):
    """Command to soft-delete a memory."""
    memory_id: uuid.UUID


class RestoreMemoryCommand(DomainBaseModel):
    """Command to restore a soft-deleted memory."""
    memory_id: uuid.UUID
