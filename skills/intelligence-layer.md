---
name: intelligence-layer
description: Five production workflows that convert accumulated vault notes into output — the Decision Feeder (surface everything the vault knows about a decision), the Writing Activator (brief before writing), the Writing Unsticker (diagnose and unstick a draft), the Output Generator (synthesize notes into a finished draft), and the Daily Thinking Partner (private real-time thinking support). Use when the user is making a decision, starting to write, stuck on a draft, ready to produce a finished piece, or wants to think through a problem with support.
version: 0.3
---

# Intelligence Layer Skill

This skill contains the three workflows that convert a vault from an archive into a production system. Each workflow answers a different question:

- **Decision Feeder** — What does my vault know about this decision?
- **Writing Activator** — What does my vault know about this topic, and how should I structure a piece about it?
- **Output Generator** — Turn everything my vault knows about this topic into a finished draft.

The key constraint on all three: they use only what is already in the vault. They do not add information from outside. They surface what the user already knows.

---

## Workflow 1: Decision Feeder

**When to use:** The user is actively working through a decision and wants to know what their accumulated notes say about it.

**What it does:** Scans the full vault for every note that is relevant to the decision — not just notes explicitly tagged with it, but notes that a thoughtful person would consider when making it. Synthesizes them into a decision brief.

```
I am working on this decision: [DECISION DESCRIPTION]

Scan all of 02 - PROJECTS, 03 - AREAS, and 04 - RESOURCES.

Find every note that is relevant to this decision.
Not just notes explicitly tagged with this decision.
Notes that contain information, perspectives, frameworks,
or evidence that a thoughtful person would consider
when making this decision.

For each relevant note found:
- State the note title
- State what the note contains that is relevant
- State whether it supports, challenges, or adds nuance
  to the decision

Then synthesize everything relevant into a decision brief:

CONTEXT: What background does the vault provide?
FOR: Notes and evidence supporting one direction
AGAINST: Notes and evidence supporting another direction
NUANCE: Notes that complicate the picture
GAPS: What the vault does not know that matters
RECOMMENDATION: The most defensible position given
  what the notes collectively support

Do not add information from outside the vault.
Only synthesize what is already in the notes.
```

**Output location:** Save the decision brief as a project note in `02 - PROJECTS/[decision-name]/` or in the relevant Area under `03 - AREAS/`.

**Why this matters:** The answer to a current decision is often already in past captures — from different contexts, different sources, different weeks. The Decision Feeder retrieves it. Most people would never manually surface those notes for a decision they are actively making.

---

## Workflow 2: Writing Activator

**When to use:** The user is about to write an article, report, email, proposal, or any substantial piece. Run this before opening a blank document.

**What it does:** Scans the vault for everything relevant to the topic and produces a writing brief — the strongest argument the notes support, the evidence, the counterarguments, the gaps, and a structure suggestion.

```
I am about to write about: [TOPIC OR WORKING TITLE]

Scan 02 - PROJECTS, 03 - AREAS, and 04 - RESOURCES
for everything relevant to this topic.

Produce a writing brief:

STRONGEST ARGUMENT
The most defensible claim my notes support on this topic.
Not what I should argue — what my notes actually support.

EVIDENCE
Specific notes that provide evidence for that argument.
Include note titles and what each note contributes.

COUNTERARGUMENTS
Notes that challenge or complicate the argument.
Be honest about what the vault says against the position.

SPECIFIC DETAILS
Any statistics, examples, case studies, or quotes in
my notes that should appear in the piece.

GAPS
What is missing from my notes that I should research
or think through before writing?

STRUCTURE SUGGESTION
Given what my notes contain, what structure would make
the strongest piece? Propose a section outline based
only on what the notes support.

Do not suggest what I should write.
Show me what my notes already know.
```

**Output location:** Save the writing brief in the relevant project under `02 - PROJECTS/` before writing the piece.

**Why this matters:** Writing from a brief produced by your own notes is fundamentally different from writing from scratch. You are articulating what you already know rather than trying to generate ideas in real time. The piece is stronger because it is grounded in accumulated evidence rather than in-the-moment thinking.

---

## Workflow 3: Output Generator

**When to use:** A piece of writing, decision summary, project report, or analysis is ready to be produced. The vault has enough notes on the topic. Run this to synthesize them into a finished draft.

**What it does:** Reads all notes tagged with a project or topic, synthesizes them into a complete draft written in the user's voice, saves it to the correct location.

```
I need to produce: [OUTPUT TYPE AND DESCRIPTION]
Relevant tags/project: [TAG OR PROJECT NAME]

Read all notes tagged with [TAG] or filed under
02 - PROJECTS/[PROJECT] or 04 - RESOURCES/topics/[TOPIC].

Also read any connection reports that reference this topic.

Produce a complete draft of [OUTPUT TYPE] that:
- Uses only information from the vault notes
- Is written in the user's voice as described in CLAUDE.md
- Synthesizes across notes rather than summarizing each one
- Produces a claim or insight that no individual note
  contains but that the combination of notes supports
- Has a clear structure with a beginning, middle, and end

After drafting, identify:
STRONGEST SECTION: Which section is best supported
  by the vault evidence?
WEAKEST SECTION: Which section has the thinnest
  support from the notes?
WHAT IS MISSING: What would make this piece significantly
  stronger if the vault contained it?
```

**Output location:** Save the draft as a project note under `02 - PROJECTS/[project]/`. When the piece is finalized, the project can be moved to `05 - ARCHIVE/` with the finished output included.

**Why this matters:** Months of accumulated notes synthesized into a finished piece in one session. The Output Generator is the moment the entire system justifies itself.

---

## Synthesis Notes

Sometimes the output of the intelligence layer is not a finished piece but a synthesis note — a new resource note that combines insights from several notes into a single, more powerful note that did not exist before.

Synthesis notes live in `04 - RESOURCES/topics/` and follow the naming convention: `YYYY-MM-DD-resource-synthesis-[topic].md`.

A synthesis note must:
- Contain a claim or insight that no individual source note contains
- Cite the specific source notes it draws from with wikilinks
- Be written in the user's voice, not as a summary of the sources
- Include a `key_insight` frontmatter field with one sentence naming the core synthesis

A synthesis that only summarizes existing notes is not a synthesis. It is a table of contents. If you cannot identify the insight that emerges from the combination, the synthesis is not ready.

---

## Output Quality Standard

Every output from the intelligence layer must pass this test:

**Does this output say something that no individual note in the vault says?**

If the answer is no — if the output is just a well-organized summary of existing notes — it is not a genuine intelligence output. It is a retrieval operation dressed up as synthesis.

The real test: could the user have produced this output by reading the source notes individually? If yes, the synthesis step has not added value. The output should produce insight the user could not have reached by reading one note at a time.

---

## Workflow 4: Writing Unsticker

**When to use:** A draft is stuck. You know what you want to say but the words are not coming, or the structure is wrong, or you cannot tell whether the argument works. Run this before staring at the document for another hour.

**What it does:** Diagnoses why the draft is stuck and provides exactly one step forward — not a rewrite, not a suggestion to add more research, just the next sentence or the structural repair that unlocks the rest.

```
I am writing about: [topic or working title]

Here is what I have so far: [paste draft]

I am stuck because: [describe what is not working —
the argument feels circular / I can't find the opening /
the middle section is wrong but I don't know why / other]

Do not rewrite this for me. Instead:
1. Tell me what the draft is actually arguing —
   not what I said I wanted it to argue, but what
   the words on the page currently support.

2. Tell me the one thing that is missing or broken.
   One thing. The diagnosis, not a list.

3. Give me the first sentence of the next paragraph only.
   Not a plan for the paragraph — the first sentence.
   Something I can write from.
```

**Why this works:** The stuck state is almost always diagnostic confusion — you cannot tell whether you are stuck because the argument is wrong, the structure is wrong, or the opening is wrong. Part 1 identifies which problem you actually have. Part 3 gives you traction without removing your authorship.

**Output location:** No note needed — this is an in-session diagnostic. If Part 2 surfaces a structural issue worth keeping (a wrong assumption, a missing concept), capture it as an INBOX note and process later.

---

## Workflow 5: Daily Thinking Partner

**When to use:** You are working through a problem — a business decision, a difficult conversation you are preparing for, a creative problem you are stuck on — and you want support thinking it through. The key word is *through*, not *at*: this is not research, it is active thinking.

**What it does:** Reads your current thinking, identifies what you are not seeing, and surfaces the question you should be asking rather than trying to answer the question you asked.

```
I am thinking through something and want to think out loud.
Here is where I am:

[Write 2–4 paragraphs of your current thinking on the problem.
 Be specific. Include what you have already considered and rejected.]

What am I not seeing?
```

This prompt runs entirely on what you write — not on vault notes. Its output is typically one of:
- A frame you have not considered
- An assumption your current thinking takes for granted
- A question that would clarify the decision if answered
- A tension you have been avoiding

**Privacy note:** This workflow is where local AI earns its setup time. The content you write for this prompt — sensitive business thinking, assessments of people, private strategy — stays on your machine. Run this on your local model, not through a cloud API.

**After the session:** If the thinking session surfaces a decision, capture it as a CLAUDE.md update. If it generates a useful insight, put it in INBOX for the next processing run.

---

## Synthesis Notes

Sometimes the output of the intelligence layer is not a finished piece but a synthesis note — a new resource note that combines insights from several notes into a single, more powerful note that did not exist before.

Synthesis notes live in `04 - RESOURCES/topics/` and follow the naming convention: `YYYY-MM-DD-resource-synthesis-[topic].md`.

A synthesis note must:
- Contain a claim or insight that no individual source note contains
- Cite the specific source notes it draws from with wikilinks
- Be written in the user's voice, not as a summary of the sources
- Include a `key_insight` frontmatter field with one sentence naming the core synthesis

A synthesis that only summarizes existing notes is not a synthesis. It is a table of contents. If you cannot identify the insight that emerges from the combination, the synthesis is not ready.

---

## Output Quality Standard

Every output from the intelligence layer must pass this test:

**Does this output say something that no individual note in the vault says?**

If the answer is no — if the output is just a well-organized summary of existing notes — it is not a genuine intelligence output. It is a retrieval operation dressed up as synthesis.

The real test: could the user have produced this output by reading the source notes individually? If yes, the synthesis step has not added value. The output should produce insight the user could not have reached by reading one note at a time.

---

## Rules

- Always read `06 - SYSTEM/CLAUDE.md` before running any workflow. The user's active projects and decisions determine the scope and relevance filter.
- Do not add information from outside the vault for Workflows 1–3 and 5. These surface what the user already knows.
- Cite specific note titles in all outputs. Unsourced claims in a synthesis are the intelligence layer equivalent of hallucination.
- Always identify gaps. The user should know what their vault does not know as clearly as what it does.
- Save outputs as notes in the vault. Intelligence that exists only in a chat response is lost.
- The Writing Unsticker (Workflow 4) is diagnostic, not generative — do not rewrite the user's draft. The goal is traction, not replacement.
- Run Workflow 5 (Daily Thinking Partner) on the local model whenever possible. This workflow handles sensitive thinking that should not leave the machine.
