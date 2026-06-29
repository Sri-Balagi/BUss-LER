import uuid
from typing import List
from app.intelligence.learning.reflection.models import ReflectionReport
from app.intelligence.learning.evaluation.models import OutcomeEvaluation
from app.intelligence.learning.synthesis.models import KnowledgeArtifact, KnowledgeCategory, KnowledgeVersion

class KnowledgeSynthesisEngine:
    """
    Synthesizes learning into reusable intelligence artifacts.
    """
    def synthesize(self, reflection: ReflectionReport, evaluation: OutcomeEvaluation) -> List[KnowledgeArtifact]:
        artifacts = []
        
        # Mock logic
        if evaluation.overall_score.value == "ACHIEVED":
            artifacts.append(KnowledgeArtifact(
                artifact_id=str(uuid.uuid4()),
                category=KnowledgeCategory.STRATEGIC,
                description="Successful execution pattern observed.",
                source_evaluation_ids=[evaluation.evaluation_id],
                version=KnowledgeVersion(version_id="v1")
            ))
        elif evaluation.overall_score.value == "FAILED":
            artifacts.append(KnowledgeArtifact(
                artifact_id=str(uuid.uuid4()),
                category=KnowledgeCategory.CAUTIONARY,
                description="Failure pattern observed. Avoid similar constraints.",
                source_evaluation_ids=[evaluation.evaluation_id],
                version=KnowledgeVersion(version_id="v1")
            ))
            
        return artifacts
