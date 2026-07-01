"""Local Ollama provider (http://localhost:11434)."""
from __future__ import annotations

import requests

from ..config import ProviderConfig
from .base import ChatMessage, LLMError


class OllamaProvider:
    def __init__(self, cfg: ProviderConfig):
        self.name = cfg.name
        self.base_url = (cfg.base_url or "http://localhost:11434").rstrip("/")
        self.chat_model = cfg.chat_model or "llama3.2:3b"
        self.embedding_model = cfg.embedding_model or "nomic-embed-text"

    def installed_models(self) -> list[str]:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=4)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except requests.RequestException:
            return []

    def available(self) -> bool:
        """Reachable AND the configured chat model is pulled."""
        models = self.installed_models()
        if not models:
            return False
        return any(m == self.chat_model or m.startswith(self.chat_model.split(":")[0])
                   for m in models)

    def chat(self, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        payload = {
            "model": self.chat_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["message"]["content"]
        except requests.RequestException as exc:
            raise LLMError(f"Ollama chat failed: {exc}") from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for t in texts:
            try:
                r = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.embedding_model, "prompt": t},
                    timeout=60,
                )
                r.raise_for_status()
                out.append(r.json()["embedding"])
            except requests.RequestException as exc:
                raise LLMError(f"Ollama embed failed: {exc}") from exc
        return out
