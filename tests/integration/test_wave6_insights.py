import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from app.infrastructure.applications.gateway.app import create_gateway_app
from app.domain.intelligence.telemetry import IntelligenceMetrics
from app.domain.intelligence.platform import IIntelligencePlatform, UnifiedExecutionResult, UnifiedExecutionMetrics
from app.shared.events.bus import EventBus
from app.domain.applications.insights.models import InsightGenerated

class MockPlatform(IIntelligencePlatform):
    async def execute_request(self, request):
        return UnifiedExecutionResult(
            success=True,
            output_data={
                "title": "Mock Insight",
                "summary": "This is a test insight",
                "findings": ["Finding 1"],
                "recommendations": ["Recommendation 1"],
                "confidence": 0.99,
                "supporting_evidence": {"source": "test"}
            },
            metrics=UnifiedExecutionMetrics(),
            errors=[],
            tenant_id=request.tenant_id
        )

    async def execute_agent_goal(self, agent_id, goal, tenant_id=None):
        return UnifiedExecutionResult(
            success=True,
            output_data={"result": "Success!"},
            metrics=UnifiedExecutionMetrics(),
            errors=[],
            tenant_id=tenant_id
        )

    async def optimize_workflow(self, workflow_id, parameters, tenant_id=None):
        pass

    async def get_execution_status(self, request_id):
        pass

class MockEventBus(EventBus):
    def __init__(self):
        self.published_events = []
    def subscribe(self, event_type, handler):
        pass
    def unsubscribe(self, event_type, handler):
        pass
    async def publish(self, event):
        self.published_events.append(event)


from app.bootstrap.container import build_container, reset_container_for_testing

@pytest.fixture
def test_container():
    reset_container_for_testing()
    container = build_container()
    
    # Override IIntelligencePlatform
    container.override(IIntelligencePlatform, MockPlatform())
    
    # Override EventBus
    mock_bus = MockEventBus()
    container.override(EventBus, mock_bus)
    
    # Force resolve
    from app.application.applications.insights.app import InsightsGenerationApplication
    container.resolve(InsightsGenerationApplication)
    
    yield container
    reset_container_for_testing()
    
@pytest.fixture
def test_client(test_container):
    app = create_gateway_app()
    return TestClient(app)
        
@pytest.fixture
def mock_event_bus(test_container):
    return test_container.resolve(EventBus)

def test_insights_metadata(test_client):
    headers = {"Authorization": "Bearer valid-test-token"}
    response = test_client.get("/apps/bizos.insights.v1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "BizOS Insights Engine"
    assert "TWIN" in data["supported_capabilities"]
    
def test_insights_job_lifecycle(test_client, mock_event_bus):
    headers = {"Authorization": "Bearer valid-test-token"}
    payload = {
        "insight_type": "STRATEGIC_FORESIGHT",
        "execution_request": {
            "required_capabilities": ["TWIN", "RETRIEVAL"],
            "parameters": {"query": "Analyze Q3 performance"}
        }
    }
    
    # Submit Job
    response = test_client.post("/apps/bizos.insights.v1/jobs", json=payload, headers=headers)
    assert response.status_code == 200, f"Submit failed: {response.text}"
    job_id = response.json()["job_id"]
    
    import time
    max_retries = 10
    final_status = None
    job_record = None
    
    # Poll for completion
    for _ in range(max_retries):
        status_resp = test_client.get(f"/apps/bizos.insights.v1/jobs/{job_id}", headers=headers)
        assert status_resp.status_code == 200
        job_record = status_resp.json()
        final_status = job_record["status"]
        if final_status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(0.1)
        
    assert final_status == "COMPLETED", f"Job failed or timed out. Last status: {final_status}. Error: {job_record.get('error')}"
    
    # Verify result
    status_resp = test_client.get(f"/apps/bizos.insights.v1/jobs/{job_id}", headers=headers)
    result_data = status_resp.json()["result"]
    assert result_data["title"] == "Mock Insight"
    assert result_data["insight_type"] == "STRATEGIC_FORESIGHT"
    assert "Finding 1" in result_data["findings"]
    assert result_data["confidence"] == 0.99
    
    # Verify event was published
    assert len(mock_event_bus.published_events) == 1
    event = mock_event_bus.published_events[0]
    assert isinstance(event, InsightGenerated)
    assert event.report_id == result_data["report_id"]
    assert event.execution_id == job_id
    assert event.insight_type.value == "STRATEGIC_FORESIGHT"
