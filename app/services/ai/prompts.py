from typing import Dict, Any

class PromptManager:
    """
    Centralized registry for all AI prompts.
    Provides versioned access and template interpolation.
    """

    def __init__(self):
        # In a real system, this could be loaded from a database or YAML.
        # Structure: { prompt_id: { version: "Template string..." } }
        self._prompts: Dict[str, Dict[str, str]] = {
            "memory_summarization": {
                "v1": (
                    "Summarize the following memory in one clear, concise sentence.\n"
                    "Do not include commentary.\n\n"
                    "Memory content:\n"
                    "{memory_content}"
                )
            }
        }

    def resolve(self, prompt_id: str, version: str, context: Dict[str, Any]) -> str:
        """
        Resolve a prompt template by interpolating context variables.
        """
        if prompt_id not in self._prompts:
            raise ValueError(f"Prompt ID '{prompt_id}' not found.")
        
        versions = self._prompts[prompt_id]
        if version not in versions:
            raise ValueError(f"Version '{version}' for prompt '{prompt_id}' not found.")
        
        template = versions[version]
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing context variable {e} for prompt '{prompt_id}:{version}'")
