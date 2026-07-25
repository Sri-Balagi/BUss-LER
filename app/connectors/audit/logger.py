"""Connector Audit Framework."""
from __future__ import annotations
import logging
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuditAction(StrEnum):
    INSTALLED = "INSTALLED"
    UNINSTALLED = "UNINSTALLED"
    AUTHENTICATED = "AUTHENTICATED"
    TOKEN_REFRESHED = "TOKEN_REFRESHED"
    PERMISSION_CHANGED = "PERMISSION_CHANGED"
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"
    SYNC_STARTED = "SYNC_STARTED"
    SYNC_COMPLETED = "SYNC_COMPLETED"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    ERROR_OCCURRED = "ERROR_OCCURRED"


class ConnectorAuditEvent(BaseModel):
    audit_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    connector_id: str
    profile_id: str = "default"
    action: AuditAction
    result: str  # "SUCCESS", "FAILURE"
    user_id: str | None = None
    tenant_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConnectorAuditLogger:
    """Publishes structured connector audit events."""

    def __init__(self, bus: Any | None = None) -> None:
        self._bus = bus

    async def log(
        self,
        connector_id: str,
        action: AuditAction | str,
        result: str,
        profile_id: str = "default",
        user_id: str | None = None,
        tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ConnectorAuditEvent:
        action_enum = AuditAction(action) if isinstance(action, str) else action
        event = ConnectorAuditEvent(
            connector_id=connector_id,
            profile_id=profile_id,
            action=action_enum,
            result=result,
            user_id=user_id,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )
        logger.info(
            "ConnectorAudit [%s]: %s - %s - %s",
            connector_id,
            event.action.value,
            event.result,
            event.metadata,
        )
        if self._bus is not None:
            await self._bus.publish(f"connector.audit.{connector_id}", event)
        return event
