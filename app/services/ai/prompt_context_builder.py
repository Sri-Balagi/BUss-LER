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
            safe_content = mem.content.replace('{', '{{').replace('}', '}}')
            lines.append(f"{i}. [{category}] {safe_content[:200]}")
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

    @staticmethod
    def build_from_enterprise_context(context: "EnterpriseContext") -> Dict[str, Any]:
        """Convert an assembled M4 EnterpriseContext into a dictionary for the AI Kernel."""
        from app.models.enums import ContextSource

        def get_section(source: ContextSource) -> str:
            section = next((s for s in context.sections if s.source == source), None)
            if not section or not section.items:
                return f"No {source.value} data."
            return PromptContextBuilder._format_enterprise_section(section)

        return {
            "intent_context": get_section(ContextSource.INTENT),
            "goals_context": get_section(ContextSource.GOAL),
            "memory_context": get_section(ContextSource.MEMORY),
            "business_state": get_section(ContextSource.BUSINESS_STATE),
            "plan_context": get_section(ContextSource.PLAN),
            "recommendation_context": get_section(ContextSource.RECOMMENDATION),
            "conversation_context": get_section(ContextSource.CONVERSATION),
            "twin_context": get_section(ContextSource.TWIN),
            "trace_context": get_section(ContextSource.TRACE),
        }

    @staticmethod
    def _format_enterprise_section(section: "ContextSection") -> str:
        if not section.items:
            return ""
        lines = []
        for i, item in enumerate(section.items, 1):
            # Show priority indicator for context item
            priority = item.priority.value.upper() if item.priority else "MEDIUM"
            safe_content = item.content.strip().replace('{', '{{').replace('}', '}}')
            lines.append(f"[{priority}] {safe_content}")
        return "\n".join(lines)
