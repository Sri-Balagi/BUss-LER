"""Dedicated Multi-Source Context Builder Service.

Assembles context across multiple system layers:
- Vector Knowledge Base
- Vector Memory Traces
- Enterprise Policies & SLAs
- Current Active Goals & Workflows
- Active Digital Twin State
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.domain.memory.models import MemoryRecord
from app.domain.memory.platform import IMemoryPlatform
from app.domain.twin.models import DigitalTwinState


class ContextBuilderService:
    """Assembles rich multi-source context for AI reasoning and decision making."""

    def __init__(self, memory_platform: Optional[IMemoryPlatform] = None):
        self._memory_platform = memory_platform

    async def assemble_context(
        self,
        query: str,
        digital_twin_state: Optional[DigitalTwinState] = None,
        policies: Optional[List[str]] = None,
        active_goals: Optional[List[Dict[str, Any]]] = None,
        extra_kb_docs: Optional[List[Dict[str, Any]]] = None,
        limit_memories: int = 5,
    ) -> Dict[str, Any]:
        """Assemble structured context bundle from all available intelligence sources."""

        # 1. Retrieve vector memories if platform available
        memories: List[MemoryRecord] = []
        if self._memory_platform:
            try:
                memories = await self._memory_platform.retrieve_context(query=query, limit=limit_memories)
            except Exception:
                memories = []

        # 2. Extract Digital Twin active ground truth
        twin_props = digital_twin_state.properties if digital_twin_state else {}
        twin_status = digital_twin_state.status.value if digital_twin_state else "UNKNOWN"

        # 3. Format policies & SOPs
        applied_policies = policies or [
            "Wait time SLA target: <= 20 minutes",
            "Kitchen staffing minimum: 4 active cooks per peak service",
            "VIP Corporate Party: Zero wait time guarantee",
        ]

        # 4. Assemble complete prompt context string
        context_sections = []

        if extra_kb_docs:
            kb_str = "\n".join([f"- [{doc.get('title', 'KB')}] {doc.get('content', '')}" for doc in extra_kb_docs])
            context_sections.append(f"=== KNOWLEDGE BASE FINDINGS ===\n{kb_str}")

        if memories:
            mem_str = "\n".join([f"- {m.title}: {m.content}" for m in memories])
            context_sections.append(f"=== RELEVANT MEMORY TRACES ===\n{mem_str}")

        if twin_props:
            twin_str = "\n".join([f"- {k}: {v}" for k, v in twin_props.items()])
            context_sections.append(f"=== DIGITAL TWIN REAL-TIME STATE [{twin_status}] ===\n{twin_str}")

        if applied_policies:
            pol_str = "\n".join([f"- {p}" for p in applied_policies])
            context_sections.append(f"=== APPLIED BUSINESS POLICIES & SLAS ===\n{pol_str}")

        if active_goals:
            goals_str = "\n".join([f"- Goal {g.get('id')}: {g.get('title')} ({g.get('priority')})" for g in active_goals])
            context_sections.append(f"=== ACTIVE CRISIS GOALS ===\n{goals_str}")

        full_context_text = "\n\n".join(context_sections)

        return {
            "query": query,
            "assembled_context_text": full_context_text,
            "raw_memories": memories,
            "digital_twin_properties": twin_props,
            "applied_policies": applied_policies,
            "extra_kb_docs": extra_kb_docs or [],
        }
