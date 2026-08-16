from app.intelligence.intake.intent.models import ExecutiveIntent, IntentClassification
from app.intelligence.intake.kpi.models import KPIAssessment, KPIStatus
from app.intelligence.intake.situation.engine import SituationAnalysisEngine
from app.intelligence.workspaces.world_model.world_model import Belief, BusinessWorldModel


def test_situation_analysis_healthy():
    engine = SituationAnalysisEngine()

    kpis = [
        KPIAssessment(
            kpi_id="rev",
            current_value=100,
            target_value=100,
            status=KPIStatus.HEALTHY,
            deviation_percentage=0.0,
        )
    ]
    world_model = BusinessWorldModel()

    assessment = engine.analyze(None, kpis, world_model)

    assert len(assessment.risks) == 0
    assert len(assessment.opportunities) == 0
    assert len(assessment.missing_information) == 1
    assert assessment.missing_information[0].gap_id == "gap_sentiment"


def test_situation_analysis_risks_and_opportunities():
    engine = SituationAnalysisEngine()

    kpis = [
        KPIAssessment(
            kpi_id="rev",
            current_value=70,
            target_value=100,
            status=KPIStatus.CRITICAL,
            deviation_percentage=-30.0,
        ),
        KPIAssessment(
            kpi_id="traffic",
            current_value=90,
            target_value=100,
            status=KPIStatus.WARNING,
            deviation_percentage=-10.0,
        ),
    ]
    world_model = BusinessWorldModel()
    world_model.update_belief(Belief("customer_sentiment", "improving", 0.9))

    intent = ExecutiveIntent(
        raw_request="Grow", classification=IntentClassification.STRATEGIC_OBJECTIVE
    )

    assessment = engine.analyze(intent, kpis, world_model)

    assert len(assessment.risks) == 2
    assert assessment.risks[0].severity == "HIGH"
    assert assessment.risks[1].severity == "MEDIUM"
    assert len(assessment.opportunities) == 1
    assert assessment.opportunities[0].opportunity_id == "opp_sentiment"
    assert len(assessment.missing_information) == 0
    assert "Influenced by intent" in assessment.summary
