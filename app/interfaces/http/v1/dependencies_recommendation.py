"""Recommendation dependencies for API v1."""

from app.bootstrap.container import get_container


async def get_recommendation_repository():
    from app.infrastructure.persistence.postgres.repositories.recommendation_repository import (
        RecommendationRepository,
    )

    return get_container().resolve(RecommendationRepository)


async def get_recommendation_service():
    from app.application.recommendation.recommendation_service import RecommendationService

    return get_container().resolve(RecommendationService)


async def get_recommendation_engine():
    from app.application.recommendation.recommendation_engine import RecommendationEngine

    return get_container().resolve(RecommendationEngine)
