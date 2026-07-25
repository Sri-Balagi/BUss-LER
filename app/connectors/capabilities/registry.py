"""Capabilities Framework for discoverability."""
from __future__ import annotations
import logging
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CapabilityScope(BaseModel):
    scope_name: str
    description: str = ""


class ConnectorCapabilityModel(BaseModel):
    capability_id: str  # e.g., "github.issue_management"
    name: str  # e.g., "Issue Management"
    connector_id: str
    description: str = ""
    operations: list[str] = Field(default_factory=list)  # ["create_issue", "list_issues"]
    canonical_model: str | None = None  # e.g., "CanonicalIssue"
    required_scopes: list[str] = Field(default_factory=list)


class CapabilityRegistry:
    """Registry to query what capabilities connectors advertise."""

    def __init__(self) -> None:
        self._capabilities: dict[str, ConnectorCapabilityModel] = {}

    def register(self, capability: ConnectorCapabilityModel) -> None:
        self._capabilities[capability.capability_id] = capability
        logger.info("Capability registered: %s for %s", capability.capability_id, capability.connector_id)

    def find_by_id(self, capability_id: str) -> ConnectorCapabilityModel | None:
        return self._capabilities.get(capability_id)

    def find_by_connector(self, connector_id: str) -> list[ConnectorCapabilityModel]:
        return [c for c in self._capabilities.values() if c.connector_id == connector_id]

    def find_connectors_for_operation(self, operation: str) -> list[str]:
        """Discover connectors that can execute a given operation."""
        return [c.connector_id for c in self._capabilities.values() if operation in c.operations]
