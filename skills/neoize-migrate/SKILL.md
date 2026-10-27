---
name: neoize-migrate
description: Migrate a project's existing written knowledge (a large CLAUDE.md, docs, a notes directory, agent memory) into neoize lessons anchored to topics and operations. Use after neoize-init, when there is a body of hard-won knowledge to move into the graph.
when_to_use: The user has an existing CLAUDE.md or docs full of gotchas and conventions and wants them in the graph, or asks to "migrate the docs", "import our notes", or "turn the CLAUDE.md into lessons".
---

# neoize-migrate

You are moving a project's existing prose knowledge into the graph as authored lessons. The goal is
retrieval by relevance: a maintainer pulls the lessons that touch what they are editing instead of
scrolling one enormous file. Precede this with `neoize-init` so `.neoize/` and the graph exist.

The failure mode to avoid is a migration that produces TWO copies of every fact, the prose and the
lesson, which then drift. So migration ends with the source prose replaced by a short pointer, not left
as a second home for the same fact.

## Step 1 - inventory the source

Ask the user which files are the knowledge to migrate (commonly `CLAUDE.md`, a `docs/` or `*-toolbox/`
tree, an agent memory directory). Read them. Classify each unit of knowledge into one of:

- **Universal rule or convention** - always applies. This STAYS in `CLAUDE.md` as prose, it is not a
  lesson. Loading it on demand would be wrong, it has to be always-on.
- **Situational gotcha or technical note** anchored to specific code - a symbol, a subsystem, a file,
  a protocol. This becomes a **Lesson anchored to a Topic** (or a structural node, if neoize-init built
  the structural layer).
- **Behavioural trap at a decision point** - a thing that bites when you push, release, close a ticket,
  run a migration. This becomes a **Lesson anchored to an Operation**, plus a row in
  `.neoize/triggers.json` so the hook surfaces it when that operation fires.
- **History** - what shipped when, in which PR. This does NOT belong in the graph. Leave it in a
  changelog or implementation log.

Report the inventory with counts per bucket before writing anything.

## Step 2 - author the lessons

Group lessons into `.neoize/lessons/<theme>.json` files, one file per topic area. Each lesson follows
`${CLAUDE_PLUGIN_ROOT}/templates/lesson.schema.json`:

- `id` - stable kebab-case, because the loader MERGEs on it.
- `title` - the one-line claim.
- `body` - the trap, the mechanism and the fix, enough to act on without re-reading the code. Keep the
  worked example and the date if the source had them; a lesson with its provenance is auditable later.
- `kind` / `scope` / `confidence` / `status` - per the schema.
- `anchors` - at least one. A `Topic` and, where the structural layer exists, the structural node the
  note is really about. For a decision-point trap, an `Operation`.
- `provenance.date` - the date the knowledge was learned, absolute. Convert any relative date.

Validate locally as you go with `neoize check .neoize/lessons`, which flags missing fields, duplicate
ids and dangling supersedes without touching the graph.

## Step 3 - load and prove

Run `neoize load-lessons .neoize/lessons`. Read the denominator: lessons loaded, and anchors resolved
out of anchors checked. An anchor that did not resolve is reported by name; it means a structural node
id is wrong or that node was never extracted. Fix the id, do not leave a lesson anchored to nothing.

Then pull a few lessons back through the MCP server by topic and by operation and confirm the bodies
read correctly. Carry the count.

## Step 4 - replace the prose with a pointer (the first modifying step - CONFIRM FIRST)

Everything up to here was ADDITIVE and reversible: you authored new lesson files under `.neoize/` and
loaded them, and touched none of the user's existing files. This step is the first that MODIFIES the
source. So before editing anything, show the user the planned changes as a list (which prose block in
which file becomes which pointer) and get an explicit confirmation. Do not edit a source file until they
say go. If they decline, stop and leave the authored lessons in place; nothing is lost.

For every block of prose that became a lesson, replace it in the source file with a one-line pointer to
its topic and the query to pull it, the way a migrated section should read:
"X now lives in the graph under Topic `x`; pull it with `MATCH (l:Lesson)-[:ANCHORS_TO]->(:Topic {id:'x'}) RETURN l.title, l.body`."
Leave universal rules as prose. Do NOT leave the full note in both places. Two correct copies is how the
source file acquires its next stale note, because the stale one gets cited with confidence.

## Finish

Report: counts per bucket, lessons authored and loaded with the resolved-anchor denominator, which
source blocks you turned into pointers, and what you deliberately left as prose (the universal rules)
and as history (the changelog). Name anything you could not classify and left for the user to decide.
