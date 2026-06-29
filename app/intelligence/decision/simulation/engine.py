import uuid
from typing import List
from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.decision.simulation.models import SimulationScenario, SimulationResult, SimulationOutcome

class SimulationEngine:
    """
    Simulates outcomes for candidate plans without executing them.
    """
    def simulate(self, plan: ExecutivePlan, scenarios: List[SimulationScenario]) -> List[SimulationResult]:
        results = []
        for scenario in scenarios:
            # Deterministic mock simulation
            impact_score = sum(scenario.variables.values()) + (len(plan.steps) * 10)
            
            outcome = SimulationOutcome(
                metric_name="estimated_value_added",
                estimated_change=impact_score,
                confidence_interval=0.15
            )
            
            results.append(SimulationResult(
                result_id=str(uuid.uuid4()),
                scenario_id=scenario.scenario_id,
                outcomes=[outcome],
                net_impact_score=impact_score
            ))
            
        return results
