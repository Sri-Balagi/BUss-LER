from abc import ABC
from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field


class IRuntimeIdentity(BaseModel, ABC):
    """
    Value object establishing execution lineage.
    """

    session_id: UUID4 = Field(default_factory=uuid4)
    execution_id: UUID4 = Field(default_factory=uuid4)
    correlation_id: UUID4 = Field(default_factory=uuid4)
    parent_execution_id: UUID4 | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
