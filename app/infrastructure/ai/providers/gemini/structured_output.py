from typing import Any, TypeVar

from google.genai import types
from pydantic import BaseModel

from app.infrastructure.ai.models import StructuredOutputError

T = TypeVar("T", bound=BaseModel)


class GeminiStructuredOutputAdapter:
    """Adapter for mapping Gemini structured outputs to Pydantic models."""

    @staticmethod
    def build_config(response_schema: type[T], **kwargs: Any) -> types.GenerateContentConfig:
        config_kwargs = kwargs.copy()
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = response_schema

        return types.GenerateContentConfig(**config_kwargs)

    @staticmethod
    def parse_response(response: types.GenerateContentResponse, response_schema: type[T]) -> T:
        if not hasattr(response, "parsed") or response.parsed is None:
            raise StructuredOutputError(
                provider="gemini",
                operation="generate_structured",
                detail="Failed to parse structured output: response.parsed is None",
            )

        if not isinstance(response.parsed, response_schema):
            raise StructuredOutputError(
                provider="gemini",
                operation="generate_structured",
                detail=f"Parsed response is not an instance of {response_schema.__name__}",
            )

        return response.parsed
