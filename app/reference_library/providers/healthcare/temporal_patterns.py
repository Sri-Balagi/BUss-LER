from app.core.modules.ai.cognition import TemporalPattern

class TemporalPatternsPack:
    @classmethod
    def build(cls, module_name: str) -> list[TemporalPattern]:
        return [
            TemporalPattern(
                artifact_id="temp_flu_season",
                name="Winter Flu Season Surge",
                description="Expected surge in respiratory complaints during winter months.",
                pattern_schedule="November to February (Northern Hemisphere)",
                impact_description="Increases ED volume by 20-30%. Requires dynamic adjustment of const_bed_capacity tolerance."
            )
        ]
