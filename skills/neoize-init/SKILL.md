---
name: neoize-init
description: Set up the neoize knowledge graph for the current project. Use once per project to bring up the local Neo4j, scaffold .neoize/, propose a project-specific structural collector, and wire the "query the graph first" reflex. Run before neoize-migrate or neoize-refresh.
when_to_use: The user wants to start using neoize in a repo that has none, or asks to "set up the graph", "initialize neoize", or "turn this project into a knowledge graph".
---

# neoize-init

You are setting up a code-derived knowledge graph for the current project. The graph has two layers.
The **knowledge layer** (Topics, Operations, Lessons) is generic and works with no code parsing at
all. The **structural/symbol layer** is project-specific, because what counts as "structure" is this
codebase's own domain, so you PROPOSE a collector for it and let the user approve it. Do not ship a
universal extractor and do not guess the domain.

Work in steps. Confirm with the user at the two marked decision points. Keep everything you create
inside `.neoize/` in the project, which the user version-controls.

## Step 1 - check the prerequisites

Report what is present and what is missing before changing anything.

- `docker` on PATH and the daemon running (`docker ps`).
- `python3` on PATH.
- `mcp-neo4j-cypher` on PATH. If missing, tell the user to install it, for example
  `uv tool install mcp-neo4j-cypher` or `pipx install mcp-neo4j-cypher`, and stop until it is there.
  This binary is what the plugin's bundled MCP server runs, so Claude cannot query the graph without it.

If a prerequisite is missing, say exactly which one and how to get it, then stop. Do not work around it.

## Step 2 - scaffold `.neoize/`

Create, if absent:

- `.neoize/docker-compose.neo4j.yml` - copy from `${CLAUDE_PLUGIN_ROOT}/templates/docker-compose.neo4j.yml`.
- `.neoize/lessons/` - the authored knowledge, one JSON file per theme. Seed it with a copy of
  `${CLAUDE_PLUGIN_ROOT}/templates/lessons.example.json` renamed to `getting-started.json`, so a first
  `load-lessons` has something real to load.
- `.neoize/triggers.json` - copy from `${CLAUDE_PLUGIN_ROOT}/templates/triggers.template.json`, then
  trim it to the operations this project actually has.
- `.neoize/queries/` - copy the saved retrieval queries from `${CLAUDE_PLUGIN_ROOT}/templates/queries/`.

Do not overwrite a file that already exists. Report what you created and what you left alone.

## Step 3 - bring the graph up and prove it

Run `neoize up` (the CLI is at `${CLAUDE_PLUGIN_ROOT}/scripts/neoize`), then `neoize status`. The graph
starts empty, which is correct. Load the seed lessons with `neoize load-lessons` and read the
denominator it prints: it must say the lessons loaded and the anchors resolved. A load that reports
zero lessons is a failure, not a clean run, so investigate rather than moving on.

Then confirm Claude can reach the graph through the MCP server. The plugin ships a read-only Neo4j MCP
server; its tools are named `mcp__plugin_neoize_neo4j__*`. Run one query through it (for example count
the Topic nodes) and confirm the count matches what `neoize status` showed. If the MCP tools are not
present, the plugin was installed in a session that has not restarted since; tell the user to restart
Claude Code, because a fresh MCP registration needs it.

## Step 4 (DECISION POINT) - propose the structural schema

This is the project-specific half. Read the codebase enough to propose, in a short
`.neoize/SCHEMA.md`, the handful of **domain entities** and **relationships** that are worth making
queryable. These are the nouns a maintainer reasons about and the edges a change propagates along, for
example (from a real project) Protocol, Tier, Module, and edges like DEPENDS_ON, GRANTS, IMPLEMENTED_BY.
Derive them from what the code actually declares (build files, a plugin registry, a route table, an
enum of kinds), never from a generic template.

State plainly what you would extract, from which files, and which questions it would answer
(blast radius, who-depends-on-what, wiring completeness). Then STOP and get the user's sign-off on the
schema before writing any collector. A wrong schema is cheap to fix now and expensive once lessons
anchor to it.

## Step 5 - scaffold the collector (after sign-off)

Write `.neoize/collect.py`: a project-specific script that reads the approved sources and emits
`.neoize/graph.json` in the node/edge shape the loader expects (see
`${CLAUDE_PLUGIN_ROOT}/templates/graph.schema.json`), plus a sibling `.neoize/graph.cypher`. Keep it a
PROJECTION: it regenerates from the code and is never hand-edited. Commit `graph.json` (it is small and
diffable); do not commit any large symbol dump, which is a rebuildable artifact.

Load it with `neoize load-lessons` afterwards is wrong; structural nodes load through the graph.cypher.
Load the structure, THEN re-run `neoize load-lessons` so lesson anchors to structural nodes resolve.
Say which commands you ran and what counts came back.

The symbol/reference layer (every function and its resolved callers) is deliberately out of scope for
v1 unless the user asks: it needs a language-aware parser and is the one piece that does not generalize
cheaply. If they want it, scope it as a separate follow-up with its own collector.

## Step 6 - wire the "graph first" reflex

Offer to add a short section to the project's `CLAUDE.md` (or create one) that tells Claude to query the
graph before grepping for a project fact, names the MCP tools, and lists the three retrieval shapes (by
topic, by operation, by structural node). Show the user the exact text before writing it. This is what
makes the graph the first source instead of a database nobody queries.

## Finish

Report, in one message: what you created, the node counts now in the graph, the one query you proved the
MCP path with, and the exact next step (run `/neoize:migrate` to move existing docs into lessons). Name
anything you did not do, for example a deferred symbol layer, rather than rounding it up to done.
