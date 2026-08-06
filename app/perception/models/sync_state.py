from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class SourceSyncState(BaseModel):
    """Delta synchronization state for an observation source."""

    source_id: str
    tenant_id: str = Field(default="default")
    last_synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sync_token: str | None = Field(default=None, description="Page token, change token, or start history ID")
    cursor: str | None = Field(default=None, description="Generic pagination cursor")
    metadata: dict[str, Any] = Field(default_factory=dict)
