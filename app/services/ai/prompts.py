"""Centralized versioned prompt library for BizOS.

All prompts are registered here with explicit version identifiers.
No prompt may be embedded inside a service or repository.

Versioning convention:
    {capability}_{version}
    Examples: intent_classification_v1, goal_planning_v1, recommendation_generation_v1

The AI Kernel resolves prompts via PromptManager.resolve(prompt_id, version, context).
"""

from typing import Dict, Any


class PromptManager:
    """Centralized registry for all AI prompts.

    Provides versioned access and template interpolation.
    In a future milestone this may be backed by a database or YAML config.
    Structure: { prompt_id: { version: "Template string..." } }
    """

    def __init__(self):
        self._prompts: Dict[str, Dict[str, str]] = {
            # =========================================================
            # Milestone 2 — Memory Engine
            # =========================================================
            "memory_summarization": {
                "v1": (
                    "Summarize the following memory in one clear, concise sentence.\n"
                    "Do not include commentary.\n\n"
                    "Memory content:\n"
                    "{memory_content}"
                )
            },
            # =========================================================
            # Milestone 3 — Intent Classification
            # =========================================================
            "intent_classification": {
                "v1": (
                    "You are an expert business intent classifier for an AI Operating System.\n\n"
                    "Analyse the following user input and return a JSON object matching the schema below.\n"
                    "Return ONLY the JSON object. No preamble, no explanation, no markdown.\n\n"
                    "User input:\n"
                    "{content}\n\n"
                    "Business context (may be empty):\n"
                    "{business_context}\n\n"
                    "Required JSON schema:\n"
                    "{{\n"
                    '  "intent_type": "<one of: inventory, calendar, analytics, finance, communication, task_management, reporting, research, general>",\n'
                    "  \"business_domain\": \"<short domain label, e.g. 'Supply Chain', 'Human Resources'>\",\n"
                    '  "entities": [\n'
                    '    {{"type": "<entity type>", "value": "<raw value>", "normalized": "<normalised form>"}}\n'
                    "  ],\n"
                    '  "related_goals": ["<goal category or title>"],\n'
                    '  "urgency": "<low|normal|high|critical>",\n'
                    '  "priority": <integer 1-10>,\n'
                    '  "timeframe": "<natural language timeframe or null>",\n'
                    '  "confidence": "<high|medium|low>",\n'
                    '  "ambiguities": ["<ambiguous aspect>"],\n'
                    '  "follow_up_questions": ["<clarifying question>"],\n'
                    '  "reasoning_metadata": {{\n'
                    '    "key_signals": ["<signal 1>"],\n'
                    '    "classifier_notes": "<brief engineering note>"\n'
                    "  }}\n"
                    "}}"
                )
            },
            # =========================================================
            # Milestone 3 — Goal Planning
            # =========================================================
            "goal_planning": {
                "v1": (
                    "You are an expert business strategist and execution planner.\n\n"
                    "Generate a structured execution plan for the goal described below.\n"
                    "Return ONLY a JSON object matching the schema. No preamble, no markdown.\n\n"
                    "Goal:\n"
                    "{goal_title}\n\n"
                    "Goal description:\n"
                    "{goal_description}\n\n"
                    "Current intent:\n"
                    "{intent_context}\n\n"
                    "Active goals (context):\n"
                    "{goals_context}\n\n"
                    "Relevant memories (context):\n"
                    "{memory_context}\n\n"
                    "Conversation history:\n"
                    "{conversation_context}\n\n"
                    "Business state:\n"
                    "{business_state}\n\n"
                    "Twin profile:\n"
                    "{twin_context}\n\n"
                    "Required JSON schema:\n"
                    "{{\n"
                    '  "rationale": "<why this plan addresses the goal>",\n'
                    '  "steps": [\n'
                    "    {{\n"
                    '      "step_number": <int>,\n'
                    '      "action": "<action description>",\n'
                    '      "expected_outcome": "<expected result>",\n'
                    '      "depends_on": [<step numbers>],\n'
                    '      "estimated_effort": "<time estimate or null>"\n'
                    "    }}\n"
                    "  ],\n"
                    '  "assumptions": ["<assumption>"],\n'
                    '  "risks": [\n'
                    '    {{"risk": "<risk description>", "likelihood": "<low|medium|high>", "mitigation": "<mitigation strategy>"}}\n'
                    "  ],\n"
                    '  "dependencies": ["<external dependency>"],\n'
                    '  "estimated_effort": "<total effort estimate or null>",\n'
                    '  "confidence": <float 0.0-1.0>\n'
                    "}}"
                )
            },
            # =========================================================
            # Milestone 3 — Recommendation Generation
            # =========================================================
            "recommendation_generation": {
                "v1": (
                    "You are a proactive AI advisor for an AI Operating System.\n\n"
                    "Analyse the context below and generate actionable business recommendations.\n"
                    "Return ONLY a JSON array. No preamble, no markdown.\n\n"
                    "Current intent:\n"
                    "{intent_context}\n\n"
                    "Active goals:\n"
                    "{goals_context}\n\n"
                    "Relevant memories:\n"
                    "{memory_context}\n\n"
                    "Conversation history:\n"
                    "{conversation_context}\n\n"
                    "Business state:\n"
                    "{business_state}\n\n"
                    "Twin profile:\n"
                    "{twin_context}\n\n"
                    "Each recommendation must follow this schema:\n"
                    "{{\n"
                    '  "title": "<short title>",\n'
                    '  "body": "<full recommendation text>",\n'
                    '  "rationale": "<why this is recommended>",\n'
                    '  "confidence": "<high|medium|low>",\n'
                    '  "supporting_memory_refs": [<indices into provided memories>],\n'
                    '  "supporting_goal_refs": [<indices into provided goals>],\n'
                    '  "explainability_note": "<brief engineering note for observability>"\n'
                    "}}\n\n"
                    "Return a JSON array of 1-5 recommendations ordered by priority descending."
                )
            },
        }

    def resolve(self, prompt_id: str, version: str, context: Dict[str, Any]) -> str:
        """Resolve a prompt template by interpolating context variables."""
        if prompt_id not in self._prompts:
            raise ValueError(f"Prompt ID '{prompt_id}' not found.")

        versions = self._prompts[prompt_id]
        if version not in versions:
            raise ValueError(f"Version '{version}' for prompt '{prompt_id}' not found.")

        template = versions[version]
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(
                f"Missing context variable {e} for prompt '{prompt_id}:{version}'"
            ) from e

    def list_prompts(self) -> Dict[str, list]:
        """Return all registered prompt IDs and their available versions."""
        return {pid: list(versions.keys()) for pid, versions in self._prompts.items()}
