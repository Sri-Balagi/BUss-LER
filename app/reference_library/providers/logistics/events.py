from app.core.modules.ai.cognition import DomainEvent

class EventsPack:
    @classmethod
    def build(cls, module_name: str) -> list[DomainEvent]:
        return [

            DomainEvent(
                artifact_id="evt_main",
                name="Proof of Delivery Signed",
                description="Significant state change in logistics.",
                payload_schema_keys=["id", "timestamp", "status"]
            )
    
        ]
