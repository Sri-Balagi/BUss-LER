from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StrategicMilestone(BaseModel):
    milestone_id: str
    description: str
    target_date: Optional[datetime] = None
    dependent_on_milestone_ids: List[str] = Field(default_factory=list)

class StrategicTimeline(BaseModel):
    """
    Descriptive organization of objectives over time.
    Does not schedule runtime execution.
    """
    timeline_id: str
    horizon_label: str
    milestones: List[StrategicMilestone] = Field(default_factory=list)
