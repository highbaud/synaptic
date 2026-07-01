"""Parse a single Markdown note into YAML frontmatter + body + section map."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body). Tolerates missing or malformed frontmatter."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
        if not isinstance(data, dict):
            data = {}
    except yaml.YAMLError:
        data = {}
    return data, text[m.end():]


def _sections(body: str) -> dict[str, str]:
    """Map `## Heading` -> text under it. Text before the first heading goes under '_intro'."""
    out: dict[str, list[str]] = {"_intro": []}
    current = "_intro"
    for line in body.splitlines():
        h = _HEADING_RE.match(line)
        if h:
            current = h.group(2).strip().lower()
            out.setdefault(current, [])
        else:
            out.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


@dataclass
class ParsedNote:
    path: Path
    frontmatter: dict[str, Any]
    body: str
    sections: dict[str, str] = field(default_factory=dict)
    wikilinks: list[str] = field(default_factory=list)

    @property
    def type(self) -> str:
        """Frontmatter `type`, else inferred from parent folder, else 'note'."""
        t = self.frontmatter.get("type")
        if t:
            return str(t).lower()
        # Check parent folder name first, then grandparent for nested PARA folders
        parent = self.path.parent.name.lower()
        # Strip leading numeric prefix (e.g. "00 - inbox" → "inbox")
        parent_clean = parent.split(" - ")[-1].strip() if " - " in parent else parent
        # Walk up one more level for notes nested inside PARA subfolders
        grandparent = self.path.parent.parent.name.lower() if self.path.parent.parent else ""
        grandparent_clean = grandparent.split(" - ")[-1].strip() if " - " in grandparent else grandparent

        folder_map = {
            # PARA top-level folders
            "inbox": "inbox",
            "notes": "note",
            "projects": "project",
            "areas": "area",
            "resources": "resource",
            "archive": "archived",
            "system": "system",
            # PARA subfolders under 01 - NOTES
            "daily": "daily",
            "meetings": "meeting",
            "books": "book",
            "courses": "course",
            # PARA subfolders under 04 - RESOURCES
            "topics": "resource",
            "topic": "resource",
            "people": "person",
            "person": "person",
            "places": "place",
            "tools": "tool",
            # Legacy folder names (backwards compat)
            "companies": "company",
            "company": "company",
            "tags": "resource",
            "interactions": "interaction",
            "interaction": "interaction",
        }
        # Prefer specific subfolder type; fall back to grandparent folder type
        return (folder_map.get(parent_clean)
                or folder_map.get(grandparent_clean)
                or "note")

    @property
    def title(self) -> str:
        fm_name = self.frontmatter.get("name")
        if fm_name:
            return str(fm_name)
        # First H1 in the body, else filename stem.
        for line in self.body.splitlines():
            h = _HEADING_RE.match(line)
            if h and len(h.group(1)) == 1:
                return h.group(2).strip()
        return self.path.stem


def parse_note(path: Path) -> ParsedNote:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    return ParsedNote(
        path=path,
        frontmatter=fm,
        body=body,
        sections=_sections(body),
        wikilinks=_WIKILINK_RE.findall(body),
    )


def dump_frontmatter(frontmatter: dict[str, Any], body: str) -> str:
    """Re-serialize a note (used when Synaptic writes tags/briefs back to a note)."""
    fm = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n\n{body.lstrip()}"
