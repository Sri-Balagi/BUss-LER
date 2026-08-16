"""Loader for prompt catalogs."""

from app.infrastructure.ai.prompts.catalog import ALL_PROMPTS
from app.infrastructure.ai.prompts.registry import PromptRegistry


def load_catalog(registry: PromptRegistry) -> None:
    """Load all core prompts into the given registry."""
    for prompt in ALL_PROMPTS:
        registry.register(prompt)
