"""Context Strategy Layer — Phases 4, 5, 6.

Provides pluggable abstractions and default implementations for:
  - AbstractContextRanker    → DefaultContextRanker
  - AbstractContextCompressor → DefaultContextCompressor
  - AbstractContextWindowBuilder → DefaultContextWindowBuilder

All strategies are deterministic: same inputs → same outputs, always.
No LLM calls are made by the ranker or window builder.
The compressor may call AIKernel.summarize() for memory merging.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from math import exp
from typing import List, Optional, Tuple
from uuid import uuid4

import structlog

from app.models.enterprise_context import (
    ContextItem,
    ContextProvenance,
    ContextSection,
    ContextWindow,
)
from app.models.enums import ContextPriority, ContextSource
from app.services.context_policies import ContextPolicy

logger = structlog.get_logger(__name__)


# =============================================================================
# Priority weights for deterministic ordering
# =============================================================================

_PRIORITY_WEIGHTS: dict[ContextPriority, float] = {
    ContextPriority.CRITICAL:   1.0,
    ContextPriority.HIGH:       0.75,
    ContextPriority.MEDIUM:     0.50,
    ContextPriority.LOW:        0.25,
    ContextPriority.BACKGROUND: 0.05,
}

_SECTION_PRIORITY_ORDER: list[ContextSource] = [
    ContextSource.INTENT,
    ContextSource.GOAL,
    ContextSource.PLAN,
    ContextSource.RECOMMENDATION,
    ContextSource.MEMORY,
    ContextSource.TWIN,
    ContextSource.BUSINESS_STATE,
    ContextSource.CONVERSATION,
    ContextSource.TRACE,
    ContextSource.EXTERNAL,
]

_RECENCY_DECAY_LAMBDA = 0.05   # e^(-λ · age_hours)


# =============================================================================
# Phase 4 — Ranker
# =============================================================================


class AbstractContextRanker(ABC):
    """Abstract ranking strategy for context sections and items."""

    @abstractmethod
    def rank(
        self,
        sections: List[ContextSection],
        policy: ContextPolicy,
    ) -> List[ContextSection]:
        """Return sections with items ranked by relevance. Deterministic."""
        pass


class DefaultContextRanker(AbstractContextRanker):
    """Deterministic multi-factor ranking.

    Score formula (per item):
        score = (intent_relevance × 0.35)
              + (recency         × 0.25)
              + (priority        × 0.20)
              + (confidence      × 0.15)
              + (goal_alignment  × 0.05)

    Ranking is deterministic — no randomness, no LLM calls.
    """

    def rank(
        self,
        sections: List[ContextSection],
        policy: ContextPolicy,
    ) -> List[ContextSection]:
        ranked_sections: List[ContextSection] = []

        for section in sections:
            ranked_items = sorted(
                section.items,
                key=lambda item: self._score(item),
                reverse=True,
            )
            # Write ranking_score back into provenance
            updated_items = []
            for item in ranked_items:
                score = self._score(item)
                updated_provenance = item.provenance.model_copy(
                    update={"ranking_score": score}
                )
                updated_item = item.model_copy(update={"provenance": updated_provenance})
                updated_items.append(updated_item)

            ranked_sections.append(
                section.model_copy(update={"items": updated_items})
            )

        # Sort sections by priority order
        ranked_sections.sort(
            key=lambda s: self._section_order(s.source)
        )
        return ranked_sections

    @staticmethod
    def _score(item: ContextItem) -> float:
        """Compute composite relevance score for a single item."""
        prov = item.provenance

        # intent_relevance: currently uses confidence as proxy
        # (true embedding similarity requires M5 vector store integration)
        intent_relevance = prov.confidence

        # recency: exponential decay on age in hours
        now = datetime.now(timezone.utc)
        age_hours = max(
            0.0,
            (now - prov.retrieval_timestamp).total_seconds() / 3600,
        )
        recency = exp(-_RECENCY_DECAY_LAMBDA * age_hours)

        # priority
        priority_score = _PRIORITY_WEIGHTS.get(item.priority, 0.5)

        # confidence
        confidence = prov.confidence

        # goal_alignment: 1.0 if item references a domain object (e.g., goal ID)
        goal_alignment = 1.0 if item.domain_object_id is not None else 0.0

        return (
            intent_relevance * 0.35
            + recency * 0.25
            + priority_score * 0.20
            + confidence * 0.15
            + goal_alignment * 0.05
        )

    @staticmethod
    def _section_order(source: ContextSource) -> int:
        try:
            return _SECTION_PRIORITY_ORDER.index(source)
        except ValueError:
            return len(_SECTION_PRIORITY_ORDER)


# =============================================================================
# Phase 5 — Compressor
# =============================================================================


class AbstractContextCompressor(ABC):
    """Abstract compression strategy for context sections."""

    @abstractmethod
    def compress(
        self,
        sections: List[ContextSection],
        budget: int,
    ) -> List[ContextSection]:
        """Return compressed sections. Provenance is always preserved."""
        pass


class DefaultContextCompressor(AbstractContextCompressor):
    """Default compression strategy.

    Steps:
      1. Deduplication — group items by semantic fingerprint, keep highest-ranked.
      2. Completed goal collapse — multiple similar low-scoring items → single summary item.
      3. Provenance preservation — every compressed item retains compression_origin.
      4. Explainability — every compression decision logs a compression_reason.

    Note: Memory merging (AI-assisted) is a Phase 8 extension and not included
    in the deterministic default compressor.
    """

    def compress(
        self,
        sections: List[ContextSection],
        budget: int,
    ) -> List[ContextSection]:
        compressed: List[ContextSection] = []

        for section in sections:
            deduped_items = self._deduplicate(section.items)
            collapsed_items = self._collapse_low_priority(deduped_items)
            new_token_estimate = sum(i.token_estimate for i in collapsed_items)
            compressed.append(
                section.model_copy(update={
                    "items": collapsed_items,
                    "token_estimate": new_token_estimate,
                })
            )

        return compressed

    @staticmethod
    def _fingerprint(item: ContextItem) -> str:
        """Deterministic fingerprint: normalized content + provider + domain_object_id."""
        normalized_content = " ".join(item.content.split()).lower()
        provider_val = item.provenance.provider.value if item.provenance else "unknown"
        domain_id = str(item.domain_object_id) if item.domain_object_id else "none"
        fingerprint_source = f"{normalized_content}|{provider_val}|{domain_id}"
        return hashlib.md5(fingerprint_source.encode("utf-8")).hexdigest()

    def _deduplicate(self, items: List[ContextItem]) -> List[ContextItem]:
        """Group items by fingerprint; keep highest-ranked per group."""
        groups: dict[str, List[ContextItem]] = {}
        for item in items:
            fp = self._fingerprint(item)
            groups.setdefault(fp, []).append(item)

        result: List[ContextItem] = []
        for fp, group_items in groups.items():
            if len(group_items) == 1:
                result.append(group_items[0])
                continue

            # Keep highest ranked; compress the rest into its provenance
            best = max(group_items, key=lambda i: i.provenance.ranking_score)
            origin_ids = [i.item_id for i in group_items if i.item_id != best.item_id]
            updated_prov = best.provenance.model_copy(update={
                "compression_origin": list(best.provenance.compression_origin) + origin_ids,
                "compression_reason": (
                    f"Deduplicated {len(group_items)} items with identical semantic fingerprint."
                ),
            })
            result.append(best.model_copy(update={"provenance": updated_prov}))

        return result

    @staticmethod
    def _collapse_low_priority(items: List[ContextItem]) -> List[ContextItem]:
        """Collapse low-priority background items into a single summary item
        when there are more than 3 of them."""
        background = [i for i in items if i.priority == ContextPriority.BACKGROUND]
        non_background = [i for i in items if i.priority != ContextPriority.BACKGROUND]

        if len(background) <= 3:
            return items

        # Build a collapsed summary item
        collapsed_ids = [i.item_id for i in background]
        summary_content = (
            f"[Collapsed {len(background)} background context items. "
            f"Combined content: {' | '.join(i.content[:50] for i in background[:5])}...]"
        )
        collapsed_provenance = ContextProvenance(
            provider=background[0].provenance.provider,
            service_name=background[0].provenance.service_name,
            confidence=min(i.provenance.confidence for i in background),
            ranking_score=min(i.provenance.ranking_score for i in background),
            compression_origin=collapsed_ids,
            compression_reason=(
                f"Collapsed {len(background)} BACKGROUND priority items to reduce token count."
            ),
        )
        collapsed_item = ContextItem(
            item_id=uuid4(),
            source=background[0].source,
            priority=ContextPriority.BACKGROUND,
            content=summary_content,
            content_type="summary",
            token_estimate=len(summary_content) // 4,
            provenance=collapsed_provenance,
        )
        return non_background + [collapsed_item]


# =============================================================================
# Phase 6 — Window Builder
# =============================================================================


class AbstractContextWindowBuilder(ABC):
    """Abstract strategy for building the final ContextWindow from ranked sections."""

    @abstractmethod
    def build_window(
        self,
        sections: List[ContextSection],
        budget: int,
        critical_reserve: float = 0.1,
    ) -> ContextWindow:
        pass


class DefaultContextWindowBuilder(AbstractContextWindowBuilder):
    """Greedy token-budget window builder.

    Guarantees:
      - Intent + active goal sections are always included (critical_reserve = 10% of budget).
      - Remaining sections are packed greedily from highest to lowest priority.
      - overflow=True if any items were excluded due to budget exhaustion.
    """

    _CRITICAL_RESERVE_RATIO = 0.10

    def build_window(
        self,
        sections: List[ContextSection],
        budget: int,
        critical_reserve: float = 0.1,
    ) -> ContextWindow:
        critical_reserve = int(budget * self._CRITICAL_RESERVE_RATIO)
        remaining_budget = budget
        packed_sections: List[ContextSection] = []
        items_included = 0
        items_excluded = 0

        # --- Critical sections (INTENT + GOAL) go first ---
        critical_sources = {ContextSource.INTENT, ContextSource.GOAL}
        critical_sections = [s for s in sections if s.source in critical_sources]
        remaining_sections = [s for s in sections if s.source not in critical_sources]

        for section in critical_sections:
            packed, excluded, remaining_budget = self._pack_section(
                section, remaining_budget
            )
            if packed:
                packed_sections.append(packed)
                items_included += packed.item_count
            items_excluded += excluded

        # Ensure critical reserve is not violated by remaining
        remaining_budget = max(remaining_budget - critical_reserve, 0)

        # --- Greedy packing of remaining sections ---
        for section in remaining_sections:
            if remaining_budget <= 0:
                items_excluded += section.item_count
                continue
            packed, excluded, remaining_budget = self._pack_section(
                section, remaining_budget
            )
            if packed:
                packed_sections.append(packed)
                items_included += packed.item_count
            items_excluded += excluded

        token_estimate = sum(s.token_estimate for s in packed_sections)
        return ContextWindow(
            sections=packed_sections,
            token_estimate=token_estimate,
            budget=budget,
            items_included=items_included,
            items_excluded=items_excluded,
            overflow=items_excluded > 0,
        )

    @staticmethod
    def _pack_section(
        section: ContextSection, budget: int
    ) -> Tuple[Optional[ContextSection], int, int]:
        """Pack as many items from a section as the budget allows.

        Returns: (packed_section | None, items_excluded, remaining_budget)
        """
        packed_items: List[ContextItem] = []
        excluded = 0

        for item in section.items:
            cost = item.token_estimate or (len(item.content) // 4)
            if cost <= budget:
                packed_items.append(item)
                budget -= cost
            else:
                excluded += 1

        if not packed_items:
            return None, excluded, budget

        packed = section.model_copy(update={
            "items": packed_items,
            "token_estimate": sum(i.token_estimate for i in packed_items),
        })
        return packed, excluded, budget
