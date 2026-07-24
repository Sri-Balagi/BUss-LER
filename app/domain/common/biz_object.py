from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def _now_utc() -> datetime:
    """Returns the current UTC time in a Python 3.10+ compatible way."""
    return datetime.now(UTC)

class BizObject(BaseModel):
    """
    The root domain entity for BizOS.
    All core OS entities MUST inherit from this class to guarantee
    consistency, ownership, and deterministic serialization across the System Bus.
    """

    id: UUID = Field(default_factory=uuid4, description="Globally unique identifier.")

    tenant_id: UUID | None = Field(default=None, description="Identifier for the overarching tenant organization.")
    owner_id: UUID | None = Field(default=None, description="Specific UUID of the user or twin that owns this object.")
    correlation_id: UUID | None = Field(default=None, description="Used for distributed tracing across workflows.")

    version: int = Field(default=1, description="Integer for optimistic concurrency control.")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary key-value dictionary for extensibility.")
    tags: list[str] = Field(default_factory=list, description="List of string labels for filtering and categorization.")

    created_at: datetime = Field(default_factory=_now_utc, description="UTC timestamp of creation.")
    updated_at: datetime = Field(default_factory=_now_utc, description="UTC timestamp of the last modification.")

    def update(self, **kwargs: Any) -> None:
        """
        Updates the object's properties, increments the version, and sets updated_at.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)

        self.version += 1
        self.updated_at = _now_utc()
