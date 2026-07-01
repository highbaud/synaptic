---
name: vault-prompts
description: Quick-reference cheat sheet of all Synaptic prompt workflows — copy, paste, and run. Covers note creation, capture processing, connections, and daily use. Use when the user wants a list of ready-to-run prompts, asks "what prompts should I use for X," or wants to batch process their vault in a single session.
version: 0.1
---

# Vault Prompts — Quick Reference

All prompts, organized by what you are trying to do. Copy the prompt, fill in the brackets, and run.

---

## CAPTURE PROCESSING

### Process today's inbox
```
Process all notes in 00 - INBOX.
For each note:
1. Can it contribute to an active project or decision in CLAUDE.md? (yes → process, no → archive)
2. For notes to process: rewrite in my own words, identify connections, determine placement (PARA).
3. Log: what was filed, what was archived, what connections were made.
```
→ Full workflow: see `capture-processor` skill

---

### Morning pass (5 minutes)
```
Here are my rough notes from yesterday: [paste yesterday's notes or daily note]

Three things only:
1. What did I decide or commit to? (not what I thought about — what I decided)
2. The single most interesting idea worth developing further.
3. One concrete next action I can start in 30 minutes.
```

---

### Daily reflection
```
Here is what I captured today: [paste or describe]

1. Most important thing I did or decided?
2. What would I do differently?
3. Main open thread for tomorrow?
4. Any idea worth a permanent note? (draft title if yes)
5. Does anything today connect to a bigger vault pattern?
```

---

## NOTE CREATION

### Turn a capture into a permanent note
```
Raw note: [paste capture]

Convert to a permanent note for 04 - RESOURCES/topics/:
1. Title as a principle (full sentence, not a label)
2. 3–5 sentences in my own words (claim, reasoning, implication)
3. Key Tension: what makes this non-obvious or worth keeping?
4. Two connections to existing vault notes (with link text)
5. Frontmatter: type: resource, status: draft, date, tags, source
6. Filename: YYYY-MM-DD-resource-[topic-slug].md
```
→ Full workflow: see `permanent-note` skill

---

### Book or article note
```
I just read: [title and author]
Highlights: [paste or summarize]

For 01 - NOTES/books/:
1. Main thesis in one sentence.
2. 3–5 key insights, in my own words.
3. Does this support, contradict, or complicate something I already believe?
4. Two questions the book raises that it doesn't answer.
5. My take: agree with, disagree with, want to push back on.
6. Frontmatter: type: book, author, finished, rating, key_insight
7. Filename: YYYY-MM-DD-book-[title-slug].md

Note: the 1–2 best ideas → separate permanent notes in 04 - RESOURCES/topics/
```

---

### Article → vault
```
Article: [paste or summarize]

Extract:
1. Main argument in one sentence.
2. 2–3 specific claims worth remembering.
3. Best example or quote.
4. How this relates to [my current focus].
5. My reaction: agree / disagree / want to challenge.

Format as Obsidian note (frontmatter + body in my voice + suggested links).
Filename: YYYY-MM-DD-resource-[topic-slug].md
```

---

### Meeting note processor
```
Raw meeting notes: [paste]

Extract for 01 - NOTES/meetings/:
1. KEY DECISIONS — what was decided (not discussed)?
2. ACTION ITEMS — [Owner] — [Action] — [Due date]
3. IMPORTANT INFORMATION — what I learned beyond this meeting
4. OPEN QUESTIONS — raised but not resolved
5. CONNECTIONS — which active project does this feed?

Frontmatter: type: meeting, attendees, decisions, actions
Filename: YYYY-MM-DD-meeting-[topic-slug].md
```

---

## CONNECTIONS

### Weekly connection surface
```
Read notes created/modified in the last 7 days across 02 - PROJECTS, 03 - AREAS, 04 - RESOURCES.

For each recent note, scan for existing vault notes with a meaningful connection:
- Same principle, different domain
- Productive contradiction (the tension is the insight)
- Evidence relationship (one supports or undermines a claim in another)
- Unnamed pattern across 3+ notes

Report: [Note A] ↔ [Note B] — connection type — what reading them together reveals.
Skip topical overlap. Skip already-linked pairs.
```
→ Full workflow: see `connection-finder` skill

---

### Connect two notes
```
Note 1 — [title]: [key idea]
Note 2 — [title]: [key idea]

1. What conceptual thread connects them (mechanism, not topic)?
2. Strong (reading together changes how I understand both) or weak (just topically close)?
3. If strong: link text for each note. What does the connection add?
4. Is there a third note worth writing that bridges them?
```

---

### Find the pattern across 3+ notes
```
These notes feel connected: [list titles + one-sentence summaries]

1. What structural pattern do they share (mechanism, not topic)?
2. Name the pattern specifically enough to distinguish it.
3. Which note expresses it most clearly (the anchor)?
4. Draft a permanent note title for the pattern itself.
```

---

### Idea synthesis
```
Note 1 — [title]: [key idea]
Note 2 — [title]: [key idea]
Note 3 — [title] (optional): [key idea]

1. What single principle connects all of these?
2. What non-obvious insight emerges from combining them?
3. Title for a synthesis note (full sentence principle)?
4. Worth writing the synthesis note, or just topically adjacent?
```

---

## VAULT INTELLIGENCE

### Query your vault
```
synaptic query "what do I know about [topic]?"
```
Semantic + keyword search across all notes. Cited sources. Optional `--save` to vault.

---

### Decision feeder
```
I am deciding: [decision in one sentence]

Scan the vault for:
- Notes that provide relevant evidence or precedent
- Notes that challenge my current assumptions
- Connections I might have missed

What does the vault know about this decision that I am not currently using?
```
→ Full workflow: see `intelligence-layer` skill

---

### Writing activator
```
I am writing about: [topic or working title]

From the vault, surface:
- The 3–5 strongest permanent notes on this topic
- Productive contradictions worth building into the argument
- Evidence notes that support or challenge the main claim
- Gaps: what the vault does not cover that this piece needs

What is the vault's strongest argument on this topic?
```
→ Full workflow: see `intelligence-layer` skill

---

## INGEST (single source)

### File a source and update the vault
```
Source to ingest: [paste article, transcript, excerpt, or notes]
Topic: [main subject]

PHASE 1 — SOURCE NOTE
File in 01 - NOTES/[books|courses|daily|meetings]/:
- Rewrite the core idea in my own words (not a quote or summary — my understanding)
- Frontmatter: type, status: draft, date, source, description (one-sentence claim), tags
- Add at least one wikilink to an existing permanent note in 04 - RESOURCES/topics/
- Filename: YYYY-MM-DD-[type]-[topic-slug].md
- This note is immutable after filing.

PHASE 2 — NEIGHBOR UPDATE
Scan 04 - RESOURCES/topics/ for permanent notes this source affects:
1. CONFIRMS existing claims → add citation wikilink to those notes
2. CONTRADICTS existing claims → add Key Tension entry: "[[source]] challenges this: [how]"
3. EXTENDS existing notes → add the new insight + wikilink
4. GAPS → list permanent notes that should now be written

Report: [source note filed] + [n permanent notes updated] + [n gaps flagged]
```
→ Full workflow: see `karpathy-ingest` skill

---

## VAULT HEALTH

### Weekly audit (45 minutes)
1. `synaptic health` — check inbox size, unlinked notes, missing frontmatter
2. Process inbox (morning pass prompt above)
3. Run weekly connection surface (connection prompt above)
4. `synaptic contribution-report` — which notes have never contributed?
5. Promote 1–2 draft notes to `status: reference` or archive them

→ Full workflow: see `weekly-ritual` skill

---

### Contribution check
```
synaptic contribution-report
```
Shows which notes have contributed to outputs vs. which have sat unused. Notes with zero contributions after 6 months are candidates for the archive.
