"""Citing what you read makes you a descendant of it.

The honest-reader gap: five people read one paper, each cited it honestly, and
the counter recorded five independent roots. Nobody lied and every gate passed.
`read_from` closes it by making the citation an ancestry edge.

See research/adversarial-weighting/citation_is_not_ancestry.py for the original
demonstration.
"""

import unittest

from provenance.graph import (
    EvidenceGraph, EvidenceNode, SideConsistencyError, UnattributedRootError,
)

DOI = "10.1000/paper"


def reader(i, read=(), value=True, evidence=None):
    return EvidenceNode(
        node_id=f"r{i}", proposition_id="p", value=value,
        observer_id=f"person{i}", source_id=f"person{i}", confidence=0.9,
        evidence={"doi": DOI} if evidence is None else evidence,
        read_from=read)


def roots(g):
    return [n for n in g._nodes.values() if n.is_root]


class CollapseTest(unittest.TestCase):
    def test_many_readers_of_one_source_collapse_to_one_root(self):
        g = EvidenceGraph(strict=True)
        for i in range(5):
            g.add(reader(i, read=(DOI,)))
        self.assertEqual(len(roots(g)), 1)
        self.assertEqual(roots(g)[0].node_id, f"source:{DOI}")

    def test_the_shared_parent_is_created_once_not_per_reader(self):
        g = EvidenceGraph(strict=True)
        for i in range(5):
            g.add(reader(i, read=(DOI,)))
        self.assertEqual(len(g._nodes), 6)          # one source, five readers

    def test_readers_of_different_sources_stay_separate(self):
        """The fix must not collapse genuinely distinct sources."""
        g = EvidenceGraph(strict=True)
        g.add(reader(0, read=("10.1000/a",)))
        g.add(reader(1, read=("10.1000/b",)))
        self.assertEqual(len(roots(g)), 2)

    def test_a_reader_is_not_a_root(self):
        g = EvidenceGraph(strict=True)
        g.add(reader(0, read=(DOI,)))
        self.assertFalse(g._nodes["r0"].is_root)

    def test_one_claim_may_read_several_sources(self):
        g = EvidenceGraph(strict=True)
        g.add(reader(0, read=("10.1000/a", "10.1000/b")))
        self.assertEqual(len(roots(g)), 2)
        self.assertFalse(g._nodes["r0"].is_root)


class CompatibilityTest(unittest.TestCase):
    def test_existing_callers_are_unaffected(self):
        """`read_from` is additive. Omitting it keeps the old behaviour exactly,
        including the old defect, which is the honest thing for a field nobody
        has migrated to yet."""
        g = EvidenceGraph(strict=True)
        for i in range(5):
            g.add(reader(i))
        self.assertEqual(len(roots(g)), 5)

    def test_a_real_observer_citing_its_own_capture_stays_a_root(self):
        """The distinction the field exists for. Evidence backs an observation
        you made; read_from names what you consulted."""
        g = EvidenceGraph(strict=True)
        g.add(reader(0, evidence={"hash": "a" * 64}))
        self.assertTrue(g._nodes["r0"].is_root)


class GateInteractionTest(unittest.TestCase):
    def test_the_materialised_source_satisfies_the_root_evidence_gate(self):
        """It is a root, so it must name something dereferenceable, and it does:
        the very reference that summoned it."""
        g = EvidenceGraph(strict=True, require_root_evidence=True)
        g.add(reader(0, read=(DOI,)))
        self.assertEqual(g._nodes[f"source:{DOI}"].evidence, {"reference": DOI})

    def test_a_reader_need_not_carry_its_own_evidence(self):
        """Having named an ancestor, a reader is no longer a parentless claim,
        so the unattributed-root gate does not apply to it."""
        g = EvidenceGraph(strict=True, require_root_evidence=True)
        g.add(reader(0, read=(DOI,), evidence={}))
        self.assertFalse(g._nodes["r0"].is_root)

    def test_a_parentless_claim_with_no_evidence_is_still_refused(self):
        g = EvidenceGraph(strict=True, require_root_evidence=True)
        with self.assertRaises(UnattributedRootError):
            g.add(reader(0, evidence={}))

    def test_two_readers_who_disagree_about_one_source_conflict(self):
        """Not papered over. Two readers of one source asserting opposite sides
        is a real disagreement and hits side-consistency like any other edge."""
        g = EvidenceGraph(strict=True)
        g.add(reader(0, read=(DOI,), value=True))
        with self.assertRaises(SideConsistencyError):
            g.add(reader(1, read=(DOI,), value=False))


if __name__ == "__main__":
    unittest.main()
