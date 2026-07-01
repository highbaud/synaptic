"""Tests for the MCP server's retrieval narrowing and MOC navigation.

Uses fakes and monkeypatched module globals rather than the real setup()
pipeline, since the server keeps state as module-level singletons.
"""
import json

import pytest

pytest.importorskip("mcp", reason="mcp package not installed")

import synaptic.mcp.server as server


class FakeStore:
    def __init__(self, rows, by_title=None):
        self._rows = rows
        self._by_title = {k.lower(): v for k, v in (by_title or {}).items()}

    def all_entities(self):
        return self._rows

    def find_entity_by_title(self, title):
        return self._by_title.get(title.lower())


class FakeCfg:
    def __init__(self, vault_path):
        self.vault_path = vault_path


def _row(id_, tags=None, type_=None, project=None, status=None):
    fm = {}
    if tags is not None:
        fm["tags"] = tags
    if type_ is not None:
        fm["type"] = type_
    if project is not None:
        fm["project"] = project
    if status is not None:
        fm["status"] = status
    return {"id": id_, "frontmatter": json.dumps(fm)}


# --------------------------------------------------------------------------- #
# _try_frontmatter_narrow                                                      #
# --------------------------------------------------------------------------- #

def test_frontmatter_narrow_matches_on_topical_tags(monkeypatch):
    rows = [
        _row("a", tags=["deliberate-practice", "learning"]),
        _row("b", tags=["cooking"]),
        _row("c", tags=["cooking", "recipes"]),
    ]
    monkeypatch.setattr(server, "_store", FakeStore(rows))
    assert server._try_frontmatter_narrow("what do I know about deliberate practice") == {"a"}


def test_frontmatter_narrow_works_on_a_small_vault(monkeypatch):
    """Regression: a 50%-reduction bar silently disabled narrowing on small
    vaults, where 1 real match out of 3 notes is useful, not a no-op."""
    rows = [
        _row("a", tags=["deliberate-practice"]),
        _row("b", tags=["cooking"]),
        _row("c", tags=["baking"]),
    ]
    monkeypatch.setattr(server, "_store", FakeStore(rows))
    assert server._try_frontmatter_narrow("deliberate practice tips") == {"a"}


def test_frontmatter_narrow_is_punctuation_insensitive(monkeypatch):
    """Regression: naive .split() left 'practice?' which never matched the tag."""
    rows = [_row("a", tags=["deliberate-practice"]), _row("b", tags=["cooking"])]
    monkeypatch.setattr(server, "_store", FakeStore(rows))
    assert server._try_frontmatter_narrow("what about deliberate practice?") == {"a"}


def test_frontmatter_narrow_ignores_generic_type_and_status_words(monkeypatch):
    """Regression (the poisoning bug): matching the word 'meeting' against every
    type:meeting note must NOT narrow — generic frontmatter words are stopwords,
    so semantically-relevant notes of other types are never excluded."""
    rows = [
        _row("a", type_="meeting", status="active"),
        _row("b", type_="resource", status="archived", tags=["pricing-strategy"]),
    ]
    monkeypatch.setattr(server, "_store", FakeStore(rows))
    assert server._try_frontmatter_narrow("what did we decide in the meeting") is None


def test_frontmatter_narrow_returns_none_when_no_match(monkeypatch):
    rows = [_row("a", tags=["cooking"]), _row("b", tags=["baking"])]
    monkeypatch.setattr(server, "_store", FakeStore(rows))
    assert server._try_frontmatter_narrow("quantum physics") is None


def test_frontmatter_narrow_skips_when_match_covers_whole_vault(monkeypatch):
    rows = [_row(f"n{i}", tags=["widget-launch"]) for i in range(10)]
    monkeypatch.setattr(server, "_store", FakeStore(rows))
    assert server._try_frontmatter_narrow("widget launch status") is None


# --------------------------------------------------------------------------- #
# _try_moc_navigation                                                         #
# --------------------------------------------------------------------------- #

def _make_moc(vault_path, stem, body):
    moc_dir = vault_path / "06 - SYSTEM" / "MOCs"
    moc_dir.mkdir(parents=True, exist_ok=True)
    (moc_dir / f"{stem}.md").write_text(body, encoding="utf-8")


def test_moc_navigation_strong_match_returns_context(tmp_path, monkeypatch):
    _make_moc(tmp_path, "deliberate-practice",
              "# Deliberate Practice\n\n- [[Feedback Loops]]\n")
    monkeypatch.setattr(server, "_cfg", FakeCfg(tmp_path))
    monkeypatch.setattr(server, "_store", FakeStore(
        [], by_title={"Feedback Loops": {"title": "Feedback Loops", "body": "..."}}))
    result = server._try_moc_navigation("notes on deliberate practice", top_k=5)
    titles = [t for t, _ in result]
    assert "deliberate-practice" in titles
    assert "Feedback Loops" in titles


def test_moc_navigation_ignores_generic_index_name(tmp_path, monkeypatch):
    """A MOC named only with generic words (meeting-notes) must never hijack a
    query on an unrelated topic via an incidental shared word like 'notes'."""
    _make_moc(tmp_path, "meeting-notes", "# Meetings\n\n- [[Standup]]\n")
    monkeypatch.setattr(server, "_cfg", FakeCfg(tmp_path))
    monkeypatch.setattr(server, "_store", FakeStore([]))
    result = server._try_moc_navigation("what do my notes say about quantum physics", top_k=5)
    assert result == []


def test_moc_navigation_requires_strong_overlap(tmp_path, monkeypatch):
    """Single incidental topic-word overlap on a multi-word MOC is not enough."""
    _make_moc(tmp_path, "trading-strategy", "# Trading\n\n- [[Risk]]\n")
    monkeypatch.setattr(server, "_cfg", FakeCfg(tmp_path))
    monkeypatch.setattr(server, "_store", FakeStore(
        [], by_title={"Risk": {"title": "Risk", "body": "..."}}))
    # Overlaps only on 'trading' (1 of 2 stem words) — below the strong bar.
    assert server._try_moc_navigation("trading psychology and discipline", top_k=5) == []
