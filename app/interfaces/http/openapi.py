from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI) -> dict:
    """
    Generates a customized OpenAPI schema for the BizOS API Gateway.
    This schema serves as the contract for generating external SDKs.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="BizOS API Gateway",
        version="6.0.0",
        description="The universal API Gateway for interacting with BizOS.",
        routes=app.routes,
    )

    # Inject Security Schemes for the API Gateway
    openapi_schema.setdefault("components", {})["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key authentication for external applications."
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer authentication for users and internal services."
        }
    }

    # Require authentication globally
    openapi_schema["security"] = [{"ApiKeyAuth": []}, {"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
