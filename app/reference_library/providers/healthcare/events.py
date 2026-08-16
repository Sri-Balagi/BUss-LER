from app.core.modules.ai.cognition import DomainEvent

class EventsPack:
    @classmethod
    def build(cls, module_name: str) -> list[DomainEvent]:
        return [
            DomainEvent(
                artifact_id="evt_patient_admitted",
                name="Patient Admitted Event",
                description="Fires when a patient is successfully assigned a bed.",
                payload_schema_keys=["patient_id", "bed_id", "admitting_physician_id", "timestamp"]
            ),
            DomainEvent(
                artifact_id="evt_vitals_deteriorated",
                name="Vitals Deteriorated Event",
                description="Fires when real-time telemetry detects a critical drop in patient vitals.",
                payload_schema_keys=["patient_id", "vital_sign", "previous_value", "current_value", "timestamp"]
            )
        ]
