import json
import sys
from pathlib import Path
from fastapi.openapi.utils import get_openapi
from app.infrastructure.applications.gateway.app import create_app

def generate_openapi(output_path: str = "openapi.json"):
    app = create_app()
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"OpenAPI schema generated successfully at {output_path}")

if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    generate_openapi(output_path)
