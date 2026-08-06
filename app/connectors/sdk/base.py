"""BizOS Connector SDK Base Framework — Phase 2 Production Grade

Defines:
  - ConnectorOperatingMode       (DEVELOPER_MODE vs PRODUCTION_OAUTH_MODE)
  - ConnectorResourceType        (canonical resource identifiers)
  - ConnectorEventType           (canonical event identifiers)
  - ConnectorCapabilities        (formal capability contract)
  - ConnectorExecuteRequest      (unified execute() input schema)
  - BaseConnector                (full 22-method lifecycle abstract base)

Design principle:  The orchestration layer NEVER calls connector-specific methods.
It always calls connector.execute(capability=...) or the explicit lifecycle methods.
This allows Planner Agents to compose workflows without hardcoding connector logic.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

import structlog
from pydantic import BaseModel, Field

from app.domain.shared.context import ExecutionContext

logger = structlog.get_logger(__name__)


# ── Operating Mode ────────────────────────────────────────────────────────────


class ConnectorOperatingMode(str, Enum):
    """Architectural separation of Connector Operating Modes."""
    DEVELOPER_MODE = "DEVELOPER_MODE"
    PRODUCTION_OAUTH_MODE = "PRODUCTION_OAUTH_MODE"


# ── Resource & Event Type Enums ───────────────────────────────────────────────


class ConnectorResourceType(str, Enum):
    """Canonical resource type identifiers across all connectors."""
    # File system resources
    FILE = "file"
    FOLDER = "folder"
    DRIVE = "drive"
    SHARED_DRIVE = "shared_drive"
    DOCUMENT_LIBRARY = "document_library"
    # Collaboration
    PERMISSION = "permission"
    REVISION = "revision"
    COMMENT = "comment"
    SHORTCUT = "shortcut"
    LABEL = "label"
    # Calendar
    CALENDAR = "calendar"
    EVENT = "event"
    ATTENDEE = "attendee"
    FREE_BUSY = "free_busy"
    # Productivity
    PAGE = "page"
    DATABASE = "database"
    BLOCK = "block"
    # Platform
    SITE = "site"
    LIST = "list"
    LIST_ITEM = "list_item"
    # Auth
    USER = "user"
    WORKSPACE = "workspace"
    # Sync
    DELTA_CHANGE = "delta_change"
    WEBHOOK_SUBSCRIPTION = "webhook_subscription"


class ConnectorEventType(str, Enum):
    """Canonical event type identifiers for webhook/watch subscriptions."""
    FILE_CREATED = "file.created"
    FILE_MODIFIED = "file.modified"
    FILE_DELETED = "file.deleted"
    FILE_MOVED = "file.moved"
    FILE_SHARED = "file.shared"
    PERMISSION_CHANGED = "permission.changed"
    COMMENT_ADDED = "comment.added"
    EVENT_CREATED = "event.created"
    EVENT_MODIFIED = "event.modified"
    EVENT_DELETED = "event.deleted"
    PAGE_CREATED = "page.created"
    PAGE_UPDATED = "page.updated"
    DATABASE_UPDATED = "database.updated"
    LIST_ITEM_CREATED = "list_item.created"
    LIST_ITEM_UPDATED = "list_item.updated"
    LIST_ITEM_DELETED = "list_item.deleted"


# ── Capabilities Contract ─────────────────────────────────────────────────────


class ConnectorCapabilities(BaseModel):
    """Formal contract declaring connector capabilities, actions, and discoverable metadata."""
    connector_id: str
    display_name: str
    version: str = "4.0.0"
    family: str = "general"
    supports_realtime: bool = True
    supports_polling: bool = True
    supports_streaming: bool = False
    supports_batch: bool = True
    supports_delta_sync: bool = False
    supported_actions: List[str] = Field(default_factory=list)
    supported_resources: List[ConnectorResourceType] = Field(default_factory=list)
    supported_events: List[ConnectorEventType] = Field(default_factory=list)
    supported_execution_modes: List[str] = Field(
        default_factory=lambda: ["SIMULATION", "DRY_RUN", "PRODUCTION"]
    )
    required_scopes: List[str] = Field(default_factory=list)
    auth_type: str = "oauth2"
    webhook_support: bool = False
    multi_account_support: bool = True
    parent_connector_id: Optional[str] = None
    operating_mode: ConnectorOperatingMode = ConnectorOperatingMode.PRODUCTION_OAUTH_MODE


# ── Unified Execute Request ───────────────────────────────────────────────────


class ConnectorExecuteRequest(BaseModel):
    """Unified input schema for connector.execute() — keeps orchestration layer provider-agnostic."""
    capability: str
    params: Dict[str, Any] = Field(default_factory=dict)
    user_id: str = "default"
    tenant_id: str = "default_tenant"
    account_id: str = "default"
    idempotency_key: Optional[str] = None
    page_token: Optional[str] = None
    page_size: int = 100


# ── Abstract Base Connector ───────────────────────────────────────────────────


class BaseConnector(ABC):
    """Abstract Base Class for all BizOS Connectors.

    All connectors MUST implement the 22-method lifecycle contract.
    The orchestration layer exclusively calls execute() for capability dispatch —
    it never calls provider-specific methods directly.

    Standard lifecycle order:
        authenticate() → [active session] → execute() / batch() / watch() / sync()
                      → refresh()         (transparent token refresh)
                      → disconnect()      (explicit teardown)
    """

    # ── Identity ──────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def connector_id(self) -> str:
        """Unique identifier of this connector (e.g. 'google_drive')."""

    @property
    @abstractmethod
    def capabilities(self) -> ConnectorCapabilities:
        """Declared capability contract for this connector."""

    # ── Lifecycle — Auth ──────────────────────────────────────────────────────

    async def authenticate(
        self, user_email: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        return {"status": "unsupported"}

    async def handle_callback(
        self, code: str, state: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        return {"status": "unsupported"}

    async def disconnect(
        self, user_id: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        return {"status": "disconnected"}

    async def refresh(
        self, user_id: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        return {"status": "refreshed"}

    # ── Lifecycle — Introspection ─────────────────────────────────────────────

    async def health(self) -> Dict[str, Any]:
        """Check connector health."""
        return {"status": "healthy", "connector": self.connector_id}

    async def capabilities_report(self) -> Dict[str, Any]:
        """Return the full capabilities contract as a serializable dict."""
        return self.get_metadata()

    async def permissions(
        self, user_id: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        return {"scopes": getattr(self.capabilities, "required_scopes", [])}

    async def metadata(self) -> Dict[str, Any]:
        """Return connector metadata."""
        return self.get_metadata()

    # ── Lifecycle — CRUD ─────────────────────────────────────────────────────

    async def search(
        self, query: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {"results": []}

    async def list(
        self, resource_type: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {"items": []}

    async def get(
        self, resource_type: str, resource_id: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    async def create(
        self, resource_type: str, data: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    async def update(
        self, resource_type: str, resource_id: str, data: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    async def delete(
        self, resource_type: str, resource_id: str, context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    async def move(
        self,
        resource_type: str,
        resource_id: str,
        destination: Dict[str, Any],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        return {}

    async def copy(
        self,
        resource_type: str,
        resource_id: str,
        destination: Dict[str, Any],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        return {}

    async def share(
        self, resource_type: str, resource_id: str, share_config: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    # ── Lifecycle — Data Transfer ─────────────────────────────────────────────

    async def export(
        self,
        resource_type: str,
        resource_id: str,
        export_format: str,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        return {}

    async def import_data(
        self, resource_type: str, data: bytes, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    # ── Lifecycle — Real-time & Sync ─────────────────────────────────────────

    async def watch(
        self,
        resource_type: str,
        resource_id: Optional[str],
        webhook_url: str,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        return {}

    async def sync(
        self,
        resource_type: str,
        sync_token: Optional[str],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        return {}

    # ── Lifecycle — Batch & Universal Execute ─────────────────────────────────

    async def batch(
        self, operations: List[Dict[str, Any]], context: ExecutionContext
    ) -> Dict[str, Any]:
        return {}

    async def execute(
        self, request: ConnectorExecuteRequest, context: ExecutionContext
    ) -> Dict[str, Any]:
        """Universal capability dispatcher default.
        Delegates to execute_action for backward compatibility.
        """
        cap = getattr(request, "capability_id", getattr(request, "capability", ""))
        params = getattr(request, "parameters", getattr(request, "params", {}))
        return await self.execute_action(cap, params, context)

    # ── Legacy compatibility bridge ───────────────────────────────────────────

    async def execute_action(
        self, action: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        """Compatibility shim: routes old execute_action() calls to new execute()."""
        req = ConnectorExecuteRequest(capability=action, params=params)
        return await self.execute(req, context)

    async def health_check(self) -> Dict[str, Any]:
        """Compatibility shim: routes old health_check() to new health()."""
        return await self.health()

    async def refresh_tokens(self, account_id: str = "default") -> Dict[str, Any]:
        """Compatibility shim: routes old refresh_tokens() to new refresh()."""
        return await self.refresh(user_id=account_id)

    # ── Metadata ──────────────────────────────────────────────────────────────

    def get_metadata(self) -> Dict[str, Any]:
        """Return rich discoverable metadata for BizOS Studio, CLI, API, and Planner Agents."""
        caps = self.capabilities
        return {
            "connector_id": caps.connector_id,
            "display_name": caps.display_name,
            "version": caps.version,
            "family": caps.family,
            "supports_realtime": caps.supports_realtime,
            "supports_polling": caps.supports_polling,
            "supports_streaming": caps.supports_streaming,
            "supports_batch": caps.supports_batch,
            "supports_delta_sync": caps.supports_delta_sync,
            "supported_actions": caps.supported_actions,
            "supported_resources": [r.value for r in caps.supported_resources],
            "supported_events": [e.value for e in caps.supported_events],
            "supported_execution_modes": caps.supported_execution_modes,
            "required_scopes": caps.required_scopes,
            "auth_type": caps.auth_type,
            "webhook_support": caps.webhook_support,
            "multi_account_support": caps.multi_account_support,
            "parent_connector_id": caps.parent_connector_id,
            "operating_mode": caps.operating_mode.value,
        }
