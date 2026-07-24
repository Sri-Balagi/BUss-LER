from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class RegistrySnapshot(BaseModel):
    """
    Represents a point-in-time state of a Registry.
    Used for backups, migrations, and distributed synchronization.
    """
    registry_name: str = Field(..., description="Name of the registry (e.g., 'ToolRegistry').")
    version: str = Field(default="1.0", description="Schema version of the snapshot format.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When this snapshot was taken.")
    items: list[dict[str, Any]] = Field(default_factory=list, description="Serialized items.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional context about the registry.")

    def to_json(self) -> str:
        """Serializes the snapshot to a JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_data: str) -> "RegistrySnapshot":
        """Deserializes a snapshot from a JSON string."""
        return cls.model_validate_json(json_data)
