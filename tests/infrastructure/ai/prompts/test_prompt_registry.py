"""Tests for PromptRegistry and PromptTemplate."""

import pytest

from app.infrastructure.ai.prompts.registry import (
    MissingContextVariableError,
    PromptNotFoundError,
    PromptRegistry,
)
from app.infrastructure.ai.prompts.template import PromptTemplate, ProviderVariant


@pytest.fixture
def empty_registry() -> PromptRegistry:
    return PromptRegistry()


@pytest.fixture
def sample_template() -> PromptTemplate:
    return PromptTemplate(
        prompt_id="test_prompt",
        version="v1",
        base_template="Hello {name}, welcome to {place}!",
        context_variables=["name", "place"],
        provider_variants=[
            ProviderVariant(
                provider_name="anthropic", template="Greetings {name}, you are now in {place}."
            )
        ],
    )


def test_register_and_get(empty_registry: PromptRegistry, sample_template: PromptTemplate) -> None:
    empty_registry.register(sample_template)

    retrieved = empty_registry.get("test_prompt", "v1")
    assert retrieved == sample_template


def test_get_not_found(empty_registry: PromptRegistry) -> None:
    with pytest.raises(PromptNotFoundError, match="Prompt ID 'missing' not found."):
        empty_registry.get("missing", "v1")


def test_get_version_not_found(
    empty_registry: PromptRegistry, sample_template: PromptTemplate
) -> None:
    empty_registry.register(sample_template)

    with pytest.raises(
        PromptNotFoundError, match="Version 'v2' for prompt 'test_prompt' not found."
    ):
        empty_registry.get("test_prompt", "v2")


def test_resolve_base_template(
    empty_registry: PromptRegistry, sample_template: PromptTemplate
) -> None:
    empty_registry.register(sample_template)

    result = empty_registry.resolve(
        prompt_id="test_prompt", version="v1", context={"name": "Alice", "place": "Wonderland"}
    )

    assert result == "Hello Alice, welcome to Wonderland!"


def test_resolve_provider_variant(
    empty_registry: PromptRegistry, sample_template: PromptTemplate
) -> None:
    empty_registry.register(sample_template)

    result = empty_registry.resolve(
        prompt_id="test_prompt",
        version="v1",
        context={"name": "Alice", "place": "Wonderland"},
        provider_name="anthropic",
    )

    assert result == "Greetings Alice, you are now in Wonderland."


def test_resolve_provider_fallback(
    empty_registry: PromptRegistry, sample_template: PromptTemplate
) -> None:
    empty_registry.register(sample_template)

    result = empty_registry.resolve(
        prompt_id="test_prompt",
        version="v1",
        context={"name": "Alice", "place": "Wonderland"},
        provider_name="unknown_provider",
    )

    assert result == "Hello Alice, welcome to Wonderland!"


def test_resolve_missing_context(
    empty_registry: PromptRegistry, sample_template: PromptTemplate
) -> None:
    empty_registry.register(sample_template)

    with pytest.raises(
        MissingContextVariableError, match="Missing context variable.s. \\['place'\\]"
    ):
        empty_registry.resolve(prompt_id="test_prompt", version="v1", context={"name": "Alice"})


def test_resolve_implicit_missing_context(empty_registry: PromptRegistry) -> None:
    # A template that uses {secret} but doesn't declare it
    template = PromptTemplate(
        prompt_id="sneaky",
        version="v1",
        base_template="The secret is {secret}.",
        context_variables=[],
    )
    empty_registry.register(template)

    with pytest.raises(MissingContextVariableError, match="Missing context variable 'secret'"):
        empty_registry.resolve("sneaky", "v1", context={})


def test_list_prompts(empty_registry: PromptRegistry, sample_template: PromptTemplate) -> None:
    empty_registry.register(sample_template)

    v2_template = PromptTemplate(
        prompt_id="test_prompt", version="v2", base_template="Hi {name}", context_variables=["name"]
    )
    empty_registry.register(v2_template)

    prompts = empty_registry.list_prompts()
    assert "test_prompt" in prompts
    assert set(prompts["test_prompt"]) == {"v1", "v2"}
