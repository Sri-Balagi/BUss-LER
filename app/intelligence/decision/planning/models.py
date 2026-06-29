from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class PlanningDependency(BaseModel):
    step_id: str
    depends_on_step_id: str

class PlanningStep(BaseModel):
    step_id: str
    action_description: str
    estimated_effort_hours: float
    required_capabilities: List[str] = Field(default_factory=list)

class ExecutiveDirective(BaseModel):
    """The final payload sent to the Supervisor for execution mapping."""
    directive_id: str
    intent: str
    success_conditions: List[str] = Field(default_factory=list)

class ExecutivePlan(BaseModel):
    """The logical sequence of steps to fulfill a decision."""
    plan_id: str
    decision_id: str
    steps: List[PlanningStep] = Field(default_factory=list)
    dependencies: List[PlanningDependency] = Field(default_factory=list)
    generated_directives: List[ExecutiveDirective] = Field(default_factory=list)
