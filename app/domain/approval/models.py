import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalState(StrEnum):
    NONE = "NONE"
    REQUIRED = "REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class Approval(BaseModel):
    """
    Independent Aggregate Root for Approvals.
    Supports arbitrary platform resources (Jobs, Workflows, Agents, Policies, etc.).
    """
    approval_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_type: str
    target_id: str
    state: ApprovalState = ApprovalState.NONE
    requested_by: str
    approved_by: str | None = None
    reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def approve(self, user_id: str):
        if self.state != ApprovalState.REQUIRED:
            raise ValueError(f"Cannot approve from state {self.state}")
        self.state = ApprovalState.APPROVED
        self.approved_by = user_id
        self.resolved_at = datetime.now(UTC)

    def reject(self, user_id: str, reason: str | None = None):
        if self.state != ApprovalState.REQUIRED:
            raise ValueError(f"Cannot reject from state {self.state}")
        self.state = ApprovalState.REJECTED
        self.approved_by = user_id
        if reason:
            self.reason = reason
        self.resolved_at = datetime.now(UTC)

    def expire(self):
        if self.state != ApprovalState.REQUIRED:
            raise ValueError(f"Cannot expire from state {self.state}")
        self.state = ApprovalState.EXPIRED
        self.resolved_at = datetime.now(UTC)
        self.reason = "Approval request expired due to timeout."
