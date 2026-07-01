"""Anthropic (Claude) provider via the Messages API."""
from __future__ import annotations

import requests

from ..config import ProviderConfig
from .base import ChatMessage, LLMError

_BASE = "https://api.anthropic.com/v1"
_API_VERSION = "2023-06-01"


class AnthropicProvider:
    def __init__(self, cfg: ProviderConfig):
        self.name = cfg.name
        self.cfg = cfg
        self.base_url = (cfg.base_url or _BASE).rstrip("/")
        self.chat_model = cfg.chat_model or "claude-sonnet-4"

    def available(self) -> bool:
        return bool(self.cfg.api_key)

    def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        if not self.cfg.api_key:
            raise LLMError(f"Provider '{self.name}' has no API key "
                           f"(expected env var {self.cfg.api_key_env}).")
        system = "\n".join(m.content for m in messages if m.role == "system")
        turns = [{"role": m.role, "content": m.content}
                 for m in messages if m.role in ("user", "assistant")]
        payload = {
            "model": self.chat_model,
            "max_tokens": 2048,
            "temperature": temperature,
            "messages": turns,
        }
        if system:
            payload["system"] = system
        headers = {
            "x-api-key": self.cfg.api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        }
        try:
            r = requests.post(f"{self.base_url}/messages",
                              json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            blocks = r.json().get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        except requests.RequestException as exc:
            raise LLMError(f"{self.name} chat failed: {exc}") from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Anthropic has no first-party embeddings endpoint; route embeddings elsewhere.
        raise LLMError("Anthropic does not provide embeddings; "
                       "route 'embeddings' to ollama or openai.")
