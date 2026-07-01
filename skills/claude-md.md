---
name: claude-md
description: Read, generate, and apply the user's CLAUDE.md — the personal intelligence activation file that tells every workflow what usefulness means for this specific person. Use at the start of any significant vault task, when generating a new CLAUDE.md for a user, or when a workflow needs to evaluate whether something is worth keeping.
version: 0.2
---

# CLAUDE.md Skill

CLAUDE.md is the document that tells every Synaptic workflow what usefulness means for this specific user. Without it, the system can organize notes but cannot evaluate whether a note is worth keeping, connecting, or surfacing.

It lives at `06 - SYSTEM/CLAUDE.md`.

---

## Personal vs. Shared Vaults

`synaptic init` asks up front whether the vault is personal or a shared team brain, and the CLAUDE.md it generates differs accordingly. This skill covers both — check which shape a vault already has (a shared CLAUDE.md opens with a "Team Charter" section) before generating or editing.

**Personal** (the default, covered in full below): one person's active projects, decisions, writing topics, and voice.

**Shared** replaces the personal framing with a Team Charter and adds two things a single-user vault doesn't need:
- **A named champion** — the person empowered to add sources, grant access, and correct the vault without needing approval for each change. This is not optional decoration: an unempowered champion is the single most common reason a shared vault stalls. If a shared CLAUDE.md has no named champion, or the champion needs sign-off for routine changes, flag it.
- **An attribution convention** — notes carry a `contributor:` frontmatter field (see `vault-structure` skill). This is a convention Synaptic doesn't enforce, not real access control; anyone who can open the vault folder can read and write everything in it. Say so plainly if a user asks whether shared mode restricts who can do what — it does not.

Both modes share the same processing standards, maturity levels, and skills. The difference is entirely in what CLAUDE.md says the vault is for and who is accountable for it — not in how notes get filed, tagged, or connected.

A shared CLAUDE.md also documents how the vault gets sharper: not from someone maintaining a wiki, but from corrections during real use (see `synaptic review`'s rejection-pattern surfacing, described in section 5 below). Treat a shared vault that only grows from deliberate document uploads as stalling, even if the note count looks healthy.

---

## What CLAUDE.md Contains

### 1. What I Use Notes For
The primary and secondary use cases for notes. What the user actually produces with their knowledge.

This section answers: what is this vault for?

```
Primary: [writing/decisions/work/research/teaching]
Secondary: [secondary use case]
What I produce: [articles, decisions, client briefs, presentations, etc.]
```

### 2. My Active Projects
The specific projects that notes should be feeding right now. Updated whenever a project starts or completes.

When processing a capture, this list is the primary filter for whether a note belongs in `02 - PROJECTS/`.

```
- [Project name] — [one line description of what it is and what it needs]
- [Project name] — [one line description]
```

### 3. Current Active Decisions
The actual questions the user is trying to answer right now. These are the highest-value targets for the Decision Feeder workflow.

When a note could inform any of these decisions, it is automatically worth keeping.

```
- [Decision or question being actively worked on]
- [Decision or question being actively worked on]
```

### 4. My Writing Topics
The topics the user writes about regularly. When processing captures, these topics define which notes belong in `04 - RESOURCES/topics/` vs. which should be archived.

```
- [Topic] — [what angle or perspective the user brings to it]
- [Topic] — [what angle]
```

### 5. What Makes a Note Useful For Me
The most important section. Explicit criteria for what gets processed vs. archived.

```
Useful: [specific description of captures that have contributed to output]
Not useful: [specific description of captures that consistently go unused]
```

**This section should not be written from scratch — it should be corrected into shape.** The user rarely knows their own filtering criteria well enough to write it down cold. They know it by reacting: rejecting a tag suggestion, archiving a note, correcting a query answer. `synaptic review` tracks rejected tag suggestions and surfaces a pattern once the same tag has been turned down 3+ times — that pattern is a candidate line for "Not useful," generated from actual correction rather than upfront guesswork. When `synaptic review` reports a rejection pattern, offer to add it to this section rather than waiting for the user to notice and write it themselves.

### 6. Processing Standards
The bar a note must clear to move from INBOX to a permanent home.

```
A note is ready to file when:
- It is written in my own words, not copied from a source
- It connects to at least one existing note
- It could contribute to at least one active project or decision
- Its title describes the idea, not the source

A note should be archived when:
- The project or decision it relates to is complete
- The information is outdated
- It has not been accessed in 6 months
- It has no connection to anything currently active
```

### 7. Output Goals
What the user wants to produce from their notes. Be specific — this drives the Output Generator workflow and is the long-term success measure for the vault.

```
[Specific, measurable output goal]
Example: "one long-form article per week on [topic]"
Example: "monthly decision review for [team/area]"
Example: "quarterly synthesis of learnings from [domain]"
```

### 8. Voice & Interaction Style (optional)
How Claude should talk to this user, across every session — not just the local-model plugin. This is the file that makes responses sound like the user's own assistant instead of a generic chatbot, because tone gets set once here and every answer inherits it.

```
- Talk to me like [a sharp operator / a research partner / a collaborator], not a support bot.
- Lead with the conclusion, then the reasoning. [or: walk me through the reasoning first.]
- [No hedging / push back if I'm wrong / ask before assuming / be terse].
- [Any other standing instruction about tone, structure, or how much explanation to include.]
```

For vaults that keep growing this section, split it into its own file — `06 - SYSTEM/personality.md` — and reference it from CLAUDE.md with a one-line pointer: "Voice: see `personality.md`." Keeping it separate makes tone easy to tweak without touching active project state, and it is the one section that rarely needs to change once it is right.

### 9. Local AI System Prompt (optional)
The system prompt to use when the Obsidian plugin connects to a local model. Storing it here means every agent reading CLAUDE.md can apply it consistently.

The default prompt that works for most vaults:
```
You are a thinking partner helping me work through ideas in my Obsidian vault.
You are direct, specific, and concise. You help me find non-obvious connections
between ideas, surface the tensions in my thinking, and develop half-formed
captures into ideas worth keeping. You do not pad responses with affirmations
or restate what I just said. When I share a note or ask a question, respond
in a way that genuinely advances my thinking. If an idea is weak, say so and
explain why. If a note is not worth keeping, say that.
```

Customize by adding context about the user's domain, voice, or specific tasks. The system prompt is the single biggest quality lever for local model output — a specific prompt outperforms a generic one at every model size.

---

## Full Template

Copy this into `06 - SYSTEM/CLAUDE.md` and fill it in. A filled example lives at `examples/vault/06 - SYSTEM/CLAUDE.md`.

```markdown
# CLAUDE.md — Intelligence Activation File

## What I Use Notes For
Primary: 
Secondary: 
What I produce: 

## My Active Projects
- 
- 

## Current Active Decisions
- 
- 

## My Writing Topics
- 
- 

## What Makes a Note Useful For Me
Useful: 
Not useful: 

## Processing Standards
A note is ready to file when:
- It is written in my own words, not copied from a source
- It connects to at least one existing note
- It could contribute to at least one active project or decision
- Its title describes the idea, not the source

A note should be archived when:
- The project or decision it relates to is complete
- The information is outdated
- It has not been accessed in 6 months

## Output Goals

## Voice & Interaction Style
<!-- How I want Claude to talk to me, every session. Split into personality.md if this grows. -->
- 
- 

## Local AI System Prompt
<!-- Paste into Obsidian plugin settings. Update to match your domain and voice. -->
```
You are a thinking partner helping me work through ideas in my Obsidian vault.
You are direct, specific, and concise. You help me find non-obvious connections
between ideas, surface the tensions in my thinking, and develop half-formed
captures into ideas worth keeping. You do not pad responses with affirmations.
When I share a note or ask a question, respond in a way that genuinely advances
my thinking. If an idea is weak, say so. If a note is not worth keeping, say that.
```

```

---

## How Each Workflow Uses CLAUDE.md

| Workflow | How it uses CLAUDE.md |
|----------|----------------------|
| **Capture Processor** | Checks Active Projects and Active Decisions to assess whether a capture is worth keeping |
| **Morning Capture Pass** | Reads Active Projects to identify what signal matters from yesterday's captures |
| **Decision Feeder** | Reads Active Decisions to know which questions to surface notes for |
| **Writing Activator** | Reads Writing Topics to scope the vault scan |
| **Writing Unsticker** | Reads voice/style notes to calibrate diagnostic tone |
| **Connection Finder** | Uses Active Projects and Writing Topics to prioritize which connections are most valuable |
| **Daily Thinking Partner** | Reads voice and active context to frame thinking support correctly |
| **Output Generator** | Reads Output Goals and voice description to shape the final output |
| **Weekly Ritual** | Reads Active Projects to know what is active vs. should be closed |
| **Weekly Note Audit** | Uses Processing Standards to decide which notes should be archived |
| **Project Completion** | Checks that project outcome matches Active Projects entry before closing |

---

## Generating CLAUDE.md for a New User

If `06 - SYSTEM/CLAUDE.md` does not exist, first ask: **is this a personal vault, or a shared vault multiple people will write to?** That answer picks the question set.

### Personal

1. What do you mainly use your notes for — writing, making decisions, tracking projects, research, something else?
2. What are you actively working on right now? Name 2–4 projects.
3. What are the most important decisions or questions you are working through right now?
4. What topics do you write or think about regularly?
5. Looking back at notes you have actually used — what did they have in common? What kinds of captures do you consistently ignore?
6. What is one concrete thing you want to produce from your vault in the next 90 days?
7. How do you want Claude to talk to you? Direct and terse, or walk-through-the-reasoning? Should it push back when it disagrees, or just flag concerns and defer?
8. Are you running a local AI model (Ollama / LM Studio), cloud AI (Claude/GPT), or both? This determines how sensitive the thinking-partner prompts can be.

### Shared

1. What is this vault for — team, project, purpose?
2. Who is the champion? This must be a real, named person empowered to add sources, grant access, and fix mistakes without asking permission each time. Push back if the answer is vague ("whoever's around") — an unaccountable champion is the top predictor of a shared vault failing.
3. Who else writes to this vault? Names or roles.
4. What does the team produce from this vault?
5. What are the active projects and open decisions right now?
6. What makes a note useful to the team, not just to one person?
7. If the vault gives a wrong or outdated answer, who is responsible for correcting it? (Often the champion, but confirm.)

Generate the shared CLAUDE.md with the Team Charter shape (see "Personal vs. Shared Vaults" above), including the attribution convention and the note that context compounds from corrections, not just uploads.

Generate the file, then ask the user to review and correct it before any significant vault work begins.

---

## Behavior

At the start of any significant task:

1. Check if `06 - SYSTEM/CLAUDE.md` exists
2. If it exists: read it fully and extract the active projects, current decisions, writing topics, and processing standards before doing anything else
3. If it does not exist: offer to generate it before proceeding
4. If it is incomplete: flag the missing sections and offer to fill them in

Never override explicit instructions in CLAUDE.md. If CLAUDE.md says a type of note is not useful, do not argue — archive it.

The vault should learn the user's patterns. If the same type of capture consistently gets archived, note this and suggest updating the "Not useful" section of CLAUDE.md.
