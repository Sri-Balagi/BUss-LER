from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_food_cost_pct', name='Food Cost Percentage', description='Ratio of food inventory costs to gross food sales. Measures kitchen efficiency and menu profitability.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 32, 911079), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Food Cost % = (COGS / Food Revenue) * 100'), SemanticTerm(artifact_id='term_revpash', name='RevPASH', description='Revenue Per Available Seat Hour. Measures dining room capacity utilization and sales speed.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 32, 911079), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='RevPASH = Total Revenue / (Available Seats * Operating Hours)')])
