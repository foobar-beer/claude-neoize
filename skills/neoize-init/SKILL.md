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

That is the whole list. The MCP server Claude queries the graph through is bundled in the plugin
(`${CLAUDE_PLUGIN_ROOT}/scripts/neoize-mcp`, pure standard library), so there is nothing else to install.

If a prerequisite is missing, say exactly which one and how to get it, then stop. Do not work around it.

## Step 2 - decide where `.neoize/` lives

`.neoize/` holds authored data (lessons, the collector, the trigger table) that the user
version-controls, so it must land inside a git repository. Do NOT assume the project directory is one.
Check it: `git -C <project> rev-parse --show-toplevel`.

- If the project directory is itself a git repo, `.neoize/` goes at its root. Normal case.
- If it is NOT a repo, or it is a **multi-repo workspace** (a directory holding several independent
  repos with no repo at the top, which is common for a product split across many repos), then a
  `.neoize/` at the top would be untracked and its lessons would not be version-controlled. STOP and
  ask the user which repo or sub-directory should hold the version-controlled `.neoize/` (a shared
  tooling or dev repo is the usual answer). Create it there, then make a symlink at the workspace root,
  `<workspace>/.neoize -> <that path>`, so the plugin, which looks for `.neoize/` under
  `$CLAUDE_PROJECT_DIR`, still finds it.

Report where `.neoize/` will live and why before creating anything.

## Step 3 - scaffold `.neoize/`

Create, if absent:

- `.neoize/docker-compose.neo4j.yml` - copy from `${CLAUDE_PLUGIN_ROOT}/templates/docker-compose.neo4j.yml`.
- `.neoize/lessons/` - the authored knowledge, one JSON file per theme. Seed it with a copy of
  `${CLAUDE_PLUGIN_ROOT}/templates/lessons.example.json` renamed to `getting-started.json`, so a first
  `load-lessons` has something real to load.
- `.neoize/triggers.json` - copy from `${CLAUDE_PLUGIN_ROOT}/templates/triggers.template.json`, then
  trim it to the operations this project actually has.
- `.neoize/wrap.md` - copy from `${CLAUDE_PLUGIN_ROOT}/templates/wrap.template.md`, then set its paths to
  this project's real stores (the always-on rules file, the changelog, the agent-memory location). This
  is what `/neoize:wrap` reads to route end-of-session facts to their one home.
- `.neoize/queries/` - copy the saved retrieval queries from `${CLAUDE_PLUGIN_ROOT}/templates/queries/`.

Do not overwrite a file that already exists. Report what you created and what you left alone.

## Step 4 - bring the graph up and prove it

Run `neoize up` (the CLI is at `${CLAUDE_PLUGIN_ROOT}/scripts/neoize`), then `neoize status`. The graph
starts empty, which is correct. Load the seed lessons with `neoize load-lessons` and read the
denominator it prints: it must say the lessons loaded and the anchors resolved. A load that reports
zero lessons is a failure, not a clean run, so investigate rather than moving on.

Then confirm Claude can reach the graph through the MCP server. The plugin ships a read-only Neo4j MCP
server; its tools are named `mcp__plugin_neoize_neo4j__*`. Run one query through it (for example count
the Topic nodes) and confirm the count matches what `neoize status` showed. If the MCP tools are not
present, the plugin was installed in a session that has not restarted since; tell the user to restart
Claude Code, because a fresh MCP registration needs it.

## Step 5 (DECISION POINT) - propose the structural schema

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

## Step 6 - scaffold the collector (after sign-off)

Write `.neoize/collect.py`: a project-specific script that reads the approved sources and emits
`.neoize/graph.json` in the node/edge shape the loader expects (see
`${CLAUDE_PLUGIN_ROOT}/templates/graph.schema.json`), plus a sibling `.neoize/graph.cypher`. Keep it a
PROJECTION: it regenerates from the code and is never hand-edited. Commit `graph.json` (it is small and
diffable); do not commit any large symbol dump, which is a rebuildable artifact.

Load the structure with `neoize load-graph .neoize/graph.cypher`, which resets only the structural
projection and preserves the lesson, topic, operation and symbol layers. THEN re-run
`neoize load-lessons` so the lesson anchors to structural nodes resolve. Say which commands you ran and
what counts came back.

`.neoize/` legitimately holds more than lessons: a project puts whatever tooling its graph needs there,
alongside `collect.py`. Two common additions, both optional, both scaffolded only when the project wants
them:

- **A structural check.** `.neoize/check.py`: project-specific validation over `graph.json` (wiring
  completeness, an invariant that must hold, orphans). It prints the denominator it examined and exits
  non-zero on a finding, so it works offline and in CI. Run it with `neoize check-graph`.
- **A symbol / reference layer.** `.neoize/symbols/`: a language-aware extractor (every declaration a
  Symbol node, every resolved call a REFERENCES edge) plus a small loader. This is the one layer that
  does not generalize cheaply, because it needs a parser for the project's language (javaparser, a
  tree-sitter grammar, a language server), so it is a per-project tool and may carry its own build (a
  jar, a venv). Offer it when the user wants symbol-level lesson anchoring or a resolved call graph;
  skip it otherwise. `neoize load-graph` already preserves Symbol and File nodes across a structural
  reload, so the symbol layer survives a `collect.py` rebuild.

## Step 7 - wire the "graph first" reflex

Offer to add a short section to the project's `CLAUDE.md` (or create one) that tells Claude to query the
graph before grepping for a project fact, names the MCP tools, and lists the three retrieval shapes (by
topic, by operation, by structural node). Show the user the exact text before writing it. This is what
makes the graph the first source instead of a database nobody queries.

## Finish

Report, in one message: what you created, the node counts now in the graph, the one query you proved the
MCP path with, and the exact next step (run `/neoize:migrate` to move existing docs into lessons). Name
anything you did not do, for example a deferred symbol layer, rather than rounding it up to done.
