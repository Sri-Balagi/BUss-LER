"""Prompt Registry for BizOS."""

from typing import Any

import structlog

from app.infrastructure.ai.prompts.template import PromptTemplate

logger = structlog.get_logger(__name__)


class PromptNotFoundError(Exception):
    """Raised when a requested prompt ID or version is not found in the registry."""

    pass


class MissingContextVariableError(Exception):
    """Raised when a required context variable is not provided during resolution."""

    pass


class PromptRegistry:
    """Centralized, typed registry for all AI prompts.

    Replaces the legacy dict-based PromptManager.
    """

    def __init__(self):
        # Structure: { prompt_id: { version: PromptTemplate } }
        self._prompts: dict[str, dict[str, PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> None:
        """Register a new prompt template or overwrite an existing one."""
        if template.prompt_id not in self._prompts:
            self._prompts[template.prompt_id] = {}

        self._prompts[template.prompt_id][template.version] = template
        logger.debug("prompt_registered", prompt_id=template.prompt_id, version=template.version)

    def get(self, prompt_id: str, version: str) -> PromptTemplate:
        """Retrieve a specific prompt template by ID and version."""
        if prompt_id not in self._prompts:
            raise PromptNotFoundError(f"Prompt ID '{prompt_id}' not found.")

        versions = self._prompts[prompt_id]
        if version not in versions:
            raise PromptNotFoundError(f"Version '{version}' for prompt '{prompt_id}' not found.")

        return versions[version]

    def resolve(
        self,
        prompt_id: str,
        version: str,
        context: dict[str, Any],
        provider_name: str | None = None,
    ) -> str:
        """Resolve a prompt template by interpolating context variables.

        Args:
            prompt_id: The ID of the prompt to resolve
            version: The version string (e.g. 'v1')
            context: Dictionary of variables for interpolation
            provider_name: Optional provider name to select an optimized variant

        Returns:
            The fully interpolated prompt string

        Raises:
            PromptNotFoundError: If the prompt or version is not registered
            MissingContextVariableError: If a required context variable is missing
        """
        template_obj = self.get(prompt_id, version)

        # Validate context against declared variables
        missing_vars = [var for var in template_obj.context_variables if var not in context]
        if missing_vars:
            raise MissingContextVariableError(
                f"Missing context variable(s) {missing_vars} for prompt '{prompt_id}:{version}'"
            )

        # Select the appropriate template string
        template_str = template_obj.base_template
        if provider_name:
            for variant in template_obj.provider_variants:
                if variant.provider_name == provider_name:
                    template_str = variant.template
                    break

        # Interpolate variables
        try:
            return template_str.format(**context)
        except KeyError as e:
            # Fallback for implicit variables not in context_variables
            raise MissingContextVariableError(
                f"Missing context variable {e} for prompt '{prompt_id}:{version}'"
            ) from e

    def list_prompts(self) -> dict[str, list[str]]:
        """Return all registered prompt IDs and their available versions."""
        return {pid: list(versions.keys()) for pid, versions in self._prompts.items()}
