import pytest

from app.runtime.registry.model_registry import ModelMetadata, ModelRegistry
from app.runtime.registry.store import InMemoryRegistryStore
from app.runtime.registry.tool_registry import ToolMetadata, ToolRegistry


@pytest.mark.asyncio
async def test_tool_registry():
    store = InMemoryRegistryStore[ToolMetadata]()
    registry = ToolRegistry("Tools", store)

    tool = ToolMetadata(id="tool-1", name="search", description="Search the web")
    await registry.register("tool-1", tool)

    retrieved = await registry.get("tool-1")
    assert retrieved.name == "search"
    assert retrieved.risk_level == "LOW"

@pytest.mark.asyncio
async def test_model_registry():
    store = InMemoryRegistryStore[ModelMetadata]()
    registry = ModelRegistry("Models", store)

    model = ModelMetadata(id="gpt4", provider="openai", name="GPT-4", context_window=128000)
    await registry.register("gpt4", model)

    retrieved = await registry.get("gpt4")
    assert retrieved.provider == "openai"
