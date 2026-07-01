"""Tests for the vault loader's file selection."""
from pathlib import Path

from synaptic.obsidian.vault import Vault


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_load_excludes_templates_and_claude_md(tmp_path):
    """Regression: templates and CLAUDE.md were indexed as notes, so a fresh
    vault's queries surfaced {{placeholder}} scaffolding as results."""
    _write(tmp_path / "04 - RESOURCES" / "topics" / "real-note.md",
           "---\ntype: resource\n---\n\n# A real idea\n\nBody.\n")
    _write(tmp_path / "06 - SYSTEM" / "templates" / "daily.md",
           "---\ntype: daily\n---\n\n# {{date}}\n\n## {{title}}\n")
    _write(tmp_path / "06 - SYSTEM" / "CLAUDE.md",
           "# Vault intelligence context\n\nActive projects...\n")
    _write(tmp_path / "06 - SYSTEM" / "MOCs" / "topic-index.md",
           "---\ntype: note\n---\n\n# Topic MOC\n\n- [[A real idea]]\n")

    titles = {e.title for e in Vault(tmp_path).load()}

    assert "A real idea" in titles           # real notes are indexed
    assert "Topic MOC" in titles             # MOCs stay indexed (navigable content)
    assert not any("{{" in t for t in titles)  # no template scaffolding
    assert "Vault intelligence context" not in titles  # CLAUDE.md excluded


def test_load_still_skips_hidden_dirs(tmp_path):
    _write(tmp_path / ".obsidian" / "workspace.md", "# internal\n")
    _write(tmp_path / "01 - NOTES" / "keep.md", "# Keep me\n")
    titles = {e.title for e in Vault(tmp_path).load()}
    assert "Keep me" in titles
    assert "internal" not in titles
