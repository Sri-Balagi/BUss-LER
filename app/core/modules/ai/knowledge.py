"""AI Knowledge Extension Framework for injecting business domain expertise into BizOS AI Platform."""

from typing import Any

from pydantic import BaseModel, Field

from app.core.modules.ai.cognition import BusinessKnowledgeModel


class DomainVocabulary(BaseModel):
    """Business terminology and domain vocabulary mapping taught by a module."""

    term: str
    definition: str
    aliases: list[str] = Field(default_factory=list)
    formula: str | None = None


class PromptTemplatePack(BaseModel):
    """Domain-specific system prompt templates provided by a module."""

    template_id: str
    name: str
    description: str
    system_prompt: str
    user_prompt_template: str


class ReasoningRule(BaseModel):
    """Business reasoning rule (Deprecated: prefer BusinessKnowledgeModel decision frameworks)."""

    rule_id: str
    condition: str
    recommendation: str
    severity: str = "warning"


class ModuleKnowledgePack(BaseModel):
    """Legacy AI Knowledge Pack exposed by a business module."""

    module_id: str
    vocabularies: list[DomainVocabulary] = Field(default_factory=list)
    prompt_templates: list[PromptTemplatePack] = Field(default_factory=list)
    reasoning_rules: list[ReasoningRule] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "DomainVocabulary",
    "PromptTemplatePack",
    "ReasoningRule",
    "ModuleKnowledgePack",
    "BusinessKnowledgeModel",
]
