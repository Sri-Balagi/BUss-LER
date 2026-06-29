from pydantic import BaseModel, Field
from typing import List
from app.intelligence.learning.synthesis.models import KnowledgeArtifact

class KnowledgeRepositoryState(BaseModel):
    """The state of stored organizational intelligence."""
    artifacts: List[KnowledgeArtifact] = Field(default_factory=list)
