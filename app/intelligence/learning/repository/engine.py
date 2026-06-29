from typing import List
from app.intelligence.learning.repository.models import KnowledgeRepositoryState
from app.intelligence.learning.synthesis.models import KnowledgeArtifact

class ExecutiveKnowledgeRepository:
    """
    Stores and retrieves validated organizational intelligence.
    """
    def __init__(self):
        self._state = KnowledgeRepositoryState()
        
    def store_artifact(self, artifact: KnowledgeArtifact):
        self._state.artifacts.append(artifact)
        
    def retrieve_artifacts(self) -> List[KnowledgeArtifact]:
        return self._state.artifacts
        
    def get_state(self) -> KnowledgeRepositoryState:
        return self._state
