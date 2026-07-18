from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

class ILLMProvider(ABC):
    """Base interface for all LLM providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None
    ) -> BaseModel:
        """Generate structured output adhering to a Pydantic schema."""
        pass
        
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None
    ) -> str:
        """Standard chat completion."""
        pass
