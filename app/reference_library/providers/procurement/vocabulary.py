from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_spend_under_management', name='Spend Under Management', description='Controlled spend.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 4, 7, 340685), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Managed / Total')])
