import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EvidenceAlignmentTests(unittest.TestCase):
    def test_foundations_require_verifier_independence(self):
        foundations = (ROOT / "FOUNDATIONS.md").read_text()
        self.assertIn("Verifier independence", foundations)
        self.assertIn("not trusted merely because it is a\n   third party", foundations)
        self.assertIn("unable to mint, alter, or promote the evidence it verifies", foundations)
        self.assertIn("Unknown or overlapping provenance widens uncertainty", foundations)

    def test_hvi_1_is_falsifiable_and_does_not_overclaim_independence(self):
        hypotheses = (ROOT / "RESEARCH-HYPOTHESES.md").read_text()
        prose = " ".join(hypotheses.split())
        self.assertIn("HVI-1 — verifier independence under shared control", hypotheses)
        self.assertIn("**Null hypothesis:**", hypotheses)
        self.assertIn("**Failure condition:**", hypotheses)
        self.assertIn("**Success condition:**", hypotheses)
        self.assertIn("unknown control always abstains or escalates", prose)
        self.assertIn("cannot discover undisclosed real-world common control", prose)
        self.assertIn("does not itself grant authority", prose)

    def test_formal_ledger_matches_bounded_issuance_reference(self):
        ledger = json.loads((ROOT / "formal/THEOREM-LEDGER.json").read_text())
        entries = {entry["id"]: entry for entry in ledger["claims"]}
        bounded = entries["LEDGER-H2"]
        self.assertEqual(bounded["proof_status"], "tested_reference_implementation")
        self.assertGreaterEqual(len(bounded["implementation_tests"]), 4)
        self.assertIn("not evidence that a particular production path uses it",
                      bounded["prohibited_overstatement"])
        requirements = (ROOT / "PROVENANCE-REQUIREMENTS.md").read_text()
        self.assertNotIn("new in v3, unimplemented", requirements)

    def test_active_paper_uses_canonical_exp007a_values(self):
        paper = (ROOT / "papers/minority-prophet-v1.0.7.md").read_text()
        self.assertIn("EXP007A", paper)
        self.assertIn("(0.701175, 1.0, 0.0, 0.0)", paper)
        self.assertIn("Welch t = 25.1144", paper)
        for unsupported in ("(0.93, 0.91, 0.35, 0.36)", "Welch t = 9.89"):
            self.assertNotIn(unsupported, paper)

    def test_alignment_values_equal_canonical_result(self):
        result = json.loads((ROOT / "results/exp007a-v1/result.json").read_text())
        ledger = (ROOT / "EVIDENCE-ALIGNMENT.md").read_text()
        self.assertEqual(result["selected_params"], [0.701175, 1.0, 0.0, 0.0])
        self.assertEqual(result["overall_verdict"], "supported")
        for value in ("0.701175", "0.371544", "3.7684", "5.6886", "25.1144"):
            self.assertIn(value, ledger)

    def test_exp008_is_not_presented_as_exp007a_attack(self):
        source = (ROOT / "experiments/exp008_shootout.py").read_text()
        active_paper = (ROOT / "papers/minority-prophet-v1.0.7.md").read_text()
        self.assertIn("it is not EXP007A's selected attack", source)
        self.assertIn("historical exploratory mixture", active_paper)

    def test_active_paper_tracks_current_research_boundaries(self):
        paper = (ROOT / "papers/minority-prophet-v1.0.7.md").read_text()
        ledger = (ROOT / "EVIDENCE-ALIGNMENT.md").read_text()
        readme = (ROOT / "README.md").read_text()

        self.assertIn("RootRegistry", paper)
        self.assertIn("conversions_to_reverse", paper)
        self.assertIn("EXP009 (canonical selective-hybrid confirmation; SUPPORTED)", paper)
        self.assertIn("Field observation (noncanonical)", paper)
        self.assertIn("minority-prophet-v1.0.7.md", ledger)
        self.assertIn("papers/00-CURRENT-PAPER.md", readme)
        self.assertIn("evidence ledger", paper)
        self.assertIn("search ledger", paper)
        self.assertIn("not established", paper)
        self.assertIn("HGD-1 (canonical graded-dependence experiment; REJECTED)", paper)
        self.assertIn("HGD-2 (canonical graded-dependence replication; REJECTED)", paper)
        self.assertIn("HES-1 (canonical evidence-seeking experiment; SUPPORTED WITH MATERIAL SUBGROUP LIMITATION)", paper)
        self.assertIn("LIR-3 (canonical observable-provenance bridge; SUPPORTED)", paper)
        self.assertIn("LIR-4 (canonical provenance-degradation experiment; REJECTED)", paper)
        self.assertIn("No general resistance-to-misbinding claim is permitted", paper)

        current_pointer = (ROOT / "papers/00-CURRENT-PAPER.md").read_text()
        papers_index = (ROOT / "papers/README.md").read_text()
        self.assertIn("minority-prophet-v1.0.7.md", current_pointer)
        self.assertIn("minority-prophet-v1.0.7.md", papers_index)

        for stale in (
            "Lean 4 formalization in progress",
            "two Lean obligations remain open",
            "121,944 rewirings",
            "partial parent function",
            "root(c) is c's unique root ancestor",
        ):
            self.assertNotIn(stale, paper)

        self.assertIn("116,032 root-preserving rewirings", paper)
        self.assertIn("1,992 root-preserving rewirings", paper)
        self.assertIn("parents(c) ⊆ C", paper)

    def test_active_paper_has_a_reader_first_layer_without_hiding_boundaries(self):
        paper = (ROOT / "papers/minority-prophet-v1.0.7.md").read_text()
        self.assertTrue(paper.startswith(
            "# The Minority Prophet Property\n\n"
            "## Truth recovery under copying pressure requires unforgeable origins, "
            "unblended sides, and a protected margin — and nothing more"
        ))
        self.assertIn("### The idea in one minute", paper)
        self.assertIn("```mermaid", paper)
        self.assertIn("### What the paper establishes—and what it does not", paper)
        self.assertIn("### Results at a glance", paper)
        self.assertIn("### Choose a reading path", paper)
        self.assertIn("### Glossary", paper)
        self.assertIn("### Selected primary references", paper)
        self.assertIn("They do not grant authority", paper)
        self.assertIn("literature citations still require primary-source verification", paper)
        self.assertGreater(paper.index("### Appendix A — Version history"),
                           paper.index("### 10. Provenance of this paper"))
