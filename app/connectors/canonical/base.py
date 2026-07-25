"""Canonical data model base — all vendor data maps to canonical objects."""
from __future__ import annotations
import uuid
from datetime import UTC, datetime
from typing import Any
from pydantic import BaseModel, Field


class CanonicalObject(BaseModel):
    """
    Base class for all canonical BizOS business objects.

    Vendor-specific data never leaves the connector boundary as raw objects.
    Every connector maps its native API responses to a CanonicalObject subclass.
    """

    biz_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="BizOS internal ID")
    source_connector: str = Field(..., description="Connector that produced this object")
    source_id: str = Field(..., description="Vendor-native object ID")
    source_profile: str = Field(default="default")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw: dict[str, Any] | None = Field(
        default=None,
        description="Optional raw vendor payload for debugging. Not persisted in production.",
    )

    class Config:
        extra = "allow"
