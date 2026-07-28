from app.core.modules.ai.cognition import CapabilityDefinition

class CapabilityDefinitionsPack:
    @classmethod
    def build(cls, module_name: str) -> list[CapabilityDefinition]:
        return [
            CapabilityDefinition(
                artifact_id="cap_ehr_integration",
                name="Electronic Health Record Integration",
                description="Ability to read and write directly to the hospital's EHR database.",
                category="Integration",
                dependent_capabilities=[]
            )
        ]
