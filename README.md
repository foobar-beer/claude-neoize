# neoize

Turn a codebase and the hard-won knowledge around it into a local Neo4j graph that Claude queries by
relevance, instead of a wiki nobody reads and a CLAUDE.md that grows until nobody can find anything in
it.

neoize is a Claude Code plugin. You install it, run one setup command in your project, and point it at
the notes you already have. From then on Claude pulls the handful of lessons that touch the code it is
editing, and a hook reminds it of the traps at the moment a risky operation fires.

## The idea

Most projects accumulate two kinds of knowledge that a long Markdown file serves badly:

- **Lessons.** The gotchas, conventions and rules a maintainer learned the expensive way. In a flat
  file they are read wholesale or not at all, and a note about a renamed symbol rots in place with
  nothing to flag it.
- **Structure.** What the project is made of and how a change propagates: modules, services, routes,
  whatever the domain's nouns are, and the edges between them.

neoize puts both in a graph. A lesson is **anchored** to the thing it concerns, a topic, a decision
point, or a structural node, so it is retrieved when that thing is in play rather than scrolled past.
The conceptual model is BloodHound: a collector reads the source, Neo4j holds it, Cypher answers the
path questions (what depends on this, which lessons touch what I am editing, what bites when I push).

The graph has two layers, and they are deliberately different in how portable they are:

- The **knowledge layer** (Topics, Operations, Lessons) is generic. It works with no code parsing at
  all, so you get value the moment you migrate your existing notes.
- The **structural layer** is yours. What counts as structure is your domain, so neoize does not ship a
  universal extractor that would fit nowhere. Instead the setup skill reads your code and proposes a
  collector for you to approve.

## Install

Prerequisites, all on your PATH:

- Docker, with the daemon running. The graph is a local Neo4j container, bound to loopback only.
- `python3`.
- `mcp-neo4j-cypher`, the read-only MCP server Claude queries the graph through. Install it with
  `uv tool install mcp-neo4j-cypher` or `pipx install mcp-neo4j-cypher`.

Then, in Claude Code:

```
/plugin marketplace add foobar-beer/claude-neoize
/plugin install neoize@foobar-beer
```

Restart Claude Code once after installing, so the bundled MCP server registers.

## Quick start

In the project you want a graph for:

```
/neoize:init       # brings up the graph, scaffolds .neoize/, proposes a structural schema
/neoize:migrate    # moves your existing CLAUDE.md / docs / notes into lessons
```

`init` sets up `.neoize/` in your repo (you version-control it), starts the local Neo4j, and walks you
through proposing the structural schema for your codebase. `migrate` reads the prose knowledge you
already have, sorts it into lessons anchored to topics and operations, loads it, and replaces each
migrated block with a one-line pointer so the same fact never lives in two places.

Ask the graph anything through the MCP server once it is up, for example "pull the lessons on the proxy
subsystem" or "what breaks if I change this module".

## How it works

**The knowledge layer.** Lessons are authored as JSON in `.neoize/lessons/*.json`, one file per theme,
validated by `templates/lesson.schema.json`. A loader merges them into Neo4j and validates every
anchor, so a lesson that points at a node which does not exist is reported and skipped, never
fabricated. Lessons are authored in the JSON and loaded, never hand-edited in the database, because a
reload would lose the edit.

**The operation hook.** A PreToolUse hook maps a tool call to an operation id through
`.neoize/triggers.json` (a git push, a release, closing a ticket) and pulls that operation's lessons the
moment it fires, so the reminder does not depend on anyone remembering to look. It never blocks and
fails open: no graph, no Docker, or a slow query never interrupts the session. Finding zero lessons on
an operation is the expected case and is fine.

**The structural layer.** `.neoize/collect.py`, the per-project collector the setup proposes, reads your
build files and registries and writes `.neoize/graph.json` plus a Cypher form. It is a projection:
regenerate it, never hand-edit it. The small JSON is committed and diffable; a large symbol dump, if you
add one, is a rebuildable artifact and stays out of git.

## The CLI

`scripts/neoize` owns the database lifecycle and the generic knowledge layer:

```
neoize up                 # start the local Neo4j (loopback only)
neoize down [--wipe]      # stop it; --wipe also drops the data volume
neoize status             # is it up, and node counts by label
neoize load-lessons [p]   # load authored lessons (default .neoize/lessons); --prune drops removed ones
neoize load-graph <file>  # load the collector's .cypher, resetting only the structural layer
neoize check [path]       # validate lessons files locally, before they touch the graph
neoize query "<cypher>"   # run one Cypher query
```

Connection comes from the environment, with local defaults matching the shipped compose:
`NEOIZE_NEO4J_CONTAINER` (neoize-neo4j), `NEOIZE_NEO4J_USER` (neo4j), `NEOIZE_NEO4J_PASSWORD`
(neoize-local). The password is a local loopback throwaway, not a secret.

## Keeping it fresh

Run `/neoize:refresh` after changing the code's structure, after editing lessons, or when a fix makes a
lesson stale. It rebuilds the structural projection, reloads the lessons (a structural reload drops the
lesson-to-structure anchors, so a lesson reload always follows it), and helps you reconcile lessons that
describe now-fixed behaviour. A fixed bug leaves its description behind, and a note stating a fixed
mechanism in the present tense goes false while nothing errors, so reconciling on a close is part of the
loop, not an afterthought.

## What is generic and what you bring

Generic, shipped, works anywhere: the lesson schema and loader, the operation hook, the Neo4j compose
and MCP wiring, the retrieval queries, the whole Topic and Operation model.

Yours, proposed per project: the structural schema and its collector, the lessons themselves, and the
trigger table that names your operations. A language-aware symbol layer (every function and its resolved
callers) is out of scope for v1, because it is the one piece that does not generalize cheaply. The setup
can scope it as a follow-up if you want it.

## Layout

```
.claude-plugin/plugin.json        plugin manifest
.claude-plugin/marketplace.json   marketplace entry
skills/neoize-init/               set up a project
skills/neoize-migrate/            move existing notes into lessons
skills/neoize-refresh/            keep the graph current
hooks/hooks.json                  PreToolUse registration
hooks/graph-operation-reminder.py the operation reminder (triggers are data, in your .neoize/)
scripts/neoize                    the CLI
scripts/load-lessons              the lesson loader
templates/                        compose, schemas, example lessons, triggers, saved queries
.mcp.json                         the read-only Neo4j MCP server
```

## License

MIT.
