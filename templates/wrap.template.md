# neoize wrap routing

Where each kind of fact goes at the end of a session. `/neoize:wrap` reads this to route what was
learned. Fill in the paths for this project (relative to the workspace root, or absolute). Each fact
lives in exactly ONE of these homes.

- **Always-on rules file** (durable rules and conventions, loaded every session):
  `CLAUDE.md`

- **Changelog / history** (what shipped, when, in which PR):
  `CHANGELOG.md`

- **Agent memory** (what to pick up next, what is still unverified, open threads):
  `~/.claude/projects/<this-project>/memory/`

- **Lessons** (situational gotchas and decision-point traps, in the graph):
  `.neoize/lessons/`  (the default; `/neoize:wrap` authors here)

## Notes

Anything project-specific about routing goes here. For example: a rule about which file is authoritative
when two could hold a fact, or a store this project does not use (leave it blank and wrap will skip it).
