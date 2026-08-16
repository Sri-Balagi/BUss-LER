"""BizOS Connector Capability Registry

Enables Planner Agents and Workflow Engine to request high-level capabilities (e.g. 'send_email', 'fetch_bank_statement')
which dynamically resolve to the appropriate registered connector (Gmail, Outlook, Open Banking, Stripe, Razorpay).
This keeps BizOS completely provider-agnostic.
"""

from typing import Any, Dict, List, Optional
import structlog
from app.connectors.sdk.base import BaseConnector

logger = structlog.get_logger(__name__)


class ConnectorCapabilityRegistry:
    """Registry mapping capabilities to connectors and resolving provider implementations."""

    _connectors_by_id: Dict[str, BaseConnector] = {}
    _connectors_by_capability: Dict[str, List[str]] = {}

    @classmethod
    def register_connector(cls, connector: BaseConnector) -> None:
        """Register a connector instance into the global capability registry."""
        cid = connector.connector_id
        cls._connectors_by_id[cid] = connector

        for action in connector.capabilities.supported_actions:
            if action not in cls._connectors_by_capability:
                cls._connectors_by_capability[action] = []
            if cid not in cls._connectors_by_capability[action]:
                cls._connectors_by_capability[action].append(cid)

        logger.info(
            "Registered connector in CapabilityRegistry",
            connector_id=cid,
            actions=connector.capabilities.supported_actions,
        )

    @classmethod
    def resolve_capability(cls, capability: str) -> List[BaseConnector]:
        """Resolves all connectors supporting the requested capability."""
        cids = cls._connectors_by_capability.get(capability, [])
        return [cls._connectors_by_id[cid] for cid in cids if cid in cls._connectors_by_id]

    @classmethod
    def resolve_primary_connector(cls, capability: str, preferred_provider: Optional[str] = None) -> Optional[BaseConnector]:
        """Resolves the best connector for a capability, honoring optional user/planner preferences."""
        connectors = cls.resolve_capability(capability)
        if not connectors:
            return None

        if preferred_provider:
            for c in connectors:
                if c.connector_id == preferred_provider or c.capabilities.family == preferred_provider:
                    return c

        # Default to first registered connector for this capability
        return connectors[0]

    @classmethod
    def get_connector(cls, connector_id: str) -> Optional[BaseConnector]:
        """Retrieves connector by unique ID."""
        return cls._connectors_by_id.get(connector_id)

    @classmethod
    def list_all_capabilities(cls) -> Dict[str, List[str]]:
        """Lists all registered capabilities and their matching provider IDs."""
        return cls._connectors_by_capability.copy()

    @classmethod
    def list_all_connectors(cls) -> List[Dict[str, Any]]:
        """Returns metadata for all registered connectors."""
        return [c.get_metadata() for c in cls._connectors_by_id.values()]

    @classmethod
    def reset(cls) -> None:
        """Clears registry (useful for testing)."""
        cls._connectors_by_id.clear()
        cls._connectors_by_capability.clear()
