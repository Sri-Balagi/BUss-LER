"""BizOS ConnectorSession Abstraction

Lightweight session object passed to runtime, planner, and workflow engines.
Raw credentials and OAuth tokens remain isolated within ConnectorAuthVault.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.connectors.sdk.permissions import ConnectorPermission
from app.shared.enums import ExecutionMode


class ConnectorLifecycleState(str, Enum):
    """Lifecycle state machine for BizOS connectors."""
    UNCONFIGURED = "UNCONFIGURED"
    AUTHORIZING = "AUTHORIZING"
    CONNECTED = "CONNECTED"
    ACTIVE = "ACTIVE"
    TOKEN_REFRESHING = "TOKEN_REFRESHING"
    EXPIRED = "EXPIRED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class ConnectorSession(BaseModel):
    """Encapsulates an active connector session without exposing raw tokens."""
    session_id: str = Field(default_factory=lambda: f"csess_{uuid.uuid4().hex[:12]}")
    tenant_id: str = "default_tenant"
    provider_id: str
    account_id: str = "default"
    permissions: List[ConnectorPermission] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.PRODUCTION
    lifecycle_state: ConnectorLifecycleState = ConnectorLifecycleState.ACTIVE
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_valid(self) -> bool:
        """Verifies if the session is currently active and not expired."""
        if self.lifecycle_state not in (ConnectorLifecycleState.CONNECTED, ConnectorLifecycleState.ACTIVE):
            return False
        if self.expires_at and datetime.now(timezone.utc) >= self.expires_at:
            return False
        return True


class ConnectorSessionManager:
    """Manages creation and lookup of ConnectorSessions."""

    _sessions: Dict[str, ConnectorSession] = {}

    @classmethod
    def create_session(
        cls,
        provider_id: str,
        tenant_id: str = "default_tenant",
        account_id: str = "default",
        permissions: Optional[List[ConnectorPermission]] = None,
        execution_mode: ExecutionMode = ExecutionMode.PRODUCTION,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConnectorSession:
        session = ConnectorSession(
            tenant_id=tenant_id,
            provider_id=provider_id,
            account_id=account_id,
            permissions=permissions or [],
            execution_mode=execution_mode,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        cls._sessions[session.session_id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> Optional[ConnectorSession]:
        return cls._sessions.get(session_id)
