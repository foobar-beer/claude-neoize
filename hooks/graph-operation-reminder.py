#!/usr/bin/env python3
"""PreToolUse reminder: before a named OPERATION, pull its lessons from the knowledge graph.

The code-lesson layer is retrieved by symbol/file/topic. This is the process layer: a handful of
decision points (closing a ticket, a mutation check, a release) each carry behavioural lessons
anchored to an Operation node, and this hook queries them at the moment the operation fires, so the
check does not depend on the agent remembering to look. Reaching into the node and finding nothing
is the expected case and is strictly better than skipping it and repeating a known mistake, so the
hook ALWAYS reminds on a matched operation, printing "0 lessons" when there are none.

It never blocks: it writes a stderr note and allows, and it fails OPEN, so a bad payload, no graph,
no docker or a slow query never interrupts the session. Reads the PreToolUse payload on stdin.

The triggers are DATA, not code: this script is project-agnostic. It reads the trigger table from
`.neoize/triggers.json` in the project (searched from $CLAUDE_PROJECT_DIR and the current directory),
so a project maps its own tool calls to its own Operation ids without editing this file. Each trigger
is {"tool": "<ToolName>", "contains": "<substring or null>", "operation": "<operation-id>"}. The
`contains` substring is matched case-insensitively against the JSON-serialised tool_input; null means
"any call to this tool".

Connection comes from the environment, with dev defaults matching the shipped docker-compose:
NEOIZE_NEO4J_CONTAINER (neoize-neo4j), NEOIZE_NEO4J_USER (neo4j), NEOIZE_NEO4J_PASSWORD (neoize-local).
"""
import json
import os
import subprocess
import sys

CONTAINER = os.environ.get("NEOIZE_NEO4J_CONTAINER", "neoize-neo4j")
USER = os.environ.get("NEOIZE_NEO4J_USER", "neo4j")
PASSWORD = os.environ.get("NEOIZE_NEO4J_PASSWORD", "neoize-local")


def _triggers_path():
    """Find .neoize/triggers.json, preferring the project dir the harness names, then the cwd."""
    candidates = []
    proj = os.environ.get("CLAUDE_PROJECT_DIR")
    if proj:
        candidates.append(os.path.join(proj, ".neoize", "triggers.json"))
    candidates.append(os.path.join(os.getcwd(), ".neoize", "triggers.json"))
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def load_triggers():
    path = _triggers_path()
    if not path:
        return []
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    rows = data.get("triggers", data) if isinstance(data, dict) else data
    out = []
    for r in rows or []:
        tool = r.get("tool")
        if tool:
            out.append((tool, r.get("contains"), r.get("operation")))
    return out


def lessons_for(operation):
    """Titles of the lessons anchored to this Operation, or None if the graph cannot be reached."""
    query = (f"MATCH (l:Lesson)-[:ANCHORS_TO]->(:Operation {{id:'{operation}'}}) "
             f"RETURN l.title ORDER BY l.title")
    try:
        out = subprocess.run(
            ["docker", "exec", "-i", CONTAINER, "cypher-shell",
             "-u", USER, "-p", PASSWORD, "--format", "plain"],
            input=query, text=True, capture_output=True, timeout=8,
        )
    except Exception:
        return None
    if out.returncode != 0:
        return None
    titles = []
    for line in out.stdout.strip().splitlines():
        t = line.strip().strip('"')
        if t and t != "l.title":
            titles.append(t)
    return titles


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    blob = json.dumps(tool_input, ensure_ascii=False).lower()

    operation = None
    for name, needle, op in load_triggers():
        if tool == name and (needle is None or str(needle).lower() in blob):
            operation = op
            break
    if operation is None:
        sys.exit(0)

    titles = lessons_for(operation)
    if titles is None:
        sys.stderr.write(f'note: before "{operation}" there are graph lessons to pull, but the graph '
                         f'is not reachable right now (check it is up). Proceeding.\n')
        sys.exit(0)

    query = (f"MATCH (l:Lesson)-[:ANCHORS_TO]->(:Operation {{id:'{operation}'}}) "
             f"RETURN l.title, l.body")
    if titles:
        listing = "".join(f"\n  - {t}" for t in titles)
        sys.stderr.write(
            f'note: before "{operation}" the graph has {len(titles)} lesson(s):{listing}\n'
            f'pull the bodies before you act:  {query}\n')
    else:
        sys.stderr.write(
            f'note: before "{operation}" the graph has 0 lessons (none yet, which is fine). '
            f'If this operation just bit you, author one anchored to Operation {{id:"{operation}"}}.\n')
    sys.exit(0)


if __name__ == "__main__":
    main()
