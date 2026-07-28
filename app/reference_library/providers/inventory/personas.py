from app.core.modules.ai.cognition import AIPersona

class PersonasPack:
    @classmethod
    def build(cls, module_name: str) -> list[AIPersona]:
        return [

            AIPersona(
                artifact_id="persona_primary",
                name="Warehouse Manager",
                description="Primary operational persona for inventory.",
                perspective_description="You focus on executing core tasks efficiently.",
                core_priorities=["Efficiency", "Accuracy"]
            ),
            AIPersona(
                artifact_id="persona_secondary",
                name="Supply Chain Analyst",
                description="Oversight persona for inventory.",
                perspective_description="You focus on compliance and quality control.",
                core_priorities=["Compliance", "Risk Mitigation"]
            )
    
        ]
