"""Gemini API client wrapper.

Provides wrappers around the google-genai SDK for inference and embedding.
This module handles only API interaction, not business logic.
"""

from typing import Any

import structlog
from google import genai
from google.genai import types

from app.config import Settings

logger = structlog.get_logger()


class GeminiService:
    """Wrapper for Gemini API operations."""

    def __init__(self, settings: Settings):
        """Initialize the Gemini client."""
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_content(
        self,
        prompt: str,
        use_pro: bool = False,
        system_instruction: str | None = None,
        response_schema: type | None = None,
        temperature: float = 0.7,
    ) -> str | Any:
        """Generate content using Gemini Flash or Pro.

        Args:
            prompt: The user prompt.
            use_pro: If True, uses Gemini Pro; otherwise uses Flash.
            system_instruction: Optional system prompt.
            response_schema: Optional Pydantic model class for structured output.
            temperature: Generation temperature (0.0 to 2.0).

        Returns:
            The text response, or the parsed Pydantic object if response_schema is provided.
        """
        model = (
            self.settings.gemini_pro_model
            if use_pro
            else self.settings.gemini_flash_model
        )

        config_kwargs = {"temperature": temperature}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema

        config = types.GenerateContentConfig(**config_kwargs)

        try:
            # Using async generation
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            
            if response_schema:
                # When schema is provided, return the parsed object
                # Google SDK usually handles this parsing internally if schema is passed
                if hasattr(response, "parsed"):
                     return response.parsed
                # Fallback if manual parsing needed (SDK behavior dependent)
                import json
                return response_schema.model_validate(json.loads(response.text))
                
            return response.text
        except Exception as e:
            logger.error("Gemini generation failed", model=model, error=str(e))
            raise

    async def embed_content(self, text: str | list[str]) -> list[list[float]]:
        """Generate embeddings for one or more texts.

        Args:
            text: A single string or a list of strings to embed.

        Returns:
            A list of embedding vectors (list of floats).
        """
        try:
            response = await self.client.aio.models.embed_content(
                model=self.settings.gemini_embedding_model,
                contents=text,
            )
            
            # Extract embeddings based on SDK response structure
            if isinstance(response.embeddings, list):
                return [emb.values for emb in response.embeddings]
            else:
                # Single embedding fallback
                return [response.embeddings.values]
                
        except Exception as e:
            logger.error("Gemini embedding failed", error=str(e))
            raise
