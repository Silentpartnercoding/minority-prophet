#!/usr/bin/env python3
"""Five honest people, one paper, five independent roots.

The natural objection to "the machine believes what you tell it about copying" is
that we should simply forbid an empty box. That objection is right, and the
system already does it: `provenance.graph` refuses a parentless claim whose
evidence names nothing dereferenceable, raising `UnattributedRootError`.

So the gap is not an empty box. It is narrower and harder. **Citing a source and
declaring an ancestor are different fields.** Reading a paper and saying so fills
the evidence field. It does not create an ancestry edge to that paper. So every
reader of one paper is, to the counter, a separate first-hand observer.

Nobody lies in this script. Every gate passes.

Run:  .venv/bin/python research/adversarial-weighting/citation_is_not_ancestry.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from provenance.graph import EvidenceGraph, EvidenceNode, UnattributedRootError

DOI = "10.1000/the-one-paper"


def honest_readers(n=5):
    g = EvidenceGraph(strict=True)
    for i in range(n):
        g.add(EvidenceNode(node_id=f"reader{i}", proposition_id="p", value=True,
                           observer_id=f"person{i}", source_id=f"person{i}",
                           confidence=0.9, evidence={"doi": DOI}, copied_from=()))
    return g


def empty_box_is_already_refused():
    g = EvidenceGraph(strict=True)
    try:
        g.add(EvidenceNode(node_id="bare", proposition_id="p", value=True,
                           observer_id="x", source_id="x", confidence=0.9,
                           evidence={}, copied_from=()))
        return False
    except UnattributedRootError:
        return True


def declared_properly(n=5):
    """The same five readers, if each declared the paper as an ancestor."""
    g = EvidenceGraph(strict=True)
    g.add(EvidenceNode(node_id="paper", proposition_id="p", value=True,
                       observer_id="author", source_id="author", confidence=0.9,
                       evidence={"doi": DOI}, copied_from=()))
    for i in range(n):
        g.add(EvidenceNode(node_id=f"reader{i}", proposition_id="p", value=True,
                           observer_id=f"person{i}", source_id=f"person{i}",
                           confidence=0.9, evidence={"doi": DOI},
                           copied_from=("paper",)))
    return g


def main() -> None:
    print("Is the empty box already forbidden?",
          "yes" if empty_box_is_already_refused() else "NO")
    print("  A parentless claim citing nothing dereferenceable is refused outright.")
    print("  So 'just enforce the box' is already done, and is not the gap.\n")

    g = honest_readers()
    roots = [n for n in g._nodes.values() if n.is_root]
    print("Five people read the same paper and each cite it honestly:")
    print(f"    claims accepted           {len(g._nodes)}")
    print(f"    counted as roots          {len(roots)}")
    print(f"    sources actually behind   1")
    print("    nobody lied; every gate passed\n")

    g2 = declared_properly()
    roots2 = [n for n in g2._nodes.values() if n.is_root]
    print("The same five, if each had named the paper as an ancestor:")
    print(f"    counted as roots          {len(roots2)}")
    print("    which is the correct answer, and it collapses as it should\n")

    print("So the machine is right that everything traces to a root. The failure is")
    print("that a reader who cites a paper is not recorded as descending from it, so")
    print("one paper becomes as many roots as it has readers. The fix is not a bigger")
    print("gate on the evidence field. It is that citing a source should propose an")
    print("ancestry edge to it, and today those two fields never speak.")


if __name__ == "__main__":
    main()
