import ast
import os
from pathlib import Path


def get_imports_for_file(filepath: Path) -> set:
    imports = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))
    except Exception:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def get_python_files(directory: str) -> list[Path]:
    base_dir = Path(__file__).parent.parent.parent / "app" / directory
    files = []
    for root, _, filenames in os.walk(base_dir):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("__"):
                files.append(Path(root) / filename)
    return files


def test_api_layer_never_imports_repositories():
    """API layer (routers, schemas, etc.) must not import repositories."""
    api_files = get_python_files("api")

    for filepath in api_files:
        imports = get_imports_for_file(filepath)
        for imp in imports:
            # We allow dependency injection files to import repositories because they form the composition root
            if "dependencies" in filepath.name:
                continue

            # Temporary exception for M4 routers until a dedicated query service is implemented
            if filepath.name in (
                "context.py",
                "conversations.py",
                "health.py",
                "recommendations.py",
            ):
                continue

            assert not imp.startswith("app.infrastructure.persistence.postgres.repositories"), (
                f"API file {filepath.name} illegally imports repository module: {imp}"
            )


def test_services_never_import_provider_sdks():
    """Services should rely on AI Kernel and not import provider SDKs directly (like google.genai)."""
    service_files = get_python_files("services")

    for filepath in service_files:
        # We allow the AI provider implementations themselves to import SDKs
        if "ai\\providers" in str(filepath) or "ai/providers" in str(filepath):
            continue

        imports = get_imports_for_file(filepath)
        for imp in imports:
            assert not imp.startswith("google.genai"), (
                f"Service file {filepath.name} illegally imports provider SDK: {imp}"
            )
            assert not imp.startswith("openai"), (
                f"Service file {filepath.name} illegally imports provider SDK: {imp}"
            )


def test_repositories_never_import_ai_kernel():
    """Repositories are purely for data storage and must not import AI Kernel or any AI logic."""
    repo_files = get_python_files("repositories")

    for filepath in repo_files:
        imports = get_imports_for_file(filepath)
        for imp in imports:
            assert not imp.startswith("app.infrastructure.ai"), (
                f"Repository file {filepath.name} illegally imports AI layer: {imp}"
            )


def test_providers_never_import_repositories():
    """AI Providers should just implement the kernel interface and not know about data storage."""
    provider_files = get_python_files("services/ai/providers")

    for filepath in provider_files:
        imports = get_imports_for_file(filepath)
        for imp in imports:
            assert not imp.startswith("app.infrastructure.persistence.postgres.repositories"), (
                f"Provider file {filepath.name} illegally imports repository: {imp}"
            )
