import uuid
from typing import List

from app.intelligence.strategy.conflict.models import ConflictAssessment, ConflictType
from app.intelligence.strategy.goals.models import Goal
from app.intelligence.strategy.objectives.models import ExecutiveObjective


class ObjectiveConflictResolver:
    """
    Detects conflicts between objectives or goals.
    Does not resolve them through planning.
    """

    def detect_conflicts(self, objectives: list[ExecutiveObjective], goals: list[Goal]) -> list[ConflictAssessment]:
        conflicts = []

        # Mock logic to detect mutually exclusive keywords
        objective_texts = [obj.description.lower() for obj in objectives]

        has_growth = any("grow" in text or "expand" in text for text in objective_texts)
        has_cut = any("reduce cost" in text or "cut" in text for text in objective_texts)

        if has_growth and has_cut:
            conflicts.append(ConflictAssessment(
                conflict_id=str(uuid.uuid4()),
                conflict_type=ConflictType.MUTUALLY_EXCLUSIVE,
                description="Growth objective conflicts with cost reduction objective.",
                involved_objective_ids=[obj.objective_id for obj in objectives if "grow" in obj.description.lower() or "cost" in obj.description.lower()]
            ))

        return conflicts
