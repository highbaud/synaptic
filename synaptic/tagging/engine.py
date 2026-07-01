"""Generate evidence-backed semantic tag suggestions for any entity type.

A topic is just an Obsidian note (`type: topic`) describing a tag in plain
English plus matching rules. The engine scores every other entity against every
topic and emits a TagSuggestion carrying confidence, the evidence that justified
it, source references, and a privacy-safe flag. Suggestions land in the review
queue as `pending` — nothing becomes canonical without human approval.

If a real LLM is routed to `tagging` and reachable, the engine uses it for
nuanced judgments; otherwise it falls back to a deterministic keyword matcher so
the feature always works.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from ..config import Config
from ..db.store import Store, TagSuggestion
from ..llm.base import ChatMessage, LLMError
from ..llm.factory import LLMRouter
from ..obsidian.vault import Entity
from ..privacy.classifier import PrivacyClassifier

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]+")
_STOP = {"the", "and", "for", "with", "people", "companies", "notes",
         "opportunities", "involved", "who", "are", "any", "related", "topics"}


@dataclass
class Topic:
    name: str
    description: str = ""
    applies_to: list[str] = field(default_factory=lambda: ["people", "companies"])
    confidence_threshold: float = 0.6
    exclude: list[str] = field(default_factory=list)
    matching_text: str = ""    # extra body text: Definition / Matching Rules sections

    @classmethod
    def from_entity(cls, e: Entity) -> "Topic":
        fm = e.frontmatter
        body_rules = " ".join(
            e.sections.get(s, "") for s in ("definition", "matching rules", "related topics")
        )
        return cls(
            name=str(fm.get("name", e.title)).lower(),
            description=str(fm.get("description", "")),
            applies_to=fm.get("applies_to") or ["people", "companies"],
            confidence_threshold=float(fm.get("confidence_threshold", 0.6)),
            exclude=fm.get("exclude") or [],
            matching_text=body_rules,
        )

    def keywords(self) -> set[str]:
        text = " ".join([self.name, self.description, self.matching_text]).lower()
        words = {w for w in _WORD_RE.findall(text) if w not in _STOP and len(w) > 2}
        # The topic name's own tokens are the strongest signals.
        words |= {w for w in _WORD_RE.findall(self.name) if len(w) > 2}
        return words

    @property
    def type_singular_map(self) -> dict[str, str]:
        return {"people": "person", "companies": "company",
                "notes": "note", "opportunities": "opportunity",
                "interactions": "interaction"}

    def applies_to_type(self, entity_type: str) -> bool:
        wanted = {self.type_singular_map.get(a, a) for a in self.applies_to}
        return entity_type in wanted


class TagEngine:
    def __init__(self, config: Config, store: Store, router: LLMRouter,
                 classifier: PrivacyClassifier):
        self.config = config
        self.store = store
        self.router = router
        self.classifier = classifier

    def load_topics(self, entities: list[Entity]) -> list[Topic]:
        return [Topic.from_entity(e) for e in entities if e.type == "topic"]

    def suggest_for_entity(self, entity: Entity, topics: list[Topic]) -> list[TagSuggestion]:
        if entity.type == "topic":
            return []
        use_llm = self.router.available_for("tagging")
        out: list[TagSuggestion] = []
        for topic in topics:
            if not topic.applies_to_type(entity.type):
                continue
            sugg = (self._llm_score(entity, topic) if use_llm
                    else self._heuristic_score(entity, topic))
            if sugg is None:
                continue
            floor = max(self.config.tagging_min_confidence, topic.confidence_threshold)
            if sugg.confidence >= floor:
                out.append(sugg)
        return out

    def run(self, entities: list[Entity]) -> int:
        """Score all entities, persist suggestions, return count of new pendings."""
        topics = self.load_topics(entities)
        count = 0
        for e in entities:
            for s in self.suggest_for_entity(e, topics):
                self.store.add_suggestion(s)
                count += 1
        return count

    # --- scoring strategies ----------------------------------------------
    def _heuristic_score(self, entity: Entity, topic: Topic) -> TagSuggestion | None:
        text = entity.searchable_text().lower()
        kw = topic.keywords()
        hits = sorted({k for k in kw if re.search(rf"\b{re.escape(k)}\b", text)})
        if not hits:
            return None
        # Confidence: coverage of the topic's distinctive keywords, capped.
        coverage = len(hits) / max(4, len(kw))
        name_hit = any(re.search(rf"\b{re.escape(t)}\b", text)
                       for t in _WORD_RE.findall(topic.name))
        confidence = min(0.95, 0.45 + coverage + (0.15 if name_hit else 0))
        evidence = self._evidence_lines(entity, hits)
        verdict = self.classifier.classify(entity.searchable_text(), entity.declared_privacy)
        return TagSuggestion(
            target_id=entity.id,
            target_type=entity.type,
            tag=topic.name,
            confidence=round(confidence, 2),
            privacy_safe=verdict.safe_for_brief,
            evidence=evidence or [{"source": entity.path.name,
                                   "quote_or_summary": f"matched: {', '.join(hits)}"}],
        )

    def _llm_score(self, entity: Entity, topic: Topic) -> TagSuggestion | None:
        prompt = (
            "You assign a single semantic tag to a CRM entity based ONLY on the "
            "provided text. Never invent facts. Respond with strict JSON:\n"
            '{"confidence": 0.0-1.0, "evidence": [{"source": str, '
            '"quote_or_summary": str}], "rationale": str}\n'
            "confidence is how strongly the entity matches the tag. evidence must "
            "quote or summarize lines from the text. If it does not match, set "
            "confidence to 0 and evidence to [].\n\n"
            f"TAG: {topic.name}\nTAG DEFINITION: {topic.description}\n"
            f"MATCHING RULES: {topic.matching_text}\n"
            f"EXCLUDE: {'; '.join(topic.exclude)}\n\n"
            f"ENTITY ({entity.type}) — source file '{entity.path.name}':\n"
            f"{entity.searchable_text()[:4000]}"
        )
        try:
            raw = self.router.chat("tagging", [ChatMessage("user", prompt)])
            data = _extract_json(raw)
        except (LLMError, ValueError):
            return self._heuristic_score(entity, topic)
        conf = float(data.get("confidence", 0))
        if conf <= 0:
            return None
        evidence = data.get("evidence") or []
        verdict = self.classifier.classify(entity.searchable_text(), entity.declared_privacy)
        return TagSuggestion(
            target_id=entity.id,
            target_type=entity.type,
            tag=topic.name,
            confidence=round(min(conf, 0.99), 2),
            privacy_safe=verdict.safe_for_brief,
            evidence=[{"source": str(e.get("source", entity.path.name)),
                       "quote_or_summary": str(e.get("quote_or_summary", ""))}
                      for e in evidence][:5],
        )

    def _evidence_lines(self, entity: Entity, hits: list[str]) -> list[dict[str, str]]:
        ev: list[dict[str, str]] = []
        for line in entity.body.splitlines():
            low = line.lower().strip()
            if low and any(h in low for h in hits):
                ev.append({"source": entity.path.name, "quote_or_summary": line.strip()})
            if len(ev) >= 3:
                break
        return ev


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start:end + 1])
