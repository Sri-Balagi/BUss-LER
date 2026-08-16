from app.core.modules.ai.cognition import StateTransitionModel

class StateTransitionsPack:
    @classmethod
    def build(cls, module_name: str) -> list[StateTransitionModel]:
        return [
            StateTransitionModel(
                artifact_id="st_bed_lifecycle_admit",
                name="Bed Lifecycle: Admit",
                description="Transition a bed from clean and available to occupied.",
                entity_reference="ent_hospital_bed",
                from_state="AVAILABLE_CLEAN",
                to_state="OCCUPIED",
                trigger_events=["evt_patient_admitted"]
            ),
            StateTransitionModel(
                artifact_id="st_bed_lifecycle_discharge",
                name="Bed Lifecycle: Discharge",
                description="Transition a bed from occupied to dirty upon discharge.",
                entity_reference="ent_hospital_bed",
                from_state="OCCUPIED",
                to_state="NEEDS_CLEANING",
                trigger_events=["evt_patient_discharged"]
            )
        ]
