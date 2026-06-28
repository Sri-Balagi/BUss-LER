"""API endpoint tests covering all edge cases."""

from uuid import uuid4

from app.models.enums import EntityType
from app.models.schemas import Entity
from app.models.twin import DigitalTwin, TwinMetadata


def test_create_entity_success(client, mock_entity_service):
    user_id = uuid4()
    entity_id = uuid4()
    mock_entity = Entity(
        id=entity_id,
        user_id=user_id,
        name="Test API Entity",
        entity_type=EntityType.STARTUP,
        description=None,
        metadata={},
        is_active=True,
        created_at="2026-06-25T00:00:00Z",
        updated_at="2026-06-25T00:00:00Z",
    )
    mock_entity_service.create_entity.return_value = mock_entity

    response = client.post(
        "/api/v1/entities", json={"name": "Test API Entity", "entity_type": "startup"}
    )
    assert response.status_code == 201
    assert response.json()["id"] == str(entity_id)


def test_create_entity_missing_fields(client):
    # Missing entity_type
    response = client.post("/api/v1/entities", json={"name": "Test"})
    assert response.status_code == 422
    assert "entity_type" in response.text


def test_create_entity_malformed_json(client):
    response = client.post(
        "/api/v1/entities",
        data="NOT JSON",
        headers={"Content-Type": "application/json"},
    )
    assert (
        response.status_code == 422
    )  # FastAPI returns 422 for unparseable JSON in newer versions, or 400.


def test_create_entity_invalid_enum(client):
    response = client.post(
        "/api/v1/entities",
        json={"name": "Test API Entity", "entity_type": "INVALID_ENUM"},
    )
    assert response.status_code == 422


def test_get_entity_success(client, mock_entity_service):
    entity_id = uuid4()
    mock_entity = Entity(
        id=entity_id,
        user_id=uuid4(),
        name="Test API Entity",
        entity_type=EntityType.STARTUP,
        description=None,
        metadata={},
        is_active=True,
        created_at="2026-06-25T00:00:00Z",
        updated_at="2026-06-25T00:00:00Z",
    )
    mock_entity_service.get_by_id.return_value = mock_entity

    response = client.get(f"/api/v1/entities/{entity_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(entity_id)


def test_get_entity_invalid_uuid(client):
    response = client.get("/api/v1/entities/not-a-uuid")
    assert response.status_code == 422


def test_create_twin_success(client, mock_twin_service):
    entity_id = uuid4()
    twin_id = uuid4()
    mock_twin = DigitalTwin(
        id=twin_id,
        entity_id=entity_id,
        state={"k": "v"},
        metadata=TwinMetadata(),
        twin_version=1,
        last_snapshot_at=None,
        created_at="2026-06-25T00:00:00Z",
        updated_at="2026-06-25T00:00:00Z",
    )
    mock_twin_service.create_twin.return_value = mock_twin

    response = client.post(
        "/api/v1/twins", json={"entity_id": str(entity_id), "state": {"k": "v"}}
    )
    assert response.status_code == 201
    assert response.json()["id"] == str(twin_id)


def test_list_twins_success(client, mock_twin_service):
    twin_id = uuid4()
    mock_twin = DigitalTwin(
        id=twin_id,
        entity_id=uuid4(),
        state={},
        metadata=TwinMetadata(),
        twin_version=1,
        last_snapshot_at=None,
        created_at="2026-06-25T00:00:00Z",
        updated_at="2026-06-25T00:00:00Z",
    )
    mock_twin_service.list.return_value = ([mock_twin], 1)

    response = client.get("/api/v1/twins?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_list_twins_invalid_pagination(client):
    response = client.get("/api/v1/twins?limit=-1&offset=-5")
    assert response.status_code == 422


def test_unsupported_method(client):
    # Entities endpoint supports GET and POST, not PUT directly on /entities
    response = client.put("/api/v1/entities")
    assert response.status_code == 405


def test_unknown_route(client):
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404


def test_system_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
