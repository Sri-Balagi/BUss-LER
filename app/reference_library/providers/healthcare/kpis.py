from app.core.modules.ai.cognition import KPIDefinition

class KPIsPack:
    @classmethod
    def build(cls, module_name: str) -> list[KPIDefinition]:
        return [
            KPIDefinition(
                artifact_id="kpi_readmission_rate",
                name="30-Day Readmission Rate",
                description="Percentage of patients readmitted within 30 days of discharge.",
                formula="(Readmissions in 30 Days / Total Discharges) * 100",
                unit_of_measure="Percentage"
            )
        ]
