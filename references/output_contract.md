# result.json

- `entities[]` — `{id, canonical, surfaces[], docs[], definitions[], explained_by}`.
  `explained_by` ∈ `definition` | `surface-form`.
- `edges[]` — `{source, target, relation, doc, source_ref, char_start, char_end,
  quote, verified, edge_id}`; `source`/`target` are canonical names.
- `aliases[]` — `{surface, canonical}` for every resolved surface form.
- `query` — `{query, resolved_to, aliases_used[], neighbours[], degree, note?}`.
- `counts` — `{entities, edges, aliases, documents}`.

`status: success` requires: every node explained, every edge re-slicing, and the
query returning exactly the edges the graph holds for the resolved node.
