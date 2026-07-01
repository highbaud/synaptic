"""Build providers from config and route tasks to them.

The router never silently leaves the machine: external providers are gated by
`Config.assert_external_allowed`. Callers ask `available_for(task)` and fall back
to their own deterministic heuristics when no model is usable — that is why every
CLI command works even with a bare Ollama install or no network at all.
"""
from __future__ import annotations

from ..config import Config, ProviderConfig
from .anthropic import AnthropicProvider
from .base import ChatMessage, LLMProvider
from .openai_compat import OpenAICompatibleProvider
from .ollama import OllamaProvider


def build_provider(cfg: ProviderConfig) -> LLMProvider:
    if cfg.type == "local":
        return OllamaProvider(cfg)
    if cfg.type == "anthropic":
        return AnthropicProvider(cfg)
    # "openai" and "openai_compatible" share the Chat Completions shape.
    return OpenAICompatibleProvider(cfg)


class LLMRouter:
    def __init__(self, config: Config):
        self.config = config
        self._cache: dict[str, LLMProvider] = {}
        self._warned: set[str] = set()

    def provider_for(self, task: str) -> LLMProvider:
        pc = self.config.provider_for_task(task)
        if pc.name not in self._cache:
            self._cache[pc.name] = build_provider(pc)
        return self._cache[pc.name]

    def available_for(self, task: str) -> bool:
        """Can this task use a real model? Respects local-only and availability."""
        pc = self.config.provider_for_task(task)
        try:
            self.config.assert_external_allowed(pc)
        except PermissionError:
            return False
        return self.provider_for(task).available()

    def _warn_external_once(self, task: str) -> None:
        pc = self.config.provider_for_task(task)
        if not pc.is_local and pc.name not in self._warned:
            self._warned.add(pc.name)
            print(f"[synaptic] NOTE: task '{task}' is sending data to EXTERNAL "
                  f"provider '{pc.name}' ({pc.base_url or 'hosted API'}).")

    def chat(self, task: str, messages: list[ChatMessage], *, temperature: float = 0.2) -> str:
        pc = self.config.provider_for_task(task)
        self.config.assert_external_allowed(pc)
        self._warn_external_once(task)
        return self.provider_for(task).chat(messages, temperature=temperature)

    def embed(self, task: str, texts: list[str]) -> list[list[float]]:
        pc = self.config.provider_for_task(task)
        self.config.assert_external_allowed(pc)
        self._warn_external_once(task)
        return self.provider_for(task).embed(texts)
