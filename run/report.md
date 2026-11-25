# reading-15-kg — case demo-kg-01

- status: **success** (every entity and edge is explained and anchored, and the query agrees with the graph)
- checks: 6/6 passed, ratio=1.0
- evidence: 2 anchored claims
- finished: 2026-11-25T07:55:08Z

## Result

```json
{
 "entities": [
  {
   "id": "sparserouting",
   "canonical": "Sparse routing",
   "surfaces": [
    "SR",
    "Sparse routing",
    "Sparse-routing"
   ],
   "docs": [
    "doc_a.md"
   ],
   "definitions": [
    {
     "doc": "doc_a.md",
     "short": "SR",
     "long": "Sparse routing",
     "reason": "defined in text"
    }
   ],
   "explained_by": "definition"
  },
  {
   "id": "blocksparseattention",
   "canonical": "Block-sparse attention",
   "surfaces": [
    "BSA",
    "Block-sparse attention",
    "Block-sparse-attention"
   ],
   "docs": [
    "doc_a.md"
   ],
   "definitions": [
    {
     "doc": "doc_a.md",
     "short": "BSA",
     "long": "Block-sparse attention",
     "reason": "defined in text"
    }
   ],
   "explained_by": "definition"
  }
 ],
 "edges": [
  {
   "source": "Sparse routing",
   "target": "Block-sparse attention",
   "relation": "combined",
   "doc": "doc_a.md",
   "source_ref": "inputs/doc_a.md",
   "char_start": 124,
   "char_end": 191,
   "quote": "Block-sparse attention (BSA) is often combined with SR in practice.",
   "edge_id": "e1",
   "verified": true
  },
  {
   "source": "Sparse routing",
   "target": "Block-sparse attention",
   "relation": "complementary",
   "doc": "doc_b.md",
   "source_ref": "inputs/doc_b.md",
   "char_start": 205,
   "char_end": 246,
   "quote": "BSA and sparse routing are complementary.",
   "edge_id": "e2",
   "verified": true
  }
 ],
 "aliases": [
  {
   "surface": "SR",
   "canonical": "Sparse routing"
  },
  {
   "surface": "Sparse routing",
   "canonical": "Sparse routing"
  },
  {
   "surface": "Sparse-routing",
   "canonical": "Sparse routing"
  },
  {
   "surface": "BSA",
   "canonical": "Block-sparse attention"
  },
  {
   "surface": "Block-sparse attention",
   "canonical": "Block-sparse attention"
  },
  {
   "surface": "Block-sparse-attention",
   "canonical": "Block-sparse attention"
  }
 ],
 "query": {
  "query": "sparse routing",
  "resolved_to": "Sparse routing",
  "aliases_used": [
   "SR",
   "Sparse routing",
   "Sparse-routing"
  ],
  "neighbours": [
   {
    "entity": "Block-sparse attention",
    "direction": "out",
    "relation": "combined",
    "doc": "doc_a.md",
    "quote": "Block-sparse attention (BSA) is often combined with SR in practice.",
    "char_start": 124,
    "char_end": 191
   },
   {
    "entity": "Block-sparse attention",
    "direction": "out",
    "relation": "complementary",
    "doc": "doc_b.md",
    "quote": "BSA and sparse routing are complementary.",
    "char_start": 205,
    "char_end": 246
   }
  ],
  "degree": 2
 },
 "counts": {
  "entities": 2,
  "edges": 2,
  "aliases": 7,
  "documents": 2
 }
}
```

## Evidence

| id | claim | locator | ok |
|---|---|---|---|
| e1 | Sparse routing —combined→ Block-sparse attention | `inputs/doc_a.md[124:191]` | ✓ |
| e2 | Sparse routing —complementary→ Block-sparse attention | `inputs/doc_b.md[205:246]` | ✓ |
