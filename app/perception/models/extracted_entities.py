from datetime import datetime
from pydantic import BaseModel, Field


class ExtractedEntities(BaseModel):
    """Entities extracted from content by the Semantic Enricher."""

    people: list[str] = Field(default_factory=list, description="Names of individuals (e.g. Alice Chen)")
    organizations: list[str] = Field(default_factory=list, description="Companies or organizations (e.g. Acme Corp)")
    projects: list[str] = Field(default_factory=list, description="Project or initiative names (e.g. Project Atlas)")
    decisions: list[str] = Field(default_factory=list, description="Explicit decisions recorded")
    deadlines: list[str] = Field(default_factory=list, description="ISO-formatted or plain string deadlines")
    technologies: list[str] = Field(default_factory=list, description="Tools, frameworks, or tech names")
    monetary_values: list[str] = Field(default_factory=list, description="Financial figures mentioned")
    action_items: list[str] = Field(default_factory=list, description="Assigned tasks or action items")
