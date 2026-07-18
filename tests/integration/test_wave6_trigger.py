import pytest
import uuid
from typing import Dict, Any

from app.domain.applications.trigger.models import TriggerType, ExecutionMode
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.shared.events.bus import EventBus
from app.bootstrap.container import get_container


# Mock EventBus for testing
class MockEventBus(EventBus):
    def __init__(self):
        self.published_events = []
        
    async def publish(self, event: Any) -> None:
        self.published_events.append(event)
        
    async def subscribe(self, event_type: type, handler: Any) -> None:
        pass

    async def unsubscribe(self, event_type: type, handler: Any) -> None:
        pass


from app.bootstrap.container import build_container, reset_container_for_testing
from app.infrastructure.applications.gateway.app import create_gateway_app
from fastapi.testclient import TestClient

@pytest.fixture
def test_container():
    reset_container_for_testing()
    container = build_container()
    
    # Override EventBus
    mock_bus = MockEventBus()
    container.override(EventBus, mock_bus)
    
    # Force resolve to register the apps
    from app.application.applications.trigger.app import CognitiveTriggerEngine
    from app.domain.applications.trigger.models import CognitiveTrigger, TriggerCondition, TriggerAction, TriggerPriority
    
    trigger_engine = container.resolve(CognitiveTriggerEngine)
    trigger_engine._event_bus = mock_bus  # ensure patch
    
    # Register a test trigger
    trigger = CognitiveTrigger(
        trigger_id="test-trigger-1",
        trigger_type=TriggerType.MANUAL,
        conditions=[
            TriggerCondition(condition_type="always_true")
        ],
        action=TriggerAction(
            target_app_id="bizos.worker.v1", # Send it to the worker
            execution_mode=ExecutionMode.QUEUE,
            priority=TriggerPriority.NORMAL,
            payload={
                "workflow_id": str(uuid.uuid4()),
                "task_id": "test-task"
            }
        ),
        tenant_id="test-tenant"
    )
    trigger_engine.register_trigger(trigger)
    
    # Ensure worker app has the mock event bus if needed
    from app.application.applications.worker.app import AutonomousWorkerApplication
    worker_app = container.resolve(AutonomousWorkerApplication)
    
    yield container
    reset_container_for_testing()

@pytest.fixture
def test_client(test_container):
    app = create_gateway_app()
    return TestClient(app)

@pytest.fixture
def mock_event_bus(test_container):
    return test_container.resolve(EventBus)

def test_trigger_metadata(test_client):
    headers = {"Authorization": "Bearer valid-test-token"}
    all_apps = test_client.get("/apps", headers=headers).json()
    response = test_client.get("/apps/bizos.trigger.v1", headers=headers)
    assert response.status_code == 200, f"GET apps failed: {response.text}, all_apps: {all_apps}"
    data = response.json()
    assert data["name"] == "BizOS Cognitive Trigger Engine"


def test_trigger_job_lifecycle(test_client, mock_event_bus):
    headers = {"Authorization": "Bearer valid-test-token"}
    payload = {
        "trigger_source": "manual_test",
        "trigger_type": "MANUAL",
        "variables": {
            "trigger_id": "test-trigger-1"
        }
    }

    # 1. Submit trigger execution
    response = test_client.post("/apps/bizos.trigger.v1/jobs", json=payload, headers=headers)
    assert response.status_code == 200, f"Failed: {response.text}"
    job_id = response.json()["job_id"]

    # 2. Poll Trigger Engine Job for completion
    import time
    max_retries = 15
    final_status = None
    job_record = None

    for _ in range(max_retries):
        status_resp = test_client.get(f"/apps/bizos.trigger.v1/jobs/{job_id}", headers=headers)
        assert status_resp.status_code == 200
        job_record = status_resp.json()
        final_status = job_record["status"]
        if final_status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(0.1)

    assert final_status == "COMPLETED", f"Trigger job failed. Last status: {final_status}. Error: {job_record.get('error')}"
    
    result = job_record.get("result", {})
    assert result.get("success") is True
    target_job_id = result.get("target_job_id")
    assert target_job_id is not None
    
    # 3. Verify Target Job (Worker) is enqueued/completed
    worker_resp = test_client.get(f"/apps/bizos.worker.v1/jobs/{target_job_id}", headers=headers)
    assert worker_resp.status_code == 200
    
    # 4. Verify Events were published
    published_types = [type(e).__name__ for e in mock_event_bus.published_events]
    assert "TriggerReceivedEvent" in published_types
    assert "TriggerAcceptedEvent" in published_types
    assert "TriggerStartedEvent" in published_types
    assert "TriggerCompletedEvent" in published_types
