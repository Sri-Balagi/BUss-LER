from app.intelligence.learning.evaluation.models import OutcomeEvaluation, SuccessScore
from app.intelligence.learning.reflection.models import ReflectionReport
from app.intelligence.learning.synthesis.engine import KnowledgeSynthesisEngine
from app.intelligence.learning.synthesis.models import KnowledgeCategory


def test_synthesize_knowledge():
    engine = KnowledgeSynthesisEngine()

    reflection = ReflectionReport(report_id="r1", cycle_id="c1")
    evaluation = OutcomeEvaluation(
        evaluation_id="e1", plan_id="p1", overall_score=SuccessScore.ACHIEVED
    )

    artifacts = engine.synthesize(reflection, evaluation)

    assert len(artifacts) == 1
    assert artifacts[0].category == KnowledgeCategory.STRATEGIC
    assert "Successful execution pattern" in artifacts[0].description

    evaluation_fail = OutcomeEvaluation(
        evaluation_id="e2", plan_id="p2", overall_score=SuccessScore.FAILED
    )
    artifacts_fail = engine.synthesize(reflection, evaluation_fail)

    assert len(artifacts_fail) == 1
    assert artifacts_fail[0].category == KnowledgeCategory.CAUTIONARY
    assert "Failure pattern" in artifacts_fail[0].description
