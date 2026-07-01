---
name: map-of-content
description: Create, update, and maintain Maps of Content — navigation notes that index clusters of related knowledge. Use when a topic has accumulated enough notes to need a navigation hub, when the user asks to build a MOC, or when adding a significant note to an already-mapped topic.
version: 0.2
---

# Map of Content Skill

A Map of Content (MOC) is a note whose primary purpose is to link to other notes rather than to contain original ideas. It is a navigation hub for a cluster of related knowledge — a way to orient yourself in a topic you have accumulated significant depth in.

A MOC is not a folder. You do not move notes into it. You link to notes from it.

MOCs live in `06 - SYSTEM/MOCs/`.

---

## When to Create a MOC

Create a MOC when a topic has accumulated **more than 20 notes** and navigation through backlinks alone becomes difficult. Before 20 notes, backlinks and search are sufficient. After 20 notes, the MOC becomes the fastest way to orient in the topic.

Also create a MOC when:
- The user asks "what do I know about [topic]?"
- A synthesis or decision brief reveals that a topic cluster exists but has no navigation note
- The Writing Activator returns more than 10 relevant notes for a single topic

Do not create a MOC for topics with fewer than 8–10 notes unless explicitly requested.

---

## MOC Structure

```markdown
---
type: resource
status: active
date: YYYY-MM-DD
tags: [topic-name, status/active]
updated: YYYY-MM-DD
---

# [Topic] MOC

## Core Question
[The fundamental question this topic is trying to answer.
Not "what is this topic" but "what problem or question 
organizes all this knowledge?"]

## Foundation Notes
[Notes that establish the basic framework or first principles.
These are the notes a newcomer to the topic should read first.]
- [[Note Title]] — [one sentence on what it contributes]
- [[Note Title]] — [one sentence on what it contributes]

## Complications and Tensions
[Notes that challenge, complicate, or contradict the foundation.
This section is what separates a MOC from an index.]
- [[Note Title]] — [one sentence on what tension it introduces]

## Applications
[Notes that apply the topic's ideas to specific domains or situations]
- [[Note Title]] — [one sentence on the application]

## Source Notes
[Books, courses, articles that this topic draws from]
- [[Book — Key Ideas]] — [one sentence on the most useful insight]

## Connected Maps
[Links to related MOCs]
- [[Related Topic MOC]] — [one sentence on the relationship]

## Open Questions
[The most generative section. Questions this topic raises that
are not yet answered in the vault. Each question is a future
research direction or note to write.]
- [Question]
- [Question]
- [Question]
```

---

## The Open Questions Section

This is the most important section of any MOC. It is an active research agenda, not a list of things you did not bother to find out.

A good Open Questions section:
- Contains questions that cannot be answered by reading the notes in the MOC
- Generates new captures when the user encounters information that addresses them
- Drives the connection-finder to surface relevant notes from other topics
- Gets shorter over time as questions are answered and longer as the topic deepens

When working with MOCs, spend more time on Open Questions than on any other section.

---

## Adding Notes to an Existing MOC

When a significant new note is created in a topic that already has a MOC:

1. Decide which section of the MOC the note belongs in (Foundation, Complications, Applications, Sources)
2. Add the note with a one-sentence explanation of what it contributes
3. Check if the new note answers any Open Questions — if so, remove the question and add the note
4. Check if the new note raises new Open Questions — if so, add them
5. Update the `updated` date in frontmatter

Do not add a note to a MOC without a one-sentence explanation. A MOC full of unexplained links is an index. A MOC with commentary is a navigation tool.

---

## Full Example

```markdown
---
type: resource
status: active
date: 2026-04-15
tags: [productivity, status/active]
updated: 2026-06-01
---

# Productivity MOC

## Core Question
How do I produce more of what matters while doing less of what doesn't?

## Foundation Notes
- [[Energy Management vs Time Management]] — the shift from scheduling to protecting cognitive capacity
- [[Why Most Productivity Systems Fail]] — systems optimize for capturing tasks, not completing the right ones
- [[The PARA Method Explained]] — how organizing by actionability beats organizing by topic

## Complications and Tensions
- [[The Focus Paradox]] — deep focus requires uninterrupted time, but uninterrupted time requires saying no to opportunities
- [[Rest Is Productive]] — challenges the view that rest is the opposite of productivity

## Applications
- [[Content Production System Build]] — applying PARA and energy management to a publishing workflow
- [[Q2 2026 Productivity Audit]] — personal experiment with time-blocking vs. task lists

## Source Notes
- [[Deep Work — Key Ideas]] — Newport's case for high-value cognitive work
- [[Atomic Habits — Key Ideas]] — system design beats goal-setting for behavior change
- [[Getting Things Done — Key Ideas]] — the capture/clarify/organize/engage framework

## Connected Maps
- [[Learning MOC]] — overlaps on deliberate practice and skill acquisition
- [[Writing MOC]] — producing output requires protecting the conditions for deep work

## Open Questions
- Does energy management scale to team productivity, or is it purely individual?
- What is the relationship between rest quality and next-day cognitive output?
- At what point does a productivity system become more work than it saves?
```

---

## MOC Maintenance

Keep MOCs current. A MOC that reflects the state of the vault six months ago is worse than no MOC — it sends the user to notes while hiding newer, better ones.

**Add to MOCs when:**
- A significant new note is created in the topic
- A connection report surfaces a link that belongs in the MOC
- An Open Question is answered by a new note

**Remove from MOCs when:**
- A note has been archived or is outdated
- A link no longer represents what the MOC section claims

**Audit MOCs during the quarterly vault review.** Check that every link is current, every Open Question is still open, and the Core Question still accurately describes what the topic is about.

---

## Rules

- A MOC links to notes. It does not contain original ideas. Write original ideas in a resource note and link to it from the MOC.
- Every link must have a one-sentence explanation. No bare links.
- The Open Questions section drives the value of the MOC. Maintain it actively.
- Update the `updated` date when modifying a MOC. Staleness is the biggest risk.
- When a topic grows beyond 50 notes, consider splitting the MOC into two more focused MOCs with a parent MOC linking to both.
