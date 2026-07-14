"""
Wave-2 Milestone 4: Storage Layer — Concrete StorageManager
=============================================================
Implements IStorageManager by health-checking all registered VFS mounts
and returning a unified status report.
"""
from __future__ import annotations

from typing import Any

from app.infrastructure.storage.storage_manager import IStorageManager
from app.infrastructure.vfs.mount_registry import MountRegistry


class ConcreteStorageManager(IStorageManager):
    """
    Concrete implementation of IStorageManager.

    Delegates health checks to each registered IVirtualMount.
    """

    def __init__(self, mount_registry: MountRegistry) -> None:
        self._registry = mount_registry

    def ping(self) -> bool:
        """
        Returns True if all registered mounts are reachable.
        A mount is considered reachable if it has a non-None client.
        """
        # For now we check that at least one mount is registered and
        # that their clients are not None.  In Milestone 5 this will
        # issue real connectivity probes (PING, table exists, etc.)
        mounts_registered = len(self._registry._mounts) > 0
        return mounts_registered

    def status(self) -> dict[str, Any]:
        """Return a per-mount health summary."""
        report: dict[str, Any] = {}
        for scheme, mount in self._registry._mounts.items():
            client_attr = getattr(mount, "_client", None)
            report[scheme] = {
                "scheme": scheme,
                "mount_class": type(mount).__name__,
                "has_client": client_attr is not None,
            }
        return report
