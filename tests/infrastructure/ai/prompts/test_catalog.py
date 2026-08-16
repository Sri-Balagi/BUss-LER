"""Tests for Prompt Catalog and PromptManager backward compatibility."""

import pytest

from app.infrastructure.ai.prompts import PromptManager
from app.infrastructure.ai.prompts.catalog import ALL_PROMPTS


def test_prompt_manager_initializes_with_catalog() -> None:
    """Verify PromptManager automatically loads the catalog."""
    manager = PromptManager()

    prompts = manager.list_prompts()

    assert "intent_classification" in prompts
    assert "memory_summarization" in prompts
    assert "goal_planning" in prompts
    assert "recommendation_generation" in prompts


def test_all_catalog_prompts_are_registered() -> None:
    """Verify all prompts declared in the catalog are registered."""
    manager = PromptManager()

    for template in ALL_PROMPTS:
        # Should not raise
        retrieved = manager.get(template.prompt_id, template.version)
        assert retrieved.prompt_id == template.prompt_id


def test_resolve_legacy_prompts() -> None:
    """Verify the four original prompts resolve correctly with test contexts."""
    manager = PromptManager()

    # 1. Memory
    mem_result = manager.resolve(
        "memory_summarization", "v1", {"memory_content": "User likes blue"}
    )
    assert "User likes blue" in mem_result

    # 2. Intent
    intent_result = manager.resolve(
        "intent_classification",
        "v1",
        {"content": "Order supplies", "business_context": "We need pens"},
    )
    assert "Order supplies" in intent_result

    # 3. Planning
    plan_result = manager.resolve(
        "goal_planning",
        "v1",
        {
            "goal_title": "Fix bug",
            "goal_description": "Fix the UI bug",
            "intent_context": "[]",
            "goals_context": "[]",
            "memory_context": "[]",
            "conversation_context": "[]",
            "business_state": "{}",
            "twin_context": "{}",
        },
    )
    assert "Fix the UI bug" in plan_result

    # 4. Recommendation
    rec_result = manager.resolve(
        "recommendation_generation",
        "v1",
        {
            "intent_context": "[]",
            "goals_context": "[]",
            "memory_context": "[]",
            "conversation_context": "[]",
            "business_state": "{}",
            "twin_context": "{}",
        },
    )
    assert "JSON array" in rec_result
