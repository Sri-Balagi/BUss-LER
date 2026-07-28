from app.core.modules.ai.cognition import DecisionFramework, DecisionFactor

class DecisionsPack:
    @classmethod
    def build(cls, module_name: str) -> list[DecisionFramework]:
        return [
            DecisionFramework(
                artifact_id="dec_triage_priority",
                name="Triage Priority Evaluation",
                description="Framework for determining the clinical urgency of a patient.",
                decision_goal="Assign an Emergency Severity Index (ESI) from 1 (Immediate) to 5 (Non-urgent).",
                factors=[
                    DecisionFactor(
                        factor_name="Airway/Breathing/Circulation Status",
                        importance_weight=1.0,
                        evaluation_criteria="If compromised, immediate ESI 1."
                    ),
                    DecisionFactor(
                        factor_name="Expected Resource Utilization",
                        importance_weight=0.6,
                        evaluation_criteria="Number of expected interventions (labs, imaging, meds)."
                    )
                ],
                trade_off_considerations=[
                    "Over-triage strains immediate resources but reduces risk of mortality.",
                    "Under-triage saves immediate resources but risks rapid deterioration."
                ]
            )
        ]
