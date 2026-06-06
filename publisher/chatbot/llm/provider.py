"""LLM provider abstraction for OpenAI-compatible chat completions."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
import os
from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional in some local environments
    OpenAI = None  # type: ignore[assignment]

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in bare environments
    def load_dotenv() -> bool:
        return False


class LLMProvider(ABC):
    """Abstract chat-completions provider."""

    @abstractmethod
    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Return a JSON object parsed from the model response."""


class OpenAICompatibleProvider(LLMProvider):
    """Shared implementation for Ollama and Groq's OpenAI-compatible APIs."""

    def __init__(
        self,
        *,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        if OpenAI is None:
            raise ImportError("openai is required to use the configured LLM provider")
        self.model = model
        client_kwargs: dict[str, Any] = {}
        if base_url:
            client_kwargs["base_url"] = base_url
        if api_key:
            client_kwargs["api_key"] = api_key
        self.client = OpenAI(**client_kwargs)

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        self.last_raw_response: str = content
        return json.loads(content)


class OllamaProvider(OpenAICompatibleProvider):
    """Provider for a local Ollama server exposing an OpenAI-compatible API."""

    def __init__(self) -> None:
        load_dotenv()
        super().__init__(
            model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        )


class GroqProvider(OpenAICompatibleProvider):
    """Provider for Groq's hosted OpenAI-compatible API."""

    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        super().__init__(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            api_key=api_key,
        )


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    """Instantiate the configured LLM provider."""

    load_dotenv()
    resolved_provider = (provider_name or os.getenv("LLM_PROVIDER", "ollama")).lower()
    if resolved_provider == "ollama":
        return OllamaProvider()
    if resolved_provider == "groq":
        return GroqProvider()
    raise ValueError(f"Unsupported LLM_PROVIDER: {resolved_provider}")
