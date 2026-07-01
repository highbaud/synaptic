"""Synaptic command-line interface."""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .briefs.generator import BriefGenerator
from .config import load_config
from .db.store import Store
from .llm.factory import LLMRouter
from .llm.ollama import OllamaProvider
from .obsidian.vault import Vault
from .privacy.classifier import PrivacyClassifier
from .tagging.engine import TagEngine

console = Console()


def _ctx(root: Path | None = None):
    cfg = load_config(root)
    store = Store(cfg.db_path)
    router = LLMRouter(cfg)
    classifier = PrivacyClassifier(
        default_level=cfg.privacy.default_level,
        allowed_levels=cfg.privacy.brief_allowed_levels,
    )
    return cfg, store, router, classifier


def _load_entities(cfg, store):
    vault = Vault(cfg.vault_path)
    entities = vault.load()
    for e in entities:
        verdict_level = e.declared_privacy or cfg.privacy.default_level
        store.upsert_entity(
            id=e.id, type=e.type, title=e.title, path=str(e.path),
            privacy_level=verdict_level,
            frontmatter=e.frontmatter, body=e.body, content_hash=e.content_hash,
        )
    return vault, entities


def _load_template(name: str) -> str:
    """Return a canonical vault template's text from packaged data.

    Templates live in synaptic/templates/ so init and the example vault share
    one source; see tests/test_templates.py for the parity guard.
    """
    from importlib.resources import files
    return (files("synaptic.templates") / name).read_text(encoding="utf-8")


def _print_rejection_patterns(store, min_rejections: int) -> None:
    """Surface tags rejected repeatedly as a suggested CLAUDE.md edit."""
    patterns = store.rejection_patterns(min_count=min_rejections)
    if not patterns:
        return
    console.print(
        "\n[bold yellow]Pattern in your rejections:[/bold yellow] "
        "these tags keep getting turned down. The vault is telling you "
        "something 06 - SYSTEM/CLAUDE.md doesn't say yet."
    )
    for p in patterns:
        last = (p["last_rejected"] or "")[:10] or "unknown"
        console.print(f"  - [cyan]{p['tag']}[/cyan] rejected {p['count']}x "
                      f"(last: {last})")
    console.print(
        "\n[dim]Consider adding under 'What Makes a Note Useful For Me' -> "
        "Not useful in CLAUDE.md:[/dim]"
    )
    for p in patterns:
        console.print(f"[dim]  - Tags like '{p['tag']}' — consistently rejected, "
                      f"not part of how I actually use the vault[/dim]")


def _inject_contributor(text: str) -> str:
    """Add a `contributor:` frontmatter key as the last field of the YAML block.

    Shared-vault attribution. Inserted structurally (before the closing `---`)
    rather than by matching a specific key, so it works on any template
    regardless of which frontmatter fields it has.
    """
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines.insert(i, "contributor:")
                break
    return "\n".join(lines)


@click.group()
@click.option("--root", type=click.Path(file_okay=False), default=None,
              help="Project root (defaults to CWD).")
@click.pass_context
def main(ctx, root):
    """Synaptic — local-first Obsidian intelligence."""
    ctx.obj = {"root": Path(root) if root else None}


@main.command()
@click.pass_context
def doctor(ctx):
    """Check config, Ollama reachability, models, and the active provider."""
    cfg, store, router, _ = _ctx(ctx.obj["root"])
    console.print(f"[bold]Vault:[/bold] {cfg.vault_path}  "
                  f"({'exists' if cfg.vault_path.exists() else 'MISSING'})")
    console.print(f"[bold]DB:[/bold] {cfg.db_path}")
    console.print(f"[bold]local_only:[/bold] {cfg.privacy.local_only}")
    console.print(f"[bold]default_provider:[/bold] {cfg.default_provider}")

    ollama_cfg = cfg.providers.get("ollama")
    if ollama_cfg:
        oll = OllamaProvider(ollama_cfg)
        models = oll.installed_models()
        reachable = bool(models) or _ping(oll.base_url)
        console.print(f"[bold]Ollama:[/bold] {oll.base_url} — "
                      f"{'reachable' if reachable else 'NOT reachable'}")
        console.print(f"  models: {', '.join(models) if models else '(none pulled)'}")
        if oll.available():
            console.print(f"  [green]chat model '{oll.chat_model}' ready[/green]")
        else:
            console.print(f"  [yellow]chat model '{oll.chat_model}' not pulled — "
                          f"run: ollama pull {oll.chat_model}[/yellow]")
            console.print("  [yellow]Synaptic will use the heuristic fallback "
                          "until a model is available.[/yellow]")
    for task in ("tagging", "briefs", "strategic_queries"):
        kind = "model" if router.available_for(task) else "heuristic fallback"
        console.print(f"  route '{task}': {cfg.routing.get(task, cfg.default_provider)} "
                      f"-> {kind}")
    store.close()


def _ping(base_url: str) -> bool:
    import requests
    try:
        requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        return True
    except Exception:
        return False


@main.command()
@click.pass_context
def scan(ctx):
    """Parse the vault and load entities into the local DB."""
    cfg, store, _, _ = _ctx(ctx.obj["root"])
    _, entities = _load_entities(cfg, store)
    by_type: dict[str, int] = {}
    for e in entities:
        by_type[e.type] = by_type.get(e.type, 0) + 1
    table = Table(title="Vault scan")
    table.add_column("type"); table.add_column("count", justify="right")
    for t, n in sorted(by_type.items()):
        table.add_row(t, str(n))
    console.print(table)
    store.close()


@main.command()
@click.pass_context
def tags(ctx):
    """List defined topics/tags and their definitions."""
    cfg, store, router, classifier = _ctx(ctx.obj["root"])
    _, entities = _load_entities(cfg, store)
    engine = TagEngine(cfg, store, router, classifier)
    topics = engine.load_topics(entities)
    if not topics:
        console.print("[yellow]No topic notes found. Add notes with type: topic.[/yellow]")
    for t in topics:
        applies = ", ".join(t.applies_to)
        console.print(f"[bold]{t.name}[/bold] (threshold {t.confidence_threshold}, "
                      f"applies_to: {applies})\n  {t.description}")
    store.close()


@main.command(name="suggest-tags")
@click.pass_context
def suggest_tags(ctx):
    """Generate pending, evidence-backed tag suggestions."""
    cfg, store, router, classifier = _ctx(ctx.obj["root"])
    _, entities = _load_entities(cfg, store)
    mode = "LLM" if router.available_for("tagging") else "heuristic"
    console.print(f"Scoring {len(entities)} entities ([italic]{mode} mode[/italic])...")
    engine = TagEngine(cfg, store, router, classifier)
    n = engine.run(entities)
    console.print(f"[green]{n} suggestion(s) written.[/green] "
                  f"Review with: synaptic review")
    store.close()


@main.command()
@click.option("--auto-approve-above", type=float, default=None,
              help="Auto-approve safe suggestions with confidence >= this value.")
@click.option("--min-rejections", type=int, default=3, show_default=True,
              help="Surface a CLAUDE.md suggestion once a tag is rejected this many times.")
@click.pass_context
def review(ctx, auto_approve_above, min_rejections):
    """Approve / reject pending tag suggestions before they become canonical."""
    cfg, store, _, _ = _ctx(ctx.obj["root"])
    pending = store.pending_suggestions()
    if not pending:
        console.print("[green]No pending suggestions.[/green]")
        # Rejection patterns still worth surfacing — an empty queue is exactly
        # when a user runs this to review what they keep turning down.
        _print_rejection_patterns(store, min_rejections)
        store.close(); return

    for row in pending:
        ent = store.get_entity(row["target_id"])
        ent_title = ent["title"] if ent else row["target_id"]
        evidence = json.loads(row["evidence"])
        safe = "safe" if row["privacy_safe"] else "[red]UNSAFE[/red]"
        console.print(f"\n[bold]{ent_title}[/bold] ({row['target_type']}) "
                      f"-> tag [cyan]{row['tag']}[/cyan]  "
                      f"conf={row['confidence']:.2f}  {safe}")
        for ev in evidence:
            console.print(f"    • {ev['source']}: {ev['quote_or_summary']}")

        if auto_approve_above is not None:
            if row["privacy_safe"] and row["confidence"] >= auto_approve_above:
                store.set_suggestion_status(row["id"], "approved")
                console.print("    [green]auto-approved[/green]")
            continue

        choice = click.prompt("    approve/reject/skip", default="skip",
                              type=click.Choice(["approve", "reject", "skip", "a", "r", "s"]))
        if choice in ("approve", "a"):
            store.set_suggestion_status(row["id"], "approved")
        elif choice in ("reject", "r"):
            store.set_suggestion_status(row["id"], "rejected")
    console.print("\n[green]Review complete.[/green]")

    _print_rejection_patterns(store, min_rejections)
    store.close()


@main.command()
@click.argument("name")
@click.option("--out", type=click.Path(), default=None,
              help="Write the brief to a file instead of stdout.")
@click.pass_context
def brief(ctx, name, out):
    """Generate a privacy-safe contact brief for a person."""
    cfg, store, router, classifier = _ctx(ctx.obj["root"])
    _, entities = _load_entities(cfg, store)
    person = next((e for e in entities
                   if e.type == "person" and e.title.lower() == name.lower()), None)
    if person is None:
        console.print(f"[red]No person note titled '{name}' found.[/red]")
        store.close(); return

    gen = BriefGenerator(cfg, store, router, classifier)
    result = gen.generate(person, entities)
    if out:
        Path(out).write_text(result.markdown, encoding="utf-8")
        console.print(f"[green]Brief written to {out}[/green]")
    else:
        console.print(result.markdown)
    if result.excluded_sources:
        console.print("\n[yellow]Excluded from brief (privacy):[/yellow]")
        for src, lvl in result.excluded_sources:
            console.print(f"  - {src} ({lvl})")
    store.close()


@main.command()
@click.pass_context
def watch(ctx):
    """Re-scan affected notes when the vault changes (Ctrl-C to stop)."""
    cfg, store, _, _ = _ctx(ctx.obj["root"])
    vault = Vault(cfg.vault_path)
    console.print(f"Watching {cfg.vault_path} ... (Ctrl-C to stop)")

    def on_change(path: Path):
        console.print(f"[dim]changed:[/dim] {path.name} — rescanning vault")
        _load_entities(cfg, store)

    try:
        vault.watch(on_change)
    except KeyboardInterrupt:
        pass
    store.close()


@main.command()
@click.pass_context
def health(ctx):
    """Show vault health: inbox size, unlinked notes, missing frontmatter, and more."""
    from .obsidian.parser import parse_note, _WIKILINK_RE

    cfg = load_config(ctx.obj["root"])
    vault_path = cfg.vault_path

    if not vault_path.exists():
        console.print(f"[red]Vault not found: {vault_path}[/red]")
        return

    # Collect every markdown file
    all_md = [p for p in vault_path.rglob("*.md") if ".obsidian" not in p.parts]

    # Classify by PARA folder
    _DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

    def para_bucket(path: Path) -> str:
        parts = [p.lower() for p in path.relative_to(vault_path).parts]
        for p in parts:
            clean = p.split(" - ")[-1].strip() if " - " in p else p
            if clean in ("inbox", "00 - inbox"):
                return "inbox"
            if clean in ("archive", "05 - archive"):
                return "archive"
            if clean in ("projects", "02 - projects"):
                return "projects"
            if clean in ("system", "06 - system"):
                return "system"
        return "active"

    inbox_notes, active_notes, archive_notes, project_folders = [], [], [], set()
    missing_fm, no_links, review_flagged = [], [], []
    stale_inbox = []

    for path in all_md:
        bucket = para_bucket(path)
        if bucket == "inbox":
            inbox_notes.append(path)
            # Check staleness by filename date or file mtime
            m = _DATE_RE.match(path.stem)
            if m:
                note_date = datetime.strptime(m.group(1), "%Y-%m-%d")
                if datetime.now() - note_date > timedelta(days=7):
                    stale_inbox.append(path)
            else:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if datetime.now() - mtime > timedelta(days=7):
                    stale_inbox.append(path)
        elif bucket == "archive":
            archive_notes.append(path)
        elif bucket == "projects":
            # Count unique project subfolders (depth 1 inside projects/)
            rel_parts = path.relative_to(vault_path).parts
            if len(rel_parts) >= 2:
                project_folders.add(rel_parts[1])
            active_notes.append(path)
        elif bucket in ("active",):
            active_notes.append(path)

        # Check only active / inbox notes for quality
        if bucket in ("active", "inbox", "projects"):
            try:
                note = parse_note(path)
            except Exception:
                continue
            required = {"type", "status", "date"}
            missing = required - set(note.frontmatter.keys())
            if missing:
                missing_fm.append((path.name, missing))
            if not note.wikilinks and bucket != "inbox":
                no_links.append(path.name)
            # status: review in frontmatter or #status/review tag
            status_val = str(note.frontmatter.get("status", "")).lower()
            tags_val = " ".join(str(t) for t in (note.frontmatter.get("tags") or []))
            if status_val == "review" or "status/review" in tags_val:
                review_flagged.append(path.name)

    total = len(all_md)
    pct_archived = round(len(archive_notes) / total * 100) if total else 0

    # -- Output --
    console.print()
    console.print("[bold]Vault health[/bold]", vault_path)
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("metric", style="dim")
    table.add_column("value")
    table.add_column("status")

    def flag(val, warn_above=0, bad_above=None):
        if bad_above is not None and val > bad_above:
            return "[red]ERR[/red]"
        if val > warn_above:
            return "[yellow]WARN[/yellow]"
        return "[green] OK [/green]"

    table.add_row("Total notes", str(total), "")
    table.add_row("Archive %", f"{pct_archived}%",
                  "[green] OK [/green]" if pct_archived >= 20 else "[yellow]WARN[/yellow]")
    table.add_row("Active projects", str(len(project_folders)), "")
    table.add_row("INBOX size", str(len(inbox_notes)),
                  flag(len(inbox_notes), warn_above=5, bad_above=20))
    table.add_row("Stale INBOX (>7d)", str(len(stale_inbox)),
                  flag(len(stale_inbox), warn_above=0, bad_above=5))
    table.add_row("Missing frontmatter", str(len(missing_fm)),
                  flag(len(missing_fm), warn_above=0, bad_above=10))
    table.add_row("Unlinked notes", str(len(no_links)),
                  flag(len(no_links), warn_above=5, bad_above=20))
    table.add_row("Needs review", str(len(review_flagged)),
                  flag(len(review_flagged), warn_above=0, bad_above=10))
    console.print(table)

    if stale_inbox:
        console.print(f"\n[yellow]Stale INBOX (>7 days):[/yellow]")
        for p in stale_inbox[:10]:
            console.print(f"  - {p.name}")
        if len(stale_inbox) > 10:
            console.print(f"  … and {len(stale_inbox) - 10} more")

    if missing_fm:
        console.print(f"\n[yellow]Missing frontmatter:[/yellow]")
        for name, fields in missing_fm[:10]:
            console.print(f"  - {name} -- missing: {', '.join(sorted(fields))}")
        if len(missing_fm) > 10:
            console.print(f"  … and {len(missing_fm) - 10} more")

    if review_flagged:
        console.print(f"\n[yellow]Flagged for review:[/yellow]")
        for name in review_flagged[:10]:
            console.print(f"  - {name}")

    if no_links:
        console.print(f"\n[dim]Unlinked notes (first 5):[/dim]")
        for name in no_links[:5]:
            console.print(f"  - {name}")
        if len(no_links) > 5:
            console.print(f"  … and {len(no_links) - 5} more")

    # Summary verdict
    console.print()
    if not stale_inbox and not missing_fm and len(no_links) <= 5:
        console.print("[green]Vault looks healthy.[/green]")
    else:
        issues = []
        if stale_inbox:
            issues.append(f"process {len(stale_inbox)} stale INBOX note(s)")
        if missing_fm:
            issues.append(f"add frontmatter to {len(missing_fm)} note(s)")
        if len(no_links) > 5:
            issues.append(f"add links to {len(no_links)} unlinked note(s)")
        console.print("[yellow]Suggested actions:[/yellow] " + " · ".join(issues))
    console.print()


@main.command(name="write-tags")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would change without writing anything.")
@click.pass_context
def write_tags(ctx, dry_run):
    """Write approved tag suggestions back into each note's frontmatter."""
    from .obsidian.parser import dump_frontmatter, parse_note

    cfg, store, _, _ = _ctx(ctx.obj["root"])
    rows = store.all_entities()
    notes_updated = 0
    tags_written = 0

    for row in rows:
        entity_id = row["id"]
        approved = store.approved_tags_for(entity_id)
        if not approved:
            continue

        path = Path(row["path"])
        if not path.exists():
            console.print(f"[yellow]File not found, skipping: {path.name}[/yellow]")
            continue

        try:
            note = parse_note(path)
        except Exception as exc:
            console.print(f"[yellow]Could not parse {path.name}: {exc}[/yellow]")
            continue

        existing = note.frontmatter.get("tags") or []
        if isinstance(existing, str):
            existing = [existing]
        existing_set = {str(t).lower() for t in existing}
        new_tags = [t for t in approved if t.lower() not in existing_set]
        if not new_tags:
            continue

        merged = list(existing) + new_tags
        if dry_run:
            console.print(f"[dim]{path.name}[/dim] would add: {new_tags}")
            notes_updated += 1
            tags_written += len(new_tags)
            continue

        updated_fm = dict(note.frontmatter)
        updated_fm["tags"] = merged
        try:
            path.write_text(dump_frontmatter(updated_fm, note.body), encoding="utf-8")
            console.print(f"[green]{path.name}[/green] +{len(new_tags)} tag(s): {new_tags}")
            notes_updated += 1
            tags_written += len(new_tags)
        except Exception as exc:
            console.print(f"[red]Error writing {path.name}: {exc}[/red]")

    verb = "Would update" if dry_run else "Updated"
    console.print(f"\n{verb} {notes_updated} note(s), {tags_written} tag(s) written.")
    store.close()


@main.command(name="init")
@click.pass_context
def init(ctx):
    """Interactively initialise a new Synaptic vault with PARA folders and CLAUDE.md."""
    default_vault = Path.home() / "Documents" / "Synaptic"
    vault_input = click.prompt("Vault path", default=str(default_vault))
    vault_path = Path(vault_input).expanduser().resolve()

    mode = click.prompt(
        "Is this a personal brain or a shared team brain?",
        type=click.Choice(["personal", "shared"]),
        default="personal",
    )
    if mode == "shared":
        console.print(
            "[yellow]Note: Synaptic has no real access control — anyone who can "
            "open this folder can read and write everything in it. 'Shared' mode "
            "sets up conventions (a named champion, attribution, stricter privacy "
            "defaults), not enforcement. Treat it like a trusted synced team "
            "folder.[/yellow]\n"
        )

    # Create PARA folder structure.
    para_dirs = [
        "00 - INBOX",
        "01 - NOTES/daily",
        "01 - NOTES/meetings",
        "01 - NOTES/books",
        "01 - NOTES/courses",
        "02 - PROJECTS",
        "03 - AREAS",
        "04 - RESOURCES/topics",
        "04 - RESOURCES/people",
        "04 - RESOURCES/tools",
        "05 - ARCHIVE",
        "06 - SYSTEM/templates",
        "06 - SYSTEM/MOCs",
    ]
    for d in para_dirs:
        (vault_path / d).mkdir(parents=True, exist_ok=True)
    console.print(f"[green]Created vault structure at {vault_path}[/green]")

    # Gather CLAUDE.md answers — question set and template both branch on mode.
    if mode == "personal":
        console.print("\n[bold]Configure your vault intelligence[/bold] (7 questions)\n")
        q1 = click.prompt("1. Primary use for notes", default="writing/decisions/projects/research")
        q2 = click.prompt("2. What do you produce from notes? (e.g. articles, decisions, briefs)",
                          default="articles")
        q3 = click.prompt("3. Active projects right now (comma-separated)", default="")
        q4 = click.prompt("4. Current active decisions or questions (comma-separated)", default="")
        q5 = click.prompt("5. Topics you write about regularly (comma-separated)", default="")
        q6 = click.prompt("6. What makes a note useful for you? (one sentence)",
                          default="A note is useful when it leads to an output.")
        q7 = click.prompt("7. One output goal for the next 90 days", default="")

        claude_md = f"""# Vault intelligence context

## Primary use
{q1}

## Outputs produced from notes
{q2}

## Active projects
{q3 or "(none yet)"}

## Active decisions / open questions
{q4 or "(none yet)"}

## Topics written about regularly
{q5 or "(none yet)"}

## What makes a note useful
{q6}

## 90-day output goal
{q7 or "(not set)"}
"""
    else:
        console.print("\n[bold]Configure your team's vault intelligence[/bold] (8 questions)\n")
        console.print("[dim]The biggest predictor of a shared brain working is an "
                      "empowered champion — someone who can add sources, fix mistakes, "
                      "and grant access without asking permission each time.[/dim]\n")
        s1 = click.prompt("1. What is this shared vault for? (team/project + purpose)")
        s_champion = click.prompt(
            "2. Who is the champion — empowered to act on this vault without "
            "approval for every change?"
        )
        s_contributors = click.prompt(
            "3. Who else writes to this vault? (comma-separated names/roles)", default=""
        )
        s2 = click.prompt(
            "4. What does the team produce from this vault? "
            "(e.g. onboarding docs, decisions, playbooks)"
        )
        s3 = click.prompt("5. Active projects right now (comma-separated)", default="")
        s4 = click.prompt("6. Current active decisions or open questions (comma-separated)",
                          default="")
        s6 = click.prompt("7. What makes a note useful for the team? (one sentence)",
                          default="A note is useful when someone else on the team can act on it.")
        s_escalation = click.prompt(
            "8. If the brain gives a wrong or outdated answer, who corrects it?",
            default=s_champion,
        )

        claude_md = f"""# Vault intelligence context — shared team brain

## Team Charter
Purpose: {s1}
Champion: {s_champion} — empowered to add sources, grant access, and correct
the vault without requiring approval for every change. A champion who needs
sign-off for each decision starves the vault of the signal it needs to become
useful.
Contributors: {s_contributors or "(just the champion, for now)"}
Escalation: if the brain gives a wrong or outdated answer, {s_escalation} corrects it.

## Attribution convention
Every note should carry a `contributor:` frontmatter field naming who wrote
it. This is a convention, not enforced access control — anyone who can open
this vault folder can read and write everything in it. Attribution exists so
contributions are traceable, not to restrict who can do what.

## What this vault produces
{s2}

## Active projects
{s3 or "(none yet)"}

## Active decisions / open questions
{s4 or "(none yet)"}

## What makes a note useful
{s6}

## How this vault gets sharper
Context does not live only in documents someone sat down to write. It lives
in the correction to a wrong answer, the exception to a policy, the "we don't
do it that way here" comment. Do not treat this vault as a wiki migration —
treat every correction as input. `synaptic review` surfaces rejection
patterns; fold repeat rejections into "What makes a note useful" above rather
than leaving them as one-off overrides.
"""
    claude_md_path = vault_path / "06 - SYSTEM" / "CLAUDE.md"
    claude_md_path.write_text(claude_md, encoding="utf-8")
    console.print(f"[green]CLAUDE.md created at {claude_md_path}[/green]")

    # Write template files from the packaged canonical set (single source of
    # truth: synaptic/templates/, kept byte-identical to examples/vault by tests).
    template_dir = vault_path / "06 - SYSTEM" / "templates"
    template_names = [
        "daily.md", "meeting.md", "book.md", "project.md",
        "area.md", "resource.md", "weekly-review.md",
    ]
    for name in template_names:
        content = _load_template(name)
        if mode == "shared":
            content = _inject_contributor(content)
        (template_dir / name).write_text(content, encoding="utf-8")
    console.print(
        f"[green]{len(template_names)} template files created in {template_dir}[/green]"
    )

    # Write / update config.yaml.
    root = ctx.obj["root"] or Path.cwd()
    config_dir = root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_yaml_path = config_dir / "config.yaml"
    example_path = config_dir / "config.example.yaml"

    if example_path.exists():
        import yaml as _yaml
        data = _yaml.safe_load(example_path.read_text(encoding="utf-8")) or {}
    else:
        data = {}

    data.setdefault("vault", {})["path"] = str(vault_path)

    if mode == "shared":
        # Multiple people's context mixes in a shared vault, so require explicit
        # opt-in before anything reaches a brief or recommendation, rather than
        # trusting a single-person default like "professional."
        privacy_cfg = data.setdefault("privacy", {})
        privacy_cfg["default_level"] = "personal_sensitive"
        privacy_cfg["brief_allowed_levels"] = ["public"]

    import yaml as _yaml
    config_yaml_path.write_text(
        _yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    console.print(f"[green]config.yaml updated: vault.path = {vault_path}[/green]")
    if mode == "shared":
        console.print(
            "[yellow]Privacy defaults tightened for shared mode: only notes "
            "marked 'privacy: public' reach a brief or recommendation by "
            "default. Add 'professional' back to brief_allowed_levels in "
            "config.yaml if the team wants that tier included too.[/yellow]"
        )

    console.print("\n[bold]Vault created. Next steps:[/bold]")
    console.print("  1) synaptic doctor")
    console.print("  2) synaptic scan")
    console.print("  3) synaptic health")
    if mode == "shared":
        console.print(
            f"\n[dim]Champion: {s_champion}. Reminder: this is a shared folder "
            "with no per-file access control — anyone who can open it can read "
            "and write everything. Treat it like a trusted synced team folder, "
            "not a permissioned system.[/dim]"
        )


@main.command()
@click.option("--force", is_flag=True, default=False,
              help="Re-embed all entities, even those already embedded.")
@click.pass_context
def embed(ctx, force):
    """Compute and store embeddings for all vault entities."""
    from rich.progress import Progress

    cfg, store, router, _ = _ctx(ctx.obj["root"])

    if not router.available_for("embeddings"):
        console.print("[yellow]Embedding model not available.[/yellow]")
        console.print("Pull a model with:  ollama pull nomic-embed-text")
        store.close()
        return

    cfg.assert_external_allowed(cfg.provider_for_task("embeddings"))

    from .obsidian.vault import Vault
    vault = Vault(cfg.vault_path)
    entities = vault.load()

    already = {eid for eid, _ in store.all_embeddings()}
    to_embed = entities if force else [e for e in entities if e.id not in already]
    skipped = len(entities) - len(to_embed)

    if not to_embed:
        console.print(f"[green]All {len(entities)} entities already embedded.[/green]")
        store.close()
        return

    # Determine model name for storage.
    pc = cfg.provider_for_task("embeddings")
    model_name = pc.embedding_model or "unknown"

    computed = 0
    errors = 0
    with Progress(console=console) as progress:
        task = progress.add_task("Embedding...", total=len(to_embed))
        for entity in to_embed:
            try:
                vecs = router.embed("embeddings", [entity.searchable_text()])
                if vecs:
                    store.upsert_embedding(entity.id, model_name, vecs[0])
                    computed += 1
            except Exception as exc:
                console.print(f"[red]Error embedding {entity.title}: {exc}[/red]")
                errors += 1
            progress.advance(task)

    console.print(
        f"[green]{computed} embedding(s) computed.[/green]  "
        f"{skipped} skipped (already current).  "
        + (f"[red]{errors} error(s).[/red]" if errors else "")
    )
    store.close()


@main.command()
@click.argument("question")
@click.option("--top-k", default=6, show_default=True,
              help="Number of notes to use as context.")
@click.option("--save/--no-save", default=False,
              help="Save the answer as a new note in 04 - RESOURCES/topics/.")
@click.pass_context
def query(ctx, question, top_k, save):
    """Answer a question using your vault as context."""
    from .search import keyword_search, semantic_search

    cfg, store, router, _ = _ctx(ctx.obj["root"])

    # Gather relevant notes.
    context_notes: list[tuple[str, str, str]] = []  # (title, body, entity_id)
    embeddings = store.all_embeddings()

    if embeddings and router.available_for("embeddings"):
        try:
            cfg.assert_external_allowed(cfg.provider_for_task("embeddings"))
            vecs = router.embed("embeddings", [question])
            if vecs:
                hits = semantic_search(store, vecs[0], top_k=top_k, min_score=0.2)
                for entity_id, _ in hits:
                    row = store.get_entity(entity_id)
                    if row:
                        context_notes.append((row["title"], row["body"] or "", row["id"]))
                        store.log_access(entity_id, accessed_via="query", query_text=question)
        except Exception:
            context_notes = []

    if not context_notes:
        _, entities = _load_entities(cfg, store)
        kw_hits = keyword_search(entities, question, top_k=top_k)
        for entity, _ in kw_hits:
            context_notes.append((entity.title, entity.body, entity.id))
            store.log_access(entity.id, accessed_via="query:keyword", query_text=question)

    if not context_notes:
        console.print("[yellow]No relevant notes found.[/yellow]")
        store.close()
        return

    source_titles = [t for t, _, _ in context_notes]
    console.print(f"[dim]Using {len(context_notes)} note(s) as context:[/dim]")
    for t in source_titles:
        console.print(f"  • {t}")
    console.print()

    answer = ""
    if router.available_for("strategic_queries"):
        try:
            cfg.assert_external_allowed(cfg.provider_for_task("strategic_queries"))
            from .llm.base import ChatMessage
            context_blob = "\n\n".join(
                f"### {title}\n{body[:1500]}" for title, body, _ in context_notes
            )
            system = (
                "You are a personal knowledge assistant. Answer the question using ONLY "
                "the provided vault notes. Cite the note titles you used in your answer. "
                "If the notes don't have enough information, say so clearly."
            )
            user = (
                f"Question: {question}\n\n"
                f"Vault notes:\n{context_blob}\n\n"
                "Provide a clear, concise answer with citations."
            )
            answer = router.chat(
                "strategic_queries",
                [ChatMessage("system", system), ChatMessage("user", user)],
            )
            console.print(answer)
        except PermissionError as exc:
            console.print(f"[red]{exc}[/red]")
        except Exception as exc:
            console.print(f"[yellow]LLM error: {exc}[/yellow]")
            answer = ""
    else:
        console.print("[yellow]LLM not available. Most relevant notes:[/yellow]")
        for i, (title, _, _) in enumerate(context_notes, 1):
            console.print(f"  {i}. {title}")

    if save and answer:
        slug = re.sub(r"[^a-z0-9]+", "-", question.lower())[:50].strip("-")
        fname = f"{datetime.now().strftime('%Y-%m-%d')}-resource-query-{slug}.md"
        save_dir = cfg.vault_path / "04 - RESOURCES" / "topics"
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / fname
        sources_block = "\n".join(f"- [[{t}]]" for t in source_titles)
        note_content = (
            f"---\ntype: resource\ndate: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"query: \"{question}\"\nstatus: active\ntags: [query-result]\n---\n\n"
            f"# Query: {question}\n\n{answer}\n\n"
            f"## Sources\n{sources_block}\n"
        )
        save_path.write_text(note_content, encoding="utf-8")
        console.print(f"\n[green]Answer saved to {save_path.name}[/green]")

    store.close()


@main.command()
@click.argument("note_title")
@click.option("--context", "context_text", default="",
              help="Describe where/how this note contributed (e.g. 'used in article draft').")
@click.option("--type", "output_type", default="general",
              help="Output type (e.g. article, decision, brief, general).")
@click.pass_context
def contributed(ctx, note_title, context_text, output_type):
    """Log that a note contributed to an output."""
    cfg, store, _, _ = _ctx(ctx.obj["root"])

    # Look up by title in DB.
    row = store.find_entity_by_title(note_title)
    if row:
        note_id = row["id"]
        resolved_title = row["title"]
    else:
        # rglob fallback.
        found = None
        if cfg.vault_path.exists():
            for p in cfg.vault_path.rglob("*.md"):
                if p.stem.lower() == note_title.lower():
                    found = p
                    break
        if found is None:
            console.print(f"[red]Note not found: {note_title}[/red]")
            store.close()
            return
        import hashlib
        rel = found.relative_to(cfg.vault_path).as_posix()
        note_id = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:16]
        resolved_title = found.stem

    store.log_contribution(note_id, resolved_title, context_text, output_type)
    label = f"[{context_text}]" if context_text else ""
    console.print(f"[green]Logged:[/green] {resolved_title} contributed to {label or output_type}")
    store.close()


@main.command(name="contribution-report")
@click.pass_context
def contribution_report(ctx):
    """Show a report of which notes have contributed to outputs."""
    cfg, store, _, _ = _ctx(ctx.obj["root"])
    report = store.contribution_report()

    total = report["total_contributions"]
    top_notes = report["top_notes"]
    never = report["never_contributed"]

    console.print(f"\n[bold]Contribution report[/bold]")
    console.print(f"Total contribution events: [cyan]{total}[/cyan]\n")

    if not top_notes:
        console.print("[yellow]No contributions logged yet.[/yellow]")
        console.print(
            "\nUse [bold]synaptic contributed <note title>[/bold] to log when a note "
            "contributes to an output (article, decision, brief, etc.)."
        )
        store.close()
        return

    table = Table(title="Top contributed notes")
    table.add_column("Note title", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Last used")
    for n in top_notes:
        table.add_row(n["title"], str(n["count"]), n["last_used"] or "")
    console.print(table)

    if never:
        console.print(f"\n[dim]{len(never)} note(s) have never contributed to an output.[/dim]")
    store.close()


@main.command()
@click.pass_context
def mcp(ctx):
    """Start the Synaptic MCP stdio server for use with Claude Code."""
    import asyncio
    import sys

    try:
        from .mcp.server import run_server
        _mcp_available = True
    except ImportError:
        _mcp_available = False

    try:
        import mcp as _mcp_pkg  # noqa: F401
        pkg_available = True
    except ImportError:
        pkg_available = False

    if not pkg_available:
        console.print("[red]The 'mcp' package is not installed.[/red]")
        console.print("Install it with:  pip install mcp")
        console.print("\nThen add this to your Claude Code settings (.claude/settings.json):")
        console.print(
            '{\n  "mcpServers": {\n    "synaptic": {\n'
            '      "command": "synaptic",\n'
            '      "args": ["mcp"]\n'
            '    }\n  }\n}'
        )
        return

    root = ctx.obj["root"]

    print(
        "Synaptic MCP server starting...\n"
        "\nAdd this to your Claude Code settings (.claude/settings.json):\n"
        '{\n  "mcpServers": {\n    "synaptic": {\n'
        '      "command": "synaptic",\n'
        '      "args": ["mcp"]\n'
        '    }\n  }\n}',
        file=sys.stderr,
    )
    asyncio.run(run_server(root))


if __name__ == "__main__":
    main()
