# neoize wrap routing

Where each kind of fact goes at the end of a session. `/neoize:wrap` reads this to route what was
learned. Fill in the paths for this project (relative to the workspace root, or absolute). Each fact
lives in exactly ONE of these homes.

- **Changelog / history** (what shipped, when, in which PR):
  `CHANGELOG.md`

- **Agent memory** (what to pick up next, what is still unverified, open threads):
  `~/.claude/projects/<this-project>/memory/`

- **Lessons** (everything the graph holds: always-on discipline AND situational gotchas AND
  decision-point traps, each with a `scope` of `always` or `situational`):
  `.neoize/lessons/`  (the default; `/neoize:wrap` authors here)

## Always-on rules file

An always-applies rule is no longer hand-written here. It is a Lesson with `scope: always`, and
`neoize apply` materialises every such lesson into a managed block in the rules file below, so the rule
is authored once in the graph and generated into the file that loads every session. Edit the lesson, not
the block. The path is also `rules_file` in `.neoize/project.json`.

  `CLAUDE.md`

## Notes

Anything project-specific about routing goes here. For example: a rule about which file is authoritative
when two could hold a fact, or a store this project does not use (leave it blank and wrap will skip it).
