"""Tests for centralized exception handlers."""

from uuid import uuid4
import pytest

from app.models.exceptions import (
    EntityNotFoundError,
    TwinNotFoundError,
    VersionConflictError,
    DuplicateTwinError,
    DomainValidationError,
    RepositoryError,
    ServiceError
)

def test_entity_not_found_handler(client, mock_entity_service):
    entity_id = uuid4()
    mock_entity_service.get_by_id.side_effect = EntityNotFoundError(str(entity_id))
    
    response = client.get(f"/api/v1/entities/{entity_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_twin_not_found_handler(client, mock_twin_service):
    twin_id = uuid4()
    mock_twin_service.get_by_id.side_effect = TwinNotFoundError(str(twin_id))
    
    response = client.get(f"/api/v1/twins/{twin_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_version_conflict_handler(client, mock_twin_service):
    twin_id = uuid4()
    mock_twin_service.update_twin.side_effect = VersionConflictError(1, 2)
    
    response = client.put(f"/api/v1/twins/{twin_id}", json={"expected_version": 1, "state": {}})
    assert response.status_code == 409
    assert "conflict" in response.json()["detail"].lower()

def test_duplicate_twin_handler(client, mock_twin_service):
    mock_twin_service.create_twin.side_effect = DuplicateTwinError(str(uuid4()))
    
    response = client.post("/api/v1/twins", json={"entity_id": str(uuid4()), "state": {}})
    assert response.status_code == 409
    assert "already has a digital twin" in response.json()["detail"].lower()

def test_domain_validation_handler(client, mock_twin_service):
    mock_twin_service.create_twin.side_effect = DomainValidationError("state", "Invalid state keys")
    
    response = client.post("/api/v1/twins", json={"entity_id": str(uuid4()), "state": {}})
    assert response.status_code == 422
    assert "state" in response.json()["detail"].lower()

def test_repository_error_handler(client, mock_twin_service):
    mock_twin_service.create_twin.side_effect = RepositoryError("twin.create", "DB down")
    
    response = client.post("/api/v1/twins", json={"entity_id": str(uuid4()), "state": {}})
    assert response.status_code == 500
    assert "internal database error" in response.json()["detail"].lower()

def test_service_error_handler(client, mock_twin_service):
    mock_twin_service.create_twin.side_effect = ServiceError("twin.create", "Logic failed")
    
    response = client.post("/api/v1/twins", json={"entity_id": str(uuid4()), "state": {}})
    assert response.status_code == 500
    assert "orchestration error" in response.json()["detail"].lower()
