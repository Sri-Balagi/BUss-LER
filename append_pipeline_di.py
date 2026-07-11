import os

with open('app/application/di.py', 'a') as f:
    f.write("""
    # =========================================================================
    # Cognitive Pipeline Engines (D1-D6)
    # =========================================================================
    from app.intelligence.decision.decision.engine import DecisionEngine
    from app.intelligence.decision.planning.engine import PlanningEngine as CognitivePlanningEngine
    from app.intelligence.intake.intent.engine import IntentEngine as CognitiveIntentEngine
    from app.intelligence.intake.situation.engine import SituationAnalysisEngine
    from app.intelligence.learning.evaluation.engine import OutcomeEvaluationEngine
    from app.intelligence.learning.heuristics.engine import ExecutiveHeuristicsEngine
    from app.intelligence.learning.reflection.engine import ReflectionEngine
    from app.intelligence.learning.repository.engine import ExecutiveKnowledgeRepository
    from app.intelligence.learning.synthesis.engine import KnowledgeSynthesisEngine
    from app.intelligence.oversight.arbitration.engine import ExecutiveArbitrationEngine
    from app.intelligence.oversight.assumptions.engine import AssumptionManager
    from app.intelligence.oversight.convergence.engine import ConvergenceEngine
    from app.intelligence.oversight.cycle.engine import CognitiveCycleController
    from app.intelligence.oversight.validation.engine import ExecutiveValidationEngine
    from app.intelligence.strategy.goals.engine import GoalManagementEngine as CognitiveGoalManagementEngine
    from app.intelligence.strategy.objectives.engine import ExecutiveObjectivesEngine

    container.register_factory(DecisionEngine, lambda c: DecisionEngine())
    container.register_factory(CognitivePlanningEngine, lambda c: CognitivePlanningEngine())
    container.register_factory(CognitiveIntentEngine, lambda c: CognitiveIntentEngine())
    container.register_factory(SituationAnalysisEngine, lambda c: SituationAnalysisEngine())
    container.register_factory(OutcomeEvaluationEngine, lambda c: OutcomeEvaluationEngine())
    container.register_factory(ExecutiveHeuristicsEngine, lambda c: ExecutiveHeuristicsEngine())
    container.register_factory(ReflectionEngine, lambda c: ReflectionEngine())
    container.register_factory(ExecutiveKnowledgeRepository, lambda c: ExecutiveKnowledgeRepository())
    container.register_factory(KnowledgeSynthesisEngine, lambda c: KnowledgeSynthesisEngine())
    container.register_factory(ExecutiveArbitrationEngine, lambda c: ExecutiveArbitrationEngine())
    container.register_factory(AssumptionManager, lambda c: AssumptionManager())
    container.register_factory(ConvergenceEngine, lambda c: ConvergenceEngine())
    container.register_factory(CognitiveCycleController, lambda c: CognitiveCycleController())
    container.register_factory(ExecutiveValidationEngine, lambda c: ExecutiveValidationEngine())
    container.register_factory(CognitiveGoalManagementEngine, lambda c: CognitiveGoalManagementEngine())
    container.register_factory(ExecutiveObjectivesEngine, lambda c: ExecutiveObjectivesEngine())
""")
