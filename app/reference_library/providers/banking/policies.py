from app.core.modules.ai.cognition import BusinessPolicy

class PoliciesPack:
    @classmethod
    def build(cls, module_name: str) -> list[BusinessPolicy]:
        return [

            BusinessPolicy(
                artifact_id="pol_main",
                name="Anti-Money Laundering (AML) Checks",
                description="Governing rules for banking operations.",
                governance_scope="Operations",
                policy_statements=["All actions must be logged.", "Secondary approval required for high-risk actions."]
            )
    
        ]
