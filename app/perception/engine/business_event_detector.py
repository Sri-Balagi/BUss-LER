import re
import structlog
from app.perception.models.observation import BusinessEvent, BusinessEventType, UnifiedKnowledgeObject

logger = structlog.get_logger(__name__)

# Pattern maps for business event detection
EVENT_PATTERNS: list[tuple[BusinessEventType, list[str], float]] = [
    (
        BusinessEventType.APPROVAL_RECEIVED,
        [r"\b(approved|approval|sign-off|signed off|looks good to me|lgtm|proceed)\b"],
        0.9,
    ),
    (
        BusinessEventType.PROPOSAL_CREATED,
        [r"\b(proposal|quote|rfp|statement of work|sow)\b"],
        0.85,
    ),
    (
        BusinessEventType.CONTRACT_SIGNED,
        [r"\b(contract signed|agreement executed|fully executed|signature completed)\b"],
        0.95,
    ),
    (
        BusinessEventType.MILESTONE_SCHEDULED,
        [r"\b(milestone|kickoff|launch date|release date|go-live|review meeting)\b"],
        0.8,
    ),
    (
        BusinessEventType.DEADLINE_SET,
        [r"\b(due by|deadline|deliver by|target date|by end of week|eod|eow)\b"],
        0.8,
    ),
    (
        BusinessEventType.TASK_ASSIGNED,
        [r"\b(assigned to|action item|todo|please review|take a look)\b"],
        0.75,
    ),
    (
        BusinessEventType.DELIVERABLE_UPLOADED,
        [r"\b(deliverable|v1\.0|final draft|completed design|report attached)\b"],
        0.8,
    ),
    (
        BusinessEventType.CLIENT_COMMUNICATION,
        [r"\b(re:|fw:|client|customer|update|meeting notes|discussion)\b"],
        0.7,
    ),
    (
        BusinessEventType.TEAM_MEETING_SCHEDULED,
        [r"\b(sync|standup|retro|retrospective|planning|1:1|one-on-one)\b"],
        0.75,
    ),
    (
        BusinessEventType.ARCHITECTURE_DOCUMENTED,
        [r"\b(architecture|tech spec|design doc|system design|adr|rfc)\b"],
        0.85,
    ),
    # ── CRM Lifecycle Events ──────────────────────────────────────────────────
    (
        BusinessEventType.NEW_LEAD,
        [r"\b(new lead|lead created|prospect added|new contact)\b"],
        0.9,
    ),
    (
        BusinessEventType.LEAD_QUALIFIED,
        [r"\b(lead qualified|qualified lead|sql|marketing qualified|mql)\b"],
        0.9,
    ),
    (
        BusinessEventType.OPPORTUNITY_CREATED,
        [r"\b(opportunity created|new deal|new opportunity|pipeline added)\b"],
        0.9,
    ),
    (
        BusinessEventType.DEAL_STAGE_CHANGED,
        [r"\b(stage changed|moved to|progressed to|deal updated|pipeline stage)\b"],
        0.85,
    ),
    (
        BusinessEventType.DEAL_WON,
        [r"\b(deal won|closed won|won the deal|opportunity won|signed|purchase order)\b"],
        0.95,
    ),
    (
        BusinessEventType.DEAL_LOST,
        [r"\b(deal lost|closed lost|lost to|opportunity lost|no decision|churned)\b"],
        0.95,
    ),
    (
        BusinessEventType.FOLLOW_UP_SCHEDULED,
        [r"\b(follow.?up|follow up scheduled|check back|touchpoint|next steps)\b"],
        0.8,
    ),
    (
        BusinessEventType.MEETING_LOGGED,
        [r"\b(meeting logged|call logged|activity logged|discovery call|demo completed)\b"],
        0.85,
    ),
    (
        BusinessEventType.QUOTE_SENT,
        [r"\b(quote sent|proposal sent|pricing sent|quotation submitted)\b"],
        0.9,
    ),
    (
        BusinessEventType.INVOICE_PAID,
        [r"\b(invoice paid|payment received|payment confirmed|settled|wire received)\b"],
        0.95,
    ),
    (
        BusinessEventType.SUPPORT_TICKET_CREATED,
        [r"\b(ticket created|support request|issue raised|case opened|help desk)\b"],
        0.9,
    ),
    # ── Universal Entity Transitions (generic fallback) ───────────────────────
    (
        BusinessEventType.STATE_TRANSITION,
        [r"\b(status changed|updated to|transitioned|moved from|now in)\b"],
        0.7,
    ),
    (
        BusinessEventType.ENTITY_CREATED,
        [r"\b(created|added|registered|submitted|opened|initiated)\b"],
        0.6,
    ),
]


class BusinessEventDetector:
    """Translates raw normalized UKO signals into semantic BusinessEvents."""

    def detect(self, uko: UnifiedKnowledgeObject) -> list[BusinessEvent]:
        """Detect business events within a UKO via pattern matching."""
        combined_text = f"{uko.title}\n{uko.content}".lower()
        events: list[BusinessEvent] = []

        for event_type, patterns, base_confidence in EVENT_PATTERNS:
            matched_evidence: list[str] = []
            for pattern in patterns:
                matches = re.findall(pattern, combined_text)
                if matches:
                    matched_evidence.extend(matches)

            if matched_evidence:
                # Boost confidence slightly if matched in title
                in_title = any(re.search(p, uko.title.lower()) for p in patterns)
                confidence = min(1.0, base_confidence + (0.1 if in_title else 0.0))

                events.append(
                    BusinessEvent(
                        event_type=event_type,
                        confidence=round(confidence, 2),
                        evidence=f"Matched keywords: {', '.join(set(matched_evidence))}",
                    )
                )

        logger.debug("Detected business events", uko_id=uko.uko_id, event_count=len(events))
        return events
