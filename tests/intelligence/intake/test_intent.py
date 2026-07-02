from app.intelligence.intake.intent.engine import IntentEngine
from app.intelligence.intake.intent.models import IntentClassification


def test_intent_engine_growth():
    engine = IntentEngine()
    intent = engine.parse_intent("We need to grow our market share in Q3")

    assert intent.classification == IntentClassification.STRATEGIC_OBJECTIVE
    assert len(intent.entities) == 1
    assert intent.entities[0].value == "growth"
    assert "increase_revenue" in intent.requested_outcomes
    assert not intent.is_ambiguous


def test_intent_engine_fix():
    engine = IntentEngine()
    intent = engine.parse_intent("Fix the deployment pipeline")

    assert intent.classification == IntentClassification.OPERATIONAL_ADJUSTMENT
    assert "operational_fix" in intent.requested_outcomes
    assert not intent.is_ambiguous


def test_intent_engine_ambiguous():
    engine = IntentEngine()
    intent = engine.parse_intent("Do something about it")

    assert intent.classification == IntentClassification.UNKNOWN
    assert intent.is_ambiguous
    assert intent.ambiguity_reason is not None


def test_intent_engine_empty():
    engine = IntentEngine()
    intent = engine.parse_intent("   ")

    assert intent.classification == IntentClassification.UNKNOWN
    assert intent.is_ambiguous
    assert intent.ambiguity_reason == "Empty request"
