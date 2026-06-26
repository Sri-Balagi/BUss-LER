"""FastAPI dependencies for API v1.

Re-exports all modular dependencies for backward compatibility.
Keeps endpoint routers clean and testable.
"""

from app.api.v1.dependencies_core import (
    get_supabase_client,
    get_qdrant_client,
    get_current_user,
    get_operation_context,
    check_rate_limit,
    audit_log_request,
    get_event_bus,
    get_entity_repository,
    get_twin_repository,
    get_snapshot_repository,
    get_history_repository,
    get_twin_service,
    get_entity_service,
)

from app.api.v1.dependencies_ai import (
    get_ai_kernel,
)

from app.api.v1.dependencies_memory import (
    get_memory_metadata_repository,
    get_memory_vector_repository,
    get_memory_service,
)

from app.api.v1.dependencies_trace import (
    get_cognitive_trace_repository,
    get_cognitive_trace_service,
)

from app.api.v1.dependencies_intent import (
    get_intent_repository,
    get_goal_repository,
    get_goal_service,
    get_intent_classifier,
    get_intent_service,
)

from app.api.v1.dependencies_planning import (
    get_plan_repository,
    get_plan_service,
    get_context_builder,
    get_planning_engine,
)

from app.api.v1.dependencies_recommendation import (
    get_recommendation_repository,
    get_recommendation_service,
    get_recommendation_engine,
)
