"""Obsidian vault parsing: markdown + YAML frontmatter, entity loading, file watching."""

from .parser import ParsedNote, parse_note, split_frontmatter
from .vault import Entity, Vault

__all__ = ["ParsedNote", "parse_note", "split_frontmatter", "Entity", "Vault"]
