"""Context Validation Layer — Extension E.

A validation gate that runs after provider collection and before ranking.
Prevents malformed EnterpriseContexts from progressing through the pipeline.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List

from app.intelligence.intake.situation.enterprise_context import ContextSection
from app.shared.enums import ContextSource
from app.interfaces.http.schemas.base import DomainBaseModel
from app.application.context.foundation.context_policies import ContextPolicy


class ValidationResult(DomainBaseModel):
    """Result of context validation."""

    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class AbstractContextValidator(ABC):
    """Abstract validation gate for assembled context sections."""

    @abstractmethod
    def validate(
        self,
        sections: List[ContextSection],
        policy: ContextPolicy,
    ) -> ValidationResult:
        pass


class DefaultContextValidator(AbstractContextValidator):
    """Default implementation of context validation.

    Performs 8 checks before allowing sections to advance to ranking:
      1. Required section check
      2. Duplicate item detection
      3. Provenance validation
      4. Citation validation
      5. Metadata timing validation
      6. Token estimation sanity check
      7. Confidence and Ranking bounds check
      8. Critical section verification (GOAL required → must have items)
    """

    def validate(
        self,
        sections: List[ContextSection],
        policy: ContextPolicy,
    ) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        present_sources = {s.source for s in sections}

        # 1. Required section check
        for required in policy.required_providers:
            if required not in present_sources:
                errors.append(
                    f"Required provider '{required.value}' has no section in assembled context."
                )

        # 2. Duplicate item detection
        seen_item_ids = set()
        for section in sections:
            for item in section.items:
                if item.item_id in seen_item_ids:
                    warnings.append(
                        f"Duplicate ContextItem ID '{item.item_id}' found across sections."
                    )
                seen_item_ids.add(item.item_id)

        # 3. Provenance validation — every item must have a populated provenance
        for section in sections:
            for item in section.items:
                if item.provenance is None:
                    errors.append(
                        f"ContextItem '{item.item_id}' in section '{section.source.value}' "
                        f"is missing ContextProvenance."
                    )

        # 4. Citation validation — no null/empty string citations
        for section in sections:
            for item in section.items:
                if item.provenance:
                    for citation in item.provenance.citations:
                        if not citation or not citation.strip():
                            warnings.append(
                                f"Empty citation found in ContextItem '{item.item_id}'."
                            )

        # 5. Metadata validation — assembled_at must not be in the future
        now = datetime.now(timezone.utc)
        for section in sections:
            if section.retrieved_at > now:
                errors.append(
                    f"Section '{section.source.value}' has a future retrieved_at timestamp: "
                    f"{section.retrieved_at.isoformat()}."
                )

        # 6. Token estimation sanity — total must not exceed budget × 5
        total_tokens = sum(s.token_estimate for s in sections)
        sanity_limit = policy.token_budget * 5
        if total_tokens > sanity_limit:
            errors.append(
                f"Total token estimate ({total_tokens}) exceeds sanity limit "
                f"({sanity_limit} = budget {policy.token_budget} × 5)."
            )
        if total_tokens < 0:
            errors.append(f"Total token estimate ({total_tokens}) is negative.")

        # 7. Confidence and Ranking Bounds
        for section in sections:
            for item in section.items:
                if item.provenance:
                    conf = item.provenance.confidence
                    if not (0.0 <= conf <= 1.0):
                        errors.append(
                            f"ContextItem '{item.item_id}' has invalid confidence: {conf}"
                        )

                    rank = item.provenance.ranking_score
                    if not (0.0 <= rank <= 1.0):
                        errors.append(
                            f"ContextItem '{item.item_id}' has invalid ranking_score: {rank}"
                        )

        # 8. Critical section verification
        if ContextSource.GOAL in policy.required_providers:
            goal_section = next(
                (s for s in sections if s.source == ContextSource.GOAL), None
            )
            if goal_section is None or goal_section.is_empty:
                errors.append(
                    "ContextSource.GOAL is required by policy but no active goals were found."
                )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
