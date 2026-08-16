from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_dso', name='Days Sales Outstanding', description='Average number of days required to collect payment after an invoice is issued. Primary metric for cash collection efficiency.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 33, 3200), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='DSO = (Accounts Receivable / Total Credit Sales) * Days in Period'), SemanticTerm(artifact_id='term_quick_ratio', name='Quick Ratio', description='Ratio of liquid current assets to short-term liabilities. Measures immediate solvency.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 33, 3200), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Quick Ratio = (Cash + Marketable Securities + AR) / Current Liabilities')])
