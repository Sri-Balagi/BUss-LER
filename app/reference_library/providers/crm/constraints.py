from app.core.modules.ai.cognition import DomainConstraint

class ConstraintsPack:
    @classmethod
    def build(cls, module_name: str) -> list[DomainConstraint]:
        return [

            DomainConstraint(
                artifact_id="const_main",
                name="Minimum Deal Size for Enterprise Tier",
                description="Hard limit on operational capacity.",
                constraint_category="Operational",
                rule_description="System must reject requests exceeding capacity limits."
            )
    
        ]
