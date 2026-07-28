from app.core.modules.ai.cognition import KPIDefinition

class KPIsPack:
    @classmethod
    def build(cls, module_name: str) -> list[KPIDefinition]:
        return [

            KPIDefinition(
                artifact_id="kpi_main",
                name="Calendar Scheduling Efficiency Metric",
                description="Primary success metric for calendar_scheduling.",
                formula="Success / Total * 100", unit_of_measure="Percentage"
            )
    
        ]
