from app.core.modules.ai.cognition import Regulation

class RegulationsPack:
    @classmethod
    def build(cls, module_name: str) -> list[Regulation]:
        return [
            Regulation(
                artifact_id="reg_hipaa",
                name="Health Insurance Portability and Accountability Act (HIPAA)",
                description="US Federal law protecting sensitive patient health information from being disclosed.",
                requirements=[
                    "PHI (Protected Health Information) must be masked in all external AI logging.",
                    "Agents must only query patient data if an active Treatment relationship exists."
                ],
                compliance_scope="Data Privacy"
            )
        ]
