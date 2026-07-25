"""Connector persistent state models."""
from __future__ import annotations
from datetime import UTC, datetime
from typing import Any
from pydantic import BaseModel, Field


class ConnectorState(BaseModel):
    """Persistent state for a connector profile. Survives restarts."""

    connector_id: str
    profile_id: str = "default"
    last_sync: datetime | None = None
    cursor: str | None = None          # pagination/incremental cursor
    delta_token: str | None = None     # Microsoft Graph delta token
    etag: str | None = None            # HTTP ETag for conditional requests
    page_token: str | None = None      # Google API page token
    checkpoint: dict[str, Any] | None = None
    subscription_id: str | None = None
    webhook_id: str | None = None
    rate_limit_window: datetime | None = None
    rate_limit_remaining: int | None = None
    custom: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Update the ``updated_at`` timestamp."""
        self.updated_at = datetime.now(UTC)
