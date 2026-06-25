"""End-to-end integration tests using real Supabase connection."""

from uuid import uuid4
import pytest
from httpx import AsyncClient

from app.main import app

# We use the real Supabase client provided by dependencies via the TestClient


def test_complete_twin_lifecycle(unmocked_client):
    """Test the complete Entity -> Twin lifecycle natively against DB.
    
    Workflow:
    1. Create Entity
    2. Create Twin
    3. Update Twin (Increment version)
    4. Fetch Snapshots
    5. Fetch History
    6. Verify Optimistic Concurrency Failure
    7. Delete Twin
    8. Delete Entity
    """
    client = unmocked_client
    
    # Generate unique test data
    test_user_id = str(uuid4())
    
    # 1. Create Entity
    entity_payload = {"name": "Integration Test Entity", "entity_type": "startup"}
    resp = client.post("/api/v1/entities", json=entity_payload)
    assert resp.status_code == 201, resp.text
    entity_id = resp.json()["id"]
    
    try:
        # 2. Create Twin
        twin_payload = {"entity_id": entity_id, "state": {"stage": "seed"}}
        resp = client.post("/api/v1/twins", json=twin_payload)
        assert resp.status_code == 201, resp.text
        twin_id = resp.json()["id"]
        assert resp.json()["twin_version"] == 1
        
        # 3. Update Twin Atomically
        update_payload = {"expected_version": 1, "state": {"stage": "series_a", "funding": 5000000}}
        resp = client.put(f"/api/v1/twins/{twin_id}", json=update_payload)
        assert resp.status_code == 200, resp.text
        assert resp.json()["twin_version"] == 2
        assert resp.json()["state"]["stage"] == "series_a"
        
        # 4. Fetch Snapshots (Expect 2 snapshots now)
        resp = client.get(f"/api/v1/twins/{twin_id}/snapshots")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2
        
        # 5. Fetch History (Expect 2 history logs)
        resp = client.get(f"/api/v1/twins/{twin_id}/history")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2
        
        # 6. Verify Optimistic Concurrency Failure (Try expected_version 1 again)
        conflict_payload = {"expected_version": 1, "state": {"stage": "failed"}}
        resp = client.put(f"/api/v1/twins/{twin_id}", json=conflict_payload)
        assert resp.status_code == 409
        
    finally:
        # 7. Cleanup - Delete Twin (Hard delete cascades to snapshots/history)
        # Note: we use variables in case twin creation failed
        if 'twin_id' in locals():
            client.delete(f"/api/v1/twins/{twin_id}")
            
        # 8. Cleanup - Delete Entity (Soft delete)
        if 'entity_id' in locals():
            client.delete(f"/api/v1/entities/{entity_id}")
