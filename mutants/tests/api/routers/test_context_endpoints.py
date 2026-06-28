import pytest
from uuid import uuid4
from unittest.mock import MagicMock


class DummyContextEngine:
    def __init__(self):
        self.build_result = None

    async def build(self, ctx, command):
        return self.build_result


class DummyContextRepo:
    def __init__(self):
        self.list_by_twin_result = None
        self.get_by_id_result = None

    async def list_by_twin(self, twin_id, status=None, limit=20, offset=0):
        return self.list_by_twin_result

    async def get_by_id(self, context_id):
        return self.get_by_id_result


@pytest.fixture
def mock_context_engine():
    engine = DummyContextEngine()
    return engine


@pytest.fixture
def mock_context_repo():
    repo = DummyContextRepo()
    return repo


def test_build_context_success(client, mock_context_engine, mocker):
    from app.api.v1.dependencies import get_context_engine

    client.app.dependency_overrides[get_context_engine] = lambda: mock_context_engine

    twin_id = uuid4()
    mock_context = MagicMock()
    mock_context.model_dump.return_value = {
        "id": str(uuid4()),
        "context_id": str(uuid4()),
        "twin_id": str(twin_id),
        "policy_id": "planning",
        "sections": [],
        "metadata": {"policy_id": "planning"},
        "window": {
            "start_time": "2026-06-28T00:00:00Z",
            "end_time": "2026-06-28T23:59:59Z",
            "budget": 1000,
        },
        "schema_version": "1.0",
        "status": "assembled",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z",
    }

    mock_context_engine.build_result = mock_context

    response = client.post(
        f"/api/v1/twins/{twin_id}/context/build", json={"policy_id": "planning"}
    )
    assert response.status_code == 201
    assert "context_id" in response.json()
    client.app.dependency_overrides.pop(get_context_engine, None)


def test_list_context_history_success(client, mock_context_repo, mocker):
    from app.api.v1.dependencies import get_context_repository

    client.app.dependency_overrides[get_context_repository] = lambda: mock_context_repo

    twin_id = uuid4()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {
        "items": [],
        "total_count": 0,
        "limit": 20,
        "offset": 0,
    }
    mock_context_repo.list_by_twin_result = mock_result

    response = client.get(f"/api/v1/twins/{twin_id}/context/history")
    assert response.status_code == 200
    assert response.json()["total_count"] == 0
    client.app.dependency_overrides.pop(get_context_repository, None)


def test_get_context_lifecycle_success(client, mock_context_repo, mocker):
    from app.api.v1.dependencies import get_context_repository

    client.app.dependency_overrides[get_context_repository] = lambda: mock_context_repo

    twin_id = uuid4()
    context_id = uuid4()

    mock_record = MagicMock()
    mock_record.twin_id = twin_id
    mock_record.model_dump.return_value = {
        "id": str(context_id),
        "context_id": str(context_id),
        "twin_id": str(twin_id),
        "status": "assembled",
        "policy_id": "planning",
        "schema_version": "1.0",
        "is_partial": False,
        "created_at": "2026-06-28T00:00:00Z",
        "updated_at": "2026-06-28T00:00:00Z",
    }
    mock_context_repo.get_by_id_result = mock_record

    response = client.get(f"/api/v1/twins/{twin_id}/context/history/{context_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(context_id)
    client.app.dependency_overrides.pop(get_context_repository, None)


def test_get_context_lifecycle_wrong_twin(client, mock_context_repo, mocker):
    from app.api.v1.dependencies import get_context_repository

    client.app.dependency_overrides[get_context_repository] = lambda: mock_context_repo

    twin_id = uuid4()
    context_id = uuid4()

    mock_record = MagicMock()
    mock_record.twin_id = uuid4()  # different twin
    mock_context_repo.get_by_id_result = mock_record

    response = client.get(f"/api/v1/twins/{twin_id}/context/history/{context_id}")
    assert response.status_code == 404
    assert "Context not found" in response.text
    client.app.dependency_overrides.pop(get_context_repository, None)
