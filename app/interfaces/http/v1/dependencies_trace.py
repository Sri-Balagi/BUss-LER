"""Cognitive Trace dependencies for API v1."""

from fastapi import Depends
from app.bootstrap.container import get_container

async def get_cognitive_trace_repository():
    from app.infrastructure.persistence.postgres.repositories.trace_repository import TraceRepository
    return get_container().resolve(TraceRepository)

async def get_cognitive_trace_service():
    from app.application.trace.cognitive_trace_service import CognitiveTraceService
    return get_container().resolve(CognitiveTraceService)
