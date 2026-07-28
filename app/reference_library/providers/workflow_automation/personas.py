from app.core.modules.ai.cognition import AIPersona

class PersonasPack:
    @classmethod
    def build(cls, module_name: str) -> list[AIPersona]:
        return [

            AIPersona(
                artifact_id="persona_primary",
                name="Lead Workflow Automation Specialist",
                description="Primary operational persona for workflow_automation.",
                perspective_description="You focus on executing core tasks efficiently.",
                core_priorities=["Efficiency", "Accuracy"]
            ),
            AIPersona(
                artifact_id="persona_secondary",
                name="Workflow Automation Auditor",
                description="Oversight persona for workflow_automation.",
                perspective_description="You focus on compliance and quality control.",
                core_priorities=["Compliance", "Risk Mitigation"]
            )
    
        ]
