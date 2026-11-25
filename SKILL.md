---
name: literature-graph
description: Build an entity graph across several notes or papers — resolve acronyms and spelling variants, keep provenance for every node and edge, and answer a query from the same graph the audit checks. Use when asked to build a knowledge graph, map entities across documents, or answer "what is connected to X".
---

# Cross-document entity graph

Alias handling is the whole problem. `Sparse routing`, `sparse-routing` and `SR`
are one entity; `Block` is not an entity at all, it is the first word of one. This
skill resolves the first case and refuses the second, and records the reason for
every merge.

## One command

**Where to run it.** The scripts resolve their own paths, so they work from
any working directory. If your shell starts in `/app/work` (the contract's work
directory), call the absolute path of the script —
`python3 /skills/weekly-skill/scripts/run.py --input /input/case.json --output /app/output`
— or `cd` into the folder holding this `SKILL.md` first and use the relative form
below.

```bash
python3 scripts/run.py --input /input/case.json --output /app/output
python3 scripts/run.py --input /input/case.json --output /app/output --query "sparse routing"
```

## How entities are decided

1. **Defined in the text** — `Long form (ABC)` makes one entity with three
   surfaces: the long form, the acronym, and the hyphenated variant.
2. **Repeated** — a capitalised term used at least twice becomes an entity, unless
   it is a prefix of an entity already defined (`Block` under `Block-sparse
   attention`).
3. **Everything else is not a node.** A single mention with no definition does not
   enter the graph, and `limits` says so.

Aliases are collected in a pass over the whole corpus before edges are built, so
an acronym used before its definition still resolves.

## What it writes

`entities.json`, `edges.json`, `graph.json` (nodes + edges + the query answer),
`result.json`. An edge is
`{source, target, relation, doc, source_ref, char_start, char_end, quote, verified, edge_id}` —
the quote is the sentence, so a reviewer can open the document at that range.

## The audit

| check | rule |
|---|---|
| `entities-explained` | every node has a definition or a surface form |
| `edges-anchored` | every edge's sentence re-slices from the document it names |
| `query-matches-graph` | the query returns exactly the edges the graph holds for that node |
| `entities-found` / `edges-found` | the corpus produced something to look at |

The query check exists because the usual failure is a query path that filters
differently from the builder: the graph looks right, the answer is wrong.

## Failure handling

| situation | behaviour |
|---|---|
| entity with no definition and one mention | not a node; recorded in `limits` |
| query matches nothing | `{resolved_to: null, note: "no entity matches"}` — not an error |
| query resolves to an isolated node | empty neighbours, recorded under `uncertainty` |
| no documents | `cannot_determine` |

## Limits

- Relations are surface verbs (`reduces`, `combined`, `complementary`) or
  `co-occurs`; no ontology mapping.
- Entities are English-capitalised or acronym-defined; lowercase Chinese terms are
  not picked up unless they repeat with an acronym.
- Edges are sentence-scoped; a relation spanning two sentences is not joined.
