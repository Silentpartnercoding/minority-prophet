#!/usr/bin/env python3
"""Every attack on the evidence graph produces a structurally valid graph.

The owner's observation: there are fake roots, and copies of fake roots, and the
root object must exist either way. That is exactly right, and it is why no amount
of validating the data structure can help. **The graph is never malformed.**

Building every failure mode shows the problem splits in two, cleanly, and the two
halves need different defences that cannot substitute for each other.

    count inflation   the graph reports more roots than exist
    root emptiness    the graph reports the right number and they are hollow

The last case is the one worth staring at. A fabricated root with nine honest
copies who all correctly declare their ancestry collapses to one root, which is
structurally perfect. The copying machinery worked exactly as designed. The answer
is still zero.

Run:  .venv/bin/python research/adversarial-weighting/two_failure_classes.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from provenance.graph import EvidenceGraph, EvidenceNode

REAL = {"doi": "10.1000/paper"}
FABRICATED = {"doi": "10.1000/never-happened"}


def node(nid, observer, evidence, parents=()):
    return EvidenceNode(node_id=nid, proposition_id="p", value=True,
                        observer_id=observer, source_id=observer, confidence=0.9,
                        evidence=evidence, copied_from=parents)


def cases():
    out = {}

    g = EvidenceGraph(strict=True)
    g.add(node("a", "alice", REAL))
    out["one real observer"] = (g, 1, "correct")

    g = EvidenceGraph(strict=True)
    for i in range(3):
        g.add(node(f"u{i}", f"p{i}", REAL))
    out["3 copies, none declared"] = (g, 1, "count inflation")

    g = EvidenceGraph(strict=True)
    for i in range(3):
        g.add(node(f"r{i}", f"q{i}", REAL))
    out["3 honest readers of 1 paper"] = (g, 1, "count inflation")

    g = EvidenceGraph(strict=True)
    g.add(node("f", "liar", FABRICATED))
    out["1 fabricated root"] = (g, 0, "root emptiness")

    g = EvidenceGraph(strict=True)
    g.add(node("f", "liar", FABRICATED))
    for i in range(9):
        g.add(node(f"c{i}", f"h{i}", FABRICATED, ("f",)))
    out["fabricated root + 9 honest copies"] = (g, 0, "root emptiness")

    return out


def main() -> None:
    print("Every case below passed every structural check the graph performs:")
    print("side consistency, no cycles, named ancestors exist, roots cite")
    print("something dereferenceable, roots authorised.\n")
    print(f"  {'case':<36} {'graph says':>11} {'truth':>7} {'failure':>18}")
    for label, (g, truth, kind) in cases().items():
        roots = sum(1 for n in g._nodes.values() if n.is_root)
        print(f"  {label:<36} {roots:>11} {truth:>7} {kind:>18}")

    print("\nThe two classes need different defences and neither substitutes for the")
    print("other. Recording ancestry properly fixes inflation and does nothing about")
    print("emptiness. Root integrity -- cost, attestation, capture-time signing --")
    print("fixes emptiness and does nothing about inflation.")

    print("\nBOTH DEFENCES NOW EXIST, and the rows above still show the graph alone:")
    print("  count inflation  knowledge_ledger/ancestry.py -- roots by declared")
    print("                   ancestry, refusing silence as originality.")
    print("  root emptiness   provenance/root_dereference.py -- dereference the")
    print("                   reference instead of shape-matching it.")
    from provenance.root_dereference import audit_roots
    registered = {"10.1000/paper"}
    resolver = lambda form, ref: ref in registered
    print(f"\n  {'case':<36} {'hollow roots':>13} {'verdict':>12}")
    for label, (g, truth, kind) in cases().items():
        report = audit_roots(g._nodes.values(), resolver)
        caught = len(report["hollowRoots"])
        verdict = "caught" if (truth == 0 and caught) else ("ok" if truth else "MISSED")
        print(f"  {label:<36} {caught:>13} {verdict:>12}")
    print("\nThe inflation rows still read 3-for-1 above: dereference does not and")
    print("should not fix them. Neither substitutes for the other, which is why")
    print("both numbers are printed and neither is collapsed into a single score.")
    print("\nAnd the last row is the one to remember. Nine honest people declared")
    print("their ancestry correctly, the collapse worked exactly as designed, the")
    print("graph returned one root, and one is the right number. It is still zero")
    print("evidence, because the root was hollow and no structural property of a")
    print("graph can tell you whether somebody actually looked.")


if __name__ == "__main__":
    main()
