"""Tests for Provider Platform Prometheus metrics."""

from prometheus_client import REGISTRY

from app.infrastructure.ai.observability.metrics import (
    LLM_BUDGET_REJECTIONS,
    LLM_ERRORS,
    LLM_ESTIMATED_COST,
    LLM_FALLBACK_ACTIVATIONS,
    LLM_REQUEST_DURATION,
    LLM_STRUCTURED_OUTPUT_FAILURES,
    LLM_TOKENS_IN,
    LLM_TOKENS_OUT,
)


def test_metrics_registered() -> None:
    """Verify all metrics are registered with the Prometheus client."""
    # Getting the metric will raise if not registered or if we mis-named it
    metric_names = [m.name for m in REGISTRY.collect()]

    assert "bizos_llm_tokens_in" in metric_names
    assert "bizos_llm_tokens_out" in metric_names
    assert "bizos_llm_request_duration_seconds" in metric_names
    assert "bizos_llm_estimated_cost_usd" in metric_names
    assert "bizos_llm_errors" in metric_names
    assert "bizos_llm_fallback_activations" in metric_names
    assert "bizos_llm_budget_rejections" in metric_names
    assert "bizos_llm_structured_output_failures" in metric_names


def test_metric_labels() -> None:
    """Verify metrics have the correct labels defined."""
    # Test that we can instantiate the labeled versions without errors
    # (prometheus_client raises ValueError if incorrect labels are passed)

    LLM_TOKENS_IN.labels(provider="mock", model="test-model", operation="generate")
    LLM_TOKENS_OUT.labels(provider="mock", model="test-model", operation="generate")
    LLM_REQUEST_DURATION.labels(provider="mock", model="test-model", operation="generate")
    LLM_ESTIMATED_COST.labels(provider="mock", model="test-model", operation="generate")
    LLM_ERRORS.labels(provider="mock", model="test-model", operation="generate", error_type="ValueError")
    LLM_FALLBACK_ACTIVATIONS.labels(primary_provider="gemini", fallback_provider="openai")
    LLM_BUDGET_REJECTIONS.labels(provider="mock", budget_type="TOKEN")
    LLM_STRUCTURED_OUTPUT_FAILURES.labels(provider="mock", model="test-model")
