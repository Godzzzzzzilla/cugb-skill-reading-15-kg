#!/usr/bin/env python3
"""Self-test for reading-15-kg."""
from __future__ import annotations
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import armkit as ak
import run as skill
PASS = FAIL = 0
def check(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ok {n}" + (f" — {d}" if d else ""))
    else: FAIL += 1; print(f"  FAIL {n}" + (f" — {d}" if d else ""))
def main():
    print("reading-15 selftest")
    check("armkit pinned", bool(ak.VERSION), ak.VERSION)
    docs = [{"name": "a.md", "rel": "inputs/a.md",
             "text": "Sparse routing (SR) reduces cost. SR is fast. Sparse-routing models differ."}]
    meta, alias, edges = skill.build_graph(docs)
    check("one entity from definition", len(meta) == 1, str(list(meta)))
    check("acronym aliased", any(a == "sr" for a in alias))
    check("hyphen variant aliased", any(a == "sparse-routing" for a in alias))
    check("no edge from a single entity", len(edges) == 0)
    with tempfile.TemporaryDirectory() as td:
        case = ak.CaseInput.load(os.path.join(ROOT, "examples", "case.json"))
        audit, res = ak.Audit("t"), ak.Result(td, "reading-15")
        ok = skill.solve(case, td, audit, res)
        doc = res.write(case, audit, ak.derive_status(audit, ok), "t", ak.utc_now(), ["selftest"])
        check("demo completes", ok)
        check("status success", doc["status"] == "success", doc["status"])
        check("entities resolved", doc["result"]["counts"]["entities"] == 2, str(doc["result"]["counts"]))
        check("aliases include acronyms", any(a["surface"] in ("SR", "BSA") for a in doc["result"]["aliases"]))
        q = doc["result"]["query"]
        check("query resolves", bool(q["resolved_to"]), str(q["resolved_to"]))
        check("query has neighbours", len(q["neighbours"]) >= 1, str(len(q["neighbours"])))
        check("no node spans a newline", all("\n" not in e["canonical"] for e in doc["result"]["entities"]))
        bad = [e for e in doc["evidence"] if not ak.verify_anchor(td, e["anchor"])[0]]
        check("edges re-slice", not bad, f"{len(doc['evidence'])} edges")
    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1
if __name__ == "__main__":
    raise SystemExit(main())
