"""A claim whose every cited source was refused is neither a root nor a descendant.

It casts no vote. Before this classification the only trace was a violation
entry, so a caller reading the verdict saw a claim silently not counted. The
third name makes the outcome visible: `classify` says it, `gate_report` lists
it, and `summary` mentions it.
"""

import unittest

from aggregation.root_vote import verdict_from_graph
from provenance.graph import EvidenceGraph, EvidenceNode, UnattributedRootError

DOI = "10.1000/paper"


def claim(i, read=(), evidence=None, value=True):
    return EvidenceNode(
        node_id=f"n{i}", proposition_id="p", value=value,
        observer_id=f"o{i}", source_id=f"o{i}", confidence=0.9,
        evidence={"hash": str(i) * 64} if evidence is None else evidence,
        read_from=read)


class ClassifyTest(unittest.TestCase):
    def test_the_three_classes(self):
        g = EvidenceGraph(strict=False, require_root_evidence=True)
        g.add(claim(0))
        g.add(claim(1, read=(DOI,)))
        g.add(claim(2, read=("trust me",)))
        self.assertEqual(g.classify("n0"), "root")
        self.assertEqual(g.classify("n1"), "descendant")
        self.assertEqual(g.classify("n2"), "unusable_ancestry")

    def test_the_unusable_claim_casts_no_vote_and_says_so(self):
        g = EvidenceGraph(strict=False, require_root_evidence=True)
        g.add(claim(0))
        g.add(claim(1, value=False))
        g.add(claim(2, read=("trust me",)))
        result = verdict_from_graph(g)
        self.assertNotIn("n2", result.support_true | result.support_false)
        self.assertEqual(g.unusable_ancestry, ("n2",))
        report = g.gate_report()
        self.assertEqual(report.unusable_ancestry, ("n2",))
        self.assertIn("1 with unusable ancestry", report.summary())

    def test_a_partly_refused_citation_is_still_a_descendant(self):
        """One good source is enough: the claim descends from what survived."""
        g = EvidenceGraph(strict=False, require_root_evidence=True)
        g.add(claim(0, read=("trust me", DOI)))
        self.assertEqual(g.classify("n0"), "descendant")
        self.assertEqual(g.roots("n0"), frozenset({f"source:{DOI}"}))
        self.assertEqual(g.unusable_ancestry, ())

    def test_strict_mode_refuses_instead_of_classifying(self):
        g = EvidenceGraph(strict=True, require_root_evidence=True)
        with self.assertRaises(UnattributedRootError):
            g.add(claim(0, read=("trust me",)))

    def test_an_ordinary_graph_reports_nothing_unusable(self):
        g = EvidenceGraph(strict=True, require_root_evidence=True)
        g.add(claim(0))
        g.add(claim(1, read=(DOI,)))
        self.assertEqual(g.gate_report().unusable_ancestry, ())
        self.assertNotIn("unusable ancestry", g.gate_report().summary())

    def test_the_classification_survives_a_roundtrip(self):
        g = EvidenceGraph(strict=False, require_root_evidence=True)
        g.add(claim(0, read=("trust me",)))
        again = EvidenceGraph.from_dict(g.to_dict())
        self.assertEqual(again.classify("n0"), "unusable_ancestry")
        self.assertEqual(again.unusable_ancestry, ("n0",))


if __name__ == "__main__":
    unittest.main()
