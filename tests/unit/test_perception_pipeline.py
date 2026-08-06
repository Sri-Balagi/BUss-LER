import pytest
import pytest_asyncio
from uuid import uuid4

from app.connectors.google_drive.connector import GoogleDriveConnector
from app.connectors.gmail.connector import GmailConnector
from app.connectors.google_calendar.connector import GoogleCalendarConnector
from app.domain.knowledge.models import EntityType, RelationshipType
from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.pipeline.builtin_phases import ObservePhase
from app.intelligence.pipeline.phases import PhaseResultStatus
from app.perception.engine.business_event_detector import BusinessEventDetector
from app.perception.engine.content_extractor import ContentExtractor
from app.perception.engine.intelligence_gate import IntelligenceGate
from app.perception.engine.pipeline import PerceptionPipeline
from app.perception.engine.semantic_enricher import SemanticEnricher
from app.perception.models.observation import (
    BusinessEventType,
    ExternalObservation,
    IntelligenceGateDecision,
    ObservationSourceType,
    UnifiedKnowledgeObject,
)
from app.perception.sources.interface import IObservationSource, PerceptionContext
from app.perception.sources.registry import ObservationSourceRegistry
from app.perception.twin_sync.service import TwinSynchronizationService
from app.shared.events.models import BusinessStateChangeEvent


class MockObservationSource(IObservationSource):
    """Mock observation source for testing."""

    @property
    def source_id(self) -> str:
        return "mock_source"

    @property
    def source_type(self) -> ObservationSourceType:
        return ObservationSourceType.CONNECTOR

    async def observe(self, context: PerceptionContext) -> list[ExternalObservation]:
        return [
            ExternalObservation(
                observation_id="mock_obs_1",
                source_id="mock_source",
                resource_type="email",
                raw_payload={
                    "id": "mock_obs_1",
                    "subject": "Re: Project Atlas — Proposal Approved",
                    "body": "Hi team, Acme Corp is happy to approve the Project Atlas proposal for $50,000.",
                    "sender": "alice@acme.com",
                },
            )
        ]

    def normalize(self, observation: ExternalObservation) -> UnifiedKnowledgeObject:
        payload = observation.raw_payload
        return UnifiedKnowledgeObject(
            uko_id="uko_mock_1",
            source_connector="mock_source",
            resource_type="email",
            title=payload.get("subject", ""),
            content=payload.get("body", ""),
            author=payload.get("sender"),
        )


@pytest.mark.asyncio
async def test_observation_source_registry():
    registry = ObservationSourceRegistry()
    mock_src = MockObservationSource()
    registry.register(mock_src)

    resolved = registry.get_source("mock_source")
    assert resolved is not None
    assert resolved.source_id == "mock_source"
    assert len(registry.list_sources()) == 1


@pytest.mark.asyncio
async def test_content_extractor():
    html_raw = "<h1>Project Atlas</h1><p>Proposal for <b>Acme Corp</b>.</p><script>alert('x');</script>"
    clean = ContentExtractor.clean_html(html_raw)
    assert "Project Atlas" in clean
    assert "Acme Corp" in clean
    assert "alert" not in clean


@pytest.mark.asyncio
async def test_intelligence_gate():
    gate = IntelligenceGate()

    # Discard OTP / password reset
    otp_uko = UnifiedKnowledgeObject(
        uko_id="1", source_connector="gmail", resource_type="email", title="Your OTP verification code", content="Code 123456"
    )
    assert await gate.evaluate(otp_uko) == IntelligenceGateDecision.DISCARD

    # Accept proposal approval
    proposal_uko = UnifiedKnowledgeObject(
        uko_id="2", source_connector="gmail", resource_type="email", title="Project Proposal Approved", content="Approved by Acme Corp"
    )
    assert await gate.evaluate(proposal_uko) == IntelligenceGateDecision.ACCEPT


@pytest.mark.asyncio
async def test_business_event_detector():
    detector = BusinessEventDetector()
    uko = UnifiedKnowledgeObject(
        uko_id="3",
        source_connector="gmail",
        resource_type="email",
        title="Re: Project Atlas — Proposal Approved",
        content="We hereby confirm that the Project Atlas proposal has been approved and signed off.",
    )
    events = detector.detect(uko)
    event_types = [e.event_type for e in events]
    assert BusinessEventType.APPROVAL_RECEIVED in event_types
    assert BusinessEventType.PROPOSAL_CREATED in event_types


@pytest.mark.asyncio
async def test_semantic_enricher():
    enricher = SemanticEnricher()
    uko = UnifiedKnowledgeObject(
        uko_id="4",
        source_connector="google_drive",
        resource_type="file",
        title="Project Atlas Design Spec",
        content="Written by Alice at Acme Corp regarding Project Atlas budget of $50,000.",
    )
    entities = enricher.extract_entities(uko)
    assert "Project Atlas" in entities.projects
    assert any("50,000" in m for m in entities.monetary_values)

    primary_node, related_nodes, edges = enricher.build_knowledge_nodes_and_edges(uko, entities)
    assert primary_node.entity_type == EntityType.DOCUMENT
    assert any(n.entity_type == EntityType.PROJECT for n in related_nodes)
    assert any(e.relationship_type == RelationshipType.REFERENCES for e in edges)


@pytest.mark.asyncio
async def test_perception_pipeline_e2e():
    pipeline = PerceptionPipeline()
    mock_src = MockObservationSource()
    ctx = PerceptionContext(limit=1, tenant_id=uuid4())

    observations = await mock_src.observe(ctx)
    assert len(observations) == 1

    state_change = await pipeline.process_observation(mock_src, observations[0], ctx)
    assert state_change is not None
    assert state_change.source_connector == "mock_source"
    assert "APPROVAL_RECEIVED" in state_change.business_event_types
    assert state_change.gate_decision == "ACCEPT"


@pytest.mark.asyncio
async def test_twin_synchronization_service():
    twin_sync = TwinSynchronizationService()
    event = BusinessStateChangeEvent(
        change_id="change_999",
        source_uko_id="uko_999",
        source_connector="gmail",
        business_event_types=["APPROVAL_RECEIVED"],
        correlation_id="corr-123",
        tenant_id=str(uuid4()),
        affected_entity_ids=[str(uuid4())],
    )

    await twin_sync.handle_business_state_change(event)


@pytest.mark.asyncio
async def test_observe_phase():
    phase = ObservePhase()
    session = CognitiveSession()
    res = await phase.execute(session)

    assert res.status == PhaseResultStatus.SUCCESS
    assert res.artifact["observation_status"] == "OBSERVED"


@pytest.mark.asyncio
async def test_connectors_implement_iobservation_source():
    assert issubclass(GoogleDriveConnector, IObservationSource)
    assert issubclass(GmailConnector, IObservationSource)
    assert issubclass(GoogleCalendarConnector, IObservationSource)
