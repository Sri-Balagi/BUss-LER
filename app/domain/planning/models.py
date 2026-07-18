import enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from app.domain.intelligence.context import IntelligenceContext
from app.domain.twin.models import TwinSnapshot
from app.domain.reasoning.models import ReasoningResponse


class Goal(BaseModel):
    """Encapsulates the intent, description, and constraints of what needs to be achieved."""
    goal_id: UUID = Field(default_factory=uuid4)
    description: str = Field(..., description="High-level description of the goal to achieve.")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints the plan must respect.")


class PlanningContext(IntelligenceContext):
    """Context passed to the Planning Engine. Stores twin and reasoning state strictly by-reference."""
    # Strict by-reference context to avoid duplicating state
    active_twin: Optional[TwinSnapshot] = Field(None, description="The current state of the twin.")
    reasoning_result: Optional[ReasoningResponse] = Field(None, description="The reasoning insights applied to the twin.")


class PlanStatus(str, enum.Enum):
    """Lifecycle status of an immutable plan."""
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    INVALID = "INVALID"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PlanDependency(BaseModel):
    """Describes dependencies between steps."""
    step_id: UUID
    depends_on_step_id: UUID


class PlanStep(BaseModel):
    """Represents an atomic action in a plan with immutable properties."""
    step_id: UUID = Field(default_factory=uuid4)
    action: str = Field(..., description="The action to perform.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action.")
    
    class Config:
        frozen = True


class Plan(BaseModel):
    """
    Aggregate root for an execution plan. 
    It becomes fully immutable *after* validation succeeds.
    """
    plan_id: UUID = Field(default_factory=uuid4)
    goal_id: UUID = Field(..., description="The goal this plan fulfills.")
    steps: List[PlanStep] = Field(default_factory=list, description="Steps in the plan.")
    dependencies: List[PlanDependency] = Field(default_factory=list, description="Dependencies between steps.")
    status: PlanStatus = Field(default=PlanStatus.DRAFT)
    validation_errors: List[str] = Field(default_factory=list, description="Errors found during validation.")
    
    def add_step(self, step: PlanStep) -> None:
        if self.status not in (PlanStatus.DRAFT, PlanStatus.VALIDATING):
            raise ValueError(f"Cannot mutate plan in status {self.status.value}")
        self.steps.append(step)
        
    def add_dependency(self, step_id: UUID, depends_on_step_id: UUID) -> None:
        if self.status not in (PlanStatus.DRAFT, PlanStatus.VALIDATING):
            raise ValueError(f"Cannot mutate plan in status {self.status.value}")
        self.dependencies.append(PlanDependency(step_id=step_id, depends_on_step_id=depends_on_step_id))
        
    def transition_status(self, new_status: PlanStatus, errors: Optional[List[str]] = None) -> None:
        """Transitions the plan status."""
        self.status = new_status
        if errors is not None:
            self.validation_errors = errors
