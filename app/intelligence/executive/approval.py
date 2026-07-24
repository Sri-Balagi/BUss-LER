from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


@dataclass
class ApprovalRequestEvent:
    """Event emitted when a capability requires external approval before execution."""

    session_id: str
    capability_id: str
    workflow_id: UUID
    task_id: UUID
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    status: ApprovalStatus = ApprovalStatus.PENDING

    # Populated upon resolution
    resolved_by: str | None = None
    resolution_notes: str | None = None


class IApprovalProvider(ABC):
    """Generalized provider for resolving security approvals.

    Can be backed by a Human UI, an Organization Policy engine, or an AI Supervisor.
    """

    @abstractmethod
    async def request_approval(self, event: ApprovalRequestEvent) -> None:
        """Submit an approval request to this provider.

        The provider should arrange for the request to be resolved asynchronously.
        """
        pass

    @abstractmethod
    async def get_status(self, event_id: UUID) -> ApprovalStatus:
        """Check the current status of an approval request."""
        pass


class HumanApprovalProvider(IApprovalProvider):
    """Stub provider representing human-in-the-loop interaction."""

    def __init__(self) -> None:
        self._requests: dict[UUID, ApprovalRequestEvent] = {}

    async def request_approval(self, event: ApprovalRequestEvent) -> None:
        # In a real system, this might push a notification or WebSocket message to a UI.
        self._requests[event.event_id] = event

    async def get_status(self, event_id: UUID) -> ApprovalStatus:
        req = self._requests.get(event_id)
        if not req:
            raise KeyError(f"Approval request {event_id} not found")
        return req.status

    def resolve(self, event_id: UUID, approved: bool, notes: str = "") -> None:
        """Called by an HTTP API endpoint to resolve a pending request."""
        req = self._requests.get(event_id)
        if req:
            req.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.DENIED
            req.resolved_by = "human_user"
            req.resolution_notes = notes
