from app.shared.exceptions.errors import (
    AIKernelError,
    AIOutputValidationError,
    BizOSError,
    CognitiveTraceNotFoundError,
    ContextAssemblyError,
    ContextBuildError,
    ContextDependencyCycleError,
    ContextValidationError,
    ConversationNotFoundError,
    DomainValidationError,
    DuplicateMemoryError,
    DuplicateTwinError,
    EntityNotFoundError,
    GoalNotFoundError,
    IntentClassificationError,
    IntentNotFoundError,
    InvalidGoalTransitionError,
    InvalidIntentTransitionError,
    InvalidPlanTransitionError,
    MemoryNotFoundError,
    NotFoundError,
    PlanGenerationError,
    PlanNotFoundError,
    ProviderConfigurationError,
    ProviderNotRegisteredError,
    RecommendationGenerationError,
    RecommendationNotFoundError,
    RepositoryError,
    ServiceError,
    TwinNotFoundError,
    VectorDatabaseError,
    VersionConflictError,
)


def test_bizos_error():
    err = BizOSError("Test message", detail="Test detail")
    assert err.message == "Test message"
    assert err.detail == "Test detail"
    assert str(err) == "Test message"


def test_not_found_error():
    err = NotFoundError("Resource missing")
    assert err.message == "Resource missing"


def test_entity_not_found_error():
    err = EntityNotFoundError("123")
    assert err.entity_id == "123"
    assert "123" in err.message
    assert "123" in err.detail


def test_twin_not_found_error():
    err = TwinNotFoundError("456")
    assert err.twin_id == "456"
    assert "456" in err.message


def test_version_conflict_error():
    err = VersionConflictError(1, 2)
    assert err.expected_version == 1
    assert err.actual_version == 2
    assert "1" in err.message
    assert "2" in err.message


def test_duplicate_twin_error():
    err = DuplicateTwinError("789")
    assert err.entity_id == "789"
    assert "789" in err.message


def test_domain_validation_error():
    err = DomainValidationError("Invalid domain")
    assert err.message == "Invalid domain"


def test_repository_error():
    err = RepositoryError("save_data", detail="db disconnected")
    assert err.operation == "save_data"
    assert "save_data" in err.message
    assert err.detail == "db disconnected"


def test_vector_database_error():
    err = VectorDatabaseError("search_vec")
    assert err.operation == "search_vec"
    assert "An unexpected error" in err.detail


def test_service_error():
    err = ServiceError("do_work")
    assert err.operation == "do_work"
    assert "do_work" in err.message


def test_memory_not_found_error():
    err = MemoryNotFoundError("mem1")
    assert err.memory_id == "mem1"
    assert "mem1" in err.message


def test_duplicate_memory_error():
    err = DuplicateMemoryError()
    assert err.operation == "memory_create"
    assert err.detail == "Memory already exists"


def test_ai_kernel_error():
    err = AIKernelError("openai", "generate", "timeout")
    assert err.provider == "openai"
    assert err.operation == "generate"
    assert "timeout" in err.message


def test_provider_configuration_error():
    err = ProviderConfigurationError("openai", "no api key")
    assert err.provider == "openai"
    assert err.operation == "configuration"
    assert "no api key" in err.message


def test_intent_not_found_error():
    err = IntentNotFoundError("intent1")
    assert err.intent_id == "intent1"
    assert "intent1" in err.message


def test_intent_classification_error():
    err = IntentClassificationError("bad json")
    assert err.operation == "intent_classification"
    assert err.detail == "bad json"


def test_invalid_intent_transition_error():
    err = InvalidIntentTransitionError("DRAFT", "ACTIVE", "intent1")
    assert "intent1" in err.message
    assert "DRAFT" in err.message
    assert "ACTIVE" in err.message


def test_goal_not_found_error():
    err = GoalNotFoundError("goal1")
    assert err.goal_id == "goal1"
    assert "goal1" in err.message


def test_invalid_goal_transition_error():
    err = InvalidGoalTransitionError("A", "B", "goal1")
    assert "goal1" in err.message
    assert "A" in err.message
    assert "B" in err.message


def test_plan_not_found_error():
    err = PlanNotFoundError("plan1")
    assert err.plan_id == "plan1"
    assert "plan1" in err.message


def test_invalid_plan_transition_error():
    err = InvalidPlanTransitionError("X", "Y", "plan1")
    assert "plan1" in err.message
    assert "X" in err.message


def test_plan_generation_error():
    err = PlanGenerationError("failed")
    assert err.operation == "plan_generation"
    assert err.detail == "failed"


def test_recommendation_not_found_error():
    err = RecommendationNotFoundError("rec1")
    assert err.recommendation_id == "rec1"
    assert "rec1" in err.message


def test_recommendation_generation_error():
    err = RecommendationGenerationError("error")
    assert err.operation == "recommendation_generation"
    assert err.detail == "error"


def test_cognitive_trace_not_found_error():
    err = CognitiveTraceNotFoundError("trace1")
    assert err.trace_id == "trace1"
    assert "trace1" in err.message


def test_context_build_error():
    err = ContextBuildError("build failed")
    assert err.operation == "context_build"
    assert err.detail == "build failed"


def test_ai_output_validation_error():
    err = AIOutputValidationError("parse", "invalid format")
    assert err.operation == "ai_output_validation.parse"
    assert err.detail == "invalid format"


def test_context_assembly_error():
    err = ContextAssemblyError("asm err")
    assert err.operation == "context_assembly"
    assert err.detail == "asm err"


def test_context_validation_error():
    err = ContextValidationError(["err1", "err2"])
    assert err.operation == "context_validation"
    assert "err1; err2" in err.detail


def test_context_dependency_cycle_error():
    err = ContextDependencyCycleError(["A", "B", "A"])
    assert err.cycle == ["A", "B", "A"]
    assert "A → B → A" in err.message


def test_provider_not_registered_error():
    err = ProviderNotRegisteredError("src")
    assert err.source == "src"
    assert "src" in err.message


def test_conversation_not_found_error():
    err = ConversationNotFoundError("thread1")
    assert err.thread_id == "thread1"
    assert "thread1" in err.message
