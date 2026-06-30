from typing import List

from pydantic import BaseModel, Field

from app.intelligence.learning.synthesis.models import KnowledgeArtifact


class KnowledgeRepositoryState(BaseModel):
    """The state of stored organizational intelligence."""
    artifacts: list[KnowledgeArtifact] = Field(default_factory=list)
