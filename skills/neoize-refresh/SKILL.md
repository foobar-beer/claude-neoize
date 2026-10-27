---
name: neoize-refresh
description: Keep the neoize graph current with the code and the lessons. Use after changing the codebase structure, after authoring or editing lessons, or when closing a ticket whose fix makes an existing lesson stale. Rebuilds the structural projection, reloads lessons, and reconciles lessons that describe now-fixed behaviour.
when_to_use: The user asks to "refresh the graph", "reload lessons", "rebuild the structure", or has just finished work and wants the graph to reflect it. Also when a lesson may have gone stale.
---

# neoize-refresh

You are bringing the graph back into agreement with the code and the authored lessons. The graph is a
projection: it is always safe to rebuild, never hand-edit it in the Neo4j browser, because a reload
loses the edit. Run this against a running graph (`neoize status`; `neoize up` if it is down).

## Reload the knowledge layer

Authored lessons changed (edited, added, retired, moved between files):

1. `neoize check .neoize/lessons` first, to catch a bad file before it reaches the graph.
2. `neoize load-lessons .neoize/lessons`. It is additive by id. Read the resolved-anchor denominator.
3. If you MOVED or REMOVED a lesson, the additive load leaves the old node behind. Use
   `neoize load-lessons --prune .neoize/lessons` to drop graph lessons absent from the files, but only
   against the FULL lessons directory, and diff the ids first: dump the graph lesson ids and the file
   lesson ids and confirm the graph-minus-files set is EXACTLY the lesson you meant to remove. If it
   lists anything else, the loaded set is incomplete and prune would delete a real lesson.

## Rebuild the structural layer (if the project has one)

The code's structure changed (a new module, a renamed entity, a changed dependency):

1. Re-run the project collector: `python3 .neoize/collect.py` writes a fresh `.neoize/graph.json` and
   `.neoize/graph.cypher`. Diff `graph.json` against the committed one and sanity-check the delta.
2. Load the structure. This resets the structural projection, so the lesson-to-structural anchors are
   dropped and must be restored: re-run `neoize load-lessons .neoize/lessons` immediately after, and
   confirm the resolved-anchor count comes back to where it was. A structural reload that is not
   followed by a lesson reload leaves the graph under-anchored and nothing errors, so do not skip it.

## Reconcile a stale lesson when closing a ticket

A fixed bug leaves its description behind. A lesson that states a now-fixed mechanism in the PRESENT
tense goes false the day the fix merges, and nothing errors: it still reads as current and gets cited
with confidence. So when a fix lands:

1. Pull the lessons that name the ticket or the symbol:
   `MATCH (l:Lesson) WHERE l.body CONTAINS '<ticket-or-symbol>' RETURN l.id, l.title, l.prov_date`.
2. Read each candidate. The citation alone is only an upper bound, so this is a judgement, not an
   auto-retire. A lesson describing the now-fixed mechanism in the present tense is a reconcile
   candidate: either correct it (author a new lesson carrying `supersedes: ["<old-id>"]`), mark it
   `status: historical` if it is worth keeping as a postmortem, or set `status: retired` to tombstone
   it. A lesson citing the ticket as the ORIGIN of current behaviour is fine and stays.
3. Reload. Carry the denominator (how many cited, how many actually reconciled), and never auto-retire
   on the citation alone.

## Finish

Report what you reloaded or rebuilt, the before/after node and lesson counts, the resolved-anchor
denominator, and any lesson you reconciled with the reason. If you pruned, show the diff you checked
first. Name anything you left for the user to judge.
