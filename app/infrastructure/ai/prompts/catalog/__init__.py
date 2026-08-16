"""Prompt Catalog for BizOS."""

from app.infrastructure.ai.prompts.catalog.intent import intent_classification_v1
from app.infrastructure.ai.prompts.catalog.memory import memory_summarization_v1
from app.infrastructure.ai.prompts.catalog.planning import goal_planning_v1
from app.infrastructure.ai.prompts.catalog.recommendation import recommendation_generation_v1

ALL_PROMPTS = [
    intent_classification_v1,
    memory_summarization_v1,
    goal_planning_v1,
    recommendation_generation_v1,
]
