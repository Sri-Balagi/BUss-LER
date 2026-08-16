from fastapi import FastAPI

from app.interfaces.http.openapi import custom_openapi


def test_custom_openapi_no_schema():
    app = FastAPI()
    schema = custom_openapi(app)

    assert "securitySchemes" in schema["components"]
    assert "ApiKeyAuth" in schema["components"]["securitySchemes"]
    assert "BearerAuth" in schema["components"]["securitySchemes"]
    assert "security" in schema
    assert {"ApiKeyAuth": []} in schema["security"]
    assert {"BearerAuth": []} in schema["security"]

    # Should cache schema
    assert app.openapi_schema == schema

def test_custom_openapi_cached_schema():
    app = FastAPI()
    app.openapi_schema = {"cached": True}

    schema = custom_openapi(app)
    assert schema == {"cached": True}
