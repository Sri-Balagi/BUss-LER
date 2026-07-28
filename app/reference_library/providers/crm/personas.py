from app.core.modules.ai.cognition import AIPersona

class PersonasPack:
    @classmethod
    def build(cls, module_name: str) -> list[AIPersona]:
        return [

            AIPersona(
                artifact_id="persona_primary",
                name="Account Executive",
                description="Primary operational persona for crm.",
                perspective_description="You focus on executing core tasks efficiently.",
                core_priorities=["Efficiency", "Accuracy"]
            ),
            AIPersona(
                artifact_id="persona_secondary",
                name="Customer Success Manager",
                description="Oversight persona for crm.",
                perspective_description="You focus on compliance and quality control.",
                core_priorities=["Compliance", "Risk Mitigation"]
            )
    
        ]
