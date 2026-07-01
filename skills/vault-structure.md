---
name: vault-structure
description: Deep understanding of the Synaptic vault folder architecture and the retrieval-first principle that drives every organizational decision. Use when creating, moving, or organizing notes, when the user asks where something belongs, or when auditing the vault structure for correctness.
version: 0.3
---

# Vault Structure Skill

The vault is organized for retrieval, not storage. Every structural decision is made by asking: when I need this information in the future, what will I know about it that I can use to find it?

A filing cabinet stores things by what they were when you put them away. A thinking system retrieves things by what you know about them when you need them back. These are different architectures. Most note-taking systems fail because they are designed for the first goal while the user needs the second.

---

## The Core Principle

**You do not organize a vault to put things away neatly. You organize a vault to get things back quickly.**

Every folder you create, every tag you apply, every naming convention you adopt should be evaluated against one question: does this make retrieval faster or slower?

A folder called "Ideas" makes sense at capture time. Six months later you are looking for a specific idea and you cannot remember whether you filed it in Ideas, Projects, Business, or a daily note. The folder name encoded what the note contained when you saved it. It tells you nothing when you are trying to find it.

---

## Three Layers, Three Owners

The vault operates on three distinct layers with three distinct owners. Keep them separate — the moment these blur, the system becomes untrustworthy.

| Layer | Folder | Owner | Rule |
|-------|--------|-------|------|
| **Raw** | `01 - NOTES/` (daily, meetings, books, courses) | You | Immutable. Never edited after filing. |
| **Wiki** | `04 - RESOURCES/topics/` (permanent notes) | Model | Compiled from raw sources. Model writes here during ingest. |
| **Schema** | `06 - SYSTEM/CLAUDE.md` | Both | Active context and rules. You set intent; model reads it every session. |

**Raw is immutable.** `01 - NOTES/` holds source captures — the input layer the model reads but never writes to. If a source turns out to be wrong, add a correcting note. Do not edit the original. The moment you do, you have two systems of record with no way to tell which one is true.

**The model owns the wiki.** `04 - RESOURCES/topics/` holds compiled knowledge — permanent notes the model builds from raw sources, linked and synthesized. Synaptic writes here during ingest. You refine and promote notes; the model does the bookkeeping. If you are manually updating wiki notes to keep them current, the ingest schema is underspecified, not the model.

**This is the compile / retrieve distinction.** RAG re-derives answers from raw chunks on every query and accumulates nothing. A compiled vault answers from a built artifact. `01 - NOTES/` is source code. The model is the compiler. `04 - RESOURCES/topics/` is the executable. Queries are runtime. Knowledge that is compiled compounds; knowledge that is retrieved is rediscovered.

This maps directly to Karpathy's LLM Wiki pattern (v040426): the throughline in every section is the same — the human owns judgment, the model owns the bookkeeping, and the wiki is a compiled artifact that compounds rather than a pile that grows.

---

## The Four Retrieval Dimensions

When searching for a note in the future, you will reliably know one or more of four things:

1. **Type** — What kind of content is it? Project note, book summary, meeting note, reference, daily note, idea, task.
2. **Time** — When did you create or last use it? This week, this month, last year, during a specific project or event.
3. **Topic** — What is it about? What subject area, person, project, or concept does it relate to?
4. **Status** — What state is it in? Active, complete, archived, reference, waiting.

A well-organized vault makes it possible to filter by any one of these dimensions or any combination in seconds. The folder structure, naming convention, frontmatter, and tagging system each serve one or more of these dimensions.

---

## Folder Structure

```
VAULT/
├── 00 - INBOX/
├── 01 - NOTES/
│   ├── daily/
│   ├── meetings/
│   ├── books/
│   └── courses/
├── 02 - PROJECTS/
│   └── [active-project-name]/
├── 03 - AREAS/
│   ├── health/
│   ├── finances/
│   ├── relationships/
│   ├── career/
│   └── learning/
├── 04 - RESOURCES/
│   ├── topics/
│   ├── people/
│   ├── places/
│   └── tools/
├── 05 - ARCHIVE/
└── 06 - SYSTEM/
    ├── templates/
    └── MOCs/
```

### Folder Purposes and Retrieval Patterns

**`00 - INBOX`** — Processing queue. Everything that does not have a clear home at capture time goes here. Nothing lives here permanently. When you open INBOX you know exactly what you need to do with everything in it: process and file. Retrieval pattern: none — this folder is for processing, not retrieval.

**`01 - NOTES`** — Time-stamped captures. Daily notes, meeting notes, book notes, course notes. Every note here has a clear time association. You find notes here by knowing roughly when the thing happened. Retrieval pattern: by time → by subfolder type.

**`02 - PROJECTS`** — Active projects with a defined outcome and an end date. One subfolder per project. When a project completes, the entire folder moves to `05 - ARCHIVE`. Retrieval pattern: by project name.

**`03 - AREAS`** — Ongoing responsibilities with no end date. Health, finances, relationships, career, and learning are areas you are always responsible for. They do not complete. Retrieval pattern: by life area.

**`04 - RESOURCES`** — Reference material organized by what it is about. Your personal Wikipedia. You come here when you need information on a topic, person, place, or tool — not when you know when you captured it or which project it belongs to. Retrieval pattern: by what it's about.

**`05 - ARCHIVE`** — Everything that is no longer active. Completed projects, outdated references, old daily notes. Archive instead of deleting. Storage is cheap. Accidentally deleting something important is not. Retrieval pattern: by search (you only come here when you specifically remember something from the past).

**`06 - SYSTEM`** — Vault infrastructure. Templates, MOCs, CLAUDE.md, the skills themselves. Things that make the vault work rather than things the vault contains. Retrieval pattern: by filename (you know exactly what you are looking for).

### Key Rules

- `00 - INBOX` is a queue. Nothing lives there permanently. Process it daily or at minimum weekly.
- `02 - PROJECTS` folders have an end date. When a project completes, move the entire folder to `05 - ARCHIVE`.
- `03 - AREAS` never completes. Do not move an Area to Archive because it feels "done" — it will always be relevant.
- Archive instead of delete. The cost of a wrong deletion is much higher than the cost of extra storage.
- Keep top-level folders between 5 and 8. More than 8 top-level folders becomes a navigation problem in its own right.
- Never create a folder called "Ideas," "Misc," or "Random." These are INBOX by another name.

---

## Naming Convention

```
YYYY-MM-DD-[TYPE]-[TOPIC].md
```

**Examples:**
```
2026-05-20-daily-wednesday.md
2026-05-18-project-website-launch.md
2026-05-15-meeting-client-quarterly-review.md
2026-05-10-book-thinking-fast-and-slow.md
2026-04-28-resource-claude-prompting-techniques.md
2026-04-20-area-finances-q2-review.md
2026-03-15-resource-deliberate-practice-requires-feedback.md
```

The date prefix does three things:
1. Sorts files chronologically automatically — most recent notes always appear at the top
2. Enables retrieval by approximate date when you cannot remember the specific name
3. Prevents naming conflicts — two notes on the same topic created on different dates have different names

The type identifier tells you what the note contains before you open it. Combined with the topic identifier you can often tell from the filename alone whether a note is what you need.

**For topic slugs:** lowercase, hyphenated, describe the idea not the source. `deliberate-practice-requires-feedback` not `ericsson-notes`.

---

## Properties (Frontmatter)

Every note must have these universal properties:

```yaml
---
type: [daily/meeting/project/area/resource/book/course/idea/task]
status: [active/complete/archived/reference/waiting]
date: 2026-05-20
description: One sentence — what this note is about, stated as a claim or fact.
tags: [topic1, topic2, status/active, project/project-name]
---
```

`type` serves the retrieval dimension of content type.
`status` is the most important property — it is the primary filter for finding active vs. inactive notes.
`date` serves the retrieval dimension of time.
`description` is a one-sentence summary used by the MCP server's `list_notes` tool — it lets an agent skim dozens of notes without loading full bodies. Write it as a claim, not a label: "Deliberate practice requires feedback, not volume" beats "Notes on practice." Optional on daily and meeting notes where the date and title carry enough context.
`tags` serve the topic and project retrieval dimensions.

**Shared vaults add one more:** `contributor` — who wrote this note, added automatically by `synaptic init` templates when the vault is set up in shared mode. This is an attribution convention, not access control — the vault has no per-file permissions, so `contributor` exists to make contributions traceable, not to restrict who can read or write what. Skip it in personal vaults; there's only one author and naming them adds nothing.

**Type-specific additional properties:**

```yaml
# Project notes
deadline: 2026-06-15
priority: [high/medium/low]
next_action: Write the project brief
completion: 35  # percentage

# Book notes
author: Author Name
finished: 2026-05-10
rating: [1-5]
key_insight: One sentence — the single most important idea

# Meeting notes
attendees: [Name1, Name2]
decisions: Key decisions made in this meeting
actions: Action items with owners

# Resource / topic notes
topic: Primary topic
source: Where this came from (optional)
reliability: [high/medium/low]
```

---

## Tagging System

Three tag categories. Each serves a different retrieval dimension.

| Category | Prefix | Examples | Retrieval dimension |
|----------|--------|---------|---------------------|
| Topic | none | `#productivity` `#machine-learning` | What the note is about |
| Status | `status/` | `#status/active` `#status/waiting` | Where the note is in a workflow |
| Project | `project/` | `#project/website-launch` | Which active project it feeds |

The prefix makes the category visible in search. `#status/active` returns every active note regardless of topic. `#project/website-launch` returns every note connected to that project regardless of type. `#productivity` returns every note on that topic regardless of status or project.

**The anti-bloat rule:** Only create a tag you will use on at least 5 notes. Tags on 1–2 notes are noise that clutters search without enabling retrieval. When in doubt, skip the tag and rely on search or properties instead.

---

## Placement Logic

When deciding where a note belongs, work through this sequence:

1. **Does it have a defined end date?** → `02 - PROJECTS/[project-name]/`
2. **Is it an ongoing responsibility with no end date?** → `03 - AREAS/[area]/`
3. **Is it reference material you will look up by what it's about?** → `04 - RESOURCES/[topics|people|places|tools]/`
4. **Is it time-stamped (daily, meeting, book, course)?** → `01 - NOTES/[daily|meetings|books|courses]/`
5. **Not sure?** → `00 - INBOX` for processing later

The most common mistake: filing a conceptual note as a project note. Ask: will this idea still be relevant when the project ends? If yes, it belongs in `04 - RESOURCES/topics/` with a `#project/x` tag pointing to the project.

---

## Note Lifecycle

Every note moves through a lifecycle. Knowing where a note is in its lifecycle determines what to do with it.

```
Capture → INBOX (raw, unprocessed)
    ↓ Daily processing
Filed note → NOTES / PROJECTS / AREAS / RESOURCES (active, connected)
    ↓ Project completes / topic becomes inactive / 6 months unaccessed
Archived note → ARCHIVE (preserved, not actively maintained)
```

A note should move to `05 - ARCHIVE` when:
- The project it belonged to is complete
- The decision it informed has been made
- The information is outdated
- It has not been accessed in 6 months and connects to nothing currently active

A note should **not** be deleted unless it is a duplicate of another note with better content, or it contains information that is actively misleading.

---

## Common Mistakes

These patterns appear in almost every vault that stalls out. Knowing them in advance saves months of restructuring.

### 1. Building the system before using it
Spending the first month setting up folders, templates, plugins, and conventions instead of capturing notes. The vault is not ready when it is perfectly organized — it is ready when you put the first real note in it. Build just enough structure to start, then refine as real usage reveals what you actually need.

### 2. Copying instead of writing
Pasting quotes, highlights, or screenshots into notes and calling it knowledge capture. Copied text is not a note — it is a bookmark. A note is the idea rewritten in your own words, with at least one connection to something you already know. If it took you 10 seconds to file it, it is not a permanent note.

### 3. Treating it as a filing cabinet
Organizing to put things away rather than to get them back. A filing cabinet sorts by where things came from. A thinking system sorts by what you will know when you need them back. If your folder names describe sources (Books, Articles, Videos, Meetings), you are building a filing cabinet. Use PARA — which encodes what you are doing with the information — instead.

### 4. Over-organizing
Installing 30 plugins, building nested folder hierarchies 5 levels deep, or designing a tagging taxonomy before there are enough notes to know what tags you need. Every layer of structure has a maintenance cost. Add structure only when you feel friction — when you are losing notes or retrieval is failing. The best vault for most people has fewer than 8 top-level folders and fewer than 20 tags.

### 5. Vague note titles
Titles like "Interesting ideas from podcast" or "Notes on habit book" force you to open the note every time to decide if it is what you are looking for. Write note titles as full sentences that describe the idea: "Deliberate practice requires feedback, not volume." You should be able to decide whether a note is useful from its title alone.

### 6. Never connecting notes
A vault of perfectly formatted, well-written notes with no wikilinks between them is not a thinking network — it is an indexed hard drive. The compounding happens in the links. A note with zero outgoing links will not surface organically during future work. Before filing any note, ask: what other note does this connect to? Add the link immediately. Link every note on creation. No exceptions.

### 7. Wrong note granularity
Writing book-length notes that contain multiple ideas instead of one idea per note. A note with three distinct ideas is three notes that cannot be separately retrieved, linked, or contributed. The test: can you state what this note is about in a single sentence without using "and"? If not, split it. One idea per note, always.

### 8. No daily notes habit
Not capturing at all — or capturing only in an app that doesn't connect to the vault. Ideas die before they reach the vault. A daily note is the lowest-friction capture surface: one note, created automatically, where anything goes. Process it weekly. Without a daily notes habit, the inbox stays empty because there's nothing to process — not because the vault is healthy.

### 9. Ignoring the connection graph
In Obsidian this is the Graph View; in Synaptic this is `synaptic contribution-report` and `find_connections`. The graph shows where your thinking has holes: which notes are orphans (zero links), which topics are siloed, which ideas cluster together but haven't been named. Open the graph (or run the report) every week. Notes with no connections are candidates for linking or archiving. A graph you never look at is a map you never read.

### 10. No Maps of Content
Skipping index notes (MOCs) that sit above clusters of related notes. Without them, when a topic grows past 10–15 notes it becomes a jungle — you know the notes are there but you can't navigate them. An MOC is just a note whose job is to link to all other notes on a topic. Create one when a topic has more than 10 notes. `06 - SYSTEM/MOCs/` is the home for these. See the `map-of-content` skill.

### 11. Never reviewing notes
Notes only compound when revisited. A note that is filed and never opened again contributes nothing — it is storage, not thinking. The weekly ritual (see `weekly-ritual` skill) is the practice that converts a vault from storage into a thinking system. Without weekly review, `#status/review` flags accumulate, orphans multiply, and the vault gradually becomes a graveyard of past thinking.

### 12. Quitting before the compound effect
A vault with 20 notes feels like any other app. At 100 notes, connections start surfacing. At 500 notes, the vault starts thinking with you. Most people quit at 20, before the system has enough mass to demonstrate its value. The compound effect is real, but it requires reaching a threshold. Expect two to four weeks before the vault feels meaningfully different from a folder of text files.

---

## Behavior

When asked about structure or when processing notes:
1. Identify the note's type, time association, topic, and status (the four retrieval dimensions)
2. Apply placement logic to determine the correct folder
3. Suggest the naming convention string for the filename
4. Specify which universal properties are required and which type-specific properties apply
5. Recommend appropriate tags from all three categories
6. If a note is in the wrong location, explain why using the retrieval logic — not "it belongs here" but "when you search for this note in the future, what will you know about it?"
