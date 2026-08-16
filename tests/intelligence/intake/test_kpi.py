from app.intelligence.intake.kpi.engine import KPIEngine
from app.intelligence.intake.kpi.models import KPIStatus


def test_kpi_healthy():
    engine = KPIEngine()
    assessment = engine.evaluate_metric("revenue", 100, 100)
    assert assessment.status == KPIStatus.HEALTHY
    assert assessment.deviation_percentage == 0.0


def test_kpi_warning():
    engine = KPIEngine()
    # Target 100, actual 90 -> -10% deviation
    assessment = engine.evaluate_metric("revenue", 90, 100)
    assert assessment.status == KPIStatus.WARNING
    assert assessment.deviation_percentage == -10.0


def test_kpi_critical():
    engine = KPIEngine()
    # Target 100, actual 70 -> -30% deviation
    assessment = engine.evaluate_metric("revenue", 70, 100)
    assert assessment.status == KPIStatus.CRITICAL
    assert assessment.deviation_percentage == -30.0


def test_kpi_zero_target():
    engine = KPIEngine()
    assessment = engine.evaluate_metric("errors", 5, 0)
    assert assessment.status == KPIStatus.HEALTHY
    assert assessment.deviation_percentage == 0.0
