from app.intelligence.oversight.convergence.engine import ConvergenceEngine
from app.intelligence.oversight.convergence.models import ConvergenceStatus
from app.intelligence.decision.decision.models import ExecutiveDecision

def test_convergence_progressing():
    engine = ConvergenceEngine()
    
    d1 = ExecutiveDecision(decision_id="d1", objective_id="o1", selected_alternative_id="a1", rationale="")
    
    assessment = engine.evaluate_convergence([], d1)
    
    assert assessment.status == ConvergenceStatus.PROGRESSING

def test_convergence_converged():
    engine = ConvergenceEngine()
    
    d1 = ExecutiveDecision(decision_id="d1", objective_id="o1", selected_alternative_id="a1", rationale="")
    d2 = ExecutiveDecision(decision_id="d2", objective_id="o1", selected_alternative_id="a1", rationale="")
    
    assessment = engine.evaluate_convergence([d1], d2)
    
    assert assessment.status == ConvergenceStatus.CONVERGED
    assert assessment.confidence == 0.9

def test_convergence_oscillating():
    engine = ConvergenceEngine()
    
    d1 = ExecutiveDecision(decision_id="d1", objective_id="o1", selected_alternative_id="a1", rationale="")
    d2 = ExecutiveDecision(decision_id="d2", objective_id="o1", selected_alternative_id="a2", rationale="")
    d3 = ExecutiveDecision(decision_id="d3", objective_id="o1", selected_alternative_id="a1", rationale="")
    
    assessment = engine.evaluate_convergence([d1, d2], d3)
    
    assert assessment.status == ConvergenceStatus.OSCILLATING
