from app.intelligence.learning.repository.engine import ExecutiveKnowledgeRepository
from app.intelligence.learning.synthesis.models import (
    KnowledgeArtifact,
    KnowledgeCategory,
    KnowledgeVersion,
)


def test_knowledge_repository():
    repo = ExecutiveKnowledgeRepository()

    artifact = KnowledgeArtifact(
        artifact_id="a1",
        category=KnowledgeCategory.STRATEGIC,
        description="test",
        version=KnowledgeVersion(version_id="v1"),
    )

    repo.store_artifact(artifact)
    artifacts = repo.retrieve_artifacts()

    assert len(artifacts) == 1
    assert artifacts[0].artifact_id == "a1"

    state = repo.get_state()
    assert len(state.artifacts) == 1
