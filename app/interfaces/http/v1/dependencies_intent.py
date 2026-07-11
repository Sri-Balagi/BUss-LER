"""Intent and Goal dependencies for API v1."""

from fastapi import Depends
from app.bootstrap.container import get_container

async def get_intent_repository():
    from app.infrastructure.persistence.postgres.repositories.intent_repository import IntentRepository
    return get_container().resolve(IntentRepository)

async def get_goal_repository():
    from app.infrastructure.persistence.postgres.repositories.goal_repository import GoalRepository
    return get_container().resolve(GoalRepository)

async def get_goal_service():
    from app.application.goal.goal_service import GoalService
    return get_container().resolve(GoalService)

async def get_intent_classifier():
    from app.application.intent.intent_classifier import IntentClassifier
    return get_container().resolve(IntentClassifier)

async def get_intent_service():
    from app.application.intent.intent_service import IntentService
    return get_container().resolve(IntentService)
