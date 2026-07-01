---
name: karpathy-ingest
description: Single-source ingest workflow based on Karpathy's LLM Wiki pattern — file one raw source, then compile it into the vault by updating every permanent note it affects. Use when the user wants to absorb a new article, transcript, PDF, or piece of writing into the vault properly. This is not the same as filing a note; it is the two-phase process that turns a new source into compiled knowledge.
version: 0.1
---

# Karpathy Ingest Skill

The core insight in Karpathy's LLM Wiki (v040426): most personal knowledge systems die of maintenance, not bad ideas. Collecting is easy. Keeping fifty interlinked notes current is the work nobody does twice. The pattern here moves that work to the model.

The ingest is how a new source enters the compiled wiki. It has two phases and one rule.

**The rule:** One source at a time. Never in batches.

Batch-importing produces a dump, not a wiki, because nothing gets linked while the pile is forming. One source at a time means the model traces that source's full implications before the next one arrives.

---

## The Two Phases

### Phase 1: File the Source (immutable)

The source note goes into `01 - NOTES/` and is never edited after filing.

`01 - NOTES/` is the raw layer — the source of truth the wiki is built from. If a source turns out to be wrong, add a correcting source; do not rewrite history. The moment you edit a filed source, you have two systems of record with no way to tell which is true.

**What a filed source note contains:**
- The core idea rewritten in the user's own words (not a quote or summary — the understanding)
- Universal frontmatter: `type`, `status: draft`, `date`, `source`, `tags`
- The `description` field: one-sentence claim the note makes
- At least one wikilink to an existing permanent note

**What it does not contain:**
- Analysis of what the source means for the rest of the vault — that belongs in the permanent notes the source updates, not in the source note itself

### Phase 2: Neighbor Update (the compilation step)

After filing, scan `04 - RESOURCES/topics/` for permanent notes the new source touches. This is the step that converts filing into compiling.

A permanent note is affected if the new source:
- **Confirms** a claim the note makes → add a citation wikilink
- **Contradicts** a claim → add a Key Tension entry
- **Extends** the note with new evidence or a new angle → add the insight + wikilink
- **Creates a gap** where a permanent note does not yet exist → flag for creation

The Neighbor Update is why the vault compounds. Without it, each new source is filed but isolated. With it, every new source propagates through the connected notes that already exist.

---

## Full Ingest Prompt

Use this as a single prompt to run both phases in one pass.

```
I want to ingest this source into my vault:

[paste article / transcript / excerpt / PDF highlights / notes]

Run the full two-phase ingest:

---
PHASE 1 — SOURCE NOTE

File this in 01 - NOTES/[books|courses|daily|meetings]/ as an immutable source record:

1. Write the core idea in my own words in 2–4 sentences.
   Not a quote, not a summary — my understanding of the idea and why it matters.

2. Draft frontmatter:
   - type: [book|resource|course|meeting]
   - status: draft
   - date: [today]
   - source: [title / URL / speaker]
   - description: [one-sentence claim the source makes]
   - tags: [2–4 relevant tags]

3. Suggest a filename: YYYY-MM-DD-[type]-[topic-slug].md

4. Add one wikilink to the most relevant existing permanent note in 04 - RESOURCES/topics/.

Note: this source note is immutable after filing. If the source is wrong,
we add a correcting source — we do not edit this one.

---
PHASE 2 — NEIGHBOR UPDATE

Now scan 04 - RESOURCES/topics/ for permanent notes this source affects:

CONFIRMS — which existing permanent notes does this source support?
  For each: add a citation wikilink with a one-sentence note on what it confirms.

CONTRADICTS — which permanent notes does this conflict with?
  For each: add a Key Tension entry:
  "[[new-source-note]] challenges this: [how it challenges it]"

EXTENDS — which permanent notes gain something from this source?
  For each: add the key insight from the source and a wikilink.

GAPS — what ideas in this source does no existing permanent note cover?
  List suggested titles for permanent notes that should be written.
  These are priority notes for the next processing pass.

---
REPORT:
- Source note filed: [path]
- Permanent notes confirmed: [n] — [titles]
- Permanent notes with new Key Tension: [n] — [titles]
- Permanent notes extended: [n] — [titles]
- Gaps flagged: [n] — [suggested titles]
```

---

## Single-Topic Deep Ingest

When a topic cluster in `04 - RESOURCES/topics/` has grown to 10+ notes and a new source arrives that touches most of them, run this extended version.

```
I am ingesting a new source on [topic]: [source title and summary]

This topic already has these permanent notes in my vault:
[list titles of existing topic notes]

Extended ingest for a dense topic cluster:

1. FILE THE SOURCE NOTE (Phase 1 as above)

2. MAP THE CHANGES
   For each existing permanent note in this cluster:
   - What does the new source add, change, or challenge?
   - Does any note need to be split (it now covers two ideas that have diverged)?
   - Does any note need to be merged (two thin notes now have enough to combine)?

3. UPDATE THE MOC
   Open or create 06 - SYSTEM/MOCs/[topic]-index.md.
   Add the new source note and any new permanent notes to the index.
   Check for orphan notes (in the cluster but not in the MOC) and add them.

4. LINT THE CLUSTER
   Scan for:
   - Contradictions between permanent notes in this cluster
   - Entities named two different ways across notes
   - Orphan notes with zero inbound links from the rest of the cluster
   Report findings — contradictions are information, not errors.

Report: map, changes, MOC state, lint findings.
```

---

## The Lint Pass

After every 10–15 ingests, run a vault-wide lint. Contradictions are not errors to fix — they are information. They mean two sources disagree and you now know where to look.

```
Run a lint pass on 04 - RESOURCES/topics/:

1. CONTRADICTIONS
   Find permanent notes making conflicting claims about the same subject.
   Report each as: "[[Note A]] claims X. [[Note B]] claims Y."
   Do not resolve — flag for review.

2. ENTITY DRIFT
   Find concepts named differently across notes (e.g. "deliberate practice"
   vs "intentional practice" vs "deep practice").
   For each: which name should be canonical? Which notes need updating?

3. LOW-CONFIDENCE CLAIMS
   Find claims in wiki notes that have no wikilink to a source note in
   01 - NOTES/. Flag these as unanchored — they should either be sourced
   or moved to Key Tension (acknowledged uncertainty).

4. ORPHANS
   Find permanent notes with zero inbound links from other permanent notes.
   Each orphan is either a gap in the graph or a note ready for the archive.

Report: contradictions, entity drift, unanchored claims, orphans.
```

---

## Rules

- Never ingest more than one source at a time. One source. Full two-phase pass. Then the next.
- Phase 1 produces an immutable source record. Do not edit `01 - NOTES/` files after filing.
- Phase 2 is not optional. A filed-but-unconnected source is storage, not knowledge.
- A gap is a good output. A new source that flags three missing permanent notes has done more work than a source that touches nothing.
- The value is in the edges, not the nodes. An entity appearing in five notes but linking to none is a signal the ingest was lazy.
- Run the lint pass regularly. A wiki that skips the lint rots from the inside while the graph still looks impressive on the surface.
