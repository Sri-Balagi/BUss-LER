from app.core.modules.ai.cognition import KPIDefinition

class KPIsPack:
    @classmethod
    def build(cls, module_name: str) -> list[KPIDefinition]:
        return [

            KPIDefinition(
                artifact_id="kpi_main",
                name="Project Management Efficiency Metric",
                description="Primary success metric for project_management.",
                formula="Success / Total * 100", unit_of_measure="Percentage"
            )
    
        ]
