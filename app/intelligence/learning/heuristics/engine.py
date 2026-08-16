import uuid

from app.intelligence.learning.heuristics.models import (
    Heuristic,
    HeuristicCatalog,
    HeuristicConfidence,
    HeuristicStatus,
)
from app.intelligence.learning.synthesis.models import KnowledgeArtifact


class ExecutiveHeuristicsEngine:
    """
    Derives reusable heuristics from knowledge artifacts.
    """

    def __init__(self):
        self._catalog = HeuristicCatalog(catalog_id=str(uuid.uuid4()))

    def derive_heuristics(self, artifact: KnowledgeArtifact) -> list[Heuristic]:
        heuristics = []
        if artifact.category.value == "CAUTIONARY":
            h = Heuristic(
                heuristic_id=str(uuid.uuid4()),
                rule_description=f"Avoid derived from: {artifact.description}",
                confidence=HeuristicConfidence(score=0.8, data_points=1),
                status=HeuristicStatus.PROPOSED,
            )
            heuristics.append(h)
            self._catalog.heuristics.append(h)

        return heuristics

    def get_catalog(self) -> HeuristicCatalog:
        return self._catalog
