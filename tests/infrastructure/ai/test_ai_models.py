"""Tests for Wave 0 foundation models — WP-01.

Tests cover all new models added in Wave 0:
  - AIRequestLifecycle: uniqueness, defaults, phase tracking
  - AIRequest: backward compatibility with new lifecycle field
  - StreamChunk: final chunk contract
  - StructuredRequest: generic type, temperature bounds, lifecycle carrier
  - ProviderError: attribute access, lifecycle_id, repr
  - StructuredOutputError: inheritance chain
  - BudgetExceededError: attribute access, lifecycle_id, repr

All tests are pure unit tests — no I/O, no network, no external dependencies.
"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import BaseModel, ValidationError

from app.infrastructure.ai.models import (
    AIRequest,
    AIRequestLifecycle,
    AIResponse,
    AIResponseMetadata,
    BudgetExceededError,
    ClassifyRequest,
    ClassifyResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderError,
    StreamChunk,
    StructuredOutputError,
    StructuredRequest,
)

# =============================================================================
# Helpers
# =============================================================================


def _metadata() -> AIResponseMetadata:
    return AIResponseMetadata(provider="test", model="test-v1", latency_ms=100.0)


# =============================================================================
# AIRequestLifecycle
# =============================================================================


class TestAIRequestLifecycle:
    def test_instantiates_with_required_operation(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        assert lc.operation == "generate"

    def test_lifecycle_id_is_uuid_v4_format(self) -> None:
        lc = AIRequestLifecycle(operation="embed")
        # Must parse as valid UUID without raising
        parsed = uuid.UUID(lc.lifecycle_id)
        assert str(parsed) == lc.lifecycle_id

    def test_lifecycle_ids_are_unique(self) -> None:
        ids = {AIRequestLifecycle(operation="generate").lifecycle_id for _ in range(50)}
        assert len(ids) == 50, "All lifecycle IDs must be unique"

    def test_created_at_defaults_to_utc_now(self) -> None:
        before = datetime.now(UTC)
        lc = AIRequestLifecycle(operation="stream")
        after = datetime.now(UTC)
        assert before <= lc.created_at <= after

    def test_phase_defaults_to_created(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        assert lc.phase == "CREATED"

    def test_entity_id_defaults_to_none(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        assert lc.entity_id is None

    def test_session_id_defaults_to_none(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        assert lc.session_id is None

    def test_prompt_id_defaults_to_none(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        assert lc.prompt_id is None

    def test_provider_name_defaults_to_none(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        assert lc.provider_name is None

    def test_entity_and_session_can_be_set(self) -> None:
        lc = AIRequestLifecycle(
            operation="generate",
            entity_id="entity-abc",
            session_id="session-xyz",
        )
        assert lc.entity_id == "entity-abc"
        assert lc.session_id == "session-xyz"

    def test_custom_lifecycle_id_is_preserved(self) -> None:
        custom_id = "00000000-0000-0000-0000-000000000001"
        lc = AIRequestLifecycle(operation="generate", lifecycle_id=custom_id)
        assert lc.lifecycle_id == custom_id

    def test_phase_can_be_updated(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        updated = lc.model_copy(update={"phase": "EXECUTING"})
        assert updated.phase == "EXECUTING"
        # Original is not mutated (Pydantic v2 models are not mutated by model_copy)
        assert lc.phase == "CREATED"

    def test_operation_is_required(self) -> None:
        with pytest.raises(ValidationError):
            AIRequestLifecycle()  # type: ignore[call-arg]

    def test_all_valid_operation_types_accepted(self) -> None:
        for op in ("generate", "generate_structured", "embed", "stream"):
            lc = AIRequestLifecycle(operation=op)
            assert lc.operation == op


# =============================================================================
# AIRequest — backward compatibility with lifecycle field
# =============================================================================


class TestAIRequestBackwardCompatibility:
    def test_existing_construction_without_lifecycle_still_works(self) -> None:
        """Critical: callers that do not pass lifecycle must not be broken."""
        req = AIRequest(prompt_id="intent_classification", version="v1", context={})
        assert req.prompt_id == "intent_classification"
        assert req.lifecycle is None

    def test_lifecycle_defaults_to_none(self) -> None:
        req = AIRequest(prompt_id="test_prompt")
        assert req.lifecycle is None

    def test_lifecycle_can_be_attached(self) -> None:
        lc = AIRequestLifecycle(operation="generate")
        req = AIRequest(prompt_id="test_prompt", lifecycle=lc)
        assert req.lifecycle is not None
        assert req.lifecycle.lifecycle_id == lc.lifecycle_id

    def test_all_original_fields_still_present(self) -> None:
        req = AIRequest(
            prompt_id="goal_planning",
            version="v2",
            context={"goal_title": "grow revenue"},
            system_instruction="Be concise.",
        )
        assert req.prompt_id == "goal_planning"
        assert req.version == "v2"
        assert req.context["goal_title"] == "grow revenue"
        assert req.system_instruction == "Be concise."

    def test_context_defaults_to_empty_dict(self) -> None:
        req = AIRequest(prompt_id="any_prompt")
        assert req.context == {}

    def test_version_defaults_to_v1(self) -> None:
        req = AIRequest(prompt_id="any_prompt")
        assert req.version == "v1"


# =============================================================================
# Existing Phase 1 Models — Non-Regression
# =============================================================================


class TestExistingModelsUnchanged:
    def test_ai_response_metadata_instantiates(self) -> None:
        meta = _metadata()
        assert meta.provider == "test"
        assert meta.model == "test-v1"
        assert meta.latency_ms == 100.0
        assert meta.prompt_tokens is None
        assert meta.completion_tokens is None

    def test_ai_response_instantiates(self) -> None:
        resp = AIResponse(content="Hello world", metadata=_metadata())
        assert resp.content == "Hello world"

    def test_embedding_request_instantiates(self) -> None:
        req = EmbeddingRequest(text="embed this")
        assert req.text == "embed this"
        assert req.model is None

    def test_embedding_response_instantiates(self) -> None:
        resp = EmbeddingResponse(vector=[0.1, 0.2, 0.3], metadata=_metadata())
        assert len(resp.vector) == 3

    def test_classify_request_instantiates(self) -> None:
        req = ClassifyRequest(prompt_id="intent_classification", content="buy milk")
        assert req.content == "buy milk"
        assert req.version == "v1"

    def test_classify_response_instantiates(self) -> None:
        resp = ClassifyResponse(raw_json={"key": "value"}, metadata=_metadata())
        assert resp.raw_json["key"] == "value"


# =============================================================================
# StreamChunk
# =============================================================================


class TestStreamChunk:
    def test_non_final_chunk_has_content_only(self) -> None:
        chunk = StreamChunk(content="Hello ")
        assert chunk.content == "Hello "
        assert chunk.is_final is False
        assert chunk.prompt_tokens is None
        assert chunk.completion_tokens is None
        assert chunk.error is None

    def test_final_chunk_carries_token_metadata(self) -> None:
        chunk = StreamChunk(
            content="world",
            is_final=True,
            prompt_tokens=10,
            completion_tokens=1,
        )
        assert chunk.is_final is True
        assert chunk.prompt_tokens == 10
        assert chunk.completion_tokens == 1

    def test_final_chunk_with_error_indicates_stream_failure(self) -> None:
        chunk = StreamChunk(
            content="partial",
            is_final=True,
            error="Stream ended prematurely",
        )
        assert chunk.is_final is True
        assert chunk.error == "Stream ended prematurely"

    def test_content_is_required(self) -> None:
        with pytest.raises(ValidationError):
            StreamChunk()  # type: ignore[call-arg]

    def test_is_final_defaults_to_false(self) -> None:
        chunk = StreamChunk(content="text")
        assert chunk.is_final is False

    def test_empty_content_is_valid(self) -> None:
        """Empty content is valid for keep-alive chunks."""
        chunk = StreamChunk(content="")
        assert chunk.content == ""


# =============================================================================
# StructuredRequest
# =============================================================================


class _TestOutputSchema(BaseModel):
    """Minimal Pydantic schema used to exercise StructuredRequest."""

    result: str
    confidence: float = 1.0


class TestStructuredRequest:
    def test_instantiates_with_required_fields(self) -> None:
        req = StructuredRequest(
            prompt_text="Classify this text",
            output_schema=_TestOutputSchema,
        )
        assert req.prompt_text == "Classify this text"
        assert req.output_schema is _TestOutputSchema

    def test_output_schema_holds_the_class_not_an_instance(self) -> None:
        req = StructuredRequest(
            prompt_text="test",
            output_schema=_TestOutputSchema,
        )
        # output_schema must be the class itself
        assert req.output_schema is _TestOutputSchema
        # It should be callable to create instances
        instance = req.output_schema(result="test")
        assert isinstance(instance, _TestOutputSchema)

    def test_temperature_defaults_to_0_2(self) -> None:
        req = StructuredRequest(prompt_text="test", output_schema=_TestOutputSchema)
        assert req.temperature == 0.2

    def test_temperature_bounds_enforced(self) -> None:
        # Below minimum
        with pytest.raises(ValidationError):
            StructuredRequest(
                prompt_text="test",
                output_schema=_TestOutputSchema,
                temperature=-0.1,
            )
        # Above maximum
        with pytest.raises(ValidationError):
            StructuredRequest(
                prompt_text="test",
                output_schema=_TestOutputSchema,
                temperature=2.1,
            )

    def test_temperature_at_boundaries_is_valid(self) -> None:
        req_low = StructuredRequest(
            prompt_text="t", output_schema=_TestOutputSchema, temperature=0.0
        )
        req_high = StructuredRequest(
            prompt_text="t", output_schema=_TestOutputSchema, temperature=2.0
        )
        assert req_low.temperature == 0.0
        assert req_high.temperature == 2.0

    def test_lifecycle_defaults_to_none(self) -> None:
        req = StructuredRequest(prompt_text="test", output_schema=_TestOutputSchema)
        assert req.lifecycle is None

    def test_lifecycle_can_be_attached(self) -> None:
        lc = AIRequestLifecycle(operation="generate_structured")
        req = StructuredRequest(
            prompt_text="test",
            output_schema=_TestOutputSchema,
            lifecycle=lc,
        )
        assert req.lifecycle is not None
        assert req.lifecycle.lifecycle_id == lc.lifecycle_id

    def test_system_instruction_defaults_to_none(self) -> None:
        req = StructuredRequest(prompt_text="test", output_schema=_TestOutputSchema)
        assert req.system_instruction is None

    def test_model_override_defaults_to_none(self) -> None:
        req = StructuredRequest(prompt_text="test", output_schema=_TestOutputSchema)
        assert req.model is None

    def test_prompt_text_is_required(self) -> None:
        with pytest.raises(ValidationError):
            StructuredRequest(output_schema=_TestOutputSchema)  # type: ignore[call-arg]

    def test_output_schema_is_required(self) -> None:
        with pytest.raises((ValidationError, TypeError)):
            StructuredRequest(prompt_text="test")  # type: ignore[call-arg]


# =============================================================================
# ProviderError
# =============================================================================


class TestProviderError:
    def test_is_exception(self) -> None:
        err = ProviderError("gemini", "generate", "API key invalid")
        assert isinstance(err, Exception)

    def test_message_format(self) -> None:
        err = ProviderError("gemini", "generate", "timeout")
        assert str(err) == "[gemini:generate] timeout"

    def test_attributes_accessible(self) -> None:
        err = ProviderError("openai", "embed", "rate limited", lifecycle_id="abc-123")
        assert err.provider == "openai"
        assert err.operation == "embed"
        assert err.detail == "rate limited"
        assert err.lifecycle_id == "abc-123"

    def test_lifecycle_id_defaults_to_none(self) -> None:
        err = ProviderError("gemini", "health_check", "connection refused")
        assert err.lifecycle_id is None

    def test_repr_without_lifecycle(self) -> None:
        err = ProviderError("gemini", "stream", "failed")
        assert "gemini" in repr(err)
        assert "stream" in repr(err)

    def test_repr_with_lifecycle(self) -> None:
        err = ProviderError("gemini", "generate", "failed", lifecycle_id="lc-001")
        assert "lc-001" in repr(err)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(ProviderError) as exc_info:
            raise ProviderError("gemini", "generate", "network error")
        assert exc_info.value.provider == "gemini"

    def test_can_be_caught_as_generic_exception(self) -> None:
        with pytest.raises(Exception):
            raise ProviderError("gemini", "generate", "network error")


# =============================================================================
# StructuredOutputError
# =============================================================================


class TestStructuredOutputError:
    def test_is_subclass_of_provider_error(self) -> None:
        err = StructuredOutputError("gemini", "generate_structured", "schema mismatch")
        assert isinstance(err, ProviderError)

    def test_is_subclass_of_exception(self) -> None:
        err = StructuredOutputError("gemini", "generate_structured", "schema mismatch")
        assert isinstance(err, Exception)

    def test_message_format_inherited(self) -> None:
        err = StructuredOutputError("anthropic", "generate_structured", "invalid JSON")
        assert str(err) == "[anthropic:generate_structured] invalid JSON"

    def test_can_be_caught_as_provider_error(self) -> None:
        with pytest.raises(ProviderError):
            raise StructuredOutputError("gemini", "generate_structured", "no schema")

    def test_can_be_caught_specifically(self) -> None:
        with pytest.raises(StructuredOutputError):
            raise StructuredOutputError("gemini", "generate_structured", "bad schema")

    def test_lifecycle_id_propagated(self) -> None:
        err = StructuredOutputError("gemini", "generate_structured", "fail", lifecycle_id="lc-456")
        assert err.lifecycle_id == "lc-456"


# =============================================================================
# BudgetExceededError
# =============================================================================


class TestBudgetExceededError:
    def test_is_exception(self) -> None:
        err = BudgetExceededError("entity-1", "hard_stop", "daily limit reached")
        assert isinstance(err, Exception)

    def test_message_format(self) -> None:
        err = BudgetExceededError("entity-1", "hard_stop", "100k tokens/day limit")
        assert "entity-1" in str(err)
        assert "hard_stop" in str(err)
        assert "100k tokens/day limit" in str(err)

    def test_attributes_accessible(self) -> None:
        err = BudgetExceededError("entity-abc", "hard_stop", "session limit", lifecycle_id="lc-789")
        assert err.entity_id == "entity-abc"
        assert err.policy == "hard_stop"
        assert err.detail == "session limit"
        assert err.lifecycle_id == "lc-789"

    def test_lifecycle_id_defaults_to_none(self) -> None:
        err = BudgetExceededError("entity-1", "hard_stop", "exceeded")
        assert err.lifecycle_id is None

    def test_repr_without_lifecycle(self) -> None:
        err = BudgetExceededError("entity-1", "hard_stop", "exceeded")
        assert "entity-1" in repr(err)
        assert "hard_stop" in repr(err)

    def test_repr_with_lifecycle(self) -> None:
        err = BudgetExceededError("entity-1", "hard_stop", "exceeded", lifecycle_id="lc-000")
        assert "lc-000" in repr(err)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(BudgetExceededError) as exc_info:
            raise BudgetExceededError("e", "hard_stop", "limit hit")
        assert exc_info.value.entity_id == "e"

    def test_is_not_provider_error(self) -> None:
        """BudgetExceededError is a distinct exception type, not a ProviderError."""
        err = BudgetExceededError("entity", "hard_stop", "exceeded")
        assert not isinstance(err, ProviderError)
