"""Pure-Python semantic + keyword search. No numpy required."""
from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .obsidian.vault import Entity


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def semantic_search(
    store,
    query_vector: list[float],
    top_k: int = 10,
    min_score: float = 0.3,
    candidate_ids: set[str] | None = None,
) -> list[tuple[str, float]]:
    """Return (entity_id, score) pairs from store's embeddings, sorted by score desc.

    Parameters
    ----------
    store:
        A ``Store`` instance that has an ``all_embeddings()`` method.
    query_vector:
        The embedding of the search query.
    top_k:
        Maximum number of results to return.
    min_score:
        Minimum cosine similarity threshold; results below this are dropped.
    candidate_ids:
        If given, restrict scoring to embeddings whose entity id is in this set.
        Used to narrow the search space (e.g. by frontmatter match) before
        semantic reranking, so a large vault searches only the relevant slice.
    """
    embeddings = store.all_embeddings()  # [(entity_id, vector)]
    if candidate_ids is not None:
        embeddings = [(eid, vec) for eid, vec in embeddings if eid in candidate_ids]
    scored: list[tuple[str, float]] = []
    for entity_id, vector in embeddings:
        score = cosine_similarity(query_vector, vector)
        if score >= min_score:
            scored.append((entity_id, score))
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:top_k]


# --------------------------------------------------------------------------- #
# Keyword search                                                               #
# --------------------------------------------------------------------------- #

_WORD_RE = re.compile(r"[a-zA-Z0-9']+")


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


# Function words plus generic vault/index words that must not drive structural
# matching. A question sharing only "what"/"my"/"notes" with a MOC filename or a
# note's frontmatter is not a real topic match — matching on these produces the
# false hits that let one MOC hijack every query.
STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "do", "does", "did", "what",
    "which", "who", "whom", "how", "when", "where", "why", "i", "me", "my",
    "we", "our", "you", "your", "it", "its", "this", "that", "these", "those",
    "about", "know", "tell", "show", "say", "said", "get", "any", "all", "can",
    # generic vault / index / status words — real in frontmatter, useless as a
    # topic signal
    "note", "notes", "index", "moc", "map", "home", "dashboard", "overview",
    "active", "complete", "draft", "status", "type", "resource", "project",
    "area", "daily", "meeting", "book", "course",
})


def content_tokens(text: str) -> set[str]:
    """Tokenize to a set of meaningful, punctuation-free words for structural
    matching (MOC filename overlap, frontmatter narrowing). Drops stopwords and
    single characters so incidental overlap on function/generic words cannot
    trigger a match."""
    return {t for t in _tokenize(text) if len(t) > 1 and t not in STOPWORDS}


def keyword_search(
    entities: list["Entity"],
    query: str,
    top_k: int = 10,
) -> list[tuple["Entity", float]]:
    """TF-style keyword search across entity searchable text.

    Title matches are worth 3× to surface exact or near-exact title hits first.

    Parameters
    ----------
    entities:
        List of ``Entity`` objects to search over.
    query:
        Raw query string.
    top_k:
        Maximum number of results to return.

    Returns
    -------
    list[tuple[Entity, float]]
        Sorted by score descending, capped at top_k.
    """
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    scored: list[tuple["Entity", float]] = []
    for entity in entities:
        body_tokens = _tokenize(entity.searchable_text())
        title_tokens = _tokenize(entity.title)

        if not body_tokens:
            continue

        # TF in body
        body_freq: dict[str, int] = {}
        for tok in body_tokens:
            body_freq[tok] = body_freq.get(tok, 0) + 1

        body_score = 0.0
        title_score = 0.0
        for qt in query_tokens:
            # body contribution: normalised term frequency
            tf = body_freq.get(qt, 0) / len(body_tokens)
            body_score += tf
            # title contribution: binary, worth 3×
            if qt in title_tokens:
                title_score += 3.0

        total = body_score + title_score
        if total > 0:
            scored.append((entity, total))

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:top_k]
