"""Guards for the single-source vault templates.

`synaptic init` loads templates from the packaged synaptic/templates/ dir; the
copies under examples/vault/06 - SYSTEM/templates/ must stay byte-identical so
there is one source of truth. These tests fail the moment the two drift.
"""
from importlib.resources import files
from pathlib import Path

import pytest

from synaptic.cli import _inject_contributor, _load_template

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = REPO_ROOT / "examples" / "vault" / "06 - SYSTEM" / "templates"
TEMPLATE_NAMES = [
    "daily.md", "meeting.md", "book.md", "project.md",
    "area.md", "resource.md", "weekly-review.md",
]


@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_packaged_and_example_templates_are_identical(name):
    packaged = _load_template(name)
    example = (EXAMPLE_DIR / name).read_text(encoding="utf-8")
    assert packaged == example, f"{name} drifted between package and example vault"


def test_no_template_ships_an_unsubstitutable_frontmatter_tag():
    """Obsidian core Templates only substitutes {{title}}/{{date}}/{{time}};
    a placeholder like {{slug}} in a frontmatter tag would ship literally."""
    for name in TEMPLATE_NAMES:
        text = _load_template(name)
        frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
        assert "{{slug}}" not in frontmatter, f"{name} frontmatter has literal {{{{slug}}}}"


def test_inject_contributor_adds_field_to_frontmatter():
    for name in TEMPLATE_NAMES:
        injected = _inject_contributor(_load_template(name))
        frontmatter = injected.split("---", 2)[1]
        assert "contributor:" in frontmatter, f"{name} did not get a contributor field"


def test_inject_contributor_is_idempotent_on_frontmatter_boundary():
    """The field lands inside frontmatter, not in the body."""
    injected = _inject_contributor(_load_template("book.md"))
    head, frontmatter, body = injected.split("---", 2)
    assert "contributor:" in frontmatter
    assert "contributor:" not in body
    # book.md's bibliographic author: must survive intact alongside contributor:
    assert "author:" in frontmatter
