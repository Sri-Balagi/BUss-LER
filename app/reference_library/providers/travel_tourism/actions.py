from app.core.modules.ai.cognition import ActionDefinition

class ActionsPack:
    @classmethod
    def build(cls, module_name: str) -> list[ActionDefinition]:
        return [

            ActionDefinition(
                artifact_id="act_primary",
                name="Execute Travel Tourism Task",
                description="Execute the primary business action.",
                preconditions=["System Available"], required_permissions=["role:operator"],
                expected_effects=["State updated"], potential_side_effects=["Resource consumed"],
                rollback_strategy="Revert state", risk_category="Low", risk_weight=0.1
            ),
            ActionDefinition(
                artifact_id="act_secondary",
                name="Validate Travel Tourism State",
                description="Perform validation or reconciliation.",
                preconditions=["Task completed"], required_permissions=["role:auditor"],
                expected_effects=["Verified state"], potential_side_effects=[],
                rollback_strategy="None", risk_category="Low", risk_weight=0.1
            )
    
        ]
