---
name: connection-finder
description: Surface high-value, non-obvious connections between notes across the vault. Covers the weekly Connection Surface (systematic scan of the last 7 days), the Two-Note Connection prompt (connecting two specific notes), and the Pattern Finder (naming unnamed patterns across 3+ notes). Use when the user asks to find connections, run their weekly review, wants to know how two specific notes relate, or has a cluster of notes that feel connected but have not been linked.
version: 0.3
---

# Connection Finder Skill

The real value of a knowledge system lives in the connections between notes across time, domains, and contexts. This skill surfaces connections the user did not intentionally create — the ones that emerge when an agent reads across a full knowledge base.

A vault that accumulates notes without building connections between them is an archive. A vault with strong connections compounds.

---

## The Connection Quality Standard

**A strong connection:** Reading both notes together creates insight that neither note provides alone.

**A weak connection:** Both notes are about the same topic.

Topic overlap is not a connection. It is just two notes sitting near each other in the same semantic neighborhood.

A strong connection has one of four structures:

### 1. The Same Principle, Different Domains
The underlying mechanism of Note A appears in a completely different domain in Note B. Neither note names the pattern explicitly. Connecting them names the pattern and makes both notes more powerful.

*Example: A note about compounding returns in finance connects to a note about deliberate practice — both are about the long-term non-linearity of consistent small actions.*

### 2. Productive Contradiction
Note A and Note B make claims that conflict or create genuine tension. Holding them together raises a question worth thinking through. Neither note, read alone, generates that question.

*Example: A note arguing that deep work requires isolation contradicts a note arguing that the best ideas emerge in conversation. The tension is the insight.*

### 3. Evidence Relationship
Note A makes a claim. Note B contains data, example, or argument that either strongly supports or undermines that claim. Most notes make claims without knowing the evidence exists elsewhere in the vault.

*Example: A note claiming that most organizational change fails connects to a case study note that documents exactly how one change succeeded — and why the exception is instructive.*

### 4. Unnamed Pattern
The same structural pattern appears in three or more notes across different contexts, but no note names the pattern. The connection makes the pattern explicit and gives it a title.

*Example: Notes on negotiation, pricing, and job offers all contain versions of the same insight about anchoring — but none of them call it anchoring.*

---

## Weekly Connection Surface Workflow

Run this workflow once per week on notes created or significantly modified in the last 7 days.

```
Read all notes created or modified in the last 7 days
across 02 - PROJECTS, 03 - AREAS, and 04 - RESOURCES.

For each recent note, scan the full vault for existing
notes that share a meaningful connection.

Meaningful connections are:
- The same underlying principle applied in different domains
- Contradictory claims worth examining together
- One note providing evidence for or against a claim in another
- A pattern that appears across multiple notes that no
  individual note names explicitly

For each connection found:
- Name both notes
- Identify which type of connection this is
- Describe specifically what new insight emerges
  from reading them together
- Explain why connecting them makes both notes
  more useful going forward

Only surface connections that are genuinely non-obvious.
Skip anything already linked.
Skip connections that are merely topical.
```

---

## Connection Report Format

Save connection reports to `04 - RESOURCES/topics/` with the naming convention `YYYY-MM-DD-resource-connections-[week].md`.

```markdown
---
type: resource
status: active
date: YYYY-MM-DD
tags: [connections, status/active]
---

# Connection Report — [Date]

## Strong Connections Found

### [Note A title] ↔ [Note B title]
**Connection type:** [same-principle / contradiction / evidence / unnamed-pattern]
**Insight:** [What reading them together reveals that neither reveals alone]
**Suggested action:** [Add link in Note A / Add link in Note B / Create new synthesis note]

### [Note A title] ↔ [Note B title]
...

## Patterns Identified
[Any unnamed patterns that appeared across 3+ notes]

## Notes Reviewed
[Count of notes scanned this week]
[Date range covered]
```

---

## Adding Links After Finding Connections

When a strong connection is found, add explicit wikilinks in both notes:

In Note A, add a section or inline link:
```markdown
See also: [[Note B]] — [one sentence on what the connection adds]
```

In Note B, add:
```markdown
See also: [[Note A]] — [one sentence on what the connection adds]
```

Do not just note the connection in a report and leave the notes unlinked. The link makes future retrieval automatic.

---

## Connecting to Active Work

After running the connection surface, check the connection report against `CLAUDE.md`:

- Does any connection directly inform an active decision? → Flag it for the Decision Feeder
- Does any connection strengthen a writing topic? → Flag it for the Writing Activator
- Does a pattern appear that matches a current project? → Add a link in the project note

The connection surface is most valuable when its output feeds directly into active work rather than sitting in a report that is never consulted.

---

## Two-Note Connection Finder

For connecting two specific notes the user suspects are related but has not formally linked.

```
I have two notes that might be related.

Note 1: [paste first note or its title and key idea]

Note 2: [paste second note or its title and key idea]

Three things:
1. What is the conceptual thread connecting these?
   Not the topic they share — the underlying principle or mechanism
   that makes reading them together more interesting than reading
   either one alone.

2. Is this a strong connection (reading them together changes how
   I understand both) or a weak connection (they are just about
   the same topic)?
   If weak: explain why and skip steps 3–4.

3. What is the specific wikilink text that should appear in each note?
   The one-sentence explanation of what the connection adds.

4. Is there a third idea that would bridge these — a note worth
   writing that the current vault is missing?
```

Use this when the weekly connection surface misses a specific pair, or when you encounter two notes that feel related and want to test whether the relationship is real.

---

## Pattern Finder

For surfacing unnamed structural patterns across three or more notes.

```
Here are [n] notes that feel connected but I have not linked:
[list note titles and one-sentence summaries of each]

Read them together and answer:
1. Is there a structural pattern these notes share?
   Not a topic. A mechanism, principle, or recurring shape
   that explains why they generate similar insights.

2. If yes: give the pattern a name. The name should be specific
   enough to distinguish this pattern from adjacent ideas.
   "The feedback gap" not "feedback is important."

3. Which of these notes should serve as the pattern's anchor —
   the one where the pattern is most clearly expressed?

4. Draft a permanent note for the pattern itself, following
   the permanent-note template. Title = the pattern name.
```

Patterns are the highest-value outputs of the connection finder. A named pattern turns three isolated notes into a reusable framework that surfaces every time a new note touches the same mechanism.

---

## Idea Synthesis Finder

For surfaces where two or three notes feel related but you have not articulated why — and want to know whether they reveal something new when combined.

```
Here are [2 or 3] notes that feel connected:

Note 1 — [title]:
[paste note or its key idea in 2–3 sentences]

Note 2 — [title]:
[paste note or its key idea in 2–3 sentences]

Note 3 — [title] (optional):
[paste note or its key idea in 2–3 sentences]

Four questions:
1. What single theme, mechanism, or principle connects these?
   Not the topic they share — the underlying structure that explains
   why reading them together is more interesting than reading each alone.

2. What non-obvious insight emerges from combining them?
   The kind of thing neither note would produce on its own.

3. Draft a title for a synthesis note that captures that insight
   as a principle. (Full sentence. Describes the idea, not the source.)

4. Is this connection strong enough to write the synthesis note,
   or are these just topically adjacent?
   If adjacent: explain why and stop here.
```

Use when you sense a connection but cannot name it. The test: if the combination produces a non-obvious principle you did not see before — write the synthesis note immediately using the permanent-note skill.

---

## Rules

- Never surface connections that are merely topical. Topic overlap is not a connection.
- When evaluating two notes, ask: "Does reading them together change how I understand either one?" If no, it is not a strong connection.
- Prefer connections across different domains or time periods. Same-domain, same-time connections are rarely non-obvious.
- If no strong connections exist in a given week, say so clearly. A report that forces weak connections is worse than no report.
- Do not add links without a one-sentence explanation of what the connection adds. Unexplained links become noise.
- Run the weekly surface on the last 7 days by default. Extend to 30 days when the user has been away or when a new topic cluster is forming.
- The Two-Note Connection prompt is for on-demand use; the weekly surface handles systematic discovery.
- When the Pattern Finder names a new pattern, write the permanent note immediately — named patterns lose their force if they exist only in a report.
