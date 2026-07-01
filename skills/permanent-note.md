---
name: permanent-note
description: Create high-quality conceptual notes for 04 - RESOURCES/topics/ — atomic, linked, and written in the user's own voice. These are the notes that compound over time: each one a clear idea, connected to existing knowledge, with an explicit statement of what makes it interesting. Use when filing a processed capture as a conceptual resource note, or when the user asks to write a permanent note on an idea.
version: 0.2
---

# Permanent Note Skill

A permanent note is a conceptual resource note that is worth keeping indefinitely because it expresses an idea clearly enough to be useful in future decisions, writing, and conversations — regardless of what project or context it was originally captured for.

Permanent notes live in `04 - RESOURCES/topics/`.

They are the compiled artifact of the vault. Raw captures in `01 - NOTES/` are the source layer — immutable inputs the model reads and never edits. Permanent notes are what the model compiles from those sources: structured, linked, synthesized knowledge. When you query the vault, you are not re-deriving answers from scattered captures — you are reading a built artifact that has been accumulating and sharpening with every ingest. This is what makes the vault compound instead of just grow.

They are different from project notes (which become irrelevant when the project ends), meeting notes (which are time-specific), and book notes (which are organized by source). A permanent note is organized by idea.

---

## The Four Standards

A permanent note must satisfy all four:

### 1. Atomic
One clear idea only. The test: can you state what the note is about in a single sentence? If the answer requires "and" or a list, the note contains more than one idea and should be split.

A note titled "Why habits form and how to break them" contains two ideas. Split it into "Why habits form" and "How to break an established habit."

### 2. Own Words
Written in the user's voice, not copied or summarized from a source. The note should express the user's understanding of the idea — what they took from it, why it matters to them, how it connects to what they already know.

Copying a highlight is not a permanent note. Rewriting what the highlight means in your own words is.

The test: could you read this note to someone without revealing its source, and would it sound like you?

### 3. Linked
Contains at least two wikilinks to other notes in the vault. A note with no links is an island — it will only be retrieved if you know it exists and search for it deliberately. Links make retrieval automatic.

Links should be to notes the idea genuinely connects to, not to notes that happen to share a topic. See the connection-finder skill for the standard of a meaningful connection.

### 4. Key Tension
Includes an explicit statement of what makes the idea interesting, non-obvious, or worth thinking about. This is the most important section and the most commonly skipped.

The key tension is what separates a note that just stores information from a note that makes you think. It is the intellectual edge of the idea — the reason you captured it instead of scrolling past it.

```
## Key Tension
[What makes this idea interesting, non-obvious, or worth thinking about.
What does it contradict? What assumption does it challenge? 
What would change if it were true?]
```

---

## Frontmatter

```yaml
---
type: resource
status: reference
date: YYYY-MM-DD
tags: [topic1, topic2]
source: [optional — where the idea came from]
---
```

Use `status: draft` when first creating the note. Upgrade to `status: reference` only when the note has two meaningful wikilinks and has contributed to at least one output.

---

## Maturity Levels

A permanent note is not finished the moment it is filed. It matures over time through three levels, reflected in the `status` field.

| Status | What it means |
|--------|---------------|
| `draft` | Idea captured, body written, Key Tension drafted. No wikilinks yet. |
| `developing` | Key Tension refined, at least one link added. Starting to connect. |
| `reference` | Two or more meaningful wikilinks. Has contributed to at least one output. Fully evergreen. |

Use `status: draft` when first creating a note. Upgrade to `reference` only when the note has both links and a contribution. A vault with too many `draft` notes that never graduate is a signal to review and prune — most should either be developed or archived within 30 days.

---

## Evergreen Note Generator

Use this prompt to convert a raw capture or rough idea into a filed permanent note.

```
Take this raw note or idea: [paste the capture]

Convert it into a permanent note for 04 - RESOURCES/topics/:
1. Write a title that states the idea as a principle.
   The title should be a full sentence, not a topic label.
   "Compounding requires consistency more than magnitude"
   — not "Compounding notes" or "Morgan Housel talk."

2. Write 3–5 sentences in my own words:
   - What is the core claim?
   - What evidence or reasoning supports it?
   - What is the implication for how I think or act?
   Not a quote or summary — my understanding, in my voice.

3. Write the Key Tension section:
   - What makes this interesting or non-obvious?
   - What does it contradict or challenge?
   - What would change if this were true?

4. Suggest two existing notes this should link to
   and write the one-sentence connection for each link.

5. Suggest frontmatter: type: resource, status: draft, date, description
   (one sentence — the idea as a claim), tags, source.
6. Suggest a filename: YYYY-MM-DD-resource-[topic-slug].md
```

---

## Writing Process

1. **State the idea in one sentence.** This becomes the note title. The title should describe the idea, not its source. "Compounding requires consistency more than magnitude" is better than "Notes from Morgan Housel talk."

2. **Write the body in 3–5 sentences** explaining the idea in the user's own words. What is the core claim? What evidence or reasoning supports it? What is the implication?

3. **Write the Key Tension section.** What makes this interesting? What does it contradict? What changes if you take it seriously?

4. **Find at least two links.** What existing notes in the vault does this idea genuinely connect to? Add wikilinks with a brief note on the connection.

5. **Add frontmatter.** Type, status, date, tags, optional source.

6. **Suggest a filename** following the naming convention: `YYYY-MM-DD-resource-[topic-slug].md`

---

## Example

```markdown
---
type: resource
status: reference
date: 2026-05-14
tags: [learning, expertise, productivity]
source: Peak — Ericsson & Pool
---

# Deliberate Practice Requires Immediate Feedback on Errors

Improvement in any skill domain requires not just repetition but
repetition with immediate feedback on what went wrong. Practice
without feedback optimizes for fluency, not accuracy. The expert
and the amateur often spend the same number of hours practicing,
but the expert's hours include corrective feedback loops that the
amateur's do not.

## Key Tension
This contradicts the popular "10,000 hours" framing. The hours do
not produce expertise — the feedback structure does. Two people
with 10,000 hours of practice can have completely different skill
levels depending on whether their practice included feedback.
This reframes the question: not "how long did you practice" but
"how much of your practice included rapid feedback on errors?"

## Connections
- [[Compounding Requires Consistency More Than Magnitude]] — both
  are about the quality of the input loop, not the volume
- [[Why Most People Plateau in Their Careers]] — plateaus often
  coincide with the point where feedback disappears from daily work
```

---

## What Makes a Note Worth Keeping as Permanent

A note is worth keeping as permanent if it passes the contribution test: could this note contribute to a decision, a piece of writing, a conversation, or an action the user might plausibly have in the next two years?

If the honest answer is no — if the note is too specific to a context that is over, too obvious to add anything to future thinking, or too vague to be actionable — archive it.

The metric that matters is not the number of notes. It is the number of times notes contribute to something. A permanent note that has never contributed to anything is indistinguishable in value from no note at all.

---

## Rules

- Never create a permanent note that violates any of the four standards.
- The Key Tension section is mandatory. Do not skip it.
- The title describes the idea, not the source. "Energy management outperforms time management" not "Notes from Deep Work."
- Prefer adding to an existing note over creating a new one when the idea is already partially covered. A denser, more developed note is more useful than two thin notes on adjacent ideas.
- When a note has been in `04 - RESOURCES/topics/` for 6 months without being linked from any project, decision, or writing output, flag it for the weekly note audit. It may belong in the archive.
