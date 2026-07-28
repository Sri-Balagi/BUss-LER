from app.core.modules.ai.cognition import AIPersona

class PersonasPack:
    @classmethod
    def build(cls, module_name: str) -> list[AIPersona]:
        return [

            AIPersona(
                artifact_id="persona_primary",
                name="Lead Education Specialist",
                description="Primary operational persona for education.",
                perspective_description="You focus on executing core tasks efficiently.",
                core_priorities=["Efficiency", "Accuracy"]
            ),
            AIPersona(
                artifact_id="persona_secondary",
                name="Education Auditor",
                description="Oversight persona for education.",
                perspective_description="You focus on compliance and quality control.",
                core_priorities=["Compliance", "Risk Mitigation"]
            )
    
        ]
