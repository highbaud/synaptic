"""Configuration loading: config.yaml + .env, provider resolution, local-only enforcement."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Provider types we treat as "the model runs on this machine".
LOCAL_PROVIDER_TYPES = {"local"}


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no extra dependency). Does not override real env vars."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


@dataclass
class ProviderConfig:
    name: str
    type: str
    chat_model: str | None = None
    embedding_model: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None

    @property
    def is_local(self) -> bool:
        return self.type in LOCAL_PROVIDER_TYPES

    @property
    def api_key(self) -> str | None:
        return os.environ.get(self.api_key_env) if self.api_key_env else None


@dataclass
class PrivacyConfig:
    local_only: bool = True
    brief_allowed_levels: list[str] = field(
        default_factory=lambda: ["public", "professional"]
    )
    default_level: str = "professional"


@dataclass
class Config:
    root: Path
    vault_path: Path
    db_path: Path
    privacy: PrivacyConfig
    default_provider: str
    routing: dict[str, str]
    providers: dict[str, ProviderConfig]
    tagging_min_confidence: float = 0.55
    raw: dict[str, Any] = field(default_factory=dict)

    def provider_for_task(self, task: str) -> ProviderConfig:
        """Resolve which provider handles a task, honoring routing then default."""
        name = self.routing.get(task, self.default_provider)
        # `local` is a routing sentinel meaning "never leave the machine".
        if name == "local":
            name = self.default_provider
        if name not in self.providers:
            raise KeyError(f"Routing for task '{task}' points at unknown provider '{name}'")
        return self.providers[name]

    def assert_external_allowed(self, provider: ProviderConfig) -> None:
        """Enforce local-only mode before any outbound LLM call."""
        env_flag = os.environ.get("SYNAPTIC_LOCAL_ONLY")
        local_only = self.privacy.local_only
        if env_flag is not None:
            local_only = env_flag.lower() in ("1", "true", "yes")
        if local_only and not provider.is_local:
            raise PermissionError(
                f"local_only mode is ON but task wants external provider "
                f"'{provider.name}'. Set privacy.local_only=false in config.yaml to allow it."
            )


def find_config_path(root: Path) -> Path:
    """config/config.yaml if present, else the tracked example."""
    primary = root / "config" / "config.yaml"
    return primary if primary.exists() else root / "config" / "config.example.yaml"


def load_config(root: Path | None = None) -> Config:
    root = (root or Path.cwd()).resolve()
    _load_dotenv(root / ".env")

    cfg_path = find_config_path(root)
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}

    vault_path = (root / data.get("vault", {}).get("path", "./examples/vault")).resolve()
    db_path = (root / data.get("storage", {}).get("db_path", "./.synaptic/synaptic.db")).resolve()

    p = data.get("privacy", {})
    privacy = PrivacyConfig(
        local_only=bool(p.get("local_only", True)),
        brief_allowed_levels=p.get("brief_allowed_levels", ["public", "professional"]),
        default_level=p.get("default_level", "professional"),
    )

    providers: dict[str, ProviderConfig] = {}
    for name, pc in (data.get("providers", {}) or {}).items():
        providers[name] = ProviderConfig(
            name=name,
            type=pc.get("type", "openai_compatible"),
            chat_model=pc.get("chat_model"),
            embedding_model=pc.get("embedding_model"),
            base_url=pc.get("base_url"),
            api_key_env=pc.get("api_key_env"),
        )

    llm = data.get("llm", {})
    return Config(
        root=root,
        vault_path=vault_path,
        db_path=db_path,
        privacy=privacy,
        default_provider=llm.get("default_provider", "ollama"),
        routing=data.get("routing", {}) or {},
        providers=providers,
        tagging_min_confidence=float(data.get("tagging", {}).get("min_confidence", 0.55)),
        raw=data,
    )
