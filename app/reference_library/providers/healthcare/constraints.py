from app.core.modules.ai.cognition import DomainConstraint

class ConstraintsPack:
    @classmethod
    def build(cls, module_name: str) -> list[DomainConstraint]:
        return [
            DomainConstraint(
                artifact_id="const_bed_capacity",
                name="Strict Bed Capacity Limit",
                description="A ward cannot admit a patient if bed occupancy is at 100%.",
                constraint_category="Operational Capacity",
                rule_description="If term_bed_occupancy == 100%, action_admit_patient is FORBIDDEN unless diverted."
            ),
            DomainConstraint(
                artifact_id="const_controlled_substances",
                name="Controlled Substance Dispensing",
                description="Controlled substances require two distinct authentications.",
                constraint_category="Clinical Safety",
                rule_description="Any medication class II or higher requires both Attending Physician and Lead Pharmacist approval."
            )
        ]
