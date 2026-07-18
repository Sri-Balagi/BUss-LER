import json
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from app.domain.intelligence.llm_provider import ILLMProvider

class MockBaseProvider(ILLMProvider):
    def __init__(self, name: str):
        self._name = name
        
    @property
    def provider_name(self) -> str:
        return self._name

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None
    ) -> BaseModel:
        # Mock structured response based on schema name
        schema_name = schema.__name__
        if schema_name == "PlannerResult":
            return schema(plan_steps=["RESEARCH", "REASONING", "EXECUTOR"], objective_summary="Mocked Plan")
        elif schema_name == "ResearchResult":
            return schema(findings="Mocked findings.", sources=["Mock Source"], confidence=0.9)
        elif schema_name == "ReasoningResult":
            return schema(
                observations=["Mock observation"],
                assumptions=["Mock assumption"],
                recommendations=["Mock recommendation"],
                risks=["Mock risk"],
                confidence=0.85
            )
        # generic fallback
        return schema(**{f: None for f in schema.__fields__})

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None
    ) -> str:
        return f"Response from {self._name}"

class GeminiProvider(MockBaseProvider):
    def __init__(self):
        super().__init__("gemini")

class OpenAIProvider(MockBaseProvider):
    def __init__(self):
        super().__init__("openai")

class ClaudeProvider(MockBaseProvider):
    def __init__(self):
        super().__init__("claude")

class OllamaProvider(MockBaseProvider):
    def __init__(self):
        super().__init__("ollama")

class CognitiveSimulatorProvider(MockBaseProvider):
    def __init__(self):
        super().__init__("simulator")
