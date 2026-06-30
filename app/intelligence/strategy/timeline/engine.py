import uuid
from typing import List

from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.strategy.timeline.models import StrategicMilestone, StrategicTimeline


class StrategicTimelineEngine:
    """
    Organizes objectives over time descriptively.
    Does not schedule runtime tasks.
    """
    def generate_timeline(self, objectives: list[ExecutiveObjective]) -> StrategicTimeline:
        milestones = []
        for obj in objectives:
            milestones.append(StrategicMilestone(
                milestone_id=f"ms_{obj.objective_id}",
                description=f"Milestone for: {obj.description}",
                target_date=None,
                dependent_on_milestone_ids=[]
            ))

        return StrategicTimeline(
            timeline_id=str(uuid.uuid4()),
            horizon_label="Current Horizon",
            milestones=milestones
        )
