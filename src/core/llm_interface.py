"""Abstract interface for LLM client integration."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMClient(ABC):
    """Abstract base class for LLM service clients.
    Decouples application logic from specific LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        **kwargs
    ) -> str:
        """Generates a text completion given a prompt and optional system instruction."""
        pass
