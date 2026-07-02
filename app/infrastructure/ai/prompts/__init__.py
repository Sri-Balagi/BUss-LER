"""Prompt management package for BizOS.

This package replaces the legacy prompts.py module, providing a typed,
versioned PromptRegistry while maintaining backward compatibility via the
PromptManager alias.
"""

from app.infrastructure.ai.prompts.loader import load_catalog
from app.infrastructure.ai.prompts.registry import (
    MissingContextVariableError,
    PromptNotFoundError,
    PromptRegistry,
)
from app.infrastructure.ai.prompts.template import PromptTemplate, ProviderVariant


class PromptManager(PromptRegistry):
    """Backward compatibility alias for PromptRegistry.

    Automatically loads the core prompt catalog on instantiation.
    """

    def __init__(self):
        super().__init__()
        load_catalog(self)


__all__ = [
    "PromptRegistry",
    "PromptManager",
    "PromptTemplate",
    "ProviderVariant",
    "PromptNotFoundError",
    "MissingContextVariableError",
]
