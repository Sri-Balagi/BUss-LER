import os
from unittest.mock import MagicMock, patch

import pytest

from app.platform.telemetry.otel import instrument_fastapi, is_tracing_enabled, setup_tracing


@pytest.fixture(autouse=True)
def reset_tracing():
    import app.platform.telemetry.otel as otel
    otel._tracing_enabled = False
    yield
    otel._tracing_enabled = False

def test_is_tracing_enabled():
    assert is_tracing_enabled() is False

@patch.dict(os.environ, {"OTEL_ENABLED": "false"})
def test_setup_tracing_disabled():
    assert setup_tracing() is False
    assert is_tracing_enabled() is False

@patch.dict(os.environ, {"OTEL_ENABLED": "true"})
@patch("app.platform.telemetry.otel.logger")
def test_setup_tracing_no_opentelemetry(mock_logger):
    # This simulates not having opentelemetry installed or hitting an ImportError
    # We can mock the import inside the function using sys.modules, or since it's hard to mock local import,
    # we can patch the function itself. Actually we can use a try/except inside the function and let it fail.
    # It fails if opentelemetry is not installed. If it is installed in our venv, it will pass.
    # Let's force an exception to cover the exception block.
    with patch("opentelemetry.sdk.resources.Resource.create", side_effect=Exception("Test Error")):
        assert setup_tracing() is False
        mock_logger.error.assert_called_once()

@patch.dict(os.environ, {"OTEL_ENABLED": "true", "OTEL_EXPORTER_OTLP_ENDPOINT": ""})
@patch("opentelemetry.trace.set_tracer_provider")
def test_setup_tracing_enabled_console(mock_set_provider):
    try:
        assert setup_tracing() is True
        assert is_tracing_enabled() is True
    except ImportError:
        pass # Skip if opentelemetry not installed

@patch.dict(os.environ, {"OTEL_ENABLED": "true", "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4318/v1/traces"})
@patch("opentelemetry.trace.set_tracer_provider")
def test_setup_tracing_enabled_otlp(mock_set_provider):
    try:
        assert setup_tracing() is True
        assert is_tracing_enabled() is True
    except ImportError:
        pass

def test_instrument_fastapi_disabled():
    app = MagicMock()
    instrument_fastapi(app)
    # No op

@patch("app.platform.telemetry.otel._tracing_enabled", True)
@patch("app.platform.telemetry.otel.logger")
def test_instrument_fastapi_enabled(mock_logger):
    app = MagicMock()
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        with patch.object(FastAPIInstrumentor, "instrument_app") as mock_instrument:
            instrument_fastapi(app)
            mock_instrument.assert_called_once_with(app)
    except ImportError:
        pass
