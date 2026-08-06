import re
import structlog
from typing import Optional
from uuid import UUID

from app.domain.knowledge.models import (
    Customer,
    Document,
    EmailEntity,
    EntityType,
    EventEntity,
    KnowledgeEdge,
    KnowledgeNode,
    Organization,
    Project,
    RelationshipType,
)
from app.perception.models.extracted_entities import ExtractedEntities
from app.perception.models.observation import UnifiedKnowledgeObject

logger = structlog.get_logger(__name__)

# Common regex patterns for fast-path entity extraction
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PROJECT_PATTERN = r"\b(Project\s+[A-Z][a-z0-9]+|Project\s+[A-Z]+)\b"
ORG_PATTERN = r"\b([A-Z][a-zA-B0-9]+(?:\s+(?:Inc|Corp|LLC|Ltd|Technologies|Solutions|Group|Labs))?)\b"
MONEY_PATTERN = r"\$[\d,]+(?:\.\d{2})?|\b\d+\s*(?:USD|EUR|GBP|K|M)\b"


class SemanticEnricher:
    """Extracts typed entities from UKO content and maps them into Knowledge Graph nodes and edges."""

    def __init__(self, knowledge_repository: Optional[object] = None) -> None:
        self._knowledge_repo = knowledge_repository

    def extract_entities(self, uko: UnifiedKnowledgeObject) -> ExtractedEntities:
        """Extract structured entities from UKO text via fast-path regex and patterns."""
        combined_text = f"{uko.title}\n{uko.content}"

        people: set[str] = set()
        orgs: set[str] = set()
        projects: set[str] = set()
        money: set[str] = set()

        # Author / sender as person/email
        if uko.author:
            if "@" in uko.author:
                people.add(uko.author.split("@")[0].replace(".", " ").title())
            else:
                people.add(uko.author)

        # Regex extractions
        emails = re.findall(EMAIL_PATTERN, combined_text)
        for e in emails:
            name_part = e.split("@")[0].replace(".", " ").title()
            people.add(name_part)

        proj_matches = re.findall(PROJECT_PATTERN, combined_text)
        projects.update(proj_matches)

        money_matches = re.findall(MONEY_PATTERN, combined_text)
        money.update(money_matches)

        # Organization heuristic keywords
        org_matches = re.findall(ORG_PATTERN, combined_text)
        for om in org_matches:
            if any(term in om for term in ["Inc", "Corp", "LLC", "Ltd", "Technologies", "Solutions", "Group", "Labs"]):
                orgs.add(om)

        return ExtractedEntities(
            people=list(people),
            organizations=list(orgs),
            projects=list(projects),
            monetary_values=list(money),
        )

    def build_knowledge_nodes_and_edges(
        self, uko: UnifiedKnowledgeObject, entities: ExtractedEntities
    ) -> tuple[KnowledgeNode, list[KnowledgeNode], list[KnowledgeEdge]]:
        """Create primary KnowledgeNode for the UKO plus related entity nodes and connecting edges."""

        # 1. Primary node for the UKO itself
        if uko.resource_type == "email":
            primary_node = EmailEntity(
                name=uko.title or "Untitled Email",
                description=uko.content[:200] if uko.content else None,
                sender=uko.author,
                subject=uko.title,
                provenance=f"perception:{uko.source_connector}",
                metadata={"uko_id": uko.uko_id, "url": uko.source_url},
            )
        elif uko.resource_type == "event":
            primary_node = EventEntity(
                name=uko.title or "Untitled Event",
                description=uko.content[:200] if uko.content else None,
                provenance=f"perception:{uko.source_connector}",
                metadata={"uko_id": uko.uko_id},
            )
        else:
            primary_node = Document(
                name=uko.title or "Untitled Document",
                description=uko.content[:200] if uko.content else None,
                uri=uko.source_url,
                provenance=f"perception:{uko.source_connector}",
                metadata={"uko_id": uko.uko_id},
            )

        related_nodes: list[KnowledgeNode] = []
        edges: list[KnowledgeEdge] = []

        # 2. Add Project nodes
        for proj_name in entities.projects:
            p_node = Project(
                name=proj_name,
                provenance=f"perception:{uko.source_connector}",
            )
            related_nodes.append(p_node)
            edges.append(
                KnowledgeEdge(
                    source_id=primary_node.id,
                    target_id=p_node.id,
                    relationship_type=RelationshipType.REFERENCES,
                    provenance=f"perception:{uko.source_connector}",
                )
            )

        # 3. Add Organization nodes
        for org_name in entities.organizations:
            o_node = Organization(
                name=org_name,
                provenance=f"perception:{uko.source_connector}",
            )
            related_nodes.append(o_node)
            edges.append(
                KnowledgeEdge(
                    source_id=primary_node.id,
                    target_id=o_node.id,
                    relationship_type=RelationshipType.RELATED_TO,
                    provenance=f"perception:{uko.source_connector}",
                )
            )

        return primary_node, related_nodes, edges
