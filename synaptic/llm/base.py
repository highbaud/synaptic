"""Provider interface shared by all LLM backends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    """Raised when a provider is unreachable or returns an error."""


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMProvider(Protocol):
    name: str

    def available(self) -> bool:
        """True if the provider can actually serve a request right now."""
        ...

    def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        ...
