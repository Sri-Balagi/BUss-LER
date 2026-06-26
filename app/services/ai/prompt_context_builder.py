"""PromptContextBuilder — Centralized context formatter for AI prompts.

Responsibilities:
  - Format typed CognitiveContext into prompt-friendly string dictionaries.
  - Removes formatting duplication from AI-powered engines.
"""

from typing import Dict, Any
from app.models.context import CognitiveContext


class PromptContextBuilder:
    """Formats CognitiveContext for ingestion by the AI Kernel."""

    @staticmethod
    def build_context_dict(cognitive_context: CognitiveContext) -> Dict[str, Any]:
        """Convert CognitiveContext into a dictionary for ClassifyRequest."""
        return {
            "intent_summary": str(cognitive_context.current_intent.raw_text if cognitive_context.current_intent else "No active intent."),
            "active_goals_context": PromptContextBuilder._format_goals(cognitive_context.active_goals),
            "memory_context": PromptContextBuilder._format_memories(cognitive_context.relevant_memories),
            "business_state": str(cognitive_context.business_state or {}),
        }

    @staticmethod
    def _format_memories(memories: list) -> str:
        if not memories:
            return "No relevant memories available."
        lines = []
        for i, mem in enumerate(memories, 1):
            category = mem.category or 'memory'
            lines.append(f"{i}. [{category}] {mem.content[:200]}")
        return "\n".join(lines)

    @staticmethod
    def _format_goals(goals: list) -> str:
        if not goals:
            return "No active goals."
        lines = []
        for i, goal in enumerate(goals, 1):
            status = goal.status.value if hasattr(goal.status, "value") else goal.status
            lines.append(f"{i}. [{status}] {goal.title} (priority: {goal.priority})")
        return "\n".join(lines)
