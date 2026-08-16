"""BizOS Connector SDK Base Framework

Defines ConnectorCapabilities, ConnectorOperatingMode (DEVELOPER_MODE vs PRODUCTION_OAUTH_MODE),
and BaseConnector abstraction.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.domain.shared.context import ExecutionContext


class ConnectorOperatingMode(str, Enum):
    """Architectural separation of Connector Operating Modes."""
    DEVELOPER_MODE = "DEVELOPER_MODE"  # Uses .env / SMTP App Passwords / Dev keys for local testing
    PRODUCTION_OAUTH_MODE = "PRODUCTION_OAUTH_MODE"  # Zero manual secrets; 100% OAuth & Vault token driven


class ConnectorCapabilities(BaseModel):
    """Formal contract declaring connector capabilities, actions, and discoverable metadata."""
    connector_id: str
    display_name: str
    version: str = "2.0.0"
    family: str = "general"
    supports_realtime: bool = True
    supports_polling: bool = False
    supported_actions: List[str] = Field(default_factory=list)
    supported_execution_modes: List[str] = Field(default_factory=lambda: ["SIMULATION", "DRY_RUN", "PRODUCTION"])
    required_scopes: List[str] = Field(default_factory=list)
    auth_type: str = "oauth2"
    webhook_support: bool = False
    multi_account_support: bool = True
    parent_connector_id: Optional[str] = None
    operating_mode: ConnectorOperatingMode = ConnectorOperatingMode.PRODUCTION_OAUTH_MODE


class BaseConnector(ABC):
    """Abstract Base Class for all BizOS Connectors."""

    @property
    @abstractmethod
    def connector_id(self) -> str:
        """Unique identifier of the connector."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ConnectorCapabilities:
        """Declared capabilities of the connector."""
        pass

    @abstractmethod
    async def execute_action(
        self, action: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute a specific action requested by the Planner."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on connector connection status."""
        pass

    async def refresh_tokens(self, account_id: str = "default") -> Dict[str, Any]:
        """Hook for refreshing OAuth/API tokens. Default implementation is no-op."""
        return {"status": "SKIPPED", "connector_id": self.connector_id, "account_id": account_id}

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
            "supported_actions": caps.supported_actions,
            "supported_execution_modes": caps.supported_execution_modes,
            "required_scopes": caps.required_scopes,
            "auth_type": caps.auth_type,
            "webhook_support": caps.webhook_support,
            "multi_account_support": caps.multi_account_support,
            "parent_connector_id": caps.parent_connector_id,
            "operating_mode": caps.operating_mode.value,
        }

