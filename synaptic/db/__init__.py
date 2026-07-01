"""Local SQLite store for canonical entities, evidence, and tag suggestions."""

from .store import Store, TagSuggestion

__all__ = ["Store", "TagSuggestion"]
