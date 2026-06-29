from app.intelligence.learning.heuristics.engine import ExecutiveHeuristicsEngine
from app.intelligence.learning.heuristics.models import HeuristicStatus
from app.intelligence.learning.synthesis.models import KnowledgeArtifact, KnowledgeCategory, KnowledgeVersion

def test_derive_heuristics():
    engine = ExecutiveHeuristicsEngine()
    
    artifact = KnowledgeArtifact(
        artifact_id="a1",
        category=KnowledgeCategory.CAUTIONARY,
        description="test artifact",
        version=KnowledgeVersion(version_id="v1")
    )
    
    heuristics = engine.derive_heuristics(artifact)
    
    assert len(heuristics) == 1
    assert heuristics[0].status == HeuristicStatus.PROPOSED
    assert heuristics[0].confidence.score == 0.8
    assert "test artifact" in heuristics[0].rule_description
    
    catalog = engine.get_catalog()
    assert len(catalog.heuristics) == 1
