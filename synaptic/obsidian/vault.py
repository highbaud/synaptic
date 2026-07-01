"""Load an Obsidian vault into typed entities and watch it for changes."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

from .parser import ParsedNote, parse_note

ENTITY_TYPES = {"person", "company", "topic", "interaction", "note"}


@dataclass
class Entity:
    id: str                       # stable id derived from vault-relative path
    type: str
    title: str
    path: Path
    frontmatter: dict[str, Any]
    body: str
    sections: dict[str, str]
    wikilinks: list[str] = field(default_factory=list)
    content_hash: str = ""

    @property
    def declared_privacy(self) -> str | None:
        v = self.frontmatter.get("privacy")
        return str(v).lower() if v else None

    @property
    def existing_tags(self) -> list[str]:
        tags = self.frontmatter.get("tags") or []
        return [str(t) for t in tags] if isinstance(tags, list) else [str(tags)]

    def searchable_text(self) -> str:
        """Body + key frontmatter fields, used for tagging/briefs/search."""
        fm_bits = [
            str(self.frontmatter.get(k, ""))
            for k in ("name", "company", "role", "industry", "description")
        ]
        return "\n".join([self.title, *fm_bits, self.body]).strip()


def _entity_id(vault_root: Path, path: Path) -> str:
    rel = path.relative_to(vault_root).as_posix()
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()[:16]


def _to_entity(vault_root: Path, parsed: ParsedNote) -> Entity:
    content_hash = hashlib.sha1(
        (str(parsed.frontmatter) + parsed.body).encode("utf-8")
    ).hexdigest()
    return Entity(
        id=_entity_id(vault_root, parsed.path),
        type=parsed.type,
        title=parsed.title,
        path=parsed.path,
        frontmatter=parsed.frontmatter,
        body=parsed.body,
        sections=parsed.sections,
        wikilinks=parsed.wikilinks,
        content_hash=content_hash,
    )


class Vault:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.root}")

    def markdown_files(self) -> Iterator[Path]:
        for p in self.root.rglob("*.md"):
            rel_parts = p.relative_to(self.root).parts
            # Skip Obsidian internals and hidden dirs.
            if any(part.startswith(".") for part in rel_parts):
                continue
            # Skip vault infrastructure that is not a real note. Note templates
            # are full of {{placeholders}} and CLAUDE.md is the context file;
            # indexing either pollutes search and query results, which is most
            # visible in a fresh vault where they would be most of the hits.
            if "templates" in rel_parts[:-1]:
                continue
            if p.name == "CLAUDE.md":
                continue
            yield p

    def load(self) -> list[Entity]:
        entities: list[Entity] = []
        for path in self.markdown_files():
            try:
                entities.append(_to_entity(self.root, parse_note(path)))
            except Exception as exc:  # one bad note must not abort the scan
                print(f"[vault] skipped {path.name}: {exc}")
        return entities

    def topics(self, entities: list[Entity] | None = None) -> list[Entity]:
        return [e for e in (entities or self.load()) if e.type == "topic"]

    def watch(self, on_change: Callable[[Path], None], poll: float = 1.0) -> None:
        """Block and call on_change(path) when any .md file changes.

        Uses watchdog if available; otherwise falls back to mtime polling so the
        feature works with zero optional dependencies.
        """
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            self._poll_watch(on_change, poll)
            return

        vault = self

        class _Handler(FileSystemEventHandler):
            def on_any_event(self, event):
                if event.is_directory or not str(event.src_path).endswith(".md"):
                    return
                p = Path(event.src_path)
                if any(part.startswith(".") for part in p.parts):
                    return
                on_change(p)

        observer = Observer()
        observer.schedule(_Handler(), str(self.root), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(poll)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def _poll_watch(self, on_change: Callable[[Path], None], poll: float) -> None:
        seen: dict[Path, float] = {}
        while True:
            for path in self.markdown_files():
                mtime = path.stat().st_mtime
                if seen.get(path) != mtime:
                    if path in seen:  # skip the initial inventory pass
                        on_change(path)
                    seen[path] = mtime
            time.sleep(poll)
