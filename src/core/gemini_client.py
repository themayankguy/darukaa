"""Concrete Gemini client implementation with graceful offline fallback."""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

from src.core.llm_interface import LLMClient
from src.core.mock_client import MockLLMClient


class GeminiClient(LLMClient):
    """Client for Google Gemini API.
    Falls back gracefully to MockLLMClient when GEMINI_API_KEY is not set.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        fallback: Optional[LLMClient] = None
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.fallback = fallback or MockLLMClient()

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        **kwargs
    ) -> str:
        if not self.api_key:
            # Offline or unconfigured: use deterministic fallback
            return self.fallback.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                **kwargs
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_instruction:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instructions: {system_instruction}\n\nUser Request: {prompt}"}]
            })
        else:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
        except Exception:
            # On network or API error, gracefully fall back
            return self.fallback.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                **kwargs
            )

        return self.fallback.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            **kwargs
        )
