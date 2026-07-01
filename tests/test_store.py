"""Tests for the SQLite metadata store — rejection pattern surfacing."""
from pathlib import Path

import pytest

from synaptic.db.store import Store, TagSuggestion


@pytest.fixture
def store(tmp_path: Path):
    s = Store(tmp_path / "test.db")
    yield s
    s.close()


def _reject(store: Store, target_id: str, tag: str) -> None:
    store.add_suggestion(TagSuggestion(
        target_id=target_id, target_type="resource", tag=tag,
        confidence=0.8, privacy_safe=True,
    ))
    matches = [r for r in store.pending_suggestions()
               if r["target_id"] == target_id and r["tag"] == tag]
    assert matches, f"expected a pending suggestion for {target_id}/{tag}"
    store.set_suggestion_status(matches[0]["id"], "rejected")


def test_rejection_patterns_below_threshold_not_surfaced(store):
    _reject(store, "note-1", "irrelevant-tag")
    _reject(store, "note-2", "irrelevant-tag")
    assert store.rejection_patterns(min_count=3) == []


def test_rejection_patterns_at_threshold_surfaced(store):
    for i in range(3):
        _reject(store, f"note-{i}", "irrelevant-tag")
    patterns = store.rejection_patterns(min_count=3)
    assert len(patterns) == 1
    assert patterns[0]["tag"] == "irrelevant-tag"
    assert patterns[0]["count"] == 3


def test_rejection_patterns_ordered_by_count_desc(store):
    for i in range(3):
        _reject(store, f"a-{i}", "tag-a")
    for i in range(5):
        _reject(store, f"b-{i}", "tag-b")
    patterns = store.rejection_patterns(min_count=3)
    assert [p["tag"] for p in patterns] == ["tag-b", "tag-a"]


def test_rejection_patterns_ignores_approved_suggestions(store):
    store.add_suggestion(TagSuggestion(
        target_id="note-1", target_type="resource", tag="good-tag",
        confidence=0.9, privacy_safe=True,
    ))
    pending = store.pending_suggestions()
    store.set_suggestion_status(pending[0]["id"], "approved")
    assert store.rejection_patterns(min_count=1) == []
