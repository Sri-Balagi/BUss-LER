"""
Wave-2 Milestone 3: Distributed Runtime
=========================================
Interfaces and abstractions for the distributed task scheduling layer.
Concrete implementations (CeleryDistributedScheduler, RedisSystemBus) live
in separate modules so the domain/application layers remain free of
infrastructure dependencies (Clean Architecture / Dependency Inversion).
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID


class IDistributedScheduler(ABC):
    """
    Schedules tasks across a cluster of worker nodes.
    The distributed counterpart to LocalScheduler.
    """

    @abstractmethod
    def schedule_task(self, task_name: str, payload: Any, queue: str = "default") -> str:
        """
        Submit a named task to a specific queue.
        Returns a task_id that can be used to poll for status.
        """
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> str:
        """
        Return the current status of a distributed task.
        Expected values: PENDING | STARTED | SUCCESS | FAILURE | RETRY
        """
        pass

    @abstractmethod
    def revoke_task(self, task_id: str, terminate: bool = False) -> None:
        """
        Cancel a pending or running task.
        """
        pass


class IDistributedSystemBus(ABC):
    """
    A publish/subscribe bus backed by a distributed broker (e.g., Redis Pub/Sub).
    Extends the local ISystemBus concept to multi-node environments.
    """

    @abstractmethod
    def publish(self, channel: str, message: Any) -> None:
        """Publish a serialised message to a named channel."""
        pass

    @abstractmethod
    def subscribe(self, channel: str) -> None:
        """Subscribe to a named channel. Messages are received via listen()."""
        pass

    @abstractmethod
    def listen(self) -> Any:
        """
        Blocking generator that yields messages received from subscribed channels.
        Intended to run in a dedicated worker thread / process.
        """
        pass


class IWorkerNode(ABC):
    """
    Represents a worker node in the BizOS distributed swarm.
    """

    @property
    @abstractmethod
    def node_id(self) -> UUID:
        """Globally unique identifier for this worker node."""
        pass

    @property
    @abstractmethod
    def is_healthy(self) -> bool:
        """Health status: True if the node is accepting tasks."""
        pass

    @abstractmethod
    def heartbeat(self) -> None:
        """Emit a heartbeat signal to the cluster registry."""
        pass
