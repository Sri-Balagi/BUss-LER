from app.core.modules.ai.cognition import *
from datetime import datetime

class VocabularyPack:
    @classmethod
    def build(cls, module_name: str) -> SemanticVocabulary:
        return SemanticVocabulary(terms=[SemanticTerm(artifact_id='term_door_to_doctor', name='Door to Doctor Time', description='Minutes elapsed from patient triage registration to physician evaluation. Primary metric for emergency department operational efficiency.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 32, 958897), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Door-to-Doctor = Consult Time - Triage Arrival Time'), SemanticTerm(artifact_id='term_bed_occupancy', name='Bed Occupancy Rate', description='Percentage of active hospital beds occupied by inpatients. Measures clinical ward capacity strain.', source=None, authority=None, evidence=[], external_references=[], last_updated=datetime(2026, 7, 24, 17, 3, 32, 958897), knowledge_confidence=1.0, metadata={}, tags=[], references=[], version='1.0', formula='Occupancy Rate = (Occupied Beds / Total Bed Capacity) * 100')])
