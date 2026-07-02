from app.intelligence.decision.planning.models import ExecutivePlan, PlanningStep
from app.intelligence.decision.simulation.engine import SimulationEngine
from app.intelligence.decision.simulation.models import SimulationScenario


def test_simulate():
    engine = SimulationEngine()

    plan = ExecutivePlan(
        plan_id="p1",
        decision_id="d1",
        steps=[PlanningStep(step_id="s1", action_description="test", estimated_effort_hours=10.0)],
    )

    scenario1 = SimulationScenario(
        scenario_id="scen1", plan_id="p1", variables={"market_growth": 50.0}
    )
    scenario2 = SimulationScenario(
        scenario_id="scen2", plan_id="p1", variables={"market_growth": -20.0}
    )

    results = engine.simulate(plan, [scenario1, scenario2])

    assert len(results) == 2
    assert results[0].net_impact_score == 60.0  # 50.0 + (1 step * 10)
    assert results[1].net_impact_score == -10.0  # -20.0 + (1 step * 10)
    assert results[0].outcomes[0].metric_name == "estimated_value_added"
