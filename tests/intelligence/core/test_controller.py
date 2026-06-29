import pytest
from app.intelligence.core.session.session import CognitiveSession, ConvergenceStatus
from app.intelligence.core.controller.interfaces import IConvergenceEvaluator
from app.intelligence.core.controller.controller import DefaultCognitiveCycleController

class MockEvaluator(IConvergenceEvaluator):
    def __init__(self, converge_on_iteration: int):
        self.converge_on_iteration = converge_on_iteration
        
    def evaluate(self, session: CognitiveSession) -> ConvergenceStatus:
        if session.metrics.iteration_count >= self.converge_on_iteration:
            return ConvergenceStatus.CONVERGED
        return ConvergenceStatus.CONTINUE_REASONING

@pytest.mark.asyncio
async def test_controller_converges():
    session = CognitiveSession()
    evaluator = MockEvaluator(converge_on_iteration=3)
    controller = DefaultCognitiveCycleController(evaluator)
    
    await controller.execute_cognitive_loop(session)
    
    assert session.metrics.iteration_count == 3
    assert session.convergence_state == ConvergenceStatus.CONVERGED

@pytest.mark.asyncio
async def test_controller_hits_budget():
    session = CognitiveSession()
    session.budget.max_iterations = 2
    evaluator = MockEvaluator(converge_on_iteration=5) # should not reach this
    controller = DefaultCognitiveCycleController(evaluator)
    
    await controller.execute_cognitive_loop(session)
    
    assert session.metrics.iteration_count == 2
    assert session.convergence_state == ConvergenceStatus.CONTINUE_REASONING # did not converge
