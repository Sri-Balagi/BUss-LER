from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.integration.models import ExecutiveIntelligenceResult
from app.intelligence.integration.interfaces import IExecutiveIntelligenceOrchestrator
from app.intelligence.integration.pipeline import CognitivePipeline

class ExecutiveIntelligenceOrchestrator(IExecutiveIntelligenceOrchestrator):
    """
    Orchestrates the cognitive pipeline for a given raw request.
    """
    def __init__(self):
        self.pipeline = CognitivePipeline()
        
    def process_request(self, raw_request: str) -> ExecutiveIntelligenceResult:
        # Create a unified cognitive session for the entire pipeline
        session = CognitiveSession()
        
        # Execute the pipeline with this session
        result = self.pipeline.run_pipeline(raw_request, session)
        
        return result
