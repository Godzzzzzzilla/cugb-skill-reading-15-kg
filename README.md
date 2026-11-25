# reading-15-kg

Cross-document entity graph with explained aliases and a query that cannot
disagree with the graph. Submission for **阅读15｜文献知识图谱构建**
(product-arena-10).

## What makes it checkable

- every node says **why** it exists: `defined in text`, or `repeated N times`;
- every edge carries the sentence it came from and a character range;
- the query is answered from the same edge list the audit counts.

## Measured on the bundled demo (2 notes)

| quantity | value |
|---|---|
| entities | 2 (`Sparse routing`, `Block-sparse attention`) |
| surfaces resolved | 7 (`SR`, `Sparse-routing`, `BSA`, hyphen variants) |
| edges | 2, both anchored |
| query `sparse routing` | resolves, 2 neighbours, aliases listed |
| audit | 6/6, `status: success` |

## Design note

A free capitalised-span parser produced nodes like `Note A\n\nSparse routing` — a
sentence boundary read as a multi-word term — and a fragment node `Block`. The
current rules (definition first, repetition second, prefix suppression third) are
stricter, and produce fewer but correct nodes.

## Files

```
SKILL.md               what an agent loads
scripts/run.py         entity resolution, edges, query
scripts/verify.py      independent anchor verifier
scripts/selftest.py    14 checks
scripts/armkit.py      shared core
examples/case.json     demo input (two notes)
run/                   a real run
```

## Reproduce

```bash
python3 scripts/run.py --input examples/case.json --output /tmp/out
python3 scripts/verify.py --result /tmp/out/result.json
python3 scripts/selftest.py
```
