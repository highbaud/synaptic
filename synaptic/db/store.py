"""SQLite metadata store.

Holds canonical entities, their source references, and AI tag suggestions with
confidence + evidence + privacy-safety + review status. Vector embeddings get
their own table; wiring a real ANN index (sqlite-vec / LanceDB) is a later
milestone, so for the prototype embeddings are optional and unused by default.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id           TEXT PRIMARY KEY,
    type         TEXT NOT NULL,
    title        TEXT NOT NULL,
    path         TEXT NOT NULL,
    privacy_level TEXT NOT NULL,
    frontmatter  TEXT NOT NULL,   -- json
    body         TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tag_suggestions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id    TEXT NOT NULL,
    target_type  TEXT NOT NULL,
    tag          TEXT NOT NULL,
    confidence   REAL NOT NULL,
    privacy_safe INTEGER NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending',  -- pending|approved|rejected
    evidence     TEXT NOT NULL,                    -- json: [{source, quote_or_summary}]
    created_at   TEXT NOT NULL,
    reviewed_at  TEXT,
    UNIQUE(target_id, tag)
);

CREATE TABLE IF NOT EXISTS embeddings (
    entity_id  TEXT PRIMARY KEY,
    model      TEXT NOT NULL,
    vector     TEXT NOT NULL,    -- json float array (prototype; ANN index TBD)
    FOREIGN KEY(entity_id) REFERENCES entities(id)
);

CREATE TABLE IF NOT EXISTS contributions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id     TEXT NOT NULL,
    note_title  TEXT NOT NULL,
    context     TEXT NOT NULL DEFAULT '',
    output_type TEXT NOT NULL DEFAULT 'general',
    logged_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS access_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id   TEXT NOT NULL,
    accessed_via TEXT NOT NULL,
    query_text  TEXT DEFAULT '',
    accessed_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_suggestions_status ON tag_suggestions(status);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_contributions_note ON contributions(note_id);
CREATE INDEX IF NOT EXISTS idx_access_log_entity ON access_log(entity_id);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class TagSuggestion:
    target_id: str
    target_type: str
    tag: str
    confidence: float
    privacy_safe: bool
    evidence: list[dict[str, str]] = field(default_factory=list)
    status: str = "pending"
    id: int | None = None


class Store:
    def __init__(self, db_path: Path):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # --- entities ---------------------------------------------------------
    def upsert_entity(self, *, id: str, type: str, title: str, path: str,
                      privacy_level: str,
                      frontmatter: dict[str, Any], body: str, content_hash: str) -> None:
        self.conn.execute(
            """INSERT INTO entities
               (id,type,title,path,privacy_level,frontmatter,body,content_hash,updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 type=excluded.type, title=excluded.title, path=excluded.path,
                 privacy_level=excluded.privacy_level,
                 frontmatter=excluded.frontmatter, body=excluded.body,
                 content_hash=excluded.content_hash, updated_at=excluded.updated_at""",
            (id, type, title, path, privacy_level,
             json.dumps(frontmatter, default=str), body, content_hash, _now()),
        )
        self.conn.commit()

    def get_entity(self, entity_id: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM entities WHERE id=?", (entity_id,)).fetchone()

    def find_entity_by_title(self, title: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM entities WHERE lower(title)=lower(?) LIMIT 1", (title,)
        ).fetchone()

    def entities_by_type(self, type: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM entities WHERE type=? ORDER BY title", (type,)
        ).fetchall()

    def all_entities(self) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM entities ORDER BY type, title").fetchall()

    # --- tag suggestions --------------------------------------------------
    def add_suggestion(self, s: TagSuggestion) -> None:
        self.conn.execute(
            """INSERT INTO tag_suggestions
               (target_id,target_type,tag,confidence,privacy_safe,status,evidence,created_at)
               VALUES (?,?,?,?,?,?,?,?)
               ON CONFLICT(target_id, tag) DO UPDATE SET
                 confidence=excluded.confidence, privacy_safe=excluded.privacy_safe,
                 evidence=excluded.evidence
               WHERE tag_suggestions.status='pending'""",
            (s.target_id, s.target_type, s.tag, s.confidence, int(s.privacy_safe),
             s.status, json.dumps(s.evidence), _now()),
        )
        self.conn.commit()

    def pending_suggestions(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM tag_suggestions WHERE status='pending' "
            "ORDER BY confidence DESC"
        ).fetchall()

    def set_suggestion_status(self, suggestion_id: int, status: str) -> None:
        self.conn.execute(
            "UPDATE tag_suggestions SET status=?, reviewed_at=? WHERE id=?",
            (status, _now(), suggestion_id),
        )
        self.conn.commit()

    def approved_tags_for(self, target_id: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT tag FROM tag_suggestions WHERE target_id=? AND status='approved' "
            "ORDER BY confidence DESC", (target_id,),
        ).fetchall()
        return [r["tag"] for r in rows]

    def rejection_patterns(self, min_count: int = 3) -> list[dict]:
        """Return tags rejected at least ``min_count`` times, most-rejected first.

        A rejection is implicit signal — the user correcting the system rather
        than writing a preference down on purpose. A tag rejected repeatedly is
        the vault telling you something CLAUDE.md's "Not useful" section
        doesn't say yet.
        """
        rows = self.conn.execute(
            """SELECT tag, COUNT(*) AS cnt, MAX(reviewed_at) AS last_rejected
               FROM tag_suggestions
               WHERE status='rejected'
               GROUP BY tag
               HAVING COUNT(*) >= ?
               ORDER BY cnt DESC""",
            (min_count,),
        ).fetchall()
        return [
            {"tag": r["tag"], "count": r["cnt"], "last_rejected": r["last_rejected"]}
            for r in rows
        ]

    # --- embeddings -------------------------------------------------------
    def upsert_embedding(self, entity_id: str, model: str, vector: list[float]) -> None:
        self.conn.execute(
            """INSERT INTO embeddings (entity_id, model, vector)
               VALUES (?, ?, ?)
               ON CONFLICT(entity_id) DO UPDATE SET
                 model=excluded.model, vector=excluded.vector""",
            (entity_id, model, json.dumps(vector)),
        )
        self.conn.commit()

    def get_embedding(self, entity_id: str) -> list[float] | None:
        row = self.conn.execute(
            "SELECT vector FROM embeddings WHERE entity_id=?", (entity_id,)
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["vector"])

    def all_embeddings(self) -> list[tuple[str, list[float]]]:
        rows = self.conn.execute("SELECT entity_id, vector FROM embeddings").fetchall()
        return [(r["entity_id"], json.loads(r["vector"])) for r in rows]

    # --- access log -------------------------------------------------------
    def log_access(self, entity_id: str, *, accessed_via: str, query_text: str = "") -> None:
        self.conn.execute(
            """INSERT INTO access_log (entity_id, accessed_via, query_text, accessed_at)
               VALUES (?, ?, ?, ?)""",
            (entity_id, accessed_via, query_text, _now()),
        )
        self.conn.commit()

    # --- contributions ----------------------------------------------------
    def log_contribution(
        self,
        note_id: str,
        note_title: str,
        context: str,
        output_type: str = "general",
    ) -> None:
        self.conn.execute(
            """INSERT INTO contributions (note_id, note_title, context, output_type, logged_at)
               VALUES (?, ?, ?, ?, ?)""",
            (note_id, note_title, context, output_type, _now()),
        )
        self.conn.commit()

    def contribution_report(self) -> dict:
        """Return stats: total_contributions, top_notes, never_contributed entity ids."""
        total_row = self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM contributions"
        ).fetchone()
        total = total_row["cnt"] if total_row else 0

        top_rows = self.conn.execute(
            """SELECT note_title, COUNT(*) AS cnt, MAX(logged_at) AS last_used
               FROM contributions
               GROUP BY note_id
               ORDER BY cnt DESC
               LIMIT 20"""
        ).fetchall()
        top_notes = [
            {"title": r["note_title"], "count": r["cnt"], "last_used": r["last_used"]}
            for r in top_rows
        ]

        never_rows = self.conn.execute(
            """SELECT id FROM entities
               WHERE id NOT IN (SELECT DISTINCT note_id FROM contributions)"""
        ).fetchall()
        never_contributed = [r["id"] for r in never_rows]

        return {
            "total_contributions": total,
            "top_notes": top_notes,
            "never_contributed": never_contributed,
        }

    def find_uncontributed(self, since_days: int = 180) -> list:
        """Entities updated within the last since_days days with no contributions."""
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat(
            timespec="seconds"
        )
        rows = self.conn.execute(
            """SELECT * FROM entities
               WHERE updated_at >= ?
                 AND id NOT IN (SELECT DISTINCT note_id FROM contributions)
               ORDER BY updated_at DESC""",
            (cutoff,),
        ).fetchall()
        return list(rows)

    def close(self) -> None:
        self.conn.close()
