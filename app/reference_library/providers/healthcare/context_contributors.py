from app.core.modules.ai.cognition import ContextContributorSpec

class ContextContributorsPack:
    @classmethod
    def build(cls, module_name: str) -> list[ContextContributorSpec]:
        return [
            ContextContributorSpec(
                contributor_id="ctx_active_allergies",
                name="Active Patient Allergies",
                provided_context_keys=["patient_allergies", "allergy_severity"]
            )
        ]
