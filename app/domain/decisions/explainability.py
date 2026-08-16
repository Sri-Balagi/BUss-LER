"""Decision Lineage & Explainability Generator."""

from typing import Any, Dict, List, Optional
from app.domain.decisions.models import Decision


class DecisionExplainabilityEngine:
    """Generates human-readable decision lineage & audit trail reports."""

    @staticmethod
    def generate_lineage_report(
        decision: Decision,
        retrieved_memories: Optional[List[Any]] = None,
        applied_policies: Optional[List[str]] = None,
        kb_sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        mem_titles = [getattr(m, "title", str(m)) for m in (retrieved_memories or [])]
        pols = applied_policies or ["Standard Operational Policy"]
        sources = kb_sources or ["Domain Knowledge Base"]

        explanation_text = (
            f"DECISION LINEAGE REPORT [Goal: {decision.goal_id}]\n"
            f"Selected Strategy: {decision.justification}\n"
            f"Confidence Score: {decision.confidence * 100:.1f}%\n"
            f"Knowledge Sources Consulted: {', '.join(sources)}\n"
            f"Retrieved Memory Traces: {', '.join(mem_titles) if mem_titles else 'None'}\n"
            f"Applied Policies: {', '.join(pols)}"
        )

        return {
            "goal_id": str(decision.goal_id),
            "confidence": decision.confidence,
            "justification": decision.justification,
            "retrieved_memories": mem_titles,
            "applied_policies": pols,
            "knowledge_sources": sources,
            "lineage_text": explanation_text,
        }
