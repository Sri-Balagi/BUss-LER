import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_context_engine(mocker):
    engine = AsyncMock()
    mocker.patch("app.api.v1.dependencies.get_context_engine", return_value=engine)
    # also override dependency in app if needed, but since it's FastAPI Depends, 
    # we usually override app.dependency_overrides. Let's see if we need that.
    return engine

@pytest.fixture
def mock_context_repo(mocker):
    repo = AsyncMock()
    mocker.patch("app.api.v1.dependencies.get_context_repository", return_value=repo)
    return repo

def test_build_context_success(client, mock_context_engine):
    # Setup dependency override
    from app.api.v1.dependencies import get_context_engine
    client.app.dependency_overrides[get_context_engine] = lambda: mock_context_engine

    twin_id = uuid4()
    mock_context = MagicMock()
    mock_context.model_dump.return_value = {
        "context_id": str(uuid4()),
        "twin_id": str(twin_id),
        "policy_id": "planning",
        "sections": []
    }
    mock_context_engine.build.return_value = mock_context
    
    response = client.post(
        f"/api/v1/twins/{twin_id}/context/build",
        json={"policy_id": "planning"}
    )
    assert response.status_code == 201
    assert response.json()["policy_id"] == "planning"
    client.app.dependency_overrides.pop(get_context_engine, None)

def test_list_context_history_success(client, mock_context_repo):
    from app.api.v1.dependencies import get_context_repository
    client.app.dependency_overrides[get_context_repository] = lambda: mock_context_repo
    
    twin_id = uuid4()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "size": 20
    }
    mock_context_repo.list_by_twin.return_value = mock_result
    
    response = client.get(f"/api/v1/twins/{twin_id}/context/history")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    client.app.dependency_overrides.pop(get_context_repository, None)

def test_get_context_lifecycle_success(client, mock_context_repo):
    from app.api.v1.dependencies import get_context_repository
    client.app.dependency_overrides[get_context_repository] = lambda: mock_context_repo
    
    twin_id = uuid4()
    context_id = uuid4()
    
    mock_record = MagicMock()
    mock_record.twin_id = twin_id
    mock_record.model_dump.return_value = {
        "context_id": str(context_id),
        "twin_id": str(twin_id),
        "status": "built"
    }
    mock_context_repo.get_by_id.return_value = mock_record
    
    response = client.get(f"/api/v1/twins/{twin_id}/context/history/{context_id}")
    assert response.status_code == 200
    assert response.json()["context_id"] == str(context_id)
    client.app.dependency_overrides.pop(get_context_repository, None)

def test_get_context_lifecycle_wrong_twin(client, mock_context_repo):
    from app.api.v1.dependencies import get_context_repository
    client.app.dependency_overrides[get_context_repository] = lambda: mock_context_repo
    
    twin_id = uuid4()
    context_id = uuid4()
    
    mock_record = MagicMock()
    mock_record.twin_id = uuid4() # different twin
    mock_context_repo.get_by_id.return_value = mock_record
    
    response = client.get(f"/api/v1/twins/{twin_id}/context/history/{context_id}")
    assert response.status_code == 404
    assert "Context not found" in response.text
    client.app.dependency_overrides.pop(get_context_repository, None)
