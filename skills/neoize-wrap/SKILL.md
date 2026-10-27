---
name: neoize-wrap
description: End-of-session capture. Decide what this session learned, route each fact to its one home (a lesson in the graph, the always-on rules file, the changelog, or agent memory), author and load the new lessons, and reconcile any that went stale. Use at the end of a working session, or when asked to "wrap", "write up what we learned", or "capture this before I close".
when_to_use: The user is ending a session and wants the knowledge captured, or asks to wrap, record lessons, or save what was learned. Run it after the work is done and verified, not mid-task.
---

# neoize-wrap

You are capturing what this session learned so the next session starts ahead of it. The one rule that
governs everything here: **each fact lives in exactly one home.** A fact written in two places drifts,
and the stale copy gets cited with confidence. So routing is the whole job, and the graph is only one of
the homes.

Run this after the work is done and verified. Capturing an unverified claim as a lesson launders a guess
into the record, so only write down what you actually confirmed, and say what you did not.

## Step 1 - read the project's routing config

The non-graph homes are project-specific, so read `.neoize/wrap.md` for where each kind of fact goes
(the always-on rules file, the changelog, the agent-memory location). If it is absent, scaffold it from
`${CLAUDE_PLUGIN_ROOT}/templates/wrap.template.md`, ask the user to confirm the targets, and proceed.
Never guess a store's path into a write.

## Step 2 - enumerate what was learned, then route each fact

List the candidate facts from this session before writing any of them. Route each to its ONE home:

- **A durable rule or convention** (always applies, not tied to one piece of code) -> the always-on
  rules file named in `wrap.md`. This is NOT a lesson. It must be loaded every session, so it belongs in
  the instructions, not behind an on-demand query.
- **A situational gotcha or technical note anchored to specific code** (a symbol, a subsystem, a file, a
  domain entity) -> a **Lesson** in `.neoize/lessons/`, anchored to that node (or a Topic). This is the
  graph's job: it surfaces only when you touch what it concerns.
- **A trap at a decision point** (bites when you push, release, migrate, close a ticket) -> a **Lesson
  anchored to an Operation**, plus a row in `.neoize/triggers.json` so the hook surfaces it when that
  operation fires.
- **History** (what shipped, when, in which PR) -> the changelog named in `wrap.md`. Not the graph.
- **Session state** (what to pick up next, what is still unverified, open threads) -> agent memory.

Report the routing (fact -> home) before writing. A fact you cannot place is one to raise with the user,
not to file twice.

## Step 3 - author the new lessons

For each fact routed to the graph, write it into `.neoize/lessons/<theme>.json` per
`${CLAUDE_PLUGIN_ROOT}/templates/lesson.schema.json`: a stable `id`, the one-line `title`, a `body` that
carries the trap, the mechanism and the fix (plus the worked example and date if there is one), the
`kind`/`scope`/`confidence`/`status`, at least one `anchor`, and `provenance.date` as an absolute date.
Set `confidence: measured` only for a fact you demonstrated with a control; otherwise `observed` or
`inferred`, honestly. Validate as you go with `neoize check .neoize/lessons`.

## Step 4 - reconcile what went stale

A fix made this session may have falsified an existing lesson. A lesson stating a now-fixed mechanism in
the present tense reads as current and gets cited, so reconcile it rather than leaving it:

- Pull candidates that name what you changed:
  `MATCH (l:Lesson) WHERE l.body CONTAINS '<ticket-or-symbol>' RETURN l.id, l.title, l.prov_date`.
- Read each (the citation is only an upper bound, this is a judgement). Correct it with a new lesson
  carrying `supersedes: ["<old-id>"]`, mark it `status: historical` if it is worth keeping as a
  postmortem, or `status: retired` to tombstone it. A lesson citing the change as the ORIGIN of current
  behaviour is fine and stays.

Never auto-retire on the citation alone, and carry the denominator (how many cited, how many actually
reconciled).

## Step 5 - load and prove

- `neoize load-lessons .neoize/lessons`, and read the resolved-anchor denominator. An anchor that did
  not resolve is reported by name: fix the id, never leave a lesson anchored to nothing.
- If the code's STRUCTURE changed this session, rebuild it too: `python3 .neoize/collect.py` then
  `neoize load-graph .neoize/graph.cypher`, and re-run `neoize load-lessons` after (a structural reload
  drops the lesson-to-structure anchors). This is the `neoize-refresh` routine; defer to it for the
  mechanics.

## Step 6 - keep one home per fact

When you wrote a durable rule into the rules file and you had also drafted it elsewhere (a scratch note,
a second file), delete the draft and leave a pointer. Two correct copies is how the project acquires its
next stale note. Grep for an older copy of anything you just wrote and collapse it to one.

## Finish

Report: the routing table (fact -> home), the lessons authored and loaded with the resolved-anchor
denominator, anything reconciled with the reason, and what you deferred or could not verify. A bare
"wrapped" is not a report; show the counts.
