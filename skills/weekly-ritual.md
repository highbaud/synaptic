---
name: weekly-ritual
description: Run the complete 45-minute weekly vault maintenance session — inbox processing, connection surface, note audit, and weekly review note. This is the single practice that keeps the vault accurate and compounding. Use when the user says it is time for their weekly review, asks to run the weekly ritual, or at the start of each week.
version: 0.1
---

# Weekly Ritual Skill

The weekly ritual is the maintenance practice that keeps the vault worth using. Without it, notes accumulate without connecting. With it, a vault becomes progressively more useful every week.

Total time: 45 minutes. Run once per week, ideally at a fixed time.

---

## The Four Parts

| Part | Time | What happens |
|------|------|-------------|
| 1. INBOX clear | 15 min | Process everything from the week. File or archive. |
| 2. Connection surface | 15 min | Find non-obvious connections among this week's notes. |
| 3. Note audit | 10 min | Flag unconnected notes. Move stale ones to review. |
| 4. Weekly review note | 5 min | Write the weekly synthesis and file it. |

Do them in order. Each part feeds the next.

---

## Part 1: INBOX Clear (15 minutes)

Run the full capture-processor Daily Processing Run on everything in `00 - INBOX`.

For each note:
1. Can it contribute to an active project or decision in CLAUDE.md? → PROCESS
2. Does it have no active contribution path? → ARCHIVE DIRECTLY

For notes marked PROCESS:
- Rewrite in your own words
- Add universal frontmatter: type, status, date, tags
- Rename to naming convention: `YYYY-MM-DD-[TYPE]-[TOPIC].md`
- Add at least one wikilink to an existing note
- Move to the correct PARA folder

**Target:** INBOX empty at the end of Part 1.

See `capture-processor` skill for the full processing prompt.

---

## Part 2: Connection Surface (15 minutes)

```
Read all notes created or modified in the last 7 days
across 02 - PROJECTS, 03 - AREAS, and 04 - RESOURCES.

For each recent note, scan the full vault for existing
notes that share a meaningful connection —
not just notes on the same topic, but notes where
reading them together creates insight that neither note
provides alone.

Connection types to look for:
- Same principle, different domains
- Productive contradiction (two notes making conflicting claims)
- Evidence relationship (one note supports or challenges another)
- Unnamed pattern (same structure appears across 3+ notes)

For each strong connection found:
1. Name both notes
2. Identify the connection type
3. Describe what new insight emerges from reading them together
4. Add wikilinks in both notes (with one-sentence explanation)

Only surface connections that are genuinely non-obvious.
Skip anything already linked. Skip topic overlap.

Report: number of notes reviewed, connections found,
links added.
```

If no strong connections exist this week, say so. A report that forces weak connections is worse than no report.

---

## Part 3: Note Audit (10 minutes)

Run `synaptic health` before anything else. Pay specific attention to the **unlinked notes** section.

**Orphan check first.** A note with zero outgoing wikilinks is an orphan — it cannot surface in the Connection Surface step and will not appear in search results rooted in other notes. Unlike notes that are just unaccessed, orphans are structurally invisible. Fix them before running the audit prompt below.

```
synaptic health

Review the "unlinked notes" output. For each orphan note (zero outgoing links):
- If the idea is worth keeping: find one note it connects to and add the wikilink now.
- If the idea has no meaningful connection after 30 seconds of consideration: archive it.

No note should leave Part 3 with zero outgoing links.
```

Then run the standard audit on everything that hasn't connected recently:

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
   Flag it with #status/review in frontmatter.

Notes already flagged #status/review from the prior audit:
If still unconnected: move to 05 - ARCHIVE.
Two consecutive audit cycles without a connection = archive.
```

---

## Part 4: Weekly Review Note (5 minutes)

After the three maintenance steps, write a weekly review note using the `weekly-review` template.

```
Using 06 - SYSTEM/templates/weekly-review.md,
write this week's review note.

Fill in:
1. INBOX counts (processed vs. archived directly)
2. What I actually worked on (what the notes show, not what I planned)
3. The most important decision or commitment in this week's notes
4. Any connections found in Part 2 worth highlighting
5. Notes still flagged for review after Part 3
6. Next week intention (one sentence)

File as: 01 - NOTES/daily/YYYY-MM-DD-weekly-review-[week-of].md
```

---

## Reducing the Ritual (When You Are Behind)

If the vault has been neglected for 2+ weeks, run the parts in order but cap each one:

- INBOX: Process the 10 most recent items only. Archive the rest.
- Connection surface: Run only on notes from the last 3 days.
- Note audit: Only flag notes — do not archive this session.
- Weekly review: Write a recovery note instead of a standard review.

Do not try to fully catch up in one session. The goal is to restart the practice, not to achieve perfection.

---

## What to Do When the Ritual Surfaces a Problem

**INBOX is overwhelming (20+ notes):** You are capturing too much or processing too rarely. Run a Triage Pass — read each INBOX note and ask: would I actually use this? Archive anything with a "no." Then do the 15-minute processing run on what remains.

**No connections found three weeks in a row:** The vault is growing but not deepening. Two causes: (1) notes are being filed but not rewritten into your own voice, or (2) the vault contains too many notes on too many unrelated topics. Narrow your writing topics in CLAUDE.md.

**Archive is empty:** You are never archiving. Projects are completing but their notes are staying in PROJECTS. Run the project-completion skill on any finished project immediately.

**review flags keep accumulating:** Notes are being created that do not connect to anything active. Check if your active projects and writing topics in CLAUDE.md are accurate. If not, update them.

---

## Scheduling It (Unattended)

The ritual works best as a habit, and the most reliable habit is one you don't have to remember. Once the manual version feels natural, wire it to run on its own.

**The mechanism:** a scheduled job invokes Claude Code non-interactively with `-p` (print mode — runs one prompt and exits), from a working directory where Synaptic's skills are discoverable (the vault root, or wherever `skills/` is loaded via `.claude/skills/` or a plugin directory).

**macOS / Linux (cron):**
```bash
# crontab -e — runs nightly at 3am
0 3 * * * cd /path/to/vault && claude -p "Run the capture-processor Daily \
Processing Run on 00 - INBOX, then run the Part 2 Connection Surface from \
the weekly-ritual skill on notes touched in the last 7 days. Report what \
was filed, archived, and connected."
```

```bash
# Weekly synthesis — Sundays at 6am
0 6 * * 0 cd /path/to/vault && claude -p "Run the full weekly-ritual skill: \
INBOX clear, connection surface, note audit (including the orphan check \
via synaptic health), and write the weekly review note."
```

**Windows (Task Scheduler):**
Create a Basic Task, trigger Daily/Weekly at the desired time, action "Start a program":
- Program: `claude`
- Arguments: `-p "Run the capture-processor Daily Processing Run on 00 - INBOX..."`
- Start in: `F:\path\to\vault`

**What to automate vs. keep manual:**

| Cadence | What runs | Why |
|---------|-----------|-----|
| Nightly | INBOX processing (capture-processor) | Keeps the inbox from ever piling up; low-risk, mechanical filing |
| Nightly | Recent-connection surface (last 24–48h) | Catches links while the source material is still fresh |
| Weekly | Full ritual: audit + orphan check + review note | Needs judgment calls (archive vs. keep) — review the output before trusting it fully |

Start with the weekly cadence run by hand for a few cycles before automating anything. Automating a workflow you haven't validated just files mistakes faster.

**One rule that doesn't change with automation:** a scheduled job should never be granted delete access beyond moving notes to `05 - ARCHIVE`. Archiving is reversible; deletion is not. If a cron job can delete a file, eventually it will delete the wrong one — control this with file permissions or a wrapper script, not with wording in the prompt.

---

## Rules

- Run this at a fixed time every week. The ritual is most valuable as a habit, not a one-off.
- Always read CLAUDE.md before Part 1. The ritual is useless without knowing what is currently active.
- Do not skip Part 4. The weekly review note is the memory that makes this ritual compound.
- Use `synaptic health` before starting. It surfaces exactly what needs attention.
- A 30-minute partial ritual is better than a 2-hour perfect ritual that happens once a month.
