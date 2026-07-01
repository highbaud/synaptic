"""Generate a privacy-safe contact brief for a person.

Pipeline: gather the person note + related interaction notes -> drop any source
whose privacy level is not brief-allowed -> redact remaining text (defense in
depth) -> build the brief from safe evidence + approved tags. Only safe,
source-backed material reaches the output; no invented CRM facts.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..config import Config
from ..db.store import Store
from ..llm.base import ChatMessage, LLMError
from ..llm.factory import LLMRouter
from ..obsidian.vault import Entity
from ..privacy.classifier import PrivacyClassifier


@dataclass
class SafeEvidence:
    source: str
    text: str
    level: str


@dataclass
class Brief:
    name: str
    markdown: str
    tags: list[str] = field(default_factory=list)
    used_sources: list[str] = field(default_factory=list)
    excluded_sources: list[tuple[str, str]] = field(default_factory=list)  # (name, level)


class BriefGenerator:
    def __init__(self, config: Config, store: Store, router: LLMRouter,
                 classifier: PrivacyClassifier):
        self.config = config
        self.store = store
        self.router = router
        self.classifier = classifier
        self.allowed = config.privacy.brief_allowed_levels

    def _related(self, person: Entity, entities: list[Entity]) -> list[Entity]:
        """Interactions/notes that reference this person by title or wikilink."""
        name = person.title.lower()
        out: list[Entity] = []
        for e in entities:
            if e.id == person.id or e.type in ("topic", "person", "company"):
                continue
            if name in e.body.lower() or any(name in w.lower() for w in e.wikilinks):
                out.append(e)
        return out

    def _collect_safe(self, sources: list[Entity]) -> tuple[list[SafeEvidence], list[tuple[str, str]]]:
        safe: list[SafeEvidence] = []
        excluded: list[tuple[str, str]] = []
        for e in sources:
            verdict = self.classifier.classify(e.searchable_text(), e.declared_privacy)
            if verdict.level not in self.allowed:
                excluded.append((e.path.name, verdict.level))
                continue
            safe.append(SafeEvidence(
                source=e.path.name,
                text=self.classifier.redact(e.body).strip(),
                level=verdict.level,
            ))
        return safe, excluded

    def generate(self, person: Entity, entities: list[Entity]) -> Brief:
        related = self._related(person, entities)
        safe, excluded = self._collect_safe([person, *related])
        tags = self.store.approved_tags_for(person.id)

        if self.router.available_for("briefs"):
            try:
                md = self._llm_brief(person, safe, tags)
            except LLMError:
                md = self._template_brief(person, safe, tags)
        else:
            md = self._template_brief(person, safe, tags)

        return Brief(
            name=person.title,
            markdown=md,
            tags=tags,
            used_sources=[s.source for s in safe],
            excluded_sources=excluded,
        )

    def _llm_brief(self, person: Entity, safe: list[SafeEvidence], tags: list[str]) -> str:
        fm = person.frontmatter
        evidence_blob = "\n\n".join(f"### {s.source} ({s.level})\n{s.text}" for s in safe)
        system = (
            "You write concise, professional contact briefs for a CRM. Use ONLY "
            "the provided evidence. Never invent facts, employers, or interests. "
            "If a section has no support, write 'No information available.' Do not "
            "include anything personal, sensitive, embarrassing, or NSFW."
        )
        user = (
            f"Person: {person.title}\n"
            f"Company: {fm.get('company','')}  Role: {fm.get('role','')}\n"
            f"Approved tags: {', '.join(tags) or 'none'}\n"
            f"Relationship strength: {fm.get('relationship_strength','')}  "
            f"Last contacted: {fm.get('last_contacted','')}\n\n"
            f"EVIDENCE (only safe sources):\n{evidence_blob or '(none)'}\n\n"
            "Produce markdown with exactly these sections:\n"
            "# Client Brief: <name>\n## Why This Person Matters\n## Relevant Topics\n"
            "## Relationship Context\n## Evidence\n## Suggested Conversation\n"
            "## Follow-Up Actions"
        )
        out = self.router.chat("briefs",
                               [ChatMessage("system", system), ChatMessage("user", user)])
        # Final redaction pass even on model output — defense in depth.
        return self.classifier.redact(out)

    def _template_brief(self, person: Entity, safe: list[SafeEvidence], tags: list[str]) -> str:
        fm = person.frontmatter
        topic_lines = "\n".join(f"- {t}" for t in tags) or "- (no approved tags yet)"
        ev_lines = []
        for s in safe:
            snippet = next((ln.strip() for ln in s.text.splitlines() if ln.strip()), "")
            if snippet:
                ev_lines.append(f"- *{s.source}*: {snippet}")
        evidence = "\n".join(ev_lines) or "- No safe source-backed evidence available."
        company = fm.get("company", "")
        role = fm.get("role", "")
        matters = (f"{person.title}"
                   + (f" — {role}" if role else "")
                   + (f" at {company}" if company else "")
                   + ".") if (role or company) else f"{person.title}."
        rel = []
        if fm.get("relationship_strength"):
            rel.append(f"Relationship strength: {fm['relationship_strength']}.")
        if fm.get("last_contacted"):
            rel.append(f"Last contacted: {fm['last_contacted']}.")
        rel_text = " ".join(rel) or "No relationship metadata recorded."
        return (
            f"# Client Brief: {person.title}\n\n"
            f"## Why This Person Matters\n{matters}\n\n"
            f"## Relevant Topics\n{topic_lines}\n\n"
            f"## Relationship Context\n{rel_text}\n\n"
            f"## Evidence\n{evidence}\n\n"
            f"## Suggested Conversation\n"
            f"- Pick up threads from the topics above.\n\n"
            f"## Follow-Up Actions\n"
            f"- Review notes and schedule next touchpoint.\n"
        )
