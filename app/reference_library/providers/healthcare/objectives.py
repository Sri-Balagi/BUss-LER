from app.core.modules.ai.cognition import BusinessObjective

class ObjectivesPack:
    @classmethod
    def build(cls, module_name: str) -> list[BusinessObjective]:
        return [
            BusinessObjective(
                artifact_id="obj_patient_safety",
                name="Maximize Patient Safety",
                description="Ensure zero critical medical errors during patient care and admission workflows.",
                target_metrics=["term_medication_error_rate", "term_readmission_rate"],
                priority_weight=1.0
            ),
            BusinessObjective(
                artifact_id="obj_operational_efficiency",
                name="Emergency Department Operational Efficiency",
                description="Minimize patient wait times while maintaining high triage accuracy.",
                target_metrics=["term_door_to_doctor", "term_bed_occupancy"],
                priority_weight=0.85
            )
        ]
