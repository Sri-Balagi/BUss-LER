from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_storage_utilization', name='Storage Utilization', description='Disk space used.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 4, 7, 352851), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Used / Capacity')])
