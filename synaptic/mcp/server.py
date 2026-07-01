"""Synaptic MCP server — vault intelligence as Claude-callable tools."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    FastMCP = None  # type: ignore[assignment,misc]

# Module-level singletons; initialised by setup() on first tool call.
_cfg: Any = None
_store: Any = None
_router: Any = None
_vault: Any = None
_mcp: Any = None
_root: Path | None = None
_setup_done = False


def setup(root: Path | None = None) -> None:
    """Lazily initialise config, store, router, and vault."""
    global _cfg, _store, _router, _vault, _root, _setup_done
    if _setup_done:
        return
    _root = root
    from ..config import load_config
    from ..db.store import Store
    from ..llm.factory import LLMRouter
    from ..obsidian.vault import Vault

    _cfg = load_config(root)
    _store = Store(_cfg.db_path)
    _router = LLMRouter(_cfg)
    try:
        _vault = Vault(_cfg.vault_path)
    except FileNotFoundError:
        _vault = None
    _setup_done = True


# Build the FastMCP app at import time (but tools are no-ops until setup() runs).
if _MCP_AVAILABLE:
    mcp = FastMCP("Synaptic")
else:
    mcp = None  # type: ignore[assignment]


def _get_mcp():
    """Return the FastMCP instance, raising ImportError if unavailable."""
    if not _MCP_AVAILABLE or mcp is None:
        raise ImportError(
            "The 'mcp' package is not installed. "
            "Install it with: pip install 'synaptic[mcp]'"
        )
    return mcp


# --------------------------------------------------------------------------- #
# Tool definitions                                                             #
# --------------------------------------------------------------------------- #

if _MCP_AVAILABLE and mcp is not None:

    @mcp.tool()
    def get_active_context() -> str:
        """Read the vault's CLAUDE.md and return its contents for active context."""
        setup(_root)
        if _cfg is None or _vault is None:
            return "Vault not initialised."

        # Try the canonical path first.
        claude_path = _cfg.vault_path / "06 - SYSTEM" / "CLAUDE.md"
        if not claude_path.exists():
            # Fall back to rglob search.
            matches = list(_cfg.vault_path.rglob("CLAUDE.md"))
            if not matches:
                return "No CLAUDE.md found in the vault."
            claude_path = matches[0]

        try:
            content = claude_path.read_text(encoding="utf-8")
            return f"# Active context from {claude_path.name}\n\n{content}"
        except Exception as exc:
            return f"Error reading CLAUDE.md: {exc}"

    @mcp.tool()
    def search_vault(query: str, top_k: int = 8) -> str:
        """Search vault notes using semantic search (with keyword fallback).

        Returns a markdown list of matching notes with title, path, and excerpt.
        """
        setup(_root)
        if _cfg is None:
            return "Vault not initialised."

        from ..search import keyword_search, semantic_search

        results: list[tuple[str, str, str]] = []  # (title, rel_path, excerpt)

        # Try semantic search first if embeddings exist.
        embeddings = _store.all_embeddings() if _store else []
        if embeddings and _router and _router.available_for("embeddings"):
            try:
                vecs = _router.embed("embeddings", [query])
                if vecs:
                    hits = semantic_search(_store, vecs[0], top_k=top_k, min_score=0.3)
                    for entity_id, score in hits:
                        row = _store.get_entity(entity_id)
                        if row:
                            path = Path(row["path"])
                            rel = path.relative_to(_cfg.vault_path).as_posix() if path.is_absolute() else str(path)
                            try:
                                fm_data = json.loads(row["frontmatter"]) if row["frontmatter"] else {}
                            except Exception:
                                fm_data = {}
                            desc = str(fm_data.get("description", "")).strip()
                            body = row["body"] or ""
                            excerpt = desc or body.replace("\n", " ").strip()[:300]
                            results.append((row["title"], rel, excerpt))
                    _store.log_access(entity_id, accessed_via="search_vault", query_text=query)
            except Exception:
                results = []

        # Keyword fallback if no semantic results.
        if not results and _vault:
            try:
                entities = _vault.load()
            except Exception:
                entities = []
            kw_hits = keyword_search(entities, query, top_k=top_k)
            for entity, _ in kw_hits:
                rel = entity.path.relative_to(_cfg.vault_path).as_posix()
                excerpt = entity.body.replace("\n", " ").strip()[:300]
                results.append((entity.title, rel, excerpt))
                if _store:
                    _store.log_access(entity.id, accessed_via="search_vault:keyword",
                                      query_text=query)

        if not results:
            return f"No results found for: {query}"

        lines = [f"## Search results for: {query}\n"]
        for i, (title, rel_path, excerpt) in enumerate(results, 1):
            lines.append(f"### {i}. {title}")
            lines.append(f"**Path:** `{rel_path}`")
            if excerpt:
                lines.append(f"> {excerpt}")
            lines.append("")
        return "\n".join(lines)

    @mcp.tool()
    def get_note(title: str) -> str:
        """Return the full content of a note by title."""
        setup(_root)
        if _cfg is None:
            return "Vault not initialised."

        # DB lookup first.
        if _store:
            row = _store.find_entity_by_title(title)
            if row:
                path = Path(row["path"])
                if path.exists():
                    _store.log_access(row["id"], accessed_via="get_note")
                    return path.read_text(encoding="utf-8")

        # Fall back to rglob.
        if _cfg.vault_path.exists():
            for path in _cfg.vault_path.rglob("*.md"):
                if path.stem.lower() == title.lower():
                    return path.read_text(encoding="utf-8")

        return f"Note not found: {title}"

    def _try_moc_navigation(question: str, top_k: int) -> list[tuple[str, str]]:
        """Navigate via a MOC index file when one is a strong topic match.

        Checks 06 - SYSTEM/MOCs/ for an index note whose filename shares real
        topic words with the question, and if found loads it plus its linked
        notes as primary context. A MOC is only accepted on a strong match
        (two+ shared content words, or a single-word topical MOC fully matched)
        so an incidental shared word cannot hijack retrieval away from semantic
        search. Returns an empty list when no MOC is a confident match.
        """
        if _cfg is None:
            return []
        moc_folder = _cfg.vault_path / "06 - SYSTEM" / "MOCs"
        if not moc_folder.exists():
            return []
        moc_files = list(moc_folder.glob("*.md"))
        if not moc_files:
            return []

        from ..search import content_tokens

        question_tokens = content_tokens(question)
        if not question_tokens:
            return []

        best_moc: Path | None = None
        best_overlap = 0
        for moc_path in moc_files:
            stem_tokens = content_tokens(moc_path.stem)
            if not stem_tokens:
                continue  # a generic index name (notes/index/moc) is not a topic
            overlap = len(stem_tokens & question_tokens)
            # Strong match only: 2+ shared topic words, or a single-word topical
            # MOC whose one word the question contains.
            strong = overlap >= 2 or (len(stem_tokens) == 1 and overlap == 1)
            if strong and overlap > best_overlap:
                best_overlap = overlap
                best_moc = moc_path

        if best_moc is None:
            return []

        from ..obsidian.parser import parse_note
        try:
            parsed = parse_note(best_moc)
        except Exception:
            return []

        # parse_note already read the file; reuse its raw content instead of a
        # second read_text of the same path.
        moc_text = parsed.body or best_moc.read_text(encoding="utf-8")

        context: list[tuple[str, str]] = [(best_moc.stem, moc_text)]
        seen: set[str] = {best_moc.stem.lower()}
        for wikilink in parsed.wikilinks[: top_k * 2]:
            if len(context) >= top_k + 1:
                break
            if wikilink.lower() in seen:
                continue
            seen.add(wikilink.lower())
            row = _store.find_entity_by_title(wikilink) if _store else None
            if row:
                context.append((row["title"], row["body"] or ""))

        return context if len(context) > 1 else []

    def _try_frontmatter_narrow(question: str) -> set[str] | None:
        """Narrow candidate entities by matching frontmatter tags/type/project
        against real topic words in the question. Returns a set of entity ids,
        or None when there is no confident narrowing signal (caller then
        searches the full vault).

        Matching runs on content words only: generic type/status values
        ("daily", "active", "project") are stopwords, so an incidental overlap
        on them cannot narrow the vault down to the wrong slice.
        """
        if _store is None:
            return None

        from ..search import content_tokens

        question_tokens = content_tokens(question)
        if not question_tokens:
            return None

        rows = _store.all_entities()
        matched: set[str] = set()
        for row in rows:
            try:
                fm = json.loads(row["frontmatter"]) if row["frontmatter"] else {}
            except Exception:
                continue
            signal_parts: list[str] = []
            tags = fm.get("tags") or []
            if isinstance(tags, list):
                signal_parts.extend(str(t) for t in tags)
            elif tags:
                signal_parts.append(str(tags))
            for key in ("type", "project", "status"):
                v = fm.get(key)
                if v:
                    signal_parts.append(str(v))

            signal_tokens = content_tokens(" ".join(signal_parts))
            if signal_tokens & question_tokens:
                matched.add(row["id"])

        # Only narrow when it excludes something without emptying the vault.
        if matched and len(matched) < len(rows):
            return matched
        return None

    @mcp.tool()
    def query_vault(question: str, top_k: int = 6) -> str:
        """Answer a question using the vault as context.

        Checks MOC index files first (compiled knowledge), then frontmatter-
        narrowed semantic search, then keyword search. If a narrowed pass finds
        nothing, retries against the full vault so a wrong narrow never hides an
        answer. Synthesises via LLM citing the sources used, or returns a
        relevance list if no LLM is available.
        """
        setup(_root)
        if _cfg is None:
            return "Vault not initialised."

        from ..search import keyword_search, semantic_search

        def _gather(candidate_ids: set[str] | None) -> list[tuple[str, str]]:
            """Semantic then keyword search, optionally restricted to candidate_ids."""
            found: list[tuple[str, str]] = []
            if _store and _router and _router.available_for("embeddings") \
                    and _store.all_embeddings():
                try:
                    vecs = _router.embed("embeddings", [question])
                    if vecs:
                        hits = semantic_search(
                            _store, vecs[0], top_k=top_k, min_score=0.2,
                            candidate_ids=candidate_ids,
                        )
                        for entity_id, _ in hits:
                            row = _store.get_entity(entity_id)
                            if row:
                                found.append((row["title"], row["body"] or ""))
                except Exception:
                    found = []
            if not found and _vault:
                try:
                    entities = _vault.load()
                except Exception:
                    entities = []
                if candidate_ids is not None:
                    entities = [e for e in entities if e.id in candidate_ids]
                for entity, _ in keyword_search(entities, question, top_k=top_k):
                    found.append((entity.title, entity.body))
            return found

        # Step 1: a strongly-matching MOC index answers from compiled knowledge.
        context_notes = _try_moc_navigation(question, top_k)

        # Step 2: frontmatter-narrowed search. If narrowing found nothing, fall
        # back to the full vault so a wrong narrow can never hide the answer.
        if not context_notes:
            narrowed_ids = _try_frontmatter_narrow(question)
            context_notes = _gather(narrowed_ids)
            if not context_notes and narrowed_ids is not None:
                context_notes = _gather(None)

        if not context_notes:
            return f"No relevant notes found for: {question}"

        # LLM synthesis.
        if _router and _router.available_for("strategic_queries"):
            from ..llm.base import ChatMessage
            context_blob = "\n\n".join(
                f"### {title}\n{body[:1500]}" for title, body in context_notes
            )
            system = (
                "You are a personal knowledge assistant. Answer the question using ONLY "
                "the provided vault notes. Cite the note titles you used. "
                "If the notes don't contain enough information, say so."
            )
            user = (
                f"Question: {question}\n\n"
                f"Vault notes:\n{context_blob}\n\n"
                "Provide a clear, concise answer with citations."
            )
            try:
                return _router.chat(
                    "strategic_queries",
                    [ChatMessage("system", system), ChatMessage("user", user)],
                )
            except Exception:
                pass  # fall through to the list fallback

        # Fallback: return the list of most relevant note titles.
        titles = [t for t, _ in context_notes]
        lines = [f"Most relevant notes for: {question}\n"]
        for i, t in enumerate(titles, 1):
            lines.append(f"{i}. {t}")
        return "\n".join(lines)

    @mcp.tool()
    def find_connections(note_title: str, top_k: int = 5) -> str:
        """Find notes most connected to the given note via semantic similarity or wikilinks."""
        setup(_root)
        if _cfg is None:
            return "Vault not initialised."

        from ..search import semantic_search

        # Locate the target note.
        target_row = _store.find_entity_by_title(note_title) if _store else None
        target_entity = None
        target_path: Path | None = None

        if target_row:
            target_path = Path(target_row["path"])
            target_id = target_row["id"]
        else:
            # rglob fallback.
            target_path = None
            target_id = None
            if _cfg.vault_path.exists():
                for p in _cfg.vault_path.rglob("*.md"):
                    if p.stem.lower() == note_title.lower():
                        target_path = p
                        break
            if target_path is None:
                return f"Note not found: {note_title}"

        # Try semantic connection via stored embedding.
        if target_id and _store:
            vec = _store.get_embedding(target_id)
            if vec:
                hits = semantic_search(_store, vec, top_k=top_k + 1, min_score=0.2)
                # Exclude self.
                hits = [(eid, score) for eid, score in hits if eid != target_id][:top_k]
                if hits:
                    if _router and _router.available_for("strategic_queries"):
                        from ..llm.base import ChatMessage
                        note_list = []
                        for eid, score in hits:
                            row = _store.get_entity(eid)
                            if row:
                                note_list.append(
                                    f"- **{row['title']}** (similarity {score:.2f})"
                                )
                        system = (
                            "You are a knowledge graph assistant. Briefly describe why these "
                            "notes are connected to the given note (1-2 sentences each)."
                        )
                        user = (
                            f"Target note: {note_title}\n\n"
                            f"Connected notes:\n" + "\n".join(note_list)
                        )
                        try:
                            return _router.chat(
                                "strategic_queries",
                                [ChatMessage("system", system), ChatMessage("user", user)],
                            )
                        except Exception:
                            pass
                    # Plain list fallback.
                    lines = [f"## Notes connected to: {note_title}\n"]
                    for eid, score in hits:
                        row = _store.get_entity(eid) if _store else None
                        if row:
                            lines.append(f"- **{row['title']}** (similarity {score:.2f})")
                    return "\n".join(lines)

        # Wikilink overlap fallback.
        from ..obsidian.parser import parse_note

        if target_path is None or not target_path.exists():
            return f"Could not load note: {note_title}"

        try:
            target_parsed = parse_note(target_path)
        except Exception as exc:
            return f"Error reading note: {exc}"

        target_links = {w.lower() for w in target_parsed.wikilinks}
        if not target_links and _vault:
            return f"No connections found for: {note_title}"

        scored: list[tuple[str, int]] = []
        if _vault:
            try:
                entities = _vault.load()
            except Exception:
                entities = []
            for entity in entities:
                if entity.title.lower() == note_title.lower():
                    continue
                overlap = len({w.lower() for w in entity.wikilinks} & target_links)
                if overlap > 0:
                    scored.append((entity.title, overlap))

        scored.sort(key=lambda t: t[1], reverse=True)
        top = scored[:top_k]

        if not top:
            return f"No connections found for: {note_title}"

        lines = [f"## Notes connected to: {note_title} (by wikilink overlap)\n"]
        for title, count in top:
            lines.append(f"- **{title}** ({count} shared link{'s' if count > 1 else ''})")
        return "\n".join(lines)

    @mcp.tool()
    def vault_health() -> str:
        """Return a brief vault health summary (inbox size, archive count, total notes)."""
        setup(_root)
        if _cfg is None or not _cfg.vault_path.exists():
            return "Vault not found or not initialised."

        vault_path = _cfg.vault_path
        all_md = [
            p for p in vault_path.rglob("*.md")
            if not any(part.startswith(".") for part in p.relative_to(vault_path).parts)
        ]
        total = len(all_md)

        inbox_count = 0
        archive_count = 0
        for p in all_md:
            parts_lower = [part.lower() for part in p.relative_to(vault_path).parts]
            parts_clean = [
                part.split(" - ")[-1].strip() if " - " in part else part
                for part in parts_lower
            ]
            if "inbox" in parts_clean or "00 - inbox" in parts_lower:
                inbox_count += 1
            elif "archive" in parts_clean or "05 - archive" in parts_lower:
                archive_count += 1

        lines = [
            "## Vault health summary",
            "",
            f"- **Total notes:** {total}",
            f"- **INBOX:** {inbox_count} note{'s' if inbox_count != 1 else ''}",
            f"- **Archive:** {archive_count} note{'s' if archive_count != 1 else ''}",
            "",
            "> Run `synaptic health` for a full health report with frontmatter and link analysis.",
        ]
        if inbox_count > 10:
            lines.insert(3, f"- ⚠ INBOX is large — consider processing notes")
        return "\n".join(lines)

    @mcp.tool()
    def list_notes(note_type: str = "", status: str = "") -> str:
        """List vault notes, optionally filtered by type and/or status (cap: 50).

        Parameters
        ----------
        note_type:
            Filter by frontmatter ``type`` field (e.g. ``person``, ``project``).
            Empty string returns all types.
        status:
            Filter by frontmatter ``status`` field (e.g. ``active``, ``review``).
            Empty string returns all statuses.
        """
        setup(_root)
        if _cfg is None:
            return "Vault not initialised."

        if _store is None:
            return "Store not available."

        rows = _store.all_entities()
        matched: list[dict] = []
        for row in rows:
            fm = {}
            try:
                fm = json.loads(row["frontmatter"]) if row["frontmatter"] else {}
            except Exception:
                pass

            row_type = (fm.get("type") or row["type"] or "").lower()
            row_status = str(fm.get("status", "")).lower()

            if note_type and row_type != note_type.lower():
                continue
            if status and row_status != status.lower():
                continue

            matched.append({
                "title": row["title"],
                "type": row_type,
                "status": row_status,
                "description": str(fm.get("description", "")).strip(),
                "path": row["path"],
            })
            if len(matched) >= 50:
                break

        if not matched:
            filters = []
            if note_type:
                filters.append(f"type={note_type}")
            if status:
                filters.append(f"status={status}")
            desc = " and ".join(filters) or "any filter"
            return f"No notes found matching {desc}."

        filter_desc = []
        if note_type:
            filter_desc.append(f"type: {note_type}")
        if status:
            filter_desc.append(f"status: {status}")
        header = "## Notes" + (f" ({', '.join(filter_desc)})" if filter_desc else "")

        lines = [header, ""]
        for n in matched:
            status_tag = f" [{n['status']}]" if n["status"] else ""
            type_tag = f" `{n['type']}`" if n["type"] else ""
            desc = f" — {n['description']}" if n["description"] else ""
            lines.append(f"- **{n['title']}**{type_tag}{status_tag}{desc}")

        total = len(rows)
        if total > 50:
            lines.append(f"\n_(showing first 50 of {total} total)_")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Entry points                                                                 #
# --------------------------------------------------------------------------- #

def create_mcp_app(root: Path | None = None):
    """Return the FastMCP app instance (for testing)."""
    global _root
    _root = root
    if not _MCP_AVAILABLE:
        raise ImportError("mcp package not installed")
    return mcp


async def run_server(root: Path | None = None) -> None:
    """Start the MCP stdio server."""
    global _root
    _root = root
    if not _MCP_AVAILABLE or mcp is None:
        raise ImportError(
            "The 'mcp' package is not installed. "
            "Install it with: pip install 'synaptic[mcp]'"
        )
    setup(root)
    await mcp.run_async()
