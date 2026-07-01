---
name: retrieval-organization
description: Operational workflows for keeping the vault organized and findable — inbox processing, search strategies, weekly note audit, Maps of Content, quarterly review, and progressive reorganization. Use when the user asks how to find something, how to process their inbox, how to build a MOC, how to run a vault review, or how to maintain vault health over time.
version: 0.2
---

# Retrieval Organization Skill

Organization is not a one-time event. It is a maintenance practice. This skill covers the operational layer: how notes get filed, how you find them when you need them, and how you keep the system accurate as the vault grows.

---

## Search Strategy

Four search modes. Use the right one for the situation. Most notes are findable in under 30 seconds when the vault is well-structured.

### Full Text Search
Type any distinctive phrase or keyword from the note's content. Obsidian searches every character of every note.

**Use when:** You remember something specific the note said. A quote, a phrase, a distinctive term. This is the most powerful mode for notes where you know the content but not the location.

### Property Search
Type structured filters directly in the search bar:
```
type:project status:active
type:book status:complete
type:meeting date:2026-05
```

**Use when:** You know the type of note and optionally its status or date range. Returns every matching note regardless of topic or folder.

### Tag Search
Type the tag with the hash symbol:
```
#productivity
#status/active
#project/website-launch
```

**Use when:** You know the topic, the workflow status, or the project the note belongs to.

### Date-Based Folder Sort
Open the relevant folder and sort by creation date.

**Use when:** You remember roughly when you created the note and which folder it lives in. Sort newest-first and scan.

### Combining Modes
The search combination that covers almost every scenario:
- Remember what the note said → full text search for a distinctive phrase
- Remember what type and roughly when → property search with type + date range
- Remember the project or topic → tag search
- Remember roughly when → sort by date in the relevant folder

If a note is not findable in under 30 seconds using these methods, the vault structure or frontmatter is the problem — not the search.

---

## Inbox Processing

`00 - INBOX` is a queue. Its purpose is to receive notes that did not have an obvious home at capture time. Process it on a fixed schedule — 15 minutes at the end of each workday is sufficient for most vaults.

**The three-question triage:**

For each note in INBOX:

1. **What type of content is this?** → determines the top-level folder (NOTES / PROJECTS / AREAS / RESOURCES)
2. **Does it already have a home?** → if a project or topic note exists that this connects to, link it there before filing
3. **Does it need its own note or should it be added to an existing note?** → a single thought that expands on an existing note is better merged than given its own file

**After answering:**
- Rewrite the note in the user's own words if it is a raw capture
- Add universal frontmatter: `type`, `status`, `date`, `tags`
- Rename to match the naming convention: `YYYY-MM-DD-[TYPE]-[TOPIC].md`
- Add at least one wikilink to an existing note it connects to
- Move from INBOX to the correct folder

Inbox is empty. The vault is organized.

---

## Weekly Note Audit

Once per week, identify notes that have been sitting in active folders without being used or connected.

```
Read all notes in 02 - PROJECTS, 03 - AREAS, and
04 - RESOURCES that have not been accessed or linked
from any other note in the last 14 days.

For each unaccessed note:

1. Can this note contribute to any active project
   or decision in CLAUDE.md?
   If yes: create a link from the relevant project
   or area note pointing to this note.

2. Does this note connect to anything currently
   active in the vault?
   If yes: add the wikilink in both directions.

3. If the note connects to nothing active:
   Flag it with #status/review

Notes with #status/review get one more audit cycle.
If still unconnected after two consecutive audits:
archive them.
```

**The logic behind the audit:** Notes that do not connect to anything active are not currently useful. They belong in the archive until something makes them relevant. An archived note that becomes relevant again is easy to retrieve. A vault full of disconnected notes that accumulate without being used is noise that degrades the signal of genuinely useful notes.

---

## Maps of Content (MOCs)

A Map of Content is a note whose purpose is to link to other notes — a navigation hub for a cluster of related knowledge. See `map-of-content` skill for the full creation and maintenance workflow.

**Quick reference:**
- Create when a topic has 20+ notes
- MOCs live in `06 - SYSTEM/MOCs/`
- A MOC links to notes; it does not contain original ideas
- Every link needs a one-sentence explanation of what it contributes
- The Open Questions section is the most important part

**When to check if a MOC is needed:**
- The Writing Activator returns 10+ notes for a single topic → create or update a MOC
- A connection report surfaces a cluster of 5+ related notes → these are MOC candidates
- The user asks "what do I know about [topic]?" and no MOC exists → create one

---

## Quarterly Vault Review

Organization degrades over time without maintenance. Run a quarterly review (every 3 months) to keep the system accurate and the vault clean.

**Four checks:**

### 1. Folder Audit
Does every folder still represent content you actively use? Are there folders with fewer than 5 notes that could be merged? Are there topics in `04 - RESOURCES/topics/` that have grown enough to need their own subfolder?

Walk every top-level folder. Remove or merge folders that no longer serve an active retrieval need.

### 2. Tag Audit
Pull up the tag list. Are all tags still relevant? Remove tags appearing on only 1–2 notes — they are noise. Check if any topics have grown to 20+ notes and now warrant a MOC.

Also check for duplicate tags (`#ai`, `#artificial-intelligence`, `#machine-learning` all meaning the same thing) and consolidate.

### 3. Archive Sweep
Walk `02 - PROJECTS` and `03 - AREAS`. Are there completed projects still sitting in PROJECTS? Outdated area notes? References in `04 - RESOURCES` that are no longer accurate?

Move anything inactive to `05 - ARCHIVE`. The goal is that everything in the active folders is genuinely active.

### 4. Naming Inconsistencies
Search for notes that do not follow the `YYYY-MM-DD-[TYPE]-[TOPIC].md` convention. Batch rename to fix inconsistencies. A vault with consistent naming is significantly more searchable than one where some notes follow the convention and some do not.

**Time commitment:** 30 minutes to 2 hours depending on vault size. The investment pays back every time a note is found in 10 seconds rather than 10 minutes.

---

## Claude Natural Language Retrieval

When the vault is connected to Claude Code via the Filesystem MCP, notes become searchable in natural language instead of requiring exact queries:

```
"Find all notes about pricing strategy I created in the last six months."
"What have I written about managing energy versus managing time?"
"Show me every project note that is currently active and has a deadline before July."
"What do my notes say about the relationship between focus and output quality?"
```

Claude reads vault structure, properties, and content — returning relevant notes with context about why they matched.

**The combination that makes this powerful:** A well-organized vault (right structure, consistent naming, complete frontmatter) gives Claude accurate retrieval. Claude's natural language understanding makes the system's power accessible without requiring exact queries or remembering which folder something is in.

The organizational system makes Claude's retrieval accurate. Claude's intelligence makes the organizational system's power accessible.

---

## Progressive Reorganization

If the vault is currently disorganized, do not start over. Reorganize progressively. A vault reorganized in stages becomes progressively more useful with each stage rather than requiring a big-bang restructure that never gets completed.

**Stage 1 — Week 1: Create the structure**
Create the 7 folders. Do not move anything yet. Just create the structure so new notes have a home.

**Stage 2 — Week 2: File new notes correctly**
File every new note into the correct folder from the moment of creation. Apply the naming convention and frontmatter to every new note. Do not touch old notes yet.

**Stage 3 — Week 3: Process the backlog**
Work through old notes and refile them with correct naming and properties. Do not try to do this all at once — 20 minutes per day for a week handles most vaults.

**Stage 4 — Month 2: Tags and connections**
Apply tags retroactively to the most important notes. Create the first MOC for the topic you engage with most. Start running the weekly note audit.

**Stage 5 — Month 3: First quarterly review**
Run the first full quarterly review. By this point the vault has enough organized material that the review will surface real structural improvements.

The vault does not become perfectly organized on day one. It becomes progressively more organized every week the system is used. After six months the vault that used to be a source of frustration becomes a system you can trust.

---

## Health Indicators

A healthy vault shows these signs:
- Every note in `00 - INBOX` is from the last 48 hours
- Every note in `02 - PROJECTS` belongs to a project with a clearly defined outcome
- Most notes in `04 - RESOURCES` have at least one wikilink from another note
- Tags follow the three-category system consistently
- MOCs exist for topics with 20+ notes
- The archive is the largest folder (most notes should eventually be archived)

An unhealthy vault shows these signs:
- INBOX has notes older than a week
- `02 - PROJECTS` contains completed projects never moved to archive
- Most notes in `04 - RESOURCES` have no links
- Tags are inconsistent or contain dozens of 1-note tags
- `05 - ARCHIVE` is empty or tiny (nothing is ever archived)
