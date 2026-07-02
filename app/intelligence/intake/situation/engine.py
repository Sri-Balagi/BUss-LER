from app.intelligence.intake.intent.models import ExecutiveIntent
from app.intelligence.intake.kpi.models import KPIAssessment, KPIStatus
from app.intelligence.intake.situation.models import (
    SituationAssessment,
    SituationGap,
    SituationOpportunity,
    SituationRisk,
)
from app.intelligence.workspaces.world_model.world_model import BusinessWorldModel


class SituationAnalysisEngine:
    """
    Combines Intent, KPIs, World Model, and Context to identify the current business situation.
    Does not plan, make decisions, or simulate.
    """

    def analyze(
        self,
        intent: ExecutiveIntent | None,
        kpis: list[KPIAssessment],
        world_model: BusinessWorldModel,
    ) -> SituationAssessment:
        risks = []
        opportunities = []
        gaps = []

        # Analyze KPIs
        for kpi in kpis:
            if kpi.status == KPIStatus.CRITICAL:
                risks.append(
                    SituationRisk(
                        risk_id=f"risk_{kpi.kpi_id}",
                        description=f"Critical deviation in {kpi.kpi_id} ({kpi.deviation_percentage}%)",
                        severity="HIGH",
                    )
                )
            elif kpi.status == KPIStatus.WARNING:
                risks.append(
                    SituationRisk(
                        risk_id=f"risk_{kpi.kpi_id}",
                        description=f"Warning deviation in {kpi.kpi_id} ({kpi.deviation_percentage}%)",
                        severity="MEDIUM",
                    )
                )

        # Analyze World Model Beliefs
        sentiment_belief = world_model.get_belief("customer_sentiment")
        if sentiment_belief and sentiment_belief.value == "improving":
            opportunities.append(
                SituationOpportunity(
                    opportunity_id="opp_sentiment",
                    description="Customer sentiment is improving.",
                    potential_value="increased_retention",
                )
            )
        elif sentiment_belief is None:
            gaps.append(
                SituationGap(gap_id="gap_sentiment", description="Missing customer sentiment data.")
            )

        summary = f"Situation analyzed based on {len(kpis)} KPIs and current world model."
        if intent:
            summary += f" Influenced by intent: {intent.classification.value}."

        return SituationAssessment(
            summary=summary, risks=risks, opportunities=opportunities, missing_information=gaps
        )
