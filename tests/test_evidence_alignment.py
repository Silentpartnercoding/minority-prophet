import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EvidenceAlignmentTests(unittest.TestCase):
    def test_active_paper_uses_canonical_exp007a_values(self):
        paper = (ROOT / "papers/minority-prophet-v1.0.2.md").read_text()
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
        active_paper = (ROOT / "papers/minority-prophet-v1.0.2.md").read_text()
        self.assertIn("it is not EXP007A's selected attack", source)
        self.assertIn("historical exploratory mixture", active_paper)

    def test_active_paper_tracks_current_research_boundaries(self):
        paper = (ROOT / "papers/minority-prophet-v1.0.2.md").read_text()
        ledger = (ROOT / "EVIDENCE-ALIGNMENT.md").read_text()
        readme = (ROOT / "README.md").read_text()

        self.assertIn("RootRegistry", paper)
        self.assertIn("conversions_to_reverse", paper)
        self.assertIn("EXP009 (preregistered; not executed)", paper)
        self.assertIn("Field observation (noncanonical)", paper)
        self.assertIn("minority-prophet-v1.0.2.md", ledger)
        self.assertIn("minority-prophet-v1.0.2.md", readme)

        for stale in (
            "Lean 4 formalization in progress",
            "two Lean obligations remain open",
        ):
            self.assertNotIn(stale, paper)
