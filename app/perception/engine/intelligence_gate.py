import re
import structlog
from typing import Optional

from app.perception.models.observation import IntelligenceGateDecision, UnifiedKnowledgeObject

logger = structlog.get_logger(__name__)

# Heuristic discard patterns (spam, OTPs, marketing, system noise)
DISCARD_PATTERNS = [
    r"\b(one-time password|otp|verification code|security code)\b",
    r"\b(unsubscribe|click here to unsubscribe|manage preferences)\b",
    r"\b(no-reply|noreply|donotreply)@\b",
    r"\b(password reset|login alert|security alert|new sign-in)\b",
    r"\b(out of office|automatic reply|auto-reply)\b",
]

# Heuristic high-value accept patterns
ACCEPT_PATTERNS = [
    r"\b(proposal|contract|agreement|invoice|quote|statement of work|sow)\b",
    r"\b(approved|signed|accepted|confirmed|milestone|deadline)\b",
    r"\b(project|architecture|design doc|spec|specification|roadmap)\b",
]


class IntelligenceGate:
    """Intelligent content filter to discard noise and prioritize high-value business signals."""

    def __init__(self, ai_kernel: Optional[object] = None) -> None:
        self._ai_kernel = ai_kernel

    async def evaluate(self, uko: UnifiedKnowledgeObject) -> IntelligenceGateDecision:
        """Score content and decide: ACCEPT, SUMMARIZE, or DISCARD."""
        text = f"{uko.title}\n{uko.content}".lower()

        # Step 1: Check fast-path discard heuristics
        for pattern in DISCARD_PATTERNS:
            if re.search(pattern, text):
                logger.debug("IntelligenceGate DISCARD (heuristic match)", pattern=pattern, title=uko.title)
                return IntelligenceGateDecision.DISCARD

        # Step 2: Check fast-path accept heuristics
        for pattern in ACCEPT_PATTERNS:
            if re.search(pattern, text):
                logger.debug("IntelligenceGate ACCEPT (heuristic match)", pattern=pattern, title=uko.title)
                return IntelligenceGateDecision.ACCEPT

        # Step 3: Length / content quality threshold
        if len(text.strip()) < 20:
            logger.debug("IntelligenceGate DISCARD (too short)", title=uko.title)
            return IntelligenceGateDecision.DISCARD

        # Step 4: Fallback / default accept for normal business content
        return IntelligenceGateDecision.ACCEPT
