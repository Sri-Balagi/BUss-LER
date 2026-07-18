from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ReplanReason(str, Enum):
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"
    NEW_INFORMATION = "NEW_INFORMATION"
    POLICY_CHANGE = "POLICY_CHANGE"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"

class DecisionPolicy(BaseModel):
    confidence_threshold: float = Field(default=0.8)
    approval_threshold: float = Field(default=0.6)
    escalation_threshold: float = Field(default=0.4)
    retry_policy: int = Field(default=3)
    risk_threshold: float = Field(default=0.7)

class Decision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    goal_id: UUID
    context: Dict[str, Any] = Field(default_factory=dict)
    options: List[Dict[str, Any]] = Field(default_factory=list)
    option_scores: Dict[str, float] = Field(default_factory=dict)
    selected_option: Optional[Dict[str, Any]] = None
    confidence: float = Field(default=0.0)
    justification: str = Field(default="")
    risks: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
