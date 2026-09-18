"""Deterministic Mock LLM Client for offline execution and testing."""

import json
from typing import Optional, Dict, Any
from src.core.llm_interface import LLMClient


class MockLLMClient(LLMClient):
    """Mock LLM client that provides deterministic offline responses without external APIs."""

    def __init__(self, canned_response: Optional[str] = None):
        self.canned_response = canned_response
        self.call_count = 0
        self.last_prompt = ""
        self.last_system = ""

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        **kwargs
    ) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system = system_instruction or ""

        if self.canned_response is not None:
            return self.canned_response

        # Default simulated responses based on system intent
        if system_instruction and "clarification" in system_instruction.lower():
            return (
                "I can assess your land, but I need at least one additional environmental factor "
                "to evaluate the ecological interactions. Could you provide your soil organic carbon level, "
                "soil moisture condition, or current habitat/biodiversity status?"
            )

        if system_instruction and "synthesis" in system_instruction.lower():
            return (
                "Based on the diagnosed multi-metric ecological conditions and peer-reviewed scientific literature, "
                "the primary recommendation is to implement agroecological diversification."
            )

        return "Mock response generated deterministically."
