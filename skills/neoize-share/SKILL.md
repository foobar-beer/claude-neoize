---
name: neoize-share
description: Import generic lessons from another product's neoize knowledge base into this project, so hard-won wisdom is reused instead of re-learned. Walks the donor's shareable lessons, lets the user pick and writes them as a new lessons file here. Product-specific knowledge (a symbol, a structural node) never travels.
when_to_use: The user wants to bring another project's or product's lessons into this one, asks to "share the KB", "import wisdom from <product>", "seed this from <product>", or to reuse lessons across products. Also offered by neoize-init when a donor product exists.
---

# neoize-share

You are importing generic knowledge from one product (the **donor**) into another (this project, the
**target**). The point is that a lesson learned the expensive way in one product is often true in a
sibling, so it should be reused rather than re-discovered. What travels is the GENERIC half only: a lesson
anchored to a Topic or an Operation. What never travels is product-specific: a lesson about the donor's
own symbols, files or structural nodes, because that knowledge is meaningless in another codebase. The
tool enforces that line, so you never have to hand-filter the obviously unshareable.

Sharing is a FILE operation: it reads the donor's `.neoize/lessons/*.json` (the source of truth, not the
graph) and writes a new lessons file in this project. So the imported lessons become durable,
version-controlled and loaded like any other, instead of a graph-only copy a rebuild would drop.

## Driving neoize: call the tools, not a shell path

Every neoize operation runs as a **plugin MCP tool**. The map:

- `share_lessons`: list a donor's shareable lessons, or import chosen ones into this project.
- `check_lessons`: validate the written file offline before it reaches the graph.
- `load_lessons`: load the imported lessons.
- `read_neo4j_cypher`: pull a lesson's body so the user can judge relevance.

The CLI equivalent is `neoize share --from <product> --from-dir <path> [--list | --lessons a,b | --all]`.

## Step 1 - identify the donor and get at its lessons

Ask which product to import FROM, if the user has not said. You need the donor's lessons files on disk:
the donor's repo, its `.neoize/`, or its `.neoize/lessons/` directory. A product can span repos; point at
the one that holds its `.neoize/lessons`. If you cannot find the donor's files, stop and ask for the path,
rather than guessing. The target is always THIS project (`CLAUDE_PROJECT_DIR`).

## Step 2 - list the candidates and read what matters

Call `share_lessons` with `from: "<donor>"`, `from_dir: "<path>"`, `list: true`. It returns the donor's
shareable lessons (id and title); a lesson anchored only to the donor's structure is not shareable and
does not appear, so the obviously product-specific is already gone.

Then pull a few bodies so the choice is informed. A lesson can be generic in FORM (anchored to a Topic)
but specific in CONTENT: "our auth uses Keycloak" is a Topic lesson that is false for a product on Auth0.
Relevance is a judgement; it is the user's, so surface the bodies rather than deciding for them.

## Step 3 - let the user pick

Present the candidates grouped by topic, with the title and a one-line gist, then ask which to bring. Offer
"all" only when the donor and target are close enough that it is plausible. Do not import a lesson the
user did not choose. The structural filter is automatic; the relevance filter is theirs.

## Step 4 - import (writes a file, does NOT load yet)

Call `share_lessons` with `from`, `from_dir` and `lessons: [<chosen ids>]` (or `all: true`). It writes
`.neoize/lessons/shared-from-<donor>.json` in this project, with each lesson's structural anchors dropped
and only its Topic/Operation anchors kept. It warns about any id that collides with a lesson this project
already has: a load would overwrite the local one, so if that is not intended, rename the id in the
written file before loading. Nothing is loaded yet; nothing the user did not pick was written.

## Step 5 - review, validate, load

- The imported lessons are a STARTING POINT, not finished knowledge. They were true for the donor, not
  necessarily here. Read them in this product's context and edit the body where it assumes the donor's
  setup. The file they live in (`shared-from-<donor>.json`) marks their origin.
- `check_lessons` on the new file, then `load_lessons`. Read the resolved-anchor denominator: the
  Topic/Operation anchors are created on demand, so they resolve; there are no structural anchors to miss.

## Finish

Report: the donor, how many lessons were candidates, which the user chose, the file written, any id
collisions you flagged and the load result. Say plainly that the imported lessons are a draft to adapt,
and name any the user still needs to reconcile against this product's reality.
