"""Tests for FastAPI middleware."""

from unittest.mock import patch
import pytest

def test_request_logging_middleware(client):
    # Test that the middleware logs the request duration and status
    with patch("app.main.logger.info") as mock_logger:
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        
        # Check that the logger was called
        mock_logger.assert_called_with(
            "Request processed",
            method="GET",
            path="/api/v1/health",
            status=200,
            duration=mock_logger.call_args[1]["duration"],
            request_id=None
        )
        assert isinstance(mock_logger.call_args[1]["duration"], float)

def test_middleware_does_not_modify_response(client):
    # Ensure the original response body is preserved
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_middleware_exception_propagation(client, mock_entity_service):
    # Test that unhandled exceptions are not swallowed by the middleware
    mock_entity_service.get_by_id.side_effect = Exception("Unhandled explosion")
    with pytest.raises(Exception, match="Unhandled explosion"):
        client.get("/api/v1/entities/00000000-0000-0000-0000-000000000000")
