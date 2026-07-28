from app.core.modules.ai.cognition import KPIDefinition

class KPIsPack:
    @classmethod
    def build(cls, module_name: str) -> list[KPIDefinition]:
        return [

            KPIDefinition(
                artifact_id="kpi_main",
                name="Analytics Efficiency Metric",
                description="Primary success metric for analytics.",
                formula="Success / Total * 100", unit_of_measure="Percentage"
            )
    
        ]
