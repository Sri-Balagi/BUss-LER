from typing import Any
from uuid import UUID

from app.domain.decisions.models import Decision
from app.domain.decisions.platform import IDecisionPlatform
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.knowledge.repository import IKnowledgeRepository
from app.domain.memory.platform import IMemoryPlatform


class DecisionPlatform(IDecisionPlatform):
    def __init__(self, intelligence: IIntelligencePlatform, memory: IMemoryPlatform, knowledge: IKnowledgeRepository):
        self._intelligence = intelligence
        self._memory = memory
        self._knowledge = knowledge

    async def evaluate_options(self, goal_id: UUID, context: dict[str, Any], options: list[dict[str, Any]]) -> Decision:
        decision = Decision(goal_id=goal_id, context=context, options=options)
        decision = await self.score_options(decision)
        decision.confidence = await self.estimate_confidence(decision)
        decision.risks = await self.assess_risks(decision)
        decision.selected_option = await self.recommend_action(decision)
        decision.justification = await self.explain_reasoning(decision)
        return decision

    async def score_options(self, decision: Decision) -> Decision:
        # Ask intelligence platform to score options based on memory and context
        # (Mock implementation for now)
        for idx, option in enumerate(decision.options):
            decision.option_scores[option.get('id', str(idx))] = 0.85 - (idx * 0.1) # simplistic mock scoring
        return decision

    async def estimate_confidence(self, decision: Decision) -> float:
        # (Mock) Calculate confidence based on scores
        if not decision.option_scores:
            return 0.0
        return max(decision.option_scores.values())

    async def assess_risks(self, decision: Decision) -> list[str]:
        # (Mock) Risk assessment
        return ["Potential latency in execution", "Resource unavailability"]

    async def recommend_action(self, decision: Decision) -> dict[str, Any]:
        if not decision.options:
            return {}
        # Return option with highest score
        best_id = max(decision.option_scores.items(), key=lambda x: x[1])[0]
        for option in decision.options:
            if option.get('id') == best_id or str(decision.options.index(option)) == best_id:
                return option
        return decision.options[0]

    async def explain_reasoning(self, decision: Decision) -> str:
        return "Selected option provides the optimal balance of speed and reliability based on historical execution memory."
