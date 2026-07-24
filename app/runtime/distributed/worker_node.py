"""
Worker node definition for the BizOS distributed swarm.
"""
from __future__ import annotations

import socket
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.runtime.distributed.interfaces import IWorkerNode


class BizOSWorkerNode(IWorkerNode):
    """
    Represents a single BizOS worker node within the distributed swarm.
    Each node registers itself with the cluster on startup via heartbeat().
    """

    def __init__(
        self,
        node_id: UUID | None = None,
        hostname: str | None = None,
    ) -> None:
        self._node_id: UUID = node_id or uuid4()
        self._hostname: str = hostname or socket.gethostname()
        self._healthy: bool = True
        self._last_heartbeat: datetime | None = None

    @property
    def node_id(self) -> UUID:
        return self._node_id

    @property
    def is_healthy(self) -> bool:
        return self._healthy

    @property
    def hostname(self) -> str:
        return self._hostname

    @property
    def last_heartbeat(self) -> datetime | None:
        return self._last_heartbeat

    def heartbeat(self) -> None:
        """
        Record a heartbeat timestamp.
        In a production system this would write to a Redis key with a TTL
        so dead nodes are detected automatically by the registry.
        """
        self._last_heartbeat = datetime.now(UTC)
        self._healthy = True

    def mark_unhealthy(self) -> None:
        """Mark this node as unhealthy (called by a health monitor)."""
        self._healthy = False
