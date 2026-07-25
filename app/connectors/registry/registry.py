"""
Connector Registry — thread-safe in-memory registry for connector manifests.

The ``ConnectorRegistry`` is the central lookup table for all registered
connectors. It is populated by the ``ConnectorLoader`` at startup and
updated dynamically when connectors are installed or removed at runtime.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from app.connectors.exceptions.errors import (
    ConnectorAlreadyRegisteredError,
    ConnectorNotFoundError,
)

if TYPE_CHECKING:
    from app.connectors.registry.manifest import ConnectorManifest

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """
    Thread-safe registry of all known connector manifests.

    Responsibilities:
    - Store and serve ConnectorManifest objects keyed by connector ID.
    - Support capability-based lookup (find connectors that provide X).
    - Support category and tag filtering.
    - Provide version metadata for dependency resolution.
    """

    def __init__(self) -> None:
        self._manifests: dict[str, ConnectorManifest] = {}
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, manifest: ConnectorManifest, overwrite: bool = False) -> None:
        """
        Register a connector manifest.

        Args:
            manifest: The manifest to register.
            overwrite: If True, silently replace an existing registration.

        Raises:
            ConnectorAlreadyRegisteredError: If the connector is already
                registered and ``overwrite=False``.
        """
        with self._lock:
            if manifest.id in self._manifests and not overwrite:
                raise ConnectorAlreadyRegisteredError(
                    f"Connector {manifest.id!r} is already registered. "
                    "Use overwrite=True to replace.",
                    connector_id=manifest.id,
                )
            self._manifests[manifest.id] = manifest
            logger.info(
                "Registered connector id=%s version=%s",
                manifest.id,
                manifest.version,
            )

    def unregister(self, connector_id: str) -> None:
        """Remove a connector from the registry."""
        with self._lock:
            if connector_id not in self._manifests:
                raise ConnectorNotFoundError(
                    f"Connector {connector_id!r} not found in registry.",
                    connector_id=connector_id,
                )
            del self._manifests[connector_id]
            logger.info("Unregistered connector id=%s", connector_id)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, connector_id: str) -> ConnectorManifest:
        """
        Retrieve a manifest by connector ID.

        Raises:
            ConnectorNotFoundError: If no manifest is registered for the ID.
        """
        with self._lock:
            manifest = self._manifests.get(connector_id)
            if manifest is None:
                raise ConnectorNotFoundError(
                    f"Connector {connector_id!r} not found in registry.",
                    connector_id=connector_id,
                )
            return manifest

    def get_or_none(self, connector_id: str) -> ConnectorManifest | None:
        with self._lock:
            return self._manifests.get(connector_id)

    def list_all(self) -> list[ConnectorManifest]:
        """Return all registered manifests."""
        with self._lock:
            return list(self._manifests.values())

    def list_ids(self) -> list[str]:
        """Return all registered connector IDs."""
        with self._lock:
            return list(self._manifests.keys())

    def exists(self, connector_id: str) -> bool:
        with self._lock:
            return connector_id in self._manifests

    # ------------------------------------------------------------------
    # Capability-based discovery
    # ------------------------------------------------------------------

    def find_by_capability(self, capability_id: str) -> list[ConnectorManifest]:
        """
        Find all connectors that declare the given capability.

        Example:
            registry.find_by_capability("github.issue_management")
        """
        with self._lock:
            return [
                m for m in self._manifests.values()
                if capability_id in m.capability_ids
            ]

    def find_by_operation(self, operation: str) -> list[ConnectorManifest]:
        """
        Find connectors that declare a specific operation.

        Example:
            registry.find_by_operation("create_issue")
        """
        with self._lock:
            results = []
            for manifest in self._manifests.values():
                for cap in manifest.capabilities:
                    if operation in cap.operations:
                        results.append(manifest)
                        break
            return results

    def find_by_category(self, category: str) -> list[ConnectorManifest]:
        with self._lock:
            return [
                m for m in self._manifests.values()
                if m.marketplace and m.marketplace.category.value == category
            ]

    def find_by_tag(self, tag: str) -> list[ConnectorManifest]:
        with self._lock:
            return [
                m for m in self._manifests.values()
                if m.marketplace and tag in m.marketplace.tags
            ]

    def find_by_auth_type(self, auth_type: str) -> list[ConnectorManifest]:
        with self._lock:
            return [
                m for m in self._manifests.values()
                if m.auth_type.value == auth_type
            ]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._manifests)

    def __repr__(self) -> str:
        return f"ConnectorRegistry(count={self.count})"


# Singleton instance
_registry: ConnectorRegistry | None = None


def get_registry() -> ConnectorRegistry:
    """Return the global singleton ConnectorRegistry."""
    global _registry
    if _registry is None:
        _registry = ConnectorRegistry()
    return _registry
