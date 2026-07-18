from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid

class ApprovalState(str, Enum):
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
    approved_by: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def approve(self, user_id: str):
        if self.state != ApprovalState.REQUIRED:
            raise ValueError(f"Cannot approve from state {self.state}")
        self.state = ApprovalState.APPROVED
        self.approved_by = user_id
        self.resolved_at = datetime.now(timezone.utc)

    def reject(self, user_id: str, reason: Optional[str] = None):
        if self.state != ApprovalState.REQUIRED:
            raise ValueError(f"Cannot reject from state {self.state}")
        self.state = ApprovalState.REJECTED
        self.approved_by = user_id
        if reason:
            self.reason = reason
        self.resolved_at = datetime.now(timezone.utc)

    def expire(self):
        if self.state != ApprovalState.REQUIRED:
            raise ValueError(f"Cannot expire from state {self.state}")
        self.state = ApprovalState.EXPIRED
        self.resolved_at = datetime.now(timezone.utc)
        self.reason = "Approval request expired due to timeout."
