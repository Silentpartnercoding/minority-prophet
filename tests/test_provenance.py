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
        evidence={"measurement": "https://example.org/obs/" + node_id},
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


class UnattributedRootTests(unittest.TestCase):
    """KL-014's decision: the attribution gap is first-order, the unit gap is not.

    Measured 2026-08-13. Bundled-artifact regimes (reviews, meta-analyses) are
    ~2% of the literature; the KL-014 pilot found 56% of real published claims
    cite no resolvable primary source. A parentless claim with no evidence is an
    evidence root that identifies nothing -- CE-01 in real data.
    """

    def _node(self, node_id, evidence, parents=()):
        return EvidenceNode(
            node_id=node_id, proposition_id="shape", value=True,
            observer_id="o", source_id="s", confidence=0.9,
            evidence=evidence, copied_from=parents,
        )

    def test_gate_is_ON_by_default(self):
        """Flipped 2026-08-13. Opting out is now explicit and visible."""
        from provenance import UnattributedRootError

        with self.assertRaises(UnattributedRootError):
            EvidenceGraph().add(self._node("bare", {}))
        permissive = EvidenceGraph(require_root_evidence=False)
        permissive.add(self._node("bare", {}))
        self.assertEqual(permissive.roots("bare"), frozenset({"bare"}))

    def test_named_but_uncheckable_evidence_is_refused(self):
        """Presence is not enough; the reference must be dereferenceable in form."""
        from provenance import UnattributedRootError

        graph = EvidenceGraph()
        with self.assertRaises(UnattributedRootError):
            graph.add(self._node("vague", {"source": "trust me"}))
        graph.add(self._node("cited", {"source": "10.1038/nature12373"}))
        self.assertEqual(graph.roots("cited"), frozenset({"cited"}))

    def test_root_without_evidence_is_refused_when_gate_is_on(self):
        from provenance import UnattributedRootError

        graph = EvidenceGraph(require_root_evidence=True)
        with self.assertRaises(UnattributedRootError):
            graph.add(self._node("bare", {}))

    def test_root_with_evidence_is_accepted_when_gate_is_on(self):
        graph = EvidenceGraph(require_root_evidence=True)
        graph.add(self._node("cited", {"source": "https://example.org/wire-123"}))
        self.assertEqual(graph.roots("cited"), frozenset({"cited"}))

    def test_non_root_is_unaffected_by_the_gate(self):
        """Only parentless claims mint roots, so only they are gated."""
        graph = EvidenceGraph(require_root_evidence=True)
        graph.add(self._node("origin", {"source": "https://example.org/wire-123"}))
        graph.add(self._node("copy", {}, ("origin",)))
        self.assertEqual(graph.roots("copy"), frozenset({"origin"}))

    def test_permissive_mode_records_rather_than_hides(self):
        graph = EvidenceGraph(strict=False, require_root_evidence=True)
        graph.add(self._node("bare", {}))
        self.assertEqual(graph.violations[0].kind, "unattributed_root")
        self.assertFalse(graph.immunity_applicable)


class GateObservabilityTests(unittest.TestCase):
    """A gate nobody reads is a gate nobody can tune.

    Before this, a caller could not tell how much the root-evidence gate was
    turning away: `violations` existed but nothing counted admissions, gave a
    rate, or survived a caller that let the exception escape.
    """

    def _node(self, node_id, evidence):
        return EvidenceNode(
            node_id=node_id, proposition_id="shape", value=True,
            observer_id="o", source_id="s", confidence=0.9, evidence=evidence,
        )

    CASES = [
        ("a", {"doi": "10.1038/nature12373"}),      # admitted
        ("b", {"url": "https://example.org/x"}),    # admitted
        ("c", {}),                                   # refused: nothing at all
        ("d", {"source": "trust me"}),               # refused: not dereferenceable
        ("e", {"sensor": "rack-4-probe-9"}),         # refused: not dereferenceable
    ]

    def _run(self, *, strict):
        from provenance import UnattributedRootError

        graph = EvidenceGraph(strict=strict)
        for node_id, evidence in self.CASES:
            try:
                graph.add(self._node(node_id, evidence))
            except UnattributedRootError:
                pass
        return graph

    def test_rate_is_identical_in_strict_and_permissive_mode(self):
        """Permissive mode admits the flagged roots but must report the same
        rate, or 'turn the gate on later' becomes unmeasurable in advance."""
        strict = self._run(strict=True).gate_report()
        permissive = self._run(strict=False).gate_report()
        self.assertEqual(strict.refusal_rate, permissive.refusal_rate)
        self.assertEqual(strict.roots_offered, permissive.roots_offered)
        self.assertEqual(strict.refused, permissive.refused)

    def test_counts_and_reasons(self):
        report = self._run(strict=True).gate_report()
        self.assertEqual(report.roots_offered, 5)
        self.assertEqual(report.roots_refused, 3)
        self.assertEqual(report.roots_admitted, 2)
        self.assertEqual(report.refusal_rate, 0.6)
        self.assertEqual(report.refused_by_reason,
                         {"no_evidence": 1, "unresolvable_reference": 2})
        self.assertEqual(report.refused, ("c", "d", "e"))

    def test_permissive_mode_keeps_flagged_roots_but_marks_the_graph(self):
        graph = self._run(strict=False)
        self.assertEqual(len(graph.nodes()), 5)
        self.assertFalse(graph.immunity_applicable)

    def test_strict_mode_excludes_them(self):
        graph = self._run(strict=True)
        self.assertEqual(len(graph.nodes()), 2)

    def test_non_roots_are_not_counted_as_offered(self):
        """Only parentless claims mint roots, so only they are gated or counted."""
        graph = EvidenceGraph()
        graph.add(self._node("origin", {"doi": "10.1038/nature12373"}))
        graph.add(EvidenceNode(
            node_id="copy", proposition_id="shape", value=True, observer_id="o",
            source_id="s", confidence=0.9, evidence={}, copied_from=("origin",)))
        self.assertEqual(graph.gate_report().roots_offered, 1)

    def test_empty_graph_reports_no_rate_rather_than_dividing_by_zero(self):
        report = EvidenceGraph().gate_report()
        self.assertEqual(report.refusal_rate, 0.0)
        self.assertIn("no roots offered", report.summary())
