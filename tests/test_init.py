"""Tests for `synaptic init` — personal vs. shared branching.

Covers the fork added for personal-brain vs. shared-team-brain setup: template
attribution field, CLAUDE.md shape, and privacy defaults.
"""
import shutil
from pathlib import Path

import yaml
from click.testing import CliRunner

from synaptic.cli import main

REPO_EXAMPLE_CONFIG = Path(__file__).resolve().parents[1] / "config" / "config.example.yaml"

# All prompts have defaults; blank answers exercise the default path.
PERSONAL_ANSWERS = ["", "", "", "", "", "", ""]

# s1 (purpose), s_champion, and s2 (what the team produces) have no default and
# require real input; the rest have defaults and can be left blank.
SHARED_ANSWERS = [
    "Team knowledge base",   # 1. purpose
    "Alex Rivera",           # 2. champion
    "",                      # 3. contributors (default)
    "Onboarding docs",       # 4. what the team produces
    "",                      # 5. active projects (default)
    "",                      # 6. active decisions (default)
    "",                      # 7. what makes a note useful (default)
    "",                      # 8. escalation (defaults to champion)
]


def _seed_config_example(root: Path) -> None:
    """Mirror a real checkout, which ships config/config.example.yaml tracked in git."""
    dest_dir = root / "config"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO_EXAMPLE_CONFIG, dest_dir / "config.example.yaml")


def _run_init(tmp_path: Path, mode: str, answers: list[str]) -> Path:
    vault_path = tmp_path / "vault"
    runner = CliRunner()
    stdin = "\n".join([str(vault_path), mode, *answers]) + "\n"
    result = runner.invoke(main, ["--root", str(tmp_path), "init"], input=stdin)
    assert result.exit_code == 0, result.output
    return vault_path


def test_personal_mode_has_no_contributor_field(tmp_path):
    vault = _run_init(tmp_path, "personal", PERSONAL_ANSWERS)
    daily = (vault / "06 - SYSTEM" / "templates" / "daily.md").read_text(encoding="utf-8")
    assert "contributor:" not in daily


def test_personal_mode_claude_md_has_no_team_charter(tmp_path):
    vault = _run_init(tmp_path, "personal", PERSONAL_ANSWERS)
    claude_md = (vault / "06 - SYSTEM" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Team Charter" not in claude_md


def test_shared_mode_adds_contributor_field_to_every_template(tmp_path):
    vault = _run_init(tmp_path, "shared", SHARED_ANSWERS)
    template_dir = vault / "06 - SYSTEM" / "templates"
    template_files = list(template_dir.glob("*.md"))
    assert len(template_files) == 7
    for path in template_files:
        assert "contributor:" in path.read_text(encoding="utf-8"), path.name


def test_shared_mode_book_template_keeps_bibliographic_author_distinct(tmp_path):
    """contributor: (who wrote this note) must not collide with author: (the book's author)."""
    vault = _run_init(tmp_path, "shared", SHARED_ANSWERS)
    book = (vault / "06 - SYSTEM" / "templates" / "book.md").read_text(encoding="utf-8")
    assert "contributor:" in book
    assert "author:" in book
    assert book.count("author:") == 1  # not overwritten or duplicated by the insertion


def test_shared_mode_claude_md_has_team_charter_and_champion(tmp_path):
    vault = _run_init(tmp_path, "shared", SHARED_ANSWERS)
    claude_md = (vault / "06 - SYSTEM" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Team Charter" in claude_md
    assert "Alex Rivera" in claude_md


def test_shared_mode_tightens_privacy_defaults(tmp_path):
    _seed_config_example(tmp_path)
    _run_init(tmp_path, "shared", SHARED_ANSWERS)
    config = yaml.safe_load((tmp_path / "config" / "config.yaml").read_text(encoding="utf-8"))
    assert config["privacy"]["default_level"] == "personal_sensitive"
    assert config["privacy"]["brief_allowed_levels"] == ["public"]
    # local_only must survive untouched — shared mode only tightens brief exposure.
    assert config["privacy"]["local_only"] is True


def test_personal_mode_keeps_default_privacy(tmp_path):
    _seed_config_example(tmp_path)
    _run_init(tmp_path, "personal", PERSONAL_ANSWERS)
    config = yaml.safe_load((tmp_path / "config" / "config.yaml").read_text(encoding="utf-8"))
    assert config["privacy"]["default_level"] == "professional"
    assert config["privacy"]["brief_allowed_levels"] == ["public", "professional"]
