from enum import StrEnum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.applications.context.models import ApplicationContext


class TriggerType(StrEnum):
    """The type of a cognitive trigger."""
    EVENT = "EVENT"
    SCHEDULE = "SCHEDULE"
    CONDITION = "CONDITION"
    MANUAL = "MANUAL"


class TriggerPriority(StrEnum):
    """Execution priority of the dispatched trigger."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExecutionMode(StrEnum):
    """How the target application should be executed."""
    IMMEDIATE = "IMMEDIATE"
    QUEUE = "QUEUE"
    SCHEDULED = "SCHEDULED"


class TriggerContext(ApplicationContext):
    """Context instance for executing a trigger evaluation."""
    trigger_source: str = Field(..., description="The source initiating the trigger")
    trigger_type: TriggerType = Field(..., description="Type of trigger being processed")


class TriggerCondition(BaseModel):
    """A condition that must be evaluated before the action is taken."""
    condition_type: str = Field(..., description="Type of evaluator to use, e.g., 'threshold', 'boolean', 'ai_predicate'")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the condition evaluator")


class TriggerAction(BaseModel):
    """The action to take when the condition evaluates to true."""
    target_app_id: str = Field(..., description="The ID of the cognitive application to dispatch")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.QUEUE)
    priority: TriggerPriority = Field(default=TriggerPriority.NORMAL)
    payload: Dict[str, Any] = Field(default_factory=dict, description="The payload to send to the target application")


class CognitiveTrigger(BaseModel):
    """The core aggregate root representing a registered trigger rule."""
    trigger_id: str = Field(..., description="Unique ID of this trigger configuration")
    trigger_type: TriggerType
    conditions: List[TriggerCondition] = Field(default_factory=list, description="All conditions must pass for the trigger to fire")
    action: TriggerAction = Field(..., description="The action to perform if conditions are met")
    tenant_id: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TriggerExecutionResult(BaseModel):
    """Result of a trigger evaluation or execution."""
    trigger_id: str
    target_job_id: Optional[str] = None
    success: bool
    reason: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
