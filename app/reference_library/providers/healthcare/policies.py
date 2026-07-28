from app.core.modules.ai.cognition import BusinessPolicy

class PoliciesPack:
    @classmethod
    def build(cls, module_name: str) -> list[BusinessPolicy]:
        return [
            BusinessPolicy(
                artifact_id="pol_discharge_approval",
                name="Inpatient Discharge Approval",
                description="Rules governing the safe discharge of patients.",
                governance_scope="Clinical Operations",
                policy_statements=[
                    "A patient cannot be discharged without a signed order from the Attending Physician.",
                    "Pharmacy must clear all discharge medications before the patient leaves the facility."
                ]
            )
        ]
