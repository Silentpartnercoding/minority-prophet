import unittest

from provenance import EvidenceGraph, EvidenceNode


def node(node_id, parents=()):
    return EvidenceNode(
        node_id=node_id,
        proposition_id="shape",
        value=True,
        observer_id=f"observer-{node_id}",
        source_id=f"source-{node_id}",
        confidence=0.9,
        evidence={"measurement": 1},
        copied_from=parents,
    )


class ProvenanceTests(unittest.TestCase):
    def test_roots_collapse_copied_claims(self):
        graph = EvidenceGraph()
        graph.add(node("root"))
        graph.add(node("copy-a", ("root",)))
        graph.add(node("copy-b", ("copy-a",)))
        self.assertEqual(graph.roots("copy-b"), frozenset({"root"}))

    def test_independence_uses_ancestry(self):
        graph = EvidenceGraph()
        graph.add(node("root-a"))
        graph.add(node("root-b"))
        graph.add(node("copy", ("root-a",)))
        self.assertTrue(graph.independent("copy", "root-b"))
        self.assertFalse(graph.independent("copy", "root-a"))

    def test_unknown_parent_is_rejected(self):
        graph = EvidenceGraph()
        with self.assertRaises(ValueError):
            graph.add(node("copy", ("missing",)))


if __name__ == "__main__":
    unittest.main()
