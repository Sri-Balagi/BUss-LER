"""
Distributed Runtime Architecture Abstractions & Pluggable Transports for BizOS.
Establishes worker roles, dynamic capability discovery, task leases, and transport contracts.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class WorkerRole(StrEnum):
    PLANNER_NODE = "PLANNER_NODE"
    WORKFLOW_NODE = "WORKFLOW_NODE"
    AGENT_NODE = "AGENT_NODE"
    CONNECTOR_WORKER = "CONNECTOR_WORKER"
    MEMORY_WORKER = "MEMORY_WORKER"
    EVENT_WORKER = "EVENT_WORKER"

class RuntimeTransportType(StrEnum):
    IN_PROCESS = "IN_PROCESS"
    REDIS = "REDIS"
    NATS = "NATS"
    KAFKA = "KAFKA"

class WorkerCapability(BaseModel):
    capability_name: str
    version: str = "1.0.0"
    max_concurrency: int = 10
    active_load: int = 0

class WorkerDescriptor(BaseModel):
    worker_id: str
    node_name: str
    roles: List[WorkerRole]
    capabilities: List[WorkerCapability] = Field(default_factory=list)
    healthy: bool = True
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TaskLease(BaseModel):
    lease_id: str
    task_id: str
    worker_id: str
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    active: bool = True

class IRuntimeTransport:
    """Pluggable communication transport interface for distributed BizOS execution."""

    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def subscribe(self, topic: str, handler: Any) -> None:
        raise NotImplementedError

class InProcessTransport(IRuntimeTransport):
    """In-memory reference transport implementation."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Any]] = {}

    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        handlers = self._subscribers.get(topic, [])
        for h in handlers:
            if asyncio.iscoroutinefunction(h):
                await h(message)
            else:
                h(message)

    async def subscribe(self, topic: str, handler: Any) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

class WorkerRegistry:
    """Central registry tracking active cluster workers and advertising capabilities."""

    def __init__(self) -> None:
        self._workers: Dict[str, WorkerDescriptor] = {}
        self._leases: Dict[str, TaskLease] = {}

    def register_worker(
        self,
        worker_id: str,
        node_name: str,
        roles: List[WorkerRole],
        capabilities: Optional[List[WorkerCapability]] = None,
    ) -> WorkerDescriptor:
        desc = WorkerDescriptor(
            worker_id=worker_id,
            node_name=node_name,
            roles=roles,
            capabilities=capabilities or [],
        )
        self._workers[worker_id] = desc
        return desc

    def record_heartbeat(self, worker_id: str) -> bool:
        if worker_id in self._workers:
            self._workers[worker_id].last_heartbeat = datetime.now(timezone.utc)
            self._workers[worker_id].healthy = True
            return True
        return False

    def find_worker_for_capability(self, capability_name: str) -> Optional[WorkerDescriptor]:
        """Capability-based worker discovery for task dispatch."""
        for w in self._workers.values():
            if not w.healthy:
                continue
            for cap in w.capabilities:
                if cap.capability_name == capability_name and cap.active_load < cap.max_concurrency:
                    return w
        return None

    def acquire_lease(self, task_id: str, worker_id: str, duration_seconds: float = 30.0) -> Optional[TaskLease]:
        now = datetime.now(timezone.utc)
        expires = datetime.fromtimestamp(now.timestamp() + duration_seconds, tz=timezone.utc)
        lease = TaskLease(
            lease_id=f"lease_{task_id}_{worker_id}",
            task_id=task_id,
            worker_id=worker_id,
            expires_at=expires,
        )
        self._leases[lease.lease_id] = lease
        return lease

    def get_cluster_status(self) -> Dict[str, Any]:
        return {
            "total_workers": len(self._workers),
            "healthy_workers": sum(1 for w in self._workers.values() if w.healthy),
            "active_leases": sum(1 for l in self._leases.values() if l.active),
            "workers": [w.model_dump() for w in self._workers.values()],
        }

class ExecutionCoordinator:
    """Dispatches tasks based on advertised worker roles and capabilities."""

    def __init__(self, registry: WorkerRegistry, transport: Optional[IRuntimeTransport] = None) -> None:
        self._registry = registry
        self._transport = transport or InProcessTransport()

    async def dispatch_task(self, task_id: str, required_capability: str, payload: Dict[str, Any]) -> bool:
        worker = self._registry.find_worker_for_capability(required_capability)
        if not worker:
            return False
        
        lease = self._registry.acquire_lease(task_id, worker.worker_id)
        if not lease:
            return False

        await self._transport.publish(f"tasks.{worker.worker_id}", {"task_id": task_id, "payload": payload})
        return True
