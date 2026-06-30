from app.intelligence.intake.kpi.models import KPIAssessment, KPIStatus


class KPIEngine:
    """
    Evaluates current business metrics. Read-only. Never recommends actions.
    """

    def evaluate_metric(self, kpi_id: str, current: float, target: float) -> KPIAssessment:
        if target == 0:
            deviation = 0.0
        else:
            deviation = (current - target) / target * 100.0

        status = KPIStatus.HEALTHY

        # Simple negative deviation thresholds
        if deviation <= -20.0:
            status = KPIStatus.CRITICAL
        elif deviation <= -5.0:
            status = KPIStatus.WARNING

        return KPIAssessment(
            kpi_id=kpi_id,
            current_value=current,
            target_value=target,
            status=status,
            deviation_percentage=deviation
        )
