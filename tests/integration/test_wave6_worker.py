import pytest
import uuid
import asyncio
from unittest.mock import AsyncMock, patch

from app.bootstrap.container import build_container, reset_container_for_testing
from app.application.applications.worker.app import AutonomousWorkerApplication
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.intelligence.platform import IIntelligencePlatform, UnifiedExecutionResult
from app.domain.applications.worker.models import JobStatus
from app.infrastructure.applications.gateway.app import create_gateway_app
from fastapi.testclient import TestClient
from app.domain.intelligence.telemetry import IntelligenceMetrics
from app.domain.intelligence.platform import UnifiedExecutionMetrics

class MockPlatform(IIntelligencePlatform):
    async def execute_request(self, request):
        pass
    async def execute_agent_goal(self, agent_id, goal, tenant_id=None):
        return UnifiedExecutionResult(
            success=True,
            output_data={"result": "Success!"},
            metrics=UnifiedExecutionMetrics(),
            errors=[],
            tenant_id=tenant_id
        )
    async def optimize_workflow(self, workflow_id, tenant_id=None):
        pass
    async def get_execution_status(self, execution_id):
        pass

@pytest.fixture
def test_container():
    reset_container_for_testing()
    container = build_container()
    
    # Replace real platform with mock to speed up tests and avoid LLM calls
    mock_platform = MockPlatform()
    container.override(IIntelligencePlatform, mock_platform)
    
    # Force resolve
    container.resolve(AutonomousWorkerApplication)
    
    yield container
    reset_container_for_testing()

@pytest.fixture
def test_client(test_container):
    app = create_gateway_app()
    return TestClient(app)

@pytest.mark.asyncio
async def test_worker_metadata(test_container):
    registry = test_container.resolve(IApplicationRegistry)
    app = registry.resolve("bizos.worker.v1")
    
    assert app is not None
    assert app.metadata().id == "bizos.worker.v1"
    assert app.metadata().name == "BizOS Autonomous Worker"

def test_worker_job_lifecycle(test_client):
    headers = {"Authorization": "Bearer valid-test-token"}
    payload = {
        "workflow_id": "wf-123",
        "task_id": "task-456",
        "variables": {"goal": "Test background goal"}
    }
    
    # 1. Submit Job
    response = test_client.post("/apps/bizos.worker.v1/jobs", json=payload, headers=headers)
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    
    import time
    max_retries = 10
    final_status = None
    
    # 2. Poll for completion
    for _ in range(max_retries):
        status_resp = test_client.get(f"/apps/bizos.worker.v1/jobs/{job_id}", headers=headers)
        assert status_resp.status_code == 200
        job_record = status_resp.json()
        final_status = job_record["status"]
        if final_status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(0.1)
        
    assert final_status == "COMPLETED", f"Job failed or timed out. Last status: {final_status}. Error: {job_record.get('error')}"
    
    # Verify result
    status_resp = test_client.get(f"/apps/bizos.worker.v1/jobs/{job_id}", headers=headers)
    job_record = status_resp.json()
    assert job_record["result"] == {"result": "Success!"}
