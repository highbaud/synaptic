---
name: capture-processor
description: Process raw captures from 00 - INBOX into filed, connected notes. Runs the Daily Processing workflow — assessing each capture against active projects and decisions, rewriting in the user's voice, connecting to existing notes, and filing correctly. Also covers the Morning Capture Processing Pass (quick daily structured review) and the Learning Accelerator (integrating new reading into the vault). Use when the user asks to process their inbox, run their morning review, integrate something they just read, or convert captures into usable notes.
version: 0.3
---

# Capture Processor Skill

Captures are candidates for usefulness, not useful notes yet. This skill converts them into notes that can contribute to decisions, writing, conversations, and actions.

## The Four Uses Every Note Should Have

Before processing any capture, understand what "useful" means. A note has been used when it contributes to one of four outcomes:

1. **Decision support** — surfaces when the user is making a decision and provides relevant context, evidence, or perspective
2. **Writing fuel** — contributes content, evidence, structure, or insight to something being written
3. **Conversation material** — gives the user something specific and valuable to say in a meeting or presentation
4. **Action trigger** — surfaces an idea at the moment when acting on it is possible

A capture that cannot plausibly contribute to any of these four outcomes should not become a note. Archive it directly.

---

## The Ingest Principle

One source at a time. Never in batches.

A good ingest is not one new file in `01 - NOTES/`. It is the model tracing the implications of that source across the whole vault — touching every permanent note in `04 - RESOURCES/topics/` whose content the new source changes, confirms, or contradicts. Batch-importing your entire reading list produces a pile, not a wiki, because nothing gets linked while the pile is still forming.

The ingest has two phases:

1. **Create the source note** — file the raw capture in `01 - NOTES/` (immutable from this point; never edit the original)
2. **Run the Neighbor Update** — find every permanent note the new source affects and update it

The Neighbor Update is what separates a storage system from a compiled knowledge base. Skip it and the new source is filed but isolated. Run it and every related permanent note absorbs the new information.

---

## The Three Capture Conventions

Well-formed captures use one of three conventions that preserve context at the moment it is richest:

### Connection Capture (default)
```
IDEA: [The thought in one or two sentences]

CONNECTS TO: [What this reminds you of or relates to]

MIGHT USE FOR: [The first application that comes to mind]
```
The `CONNECTS TO` line is the highest-value signal. It captures the natural associations that exist in the user's mind at the moment of capture — associations that fade within hours.

### Question Capture
```
[THE INFORMATION]

THIS RAISES THE QUESTION: [The question this generates]
```
Questions are often more useful than answers. They drive future inquiry and can be matched against notes that might answer them.

### Application Capture
```
[THE IDEA]

COULD APPLY TO: [Specific current situation]

ACTION IF TRUE: [What to do if this idea is correct]
```
Application captures come pre-loaded with a use case, making future retrieval automatic.

When captures lack these conventions, look for implicit versions: what connection was the user implicitly making? What question does this raise? What situation might it apply to?

---

## Daily Processing Run

Run this workflow on all notes in `00 - INBOX` from the current session or day.

```
Process all notes in 00 - INBOX.

For each captured note:

1. USEFULNESS ASSESSMENT
   Can this note contribute to:
   - Any active project listed in CLAUDE.md?
   - Any active decision listed in CLAUDE.md?
   - Any writing topic listed in CLAUDE.md?

   If yes to any: mark as PROCESS
   If no to any: mark as ARCHIVE DIRECTLY

2. FOR NOTES MARKED PROCESS
   Rewrite the note in the user's own words.
   Not a summary of the source. Their understanding
   of the idea in their voice.

   Then identify:
   - What existing notes in 02 - PROJECTS, 03 - AREAS,
     or 04 - RESOURCES does this connect to?
   - Which active project or decision does it feed?
   - What is the most likely future use case?

3. FILE THE NOTE
   Determine the correct folder using vault-structure placement logic.
   Apply the naming convention: YYYY-MM-DD-[TYPE]-[TOPIC].md
   Add universal frontmatter: type, status, date, tags
   Add links to connected existing notes
   Notes filed to 01 - NOTES/ are immutable after this step.

3b. NEIGHBOR UPDATE (for notes with ideas worth keeping in the wiki)
   Scan 04 - RESOURCES/topics/ for permanent notes this source affects.
   For each affected permanent note:
   - CONFIRMS an existing claim: add a citation wikilink
   - CONTRADICTS an existing claim: add a Key Tension entry
   - EXTENDS existing knowledge: add the new insight + wikilink
   Flag any ideas in the new source that no permanent note covers yet —
   these are gaps where permanent notes should be written.

4. ARCHIVE ORIGINAL CAPTURE
   Move the raw capture to 05 - ARCHIVE

5. LOG
   Report what was processed, what was archived directly,
   and what connections were made.
```

---

## Processing Decision Logic

For each capture, work through this sequence:

**Step 1 — Check CLAUDE.md**
Read `06 - SYSTEM/CLAUDE.md` for the user's active projects, current decisions, and writing topics. This is the filter for every processing decision.

**Step 2 — Assess contribution potential**
Ask: can this note contribute to a decision, piece of writing, conversation, or action the user currently cares about? If no clear answer, archive it. Better to archive than to create a note that accumulates without being used.

**Step 3 — Determine placement**
Use the vault-structure placement logic:
- Has an end date → `02 - PROJECTS/[project]/`
- Ongoing responsibility → `03 - AREAS/[area]/`
- Reference by topic → `04 - RESOURCES/topics/` (or `people/`, `places/`, `tools/`)
- Time-stamped capture → `01 - NOTES/[daily|meetings|books|courses]/`

**Step 4 — Rewrite before filing**
Do not file a raw capture. Rewrite it in the user's voice. The title should describe the idea, not the source. "How energy management outperforms time management" is a better title than "Note from Deep Work chapter 3."

**Step 5 — Create connections**
Before filing, identify notes the new note should link to. A note with no links to existing notes is an island. It will not be retrieved except by accident.

---

## Processing Report Format

After processing a batch, report:

```
PROCESSED: [n] captures → filed notes
  - [note title] → [destination folder] | connected to: [linked notes]
  - ...

ARCHIVED: [n] captures (no active contribution path)
  - [note title] → reason: [one line]
  - ...

CONNECTIONS MADE: [n]
  - [note A] ↔ [note B]: [what the connection reveals]
  - ...

GAPS: [Any captures that raised questions or referenced missing notes]
```

---

## Morning Capture Processing Pass

A 5-minute daily structured review of rough notes from the previous day. Faster than the full Daily Processing Run — designed for daily use, not weekly batch processing.

Run this first thing in the morning before any new captures.

```
Here are my rough notes from yesterday: [paste yesterday's daily note or raw captures]

Do three things:
1. Pull out any decisions I made or commitments I made to myself.
   Not what I was thinking about — what I decided or committed to.

2. Identify the most interesting idea worth developing further.
   One idea only. If there are multiple, pick the one that connects
   to the most active project or decision in my current context.

3. Suggest one concrete next action based on what I wrote.
   One action. Specific enough that I could start it in the next
   30 minutes without further clarification.
```

The morning pass does not file notes — it identifies signal. Notes worth keeping get processed in the full Daily Processing Run. The morning pass answers the question: what should I do with what I captured yesterday?

---

## Learning Accelerator

Run this when you have just read something worth integrating — an article, book chapter, research paper, or piece of writing that generated a reaction.

The goal is to convert reading into permanent notes, not to log that you read something.

```
I just read this: [paste the key passage or summarize the key idea]

Three things:
1. What is the single most important idea here, in one sentence?
   Not a summary of what was written — the one thing worth keeping.

2. How does this connect to or challenge something I already know
   about [your topic or field]?
   Specifically: does it support, contradict, or complicate an idea
   I already hold?

3. What is one question this raises that I should think about?
   A question the passage does not answer — a thread worth pulling.
```

The output of the Learning Accelerator is the raw material for a permanent note. Use the `permanent-note` skill to convert it into a filed note with the Key Tension and wikilinks.

**What separates learning from information collection:** The accelerator asks what question the reading raises, not what the reading says. A question is more durable than an answer — it drives future captures and connects backward to existing notes.

---

## Idea Development Loop

When you have a rough idea worth developing — a single-sentence capture, a hunch, a half-formed argument — this three-round loop develops it into something permanent.

**Round 1 — Steelman it:**
```
Here is an idea I am developing: [your idea]

Steelman this idea. Give me the strongest version of the argument
and the most compelling reason it might be true. Not what I said —
the best possible version of what I might mean.
```

**Round 2 — Challenge it:**
```
Now play devil's advocate. What is the strongest case against this idea?
What am I missing? What assumption am I making that might not hold?
```

**Round 3 — Find the core:**
```
Given both sides, what is the most defensible version of this idea —
the formulation that holds up to the challenge and is still worth saying?
Express it in one sentence.
```

Use that final sentence as the title of a permanent note in `04 - RESOURCES/topics/`. The three rounds become the Key Tension section.

---

## Book / Article Note Generator

Use this prompt immediately after finishing a book, article, or paper. It creates a source note filed in `01 - NOTES/books/`. The best ideas extracted here become permanent notes via the Learning Accelerator or permanent-note skill.

```
I just finished reading: [book or article title and author]

Here are the key passages I highlighted or marked:
[paste highlights or a summary of the content]

Create a reading note for 01 - NOTES/books/:
1. State the main thesis or argument in one sentence.
2. List 3–5 key insights worth keeping — not quotes,
   the ideas in my own words.
3. Identify how this connects to something I already know:
   - Does it support, contradict, or complicate an existing belief?
4. Generate 2 questions this raises that the book does not answer.
5. Write a "My Take" section: what do I agree with, disagree with,
   or want to challenge?
6. Suggest frontmatter (type: book, status: draft, author, finished, rating, key_insight).
7. Filename: YYYY-MM-DD-book-[title-slug].md

Note: the 1–2 best ideas should each become a separate permanent
note in 04 - RESOURCES/topics/ using the permanent-note skill.
```

---

## Meeting Note Processor

Use this prompt with raw meeting notes immediately after a meeting, before context fades.

```
Here are my raw notes from a meeting: [paste raw notes]

Extract and structure for 01 - NOTES/meetings/:
1. KEY DECISIONS: What was decided? State each as a clear
   action or commitment, not "we discussed X."
2. ACTION ITEMS: Who will do what by when?
   Format: [Owner] — [Action] — [Due date if mentioned]
3. IMPORTANT INFORMATION: What did I learn that is useful
   beyond this meeting?
4. OPEN QUESTIONS: What was raised but not resolved?
5. CONNECTIONS: Which active project does this feed?
   Link to any relevant project notes or area notes.

Suggest frontmatter (type: meeting, status: active,
attendees, decisions, actions as frontmatter fields).
Filename: YYYY-MM-DD-meeting-[topic-slug].md
```

---

## Daily Note Reflection Starter

Use this at the end of the day to convert scattered daily notes into captured signals before they fade.

```
Here is what I captured or did today:
[paste daily note, rough jottings, or brief description]

Help me extract the signal:
1. What was the most important thing I did or decided today?
   Not a summary — the single highest-leverage moment.
2. What would I do differently? One specific thing.
3. What is the main open thread going into tomorrow?
4. Any ideas or insights worth capturing as a permanent note?
   If yes, draft a one-sentence title for the note.
5. Does anything today connect to a bigger pattern in my vault?
   What note should I add a link to?

I don't need a long report — tight answers only.
```

---

## Article to Vault

Use this for a web article, essay, or research paper you want to absorb quickly without a full reading session.

```
Here is the article I want to capture: [paste article text or key excerpts]
[Or: the article is about [topic], its main argument is [summary]]

Extract for my vault:
1. Main argument in one sentence.
2. 2–3 specific claims worth remembering — the ones that surprised
   me or would change how I think about this domain.
3. The best single example or quote that makes the argument concrete.
4. How this relates to my current focus area: [your active project or topic]
5. What I agree with, and what I'd push back on.

Format this as an Obsidian note for 01 - NOTES/books/:
- Proper frontmatter (type: resource, source: [URL], date, tags)
- Body using the points above, written in my voice
- A "Links" section: suggest 1–2 vault notes this should connect to
- Filename: YYYY-MM-DD-resource-[topic-slug].md
```

---

## Source Neighbor Update

Run this after filing a new source note. It is the ingest step that converts filed information into compiled knowledge — tracing the new source's implications across the permanent notes that already exist.

```
I just filed this source note: [note title] — [one-sentence summary of what it says]

Scan 04 - RESOURCES/topics/ for permanent notes this source affects:

1. CONFIRMS: Which existing permanent notes does this source support or validate?
   For each: add a wikilink to the new source note with a brief note on what it confirms.

2. CONTRADICTS: Which permanent notes does this source conflict with?
   For each: add a Key Tension entry — "[[source-note]] challenges this:
   [how it challenges it]"

3. EXTENDS: Which permanent notes can be strengthened with something from this source?
   For each: add the key insight from the new source and a wikilink.

4. GAPS: Are there ideas in this source that no existing permanent note covers?
   If yes: list the titles of permanent notes that should be written.
   These are priority items for the next capture processing pass.

Report:
- Source note filed: [path]
- Permanent notes updated: [n] — [list titles]
- Gaps flagged: [n] — [list suggested titles]
```

---

## Rules

- Always read `CLAUDE.md` before starting a processing run. The user's current focus is the filter.
- Never file a raw capture. Always rewrite in the user's voice.
- A note with no links is an island. Every filed note needs at least one connection.
- Be conservative. Archive over filing marginal captures. A small vault of useful notes beats a large vault of noise.
- Log every decision. The user should be able to review what was processed and why.
- If a capture contains a question the vault might answer, note it in the report — it is a candidate for the Decision Feeder or Writing Activator workflows.
- The Morning Capture Processing Pass runs every day. The full Daily Processing Run runs when INBOX has more than 5 items. The Learning Accelerator runs on demand after reading.
