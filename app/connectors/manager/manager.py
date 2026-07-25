"""
Connector Manager — central runtime for the connector platform.

The ``ConnectorManager`` is the single entry point for all runtime
connector operations. Business modules and AI agents interact with
connectors exclusively through this facade.

Responsibilities:
- Load and unload connector instances
- Enforce lifecycle transitions
- Manage multi-profile state
- Enforce runtime policies
- Delegate to HealthMonitor
- Expose capabilities to the CapabilityRegistry
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from app.connectors.exceptions.errors import (
    ConnectorNotFoundError,
    DependencyNotSatisfiedError,
    PolicyViolationError,
    ProfileNotFoundError,
)
from app.connectors.manager.health import HealthMonitor, ConnectorHealthSnapshot
from app.connectors.manager.lifecycle import ConnectorLifecycleRecord
from app.connectors.registry.registry import ConnectorRegistry
from app.connectors.sdk.base import BaseConnector, ConnectorStatus, SyncResult, SyncType

if TYPE_CHECKING:
    from app.connectors.manager.health import ConnectorHealthSnapshot
    from app.connectors.registry.manifest import ConnectorManifest

logger = logging.getLogger(__name__)

# Key type: "{connector_id}:{profile_id}"
_ConnectorKey = str


class ConnectorManager:
    """
    Central runtime manager for all connector instances.

    Multi-Profile Support:
        Each connector can have multiple active profiles simultaneously.
        e.g., GitHub with personal account + organization account.

    Usage::

        manager = ConnectorManager(registry)
        await manager.install("github", profile_id="personal")
        await manager.connect("github", profile_id="personal")
    """

    def __init__(
        self,
        registry: ConnectorRegistry,
        health_monitor: HealthMonitor | None = None,
    ) -> None:
        self._registry = registry
        self._health = health_monitor or HealthMonitor()
        # Stores live connector instances
        self._instances: dict[_ConnectorKey, BaseConnector] = {}
        # Tracks lifecycle state per connector+profile
        self._lifecycle: dict[_ConnectorKey, ConnectorLifecycleRecord] = {}
        # Active policies per connector
        self._policies: dict[str, set[str]] = {}
        # Connector class factories: connector_id → type
        self._factories: dict[str, type[BaseConnector]] = {}

    # ------------------------------------------------------------------
    # Factory Registration
    # ------------------------------------------------------------------

    def register_factory(
        self,
        connector_id: str,
        factory: type[BaseConnector],
    ) -> None:
        """Register a connector class factory for runtime instantiation."""
        self._factories[connector_id] = factory
        logger.info("ConnectorManager: registered factory for %s", connector_id)

    # ------------------------------------------------------------------
    # Lifecycle Operations
    # ------------------------------------------------------------------

    async def install(
        self,
        connector_id: str,
        profile_id: str = "default",
        config: dict[str, Any] | None = None,
    ) -> None:
        """
        Install and activate a connector through the full guided lifecycle.

        Phases: INSTALL → VALIDATE → CONFIGURE → AUTHENTICATE → TEST → ENABLE → ACTIVATE
        """
        manifest = self._get_manifest(connector_id)
        self._check_dependencies(connector_id, manifest)

        key = self._key(connector_id, profile_id)
        if key in self._instances:
            logger.warning(
                "Connector %s[%s] already installed — skipping",
                connector_id, profile_id,
            )
            return

        # Create instance
        factory = self._factories.get(connector_id)
        if factory is None:
            raise ConnectorNotFoundError(
                f"No factory registered for connector {connector_id!r}. "
                "Did you call register_factory()?",
                connector_id=connector_id,
            )

        instance = factory(connector_id=connector_id, profile_id=profile_id)
        self._instances[key] = instance
        self._lifecycle[key] = ConnectorLifecycleRecord(connector_id, profile_id)

        try:
            # Phase 1: Install
            await instance.install()

            # Phase 2: Validate
            validation = await instance.validate()
            if not validation.valid:
                raise ValueError(f"Validation failed: {validation.errors}")

            # Phase 3: Configure (config is injected by ConnectorManager)
            # In production: load config from ConnectorConfigRepository
            record = self._lifecycle[key]
            record.transition(ConnectorStatus.CONFIGURED, "Configuration applied")
            instance._set_status(ConnectorStatus.CONFIGURED)

            # Phase 4: Authenticate
            await instance.authenticate()

            # Phase 5: Test connection
            health = await instance.health_check()
            if not health.healthy:
                logger.warning(
                    "Test connection failed for %s[%s]: %s",
                    connector_id, profile_id, health.message,
                )

            # Phase 6: Enable & Activate
            record.transition(ConnectorStatus.CONNECTED, "Connection established")
            instance._set_status(ConnectorStatus.CONNECTED)
            await instance.connect()

            record.transition(ConnectorStatus.ACTIVE, "Connector activated")
            instance._set_status(ConnectorStatus.ACTIVE)

            # Register with health monitor
            self._health.register(instance, interval_seconds=manifest.health_check_interval_seconds)

            logger.info(
                "Connector %s[%s] installed and active", connector_id, profile_id
            )

        except Exception as e:
            lc = self._lifecycle.get(key)
            if lc and lc.can_transition(ConnectorStatus.ERROR):
                lc.transition(ConnectorStatus.ERROR, str(e))
            instance._set_error(str(e))
            raise

    async def uninstall(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> None:
        key = self._key(connector_id, profile_id)
        instance = self._require_instance(connector_id, profile_id, key)

        self._health.unregister(connector_id, profile_id)
        await instance.shutdown()
        await instance.uninstall()

        del self._instances[key]
        del self._lifecycle[key]
        logger.info("Connector %s[%s] uninstalled", connector_id, profile_id)

    async def connect(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> None:
        key = self._key(connector_id, profile_id)
        instance = self._require_instance(connector_id, profile_id, key)
        await instance.connect()
        self._lifecycle[key].transition(ConnectorStatus.CONNECTED, "Manual connect")
        instance._set_status(ConnectorStatus.CONNECTED)

    async def disconnect(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> None:
        key = self._key(connector_id, profile_id)
        instance = self._require_instance(connector_id, profile_id, key)
        await instance.disconnect()
        self._lifecycle[key].transition(ConnectorStatus.DISCONNECTED, "Manual disconnect")
        instance._set_status(ConnectorStatus.DISCONNECTED)

    async def sync(
        self,
        connector_id: str,
        profile_id: str = "default",
        sync_type: SyncType = SyncType.INCREMENTAL,
    ) -> SyncResult:
        self._enforce_policy(connector_id, "sync")
        key = self._key(connector_id, profile_id)
        instance = self._require_instance(connector_id, profile_id, key)
        return await instance.sync(sync_type)

    async def handle_webhook(
        self,
        connector_id: str,
        payload: dict[str, Any],
        profile_id: str = "default",
    ) -> Any:
        self._enforce_policy(connector_id, "webhook")
        key = self._key(connector_id, profile_id)
        instance = self._require_instance(connector_id, profile_id, key)
        return await instance.handle_webhook(payload)

    async def refresh_token(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> None:
        key = self._key(connector_id, profile_id)
        instance = self._require_instance(connector_id, profile_id, key)
        await instance.refresh_token()

    # ------------------------------------------------------------------
    # Policy Management
    # ------------------------------------------------------------------

    def apply_policy(self, connector_id: str, policy: str) -> None:
        self._policies.setdefault(connector_id, set()).add(policy)
        logger.info("Policy %s applied to connector %s", policy, connector_id)

    def remove_policy(self, connector_id: str, policy: str) -> None:
        self._policies.get(connector_id, set()).discard(policy)

    def get_policies(self, connector_id: str) -> set[str]:
        return self._policies.get(connector_id, set())

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def get_instance(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> BaseConnector | None:
        return self._instances.get(self._key(connector_id, profile_id))

    def get_lifecycle(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> ConnectorLifecycleRecord | None:
        return self._lifecycle.get(self._key(connector_id, profile_id))

    def list_installed(self) -> list[str]:
        """Return connector IDs of all installed instances."""
        return list({key.split(":")[0] for key in self._instances})

    def list_profiles(self, connector_id: str) -> list[str]:
        prefix = f"{connector_id}:"
        return [
            key[len(prefix):]
            for key in self._instances
            if key.startswith(prefix)
        ]

    def get_health(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> ConnectorHealthSnapshot | None:
        return self._health.get_status(connector_id, profile_id)

    def get_all_health(self) -> list[ConnectorHealthSnapshot]:
        return self._health.get_all_statuses()

    def get_capabilities(self, connector_id: str) -> list[str]:
        instance = self._instances.get(
            next(
                (k for k in self._instances if k.startswith(f"{connector_id}:")),
                ""
            )
        )
        if instance:
            return instance.get_capabilities()
        return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key(connector_id: str, profile_id: str) -> _ConnectorKey:
        return f"{connector_id}:{profile_id}"

    def _get_manifest(self, connector_id: str) -> ConnectorManifest:
        return self._registry.get(connector_id)

    def _require_instance(
        self,
        connector_id: str,
        profile_id: str,
        key: _ConnectorKey,
    ) -> BaseConnector:
        instance = self._instances.get(key)
        if instance is None:
            raise ProfileNotFoundError(
                f"No active instance for connector {connector_id!r} "
                f"profile {profile_id!r}. Call install() first.",
                connector_id=connector_id,
            )
        return instance

    def _check_dependencies(
        self,
        connector_id: str,
        manifest: ConnectorManifest,
    ) -> None:
        for dep in manifest.dependencies:
            if dep.required and not self._registry.exists(dep.connector_id):
                raise DependencyNotSatisfiedError(connector_id, dep.connector_id)

    def _enforce_policy(self, connector_id: str, operation: str) -> None:
        policies = self._policies.get(connector_id, set())
        blocked_by: dict[str, set[str]] = {
            "sync": {"SYNC_DISABLED", "READ_ONLY", "SUSPENDED", "MAINTENANCE_MODE"},
            "webhook": {"WEBHOOK_DISABLED", "SUSPENDED", "MAINTENANCE_MODE"},
            "write": {"WRITE_DISABLED", "READ_ONLY", "SUSPENDED"},
        }
        blocked = blocked_by.get(operation, set())
        for policy in policies:
            if policy in blocked:
                raise PolicyViolationError(
                    connector_id=connector_id,
                    policy=policy,
                    operation=operation,
                )
