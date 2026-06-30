from app.intelligence.intake.intent.models import (
    ExecutiveIntent,
    IntentClassification,
    IntentEntity,
)


class IntentEngine:
    """
    Transforms raw user requests into structured executive intent.
    Does not plan, prioritize, or execute.
    """

    def parse_intent(self, raw_request: str) -> ExecutiveIntent:
        # A mock implementation of NLP/NLU mapping
        request_lower = raw_request.lower()

        if not raw_request.strip():
            return ExecutiveIntent(
                raw_request=raw_request,
                classification=IntentClassification.UNKNOWN,
                is_ambiguous=True,
                ambiguity_reason="Empty request"
            )

        if "grow" in request_lower or "expand" in request_lower or "increase" in request_lower:
            return ExecutiveIntent(
                raw_request=raw_request,
                classification=IntentClassification.STRATEGIC_OBJECTIVE,
                entities=[IntentEntity(entity_type="target", value="growth")],
                requested_outcomes=["increase_revenue"]
            )
        elif "fix" in request_lower or "adjust" in request_lower:
            return ExecutiveIntent(
                raw_request=raw_request,
                classification=IntentClassification.OPERATIONAL_ADJUSTMENT,
                entities=[],
                requested_outcomes=["operational_fix"]
            )
        else:
            return ExecutiveIntent(
                raw_request=raw_request,
                classification=IntentClassification.UNKNOWN,
                is_ambiguous=True,
                ambiguity_reason="Could not determine specific business intent."
            )
