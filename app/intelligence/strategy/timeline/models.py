from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class StrategicMilestone(BaseModel):
    milestone_id: str
    description: str
    target_date: datetime | None = None
    dependent_on_milestone_ids: list[str] = Field(default_factory=list)

class StrategicTimeline(BaseModel):
    """
    Descriptive organization of objectives over time.
    Does not schedule runtime execution.
    """
    timeline_id: str
    horizon_label: str
    milestones: list[StrategicMilestone] = Field(default_factory=list)
