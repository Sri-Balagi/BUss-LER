from app.core.modules.ai.cognition import ActionDefinition

class ActionsPack:
    @classmethod
    def build(cls, module_name: str) -> list[ActionDefinition]:
        return [
            ActionDefinition(
                artifact_id="act_admit_patient",
                name="Admit Patient to Ward",
                description="Formally transition a patient from the ED to an inpatient ward bed.",
                preconditions=["Triage Complete", "Bed Available", "Physician Admission Order Active"],
                required_permissions=["role:admitting_physician", "role:charge_nurse"],
                expected_effects=["Patient status becomes Inpatient", "Bed status becomes Occupied"],
                potential_side_effects=["Increases term_bed_occupancy"],
                rollback_strategy="Cancel admission order and revert bed status.",
                risk_category="Clinical Workflow",
                risk_weight=0.3
            ),
            ActionDefinition(
                artifact_id="act_prescribe_medication",
                name="Prescribe Medication",
                description="Add a new pharmaceutical intervention to the patient's treatment plan.",
                preconditions=["Active Patient Encounter", "No Known Contraindicating Allergies"],
                required_permissions=["role:licensed_prescriber"],
                expected_effects=["Medication added to ent_medical_record"],
                potential_side_effects=["Adverse drug event"],
                rollback_strategy="Discontinue order and notify pharmacy.",
                risk_category="Clinical Safety",
                risk_weight=0.8
            )
        ]
