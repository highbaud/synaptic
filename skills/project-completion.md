---
name: project-completion
description: Archive a completed project and extract its learnings into permanent notes. Covers the two-step close — moving the project folder to archive and distilling what was learned into 04 - RESOURCES/topics/ so the knowledge outlives the project. Use when a project is complete, when the user says a project is done, or as part of the weekly ritual when completed projects are found in 02 - PROJECTS.
version: 0.1
---

# Project Completion Skill

When a project ends, two things need to happen. The first is obvious: move it to the archive. The second is what most people skip: extract the learnings that should outlive the project.

A project note that goes into the archive without extraction is knowledge that dies. The next time you face a similar situation, you start from scratch. A project that is properly closed creates 2–4 permanent notes in `04 - RESOURCES/topics/` that will surface in future Decision Feeder and Writing Activator runs.

---

## Step 1: Identify Completion

A project is ready to close when:
- The defined outcome has been delivered, abandoned, or superseded
- No notes in the project folder have been accessed in 30 days
- The `next_action` field has been empty for two consecutive weekly reviews

When a project appears to be complete but is not formally closed, flag it with `#status/review` and ask the user to confirm before proceeding.

---

## Step 2: Extraction Pass

Before archiving, run the extraction pass:

```
Read every note in 02 - PROJECTS/[project-name]/.

Identify:

1. DECISIONS MADE
   Every significant decision documented in the project notes.
   What was decided. What was the reasoning. What alternatives were rejected.

2. WHAT WORKED
   Approaches, tools, patterns, or habits that produced good results.
   Be specific — not "communication was good" but "weekly async updates
   replaced standing meetings and reduced coordination overhead by half."

3. WHAT FAILED OR SURPRISED
   Things that did not go as expected. Surprises, wrong assumptions,
   approaches tried and abandoned.

4. DURABLE KNOWLEDGE
   Ideas, frameworks, or insights generated during this project that
   would be useful in future projects or decisions — regardless of
   whether those future situations look similar to this one.

For each piece of durable knowledge identified:
- Can it be expressed as a single atomic idea?
- Is it already covered by an existing permanent note in 04 - RESOURCES/topics/?
  If yes: add a wikilink from the existing note to this project.
  If no: create a new permanent note.

Generate the list of permanent notes to create.
Do not create them yet — confirm the list with the user.
```

---

## Step 3: Write the Permanent Notes

For each item on the confirmed extraction list, write a permanent note following the `permanent-note` skill standards:
- One clear idea, stated in the title
- Written in the user's own words
- Minimum two wikilinks to existing notes
- Key Tension section (mandatory)
- Frontmatter: `type: resource`, `status: reference`

File in `04 - RESOURCES/topics/` with naming convention `YYYY-MM-DD-resource-[topic-slug].md`.

---

## Step 4: Write the Project Retrospective

Add a retrospective section to the main project note before archiving:

```markdown
## Project Retrospective

**Outcome delivered:** [yes/partial/abandoned — one sentence on what was actually produced]

**What worked:**
- [Specific, repeatable approach]
- 

**What failed or surprised:**
- [Specific failure or surprise]
- 

**Learnings extracted to permanent notes:**
- [[Permanent note title]] — [one sentence on what it captures]
- 

**Archive date:** YYYY-MM-DD
```

---

## Step 5: Archive the Project

Move the entire project folder from `02 - PROJECTS/[project-name]/` to `05 - ARCHIVE/[project-name]/`.

Do not rename files. Do not delete notes. The archive is a full record of how the project ran.

Update the project's main note frontmatter:
```yaml
status: archived
archived_date: YYYY-MM-DD
```

---

## Step 6: Update Active Context

After archiving:
1. Remove the project from the "Active Projects" section of `06 - SYSTEM/CLAUDE.md`
2. Check if any notes in other active projects link to the archived project — update their links if needed
3. Check if any `#project/[name]` tags exist on resource notes — these can stay, they are historical record

---

## What Gets Extracted vs. What Gets Archived

**Extract to permanent notes:**
- Decision frameworks that generalize beyond this project
- Discoveries about how a tool, process, or person operates
- Patterns that appeared in this project that you have seen before (now worth naming)
- Surprises that changed your mental model of something

**Archive without extracting:**
- Raw meeting notes
- Status update notes
- Task lists that are complete
- Notes specific to this project's context with no generalizability

**Rule:** If you could not use this note in a completely different project or decision, archive it without extracting. If you could, extract it.

---

## Rules

- Never delete project notes. Archive everything.
- Extraction comes before archiving. A project archived without extraction loses its knowledge.
- The retrospective is mandatory. It is the document that lets future-you benefit from past-you's experience.
- If a project is being abandoned (not completed), run a shorter extraction pass: what was learned in the attempt? Abandoned projects often contain the most useful failure notes.
- A project is not closed until it is in `05 - ARCHIVE`. An orphaned project sitting in `02 - PROJECTS` with no recent activity is worse than archived — it creates the illusion that there is still work to do.
