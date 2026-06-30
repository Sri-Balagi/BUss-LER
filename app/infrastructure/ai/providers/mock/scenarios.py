"""Scenario definitions for the Mock Provider."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from app.infrastructure.ai.models import AIRequest
from app.interfaces.http.schemas.base import DomainBaseModel


class MockScenarioMode(StrEnum):
    """Execution modes for the mock provider to simulate various edge cases."""

    FIXED_RESPONSE = "FIXED_RESPONSE"
    STRUCTURED_RESPONSE = "STRUCTURED_RESPONSE"
    STREAMING_SIMULATION = "STREAMING_SIMULATION"
    TIMEOUT_SIMULATION = "TIMEOUT_SIMULATION"
    FAILURE_SIMULATION = "FAILURE_SIMULATION"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    TOKEN_LIMIT_SIMULATION = "TOKEN_LIMIT_SIMULATION"
    LATENCY_SIMULATION = "LATENCY_SIMULATION"


class MockScenarioConfig(DomainBaseModel):
    """Configuration for a specific scenario mode."""

    mode: MockScenarioMode = Field(default=MockScenarioMode.FIXED_RESPONSE)

    # Text/Structured defaults
    default_text_response: str = "This is a mock response."
    default_structured_response: dict[str, Any] | None = None

    # Latency/Timeout
    latency_ms: int = 0
    timeout_threshold_ms: int = 5000

    # Failure Simulation (raise on Nth call)
    fail_on_call_number: int = 0
    error_message: str = "Mocked provider error"

    # Token Simulation
    mock_prompt_tokens: int = 10
    mock_completion_tokens: int = 20

    # Streaming Simulation
    streaming_chunks: list[str] = Field(default_factory=lambda: ["Chunk 1", "Chunk 2", "Chunk 3"])


class ProviderCall(DomainBaseModel):
    """Immutable record of a call made to the mock provider."""

    method_name: str
    request: AIRequest | None = None
    prompt_text: str | None = None
    structured_request: Any | None = None
    embedding_request: Any | None = None
    lifecycle_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
