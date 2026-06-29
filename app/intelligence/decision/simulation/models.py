from pydantic import BaseModel, Field
from typing import List, Dict

class SimulationScenario(BaseModel):
    scenario_id: str
    plan_id: str
    variables: Dict[str, float] = Field(default_factory=dict)

class SimulationOutcome(BaseModel):
    metric_name: str
    estimated_change: float
    confidence_interval: float

class SimulationResult(BaseModel):
    """The result of simulating an ExecutivePlan without runtime execution."""
    result_id: str
    scenario_id: str
    outcomes: List[SimulationOutcome] = Field(default_factory=list)
    net_impact_score: float
