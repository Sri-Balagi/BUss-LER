from pydantic import BaseModel, Field


class PlanningDependency(BaseModel):
    step_id: str
    depends_on_step_id: str


class PlanningStep(BaseModel):
    step_id: str
    action_description: str
    estimated_effort_hours: float
    required_capabilities: list[str] = Field(default_factory=list)


class ExecutiveDirective(BaseModel):
    """The final payload sent to the Supervisor for execution mapping."""

    directive_id: str
    intent: str
    success_conditions: list[str] = Field(default_factory=list)


class ExecutivePlan(BaseModel):
    """The logical sequence of steps to fulfill a decision."""

    plan_id: str
    decision_id: str
    steps: list[PlanningStep] = Field(default_factory=list)
    dependencies: list[PlanningDependency] = Field(default_factory=list)
    generated_directives: list[ExecutiveDirective] = Field(default_factory=list)
