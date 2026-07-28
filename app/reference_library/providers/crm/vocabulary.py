from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_pipeline_velocity', name='Sales Pipeline Velocity', description='The speed at which leads move through the deal pipeline to generate revenue. Measures revenue generation throughput.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 32, 974266), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Velocity = (Qualified Opportunities * Win Rate % * Avg Deal Size) / Sales Cycle Days'), SemanticTerm(artifact_id='term_cac', name='Customer Acquisition Cost', description='Total cost of sales and marketing required to acquire a new customer. Measures sales efficiency.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 32, 974266), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='CAC = (Sales Expenses + Marketing Expenses) / New Customers Acquired')])
