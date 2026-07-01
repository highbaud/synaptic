"""OpenAI Chat Completions provider, reused for any OpenAI-compatible API.

Covers `type: openai` (api.openai.com) and `type: openai_compatible`
(xAI/Grok, DeepSeek, OpenRouter, and other compatible endpoints).
"""
from __future__ import annotations

import requests

from ..config import ProviderConfig
from .base import ChatMessage, LLMError

_DEFAULT_BASE = "https://api.openai.com/v1"


class OpenAICompatibleProvider:
    def __init__(self, cfg: ProviderConfig):
        self.name = cfg.name
        self.cfg = cfg
        self.base_url = (cfg.base_url or _DEFAULT_BASE).rstrip("/")
        self.chat_model = cfg.chat_model
        self.embedding_model = cfg.embedding_model

    def available(self) -> bool:
        return bool(self.cfg.api_key) and bool(self.chat_model)

    def _headers(self) -> dict[str, str]:
        if not self.cfg.api_key:
            raise LLMError(
                f"Provider '{self.name}' has no API key "
                f"(expected env var {self.cfg.api_key_env})."
            )
        return {"Authorization": f"Bearer {self.cfg.api_key}",
                "Content-Type": "application/json"}

    def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        payload = {
            "model": self.chat_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        try:
            r = requests.post(f"{self.base_url}/chat/completions",
                              json=payload, headers=self._headers(), timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except requests.RequestException as exc:
            raise LLMError(f"{self.name} chat failed: {exc}") from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.embedding_model:
            raise LLMError(f"Provider '{self.name}' has no embedding_model configured.")
        try:
            r = requests.post(f"{self.base_url}/embeddings",
                              json={"model": self.embedding_model, "input": texts},
                              headers=self._headers(), timeout=120)
            r.raise_for_status()
            return [d["embedding"] for d in r.json()["data"]]
        except requests.RequestException as exc:
            raise LLMError(f"{self.name} embed failed: {exc}") from exc
