import uuid
import structlog
from typing import Optional

from app.perception.engine.business_event_detector import BusinessEventDetector
from app.perception.engine.content_extractor import ContentExtractor
from app.perception.engine.intelligence_gate import IntelligenceGate
from app.perception.engine.relationship_detector import RelationshipDetector
from app.perception.engine.semantic_enricher import SemanticEnricher
from app.perception.models.observation import ExternalObservation, IntelligenceGateDecision, UnifiedKnowledgeObject
from app.perception.sources.interface import IObservationSource, PerceptionContext
from app.shared.events.models import BusinessStateChangeEvent

logger = structlog.get_logger(__name__)


class PerceptionPipeline:
    """The central assembly line of the BizOS Universal Perception Layer (Wave -1)."""

    def __init__(
        self,
        ai_kernel: Optional[object] = None,
        knowledge_repository: Optional[object] = None,
        qdrant_service: Optional[object] = None,
        event_bus: Optional[object] = None,
    ) -> None:
        self.ai_kernel = ai_kernel
        self.knowledge_repository = knowledge_repository
        self.qdrant_service = qdrant_service
        self.event_bus = event_bus

        self.content_extractor = ContentExtractor()
        self.intelligence_gate = IntelligenceGate(ai_kernel=ai_kernel)
        self.event_detector = BusinessEventDetector()
        self.enricher = SemanticEnricher(knowledge_repository=knowledge_repository)
        self.relationship_detector = RelationshipDetector()

    async def process_observation(
        self, source: IObservationSource, raw_observation: ExternalObservation, context: PerceptionContext
    ) -> BusinessStateChangeEvent:
        """Run a single ExternalObservation through the full 7-stage perception pipeline."""
        logger.info(
            "PerceptionPipeline processing observation",
            observation_id=raw_observation.observation_id,
            source_id=source.source_id,
            resource_type=raw_observation.resource_type,
        )

        # Stage 1: Normalize signal → UKO
        uko = source.normalize(raw_observation)

        # Stage 2: Content Extraction
        if not uko.content:
            uko.content = self.content_extractor.extract_text(raw_observation.raw_payload, raw_observation.resource_type)

        # Stage 3: Intelligence Gate Evaluation
        gate_decision = await self.intelligence_gate.evaluate(uko)
        uko.gate_decision = gate_decision

        if gate_decision == IntelligenceGateDecision.DISCARD:
            logger.info("Observation discarded by IntelligenceGate", uko_id=uko.uko_id)
            return BusinessStateChangeEvent(
                change_id=str(uuid.uuid4()),
                source_uko_id=uko.uko_id,
                source_connector=source.source_id,
                gate_decision=gate_decision.value,
                confidence=0.0,
                tenant_id=context.tenant_id,
            )

        # Stage 4: Business Event Detection
        detected_events = self.event_detector.detect(uko)
        uko.detected_events = detected_events

        # Stage 5: Semantic Enrichment & Knowledge Graph Nodes/Edges
        entities = self.enricher.extract_entities(uko)
        uko.extracted_entities = entities
        primary_node, related_nodes, edges = self.enricher.build_knowledge_nodes_and_edges(uko, entities)
        uko.knowledge_node_id = primary_node.id

        # Persist to Knowledge Repository if available
        if self.knowledge_repository:
            try:
                self.knowledge_repository.add_node(primary_node)
                for node in related_nodes:
                    self.knowledge_repository.add_node(node)
                for edge in edges:
                    self.knowledge_repository.add_edge(edge)
            except Exception as e:
                logger.warning("Knowledge repository write error", error=str(e))

        # Stage 6: Vector Embedding & Qdrant Upsert
        vector_stored = False
        if self.ai_kernel and uko.content:
            try:
                from app.infrastructure.ai.models import EmbeddingRequest
                emb_res = await self.ai_kernel.embed(EmbeddingRequest(text=f"{uko.title}\n{uko.content}"[:1000]))
                if emb_res and hasattr(emb_res, "vector"):
                    uko.embedding = emb_res.vector

                    if self.qdrant_service:
                        await self.qdrant_service.upsert(
                            collection_name="bizos_knowledge",
                            points=[
                                {
                                    "id": str(primary_node.id),
                                    "vector": uko.embedding,
                                    "payload": {
                                        "uko_id": uko.uko_id,
                                        "source": uko.source_connector,
                                        "title": uko.title,
                                    },
                                }
                            ],
                        )
                        vector_stored = True
            except Exception as e:
                logger.warning("Embedding/Qdrant processing warning", error=str(e))

        # Stage 7: Assemble & Publish BusinessStateChangeEvent
        event_types = [e.event_type.value for e in detected_events]
        affected_ids = [str(n.id) for n in related_nodes] + [str(primary_node.id)]
        suggested_actions = [f"Process {et} from {source.source_id}" for et in event_types]

        tenant_id_str = str(context.tenant_id) if context.tenant_id else None
        correlation_id_str = getattr(context, "correlation_id", None) or str(uuid.uuid4())

        state_change_event = BusinessStateChangeEvent(
            change_id=str(uuid.uuid4()),
            source_uko_id=uko.uko_id,
            source_connector=source.source_id,
            correlation_id=correlation_id_str,
            affected_entity_ids=affected_ids,
            business_event_types=event_types,
            confidence=max((e.confidence for e in detected_events), default=1.0),
            knowledge_node_id=str(primary_node.id),
            vector_stored=vector_stored,
            gate_decision=gate_decision.value,
            suggested_actions=suggested_actions,
            tenant_id=tenant_id_str,
        )

        if self.event_bus:
            try:
                self.event_bus.publish(state_change_event)
                logger.info("Published BusinessStateChangeEvent to EventBus", change_id=state_change_event.change_id)
            except Exception as e:
                logger.error("Failed to publish BusinessStateChangeEvent", error=str(e))

        return state_change_event
