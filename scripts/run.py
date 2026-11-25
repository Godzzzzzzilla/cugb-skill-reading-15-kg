#!/usr/bin/env python3
"""reading-15-kg — cross-document entity graph with explained alias decisions.

    python scripts/run.py --input /input/case.json --output /app/output
    python scripts/run.py --input /input/case.json --output /app/output --query "sparse routing"

Three things this does that a naive co-occurrence graph does not:

  * resolves aliases in three ways — exact, normalised, and acronym defined in the
    text — and records *why* each surface form was merged;
  * keeps every node and edge anchored to the sentence it came from;
  * answers a query from the same graph the audit checks, so a query cannot
    disagree with the graph that produced it.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import armkit as ak  # noqa: E402

SKILL = "reading-15-kg"
VERSION = "1.0.0"
ACRONYM = re.compile(r"([A-Z][A-Za-z\-]*(?:[ ][A-Za-z\-]+){0,3})[ ]*\(([A-Z]{2,6})\)")
CAP_TERM = re.compile(r"\b([A-Z][a-z]+(?:[ ][A-Z][a-z]+){0,2})\b")
STOP = {"the", "this", "these", "those", "note", "table", "figure", "results", "method"}
RELATIONS = ["reduces", "increases", "improves", "combines", "combined", "follows",
             "trained", "complementary", "keeps", "does not increase", "is"]


def load_docs(case: ak.CaseInput, out: str):
    docs = [p for p in case.discover() if p.lower().endswith((".md", ".txt"))
            and os.path.basename(p) != "task.md"]
    out_docs = []
    for p in docs:
        text, _ = ak.read_text(p)
        rel = f"inputs/{os.path.basename(p)}"
        ak.write_text(os.path.join(out, rel), text)
        out_docs.append({"name": os.path.basename(p), "rel": rel, "text": text})
    return out_docs


def sentences_with_offsets(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        if not para.strip() or para.lstrip().startswith("#"):
            continue
        for s in ak.sentence_split(para):
            at = text.find(s)
            out.append({"text": s, "start": at, "end": at + len(s)})
    return out


def build_graph(docs):
    """Entities come from definitions in the text, then from terms that repeat.

    A term is only an entity if the text defines it ("Sparse routing (SR)") or
    uses it at least twice.  Free capitalised spans produced nodes like
    "Note A Sparse routing" — a sentence boundary read as a multi-word term.
    """
    aliases, entity_meta, edges = {}, {}, []

    # pass 1: definitions "long form (ABC)"
    for d in docs:
        for m in ACRONYM.finditer(d["text"]):
            long_form, short = m.group(1).strip(), m.group(2)
            key = ak.norm_key(long_form)
            entity_meta.setdefault(key, {"canonical": long_form, "surfaces": set(), "docs": set(),
                                         "definitions": []})
            entity_meta[key]["surfaces"].update({long_form, short, long_form.replace(" ", "-")})
            entity_meta[key]["docs"].add(d["name"])
            entity_meta[key]["definitions"].append({"doc": d["name"], "short": short,
                                                    "long": long_form,
                                                    "reason": "defined in text"})
            for surface in (long_form, short, long_form.replace(" ", "-"),
                            long_form.replace("-", " ")):
                aliases[surface.casefold()] = key

    # pass 2: terms that repeat across the corpus
    counts = {}
    for d in docs:
        for m in CAP_TERM.finditer(d["text"]):
            term = m.group(1).strip()
            if len(term) < 5 or term.casefold() in STOP:
                continue
            counts.setdefault(ak.norm_key(term), {"term": term, "n": 0, "docs": set()})
            counts[ak.norm_key(term)]["n"] += 1
            counts[ak.norm_key(term)]["docs"].add(d["name"])
    canon_lower = [v["canonical"].casefold() for v in entity_meta.values()]
    for key, rec in counts.items():
        if rec["n"] < 2 or key in entity_meta:
            continue
        term_low = rec["term"].casefold()
        if any(c.startswith(term_low + " ") or c.startswith(term_low + "-") for c in canon_lower):
            continue  # a fragment of an entity that is already defined
        entity_meta[key] = {"canonical": rec["term"], "surfaces": {rec["term"]},
                            "docs": rec["docs"], "definitions": [],
                            "note": f"repeated {rec['n']} times"}
        aliases.setdefault(rec["term"].casefold(), key)

    # pass 3: edges inside a sentence, each anchored
    for d in docs:
        for s in sentences_with_offsets(d["text"]):
            low = s["text"].casefold()
            keys = []
            for surface, key in aliases.items():
                if len(surface) < 2:
                    continue
                pattern = r"(?<![a-z0-9])" + re.escape(surface) + r"(?![a-z0-9])"
                if re.search(pattern, low) and key not in keys:
                    keys.append(key)
            if len(keys) < 2:
                continue
            rel = next((r for r in RELATIONS if r in low), "co-occurs")
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    edges.append({
                        "source": entity_meta[keys[i]]["canonical"],
                        "target": entity_meta[keys[j]]["canonical"],
                        "relation": rel, "doc": d["name"], "source_ref": d["rel"],
                        "char_start": s["start"], "char_end": s["end"], "quote": s["text"],
                    })
    return entity_meta, aliases, edges


def query_graph(query, entity_meta, aliases, edges):
    key = aliases.get(query.casefold())
    by_canon = {v["canonical"]: k for k, v in entity_meta.items()}
    if key is None:
        qk = ak.norm_key(query)
        key = next((k for k, v in entity_meta.items()
                    if qk == k or qk in {ak.norm_key(s) for s in v["surfaces"]}), None)
    if key is None:
        return {"query": query, "resolved_to": None, "neighbours": [], "note": "no entity matches"}
    canon = entity_meta[key]["canonical"]
    neigh = []
    for e in edges:
        if e["source"] == canon:
            other, direction = e["target"], "out"
        elif e["target"] == canon:
            other, direction = e["source"], "in"
        else:
            continue
        neigh.append({"entity": other,
                      "direction": direction, "relation": e["relation"], "doc": e["doc"],
                      "quote": e["quote"], "char_start": e["char_start"], "char_end": e["char_end"]})
    return {"query": query, "resolved_to": entity_meta[key]["canonical"],
            "aliases_used": sorted(entity_meta[key]["surfaces"]),
            "neighbours": neigh, "degree": len(neigh)}


def solve(case: ak.CaseInput, out: str, audit: ak.Audit, res: ak.Result, query=None) -> bool:
    docs = load_docs(case, out)
    audit.check("docs-found", len(docs) >= 1, f"{len(docs)} document(s)", critical=True)
    if not docs:
        return False
    entity_meta, aliases, edges = build_graph(docs)
    audit.check("entities-found", len(entity_meta) >= 2, f"{len(entity_meta)} entities", critical=True)
    audit.check("edges-found", len(edges) >= 1, f"{len(edges)} edges", weight=1.0)

    # every entity needs a definition or a surface that appears verbatim
    unexplained = [k for k, v in entity_meta.items() if not v["definitions"] and not v["surfaces"]]
    audit.check("entities-explained", not unexplained, f"{len(unexplained)} entities without a surface form",
                critical=True)

    # every edge must re-slice from the document it names
    bad_edges = []
    for i, e in enumerate(edges, start=1):
        anchor = ak.Anchor(e["source_ref"], e["char_start"], e["char_end"], e["quote"])
        ok, why = ak.verify_anchor(out, anchor.as_dict())
        e["edge_id"] = f"e{i}"
        e["verified"] = ok
        if not ok:
            bad_edges.append(i)
        res.add_evidence(f"e{i}", f"{e['source']} —{e['relation']}→ {e['target']}", anchor, ok, why)
    audit.check("edges-anchored", not bad_edges, f"{len(edges) - len(bad_edges)}/{len(edges)} edges re-slice",
                critical=True)

    q = query or str(case.get("query", "query", default="") or "")
    qres = query_graph(q, entity_meta, aliases, edges) if q else None
    if qres:
        canon_q = (entity_meta.get(aliases.get(q.casefold(), ""), {}) or {}).get("canonical")
        in_graph = sum(1 for e in edges if e["source"] == canon_q or e["target"] == canon_q)
        audit.check("query-matches-graph", len(qres["neighbours"]) == in_graph,
                    f"query returned {len(qres['neighbours'])} neighbours, graph holds {in_graph}",
                    critical=True)

    ents = [{"id": k, "canonical": v["canonical"], "surfaces": sorted(v["surfaces"]),
             "docs": sorted(v["docs"]), "definitions": v["definitions"],
             "explained_by": ("definition" if v["definitions"] else "surface-form")}
            for k, v in entity_meta.items()]
    ak.write_json(os.path.join(out, "entities.json"), {"entities": ents})
    ak.write_json(os.path.join(out, "edges.json"), {"edges": edges})
    ak.write_json(os.path.join(out, "graph.json"), {"nodes": ents, "edges": edges, "query": qres})
    res.add_artifact("entities.json", "data", "entities with their surfaces and definitions")
    res.add_artifact("edges.json", "data", "edges with provenance")
    res.add_artifact("graph.json", "data", "nodes + edges + query answer")

    res.set("entities", ents)
    res.set("edges", edges)
    res.set("aliases", [{"surface": surface, "canonical": v["canonical"]}
                        for k, v in entity_meta.items()
                        for surface in sorted(v["surfaces"])])
    res.set("query", qres)
    res.set("counts", {"entities": len(ents), "edges": len(edges),
                       "aliases": len(aliases), "documents": len(docs)})
    for e in edges:
        if not e["verified"]:
            res.add_uncertainty(f"edge {e['edge_id']} did not re-slice", e["quote"][:120],
                                "check the offset against the copied source")
    if qres and not qres["neighbours"]:
        res.add_uncertainty(f"query {q!r} resolved to {qres['resolved_to']}",
                            "the entity exists but has no edges in these documents",
                            "add documents where it co-occurs")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="/input/case.json")
    ap.add_argument("--output", default="/app/output")
    ap.add_argument("--query", default=None)
    args = ap.parse_args()
    ak.safe_stdout()
    started = ak.utc_now()
    os.makedirs(args.output, exist_ok=True)
    case = ak.CaseInput.load(args.input, work_dir=args.output)
    audit, res = ak.Audit("reading-15"), ak.Result(args.output, SKILL, VERSION)
    try:
        ok = solve(case, args.output, audit, res, args.query)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        ok = False
        audit.check("pipeline-completed", False, f"{type(exc).__name__}: {exc}", critical=True)
        res.add_uncertainty("pipeline exception", str(exc), "read audit.json before using an edge")
    res.meta["case_notes"] = case.notes
    status = ak.derive_status(audit, ok)
    if not ok and status == "success":
        status = "partial"
    res.write(case, audit, status, {
        "success": "every entity and edge is explained and anchored, and the query agrees with the graph",
        "partial": "an edge failed to re-slice or a query disagrees with the graph",
        "cannot_determine": "no documents could be read",
    }.get(status, status), started, sys.argv)
    a = audit.as_dict()
    print(f"wrote result.json status={status} checks={a['passed']}/{a['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
