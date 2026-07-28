"""Versioned Prompt Registry for template versioning, variables, and rollback support."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PromptTemplate:
    name: str
    version: str
    template_text: str
    variables: List[str] = field(default_factory=list)
    description: str = ""


class VersionedPromptRegistry:
    """Registry managing versioned prompt templates and variable interpolation."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self._default_versions: Dict[str, str] = {}
        self._bootstrap_default_prompts()

    def register(self, template: PromptTemplate, set_as_default: bool = True) -> None:
        if template.name not in self._templates:
            self._templates[template.name] = {}
        self._templates[template.name][template.version] = template

        if set_as_default or template.name not in self._default_versions:
            self._default_versions[template.name] = template.version

    def get_template(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        if name not in self._templates:
            raise KeyError(f"Prompt template '{name}' not registered.")

        target_version = version or self._default_versions.get(name)
        if not target_version or target_version not in self._templates[name]:
            # Fallback to latest available version
            latest_version = list(self._templates[name].keys())[-1]
            return self._templates[name][latest_version]

        return self._templates[name][target_version]

    def render(self, name: str, version: Optional[str] = None, **kwargs) -> str:
        tpl = self.get_template(name, version)
        try:
            return tpl.template_text.format(**kwargs)
        except KeyError as e:
            # Fallback format handling missing variables gracefully
            text = tpl.template_text
            for k, v in kwargs.items():
                text = text.replace(f"{{{k}}}", str(v))
            return text

    def rollback(self, name: str, target_version: str) -> None:
        if name in self._templates and target_version in self._templates[name]:
            self._default_versions[name] = target_version

    def _bootstrap_default_prompts(self) -> None:
        """Register built-in system prompt templates."""
        self.register(
            PromptTemplate(
                name="planner_system_prompt",
                version="v1.0",
                template_text="Create execution plan candidates for objective: {objective}",
                variables=["objective"],
                description="Planner candidate generation prompt v1.0",
            )
        )
        self.register(
            PromptTemplate(
                name="owner_qa_prompt",
                version="v1.0",
                template_text=(
                    "You are BizOS, an AI Business Operating System. "
                    "Answer the owner's query based strictly on the provided context.\n\n"
                    "CONTEXT:\n{context}\n\n"
                    "QUERY:\n{query}"
                ),
                variables=["context", "query"],
                description="Owner Knowledge Base Q&A prompt v1.0",
            )
        )
