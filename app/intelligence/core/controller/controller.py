from app.intelligence.core.session.session import CognitiveSession, ConvergenceStatus
from app.intelligence.core.controller.interfaces import ICognitiveCycleController, IConvergenceEvaluator

class DefaultCognitiveCycleController(ICognitiveCycleController):
    def __init__(self, evaluator: IConvergenceEvaluator):
        self.evaluator = evaluator

    async def execute_cognitive_loop(self, session: CognitiveSession) -> None:
        """
        Main cognitive loop orchestrator.
        In a real implementation, this would trigger the Intake, Strategy, Decision, and Planning layers.
        """
        while True:
            # 1. Update iteration
            session.increment_iteration()

            # 2. Check termination policies
            if self.evaluate_termination_policies(session):
                # Terminate loop due to budget/time constraints
                break

            # 3. Simulate triggering engines (Intake -> Strategy -> Decision -> Planning)
            # engine_manager.run_cycle(session)
            
            # 4. Evaluate convergence
            status = self.evaluator.evaluate(session)
            session.convergence_state = status
            
            if status == ConvergenceStatus.CONVERGED:
                break
            elif status == ConvergenceStatus.REQUIRE_HUMAN_INPUT:
                # escalate to human collaboration framework
                break
            
            # If CONTINUE_REASONING or REQUEST_MORE_INFORMATION, loop continues

    def evaluate_termination_policies(self, session: CognitiveSession) -> bool:
        budget = session.budget
        metrics = session.metrics
        
        if metrics.iteration_count >= budget.max_iterations:
            return True
            
        if metrics.convergence_duration_ms >= budget.max_duration_ms:
            return True
            
        return False
