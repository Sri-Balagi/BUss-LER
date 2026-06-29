from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class KnowledgeCategory(str, Enum):
    STRATEGIC = "STRATEGIC"
    OPERATIONAL = "OPERATIONAL"
    TACTICAL = "TACTICAL"
    CAUTIONARY = "CAUTIONARY"

class KnowledgeVersion(BaseModel):
    version_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeArtifact(BaseModel):
    """Reusable organizational intelligence extracted from reasoning."""
    artifact_id: str
    category: KnowledgeCategory
    description: str
    source_evaluation_ids: List[str] = Field(default_factory=list)
    version: KnowledgeVersion
