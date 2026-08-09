"""BL-048 / M27 — publishing answers, not secrets.

The public-boundary check recognises secrets by shape. Withheld outcome values
have no shape: they are ordinary integers in a results table. They are
identifiable only against a declaration of what is currently withheld, which is
what `LIVE-COMMISSIONS.json` is for.

The regression that motivated this: RUN-20260807-10 proposed commissioning
LIN-000 and, in the same commit, published twelve of the fourteen counters that
would have falsified it.

Stdlib only; CI runs `unittest discover`.
"""
import json
import pathlib
import tempfile
import unittest

from scripts.check_withheld_leak import violations, withheld_sets

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _fixture(tmp: pathlib.Path, *, status: str, values: dict, bounds: list) -> pathlib.Path:
    results = tmp / "exp" / "result.json"
    results.parent.mkdir(parents=True, exist_ok=True)
    results.write_text(json.dumps(values))
    declaration = tmp / "research" / "knowledge-ledger" / "LIVE-COMMISSIONS.json"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    declaration.write_text(json.dumps({
        "schema": "minority-prophet.live-commissions.v0.1",
        "commissions": [{
            "id": "BL-TEST", "experiment": "EXP", "status": status,
            "resultsFile": "exp/result.json", "declaredBounds": bounds,
        }],
    }))
    return tmp


class TestWithheldLeak(unittest.TestCase):

    def test_blocks_a_withheld_value_in_either_spelling(self):
        """LEAK-101: a screen that checked only bare digits while the documents
        used commas could not have failed. Both spellings must be caught."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live",
                            values={"sideConsistentWorlds": 5912}, bounds=[])
            blocked = withheld_sets(root)
            for spelling in ("5912", "5,912"):
                found = violations([("report.md", 1, f"| worlds | {spelling} |")], blocked)
                self.assertTrue(found, f"{spelling!r} was not caught")
                self.assertIn("retires that commission's pass condition", found[0])

    def test_declared_bounds_are_publishable(self):
        """Bounds are inputs the implementer derives against, not outcomes.
        Blocking them would make the commission package unshippable."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live",
                            values={"declaredCount": 50362, "secret": 44450},
                            bounds=[50362])
            blocked = withheld_sets(root)
            self.assertEqual(violations([("brief.md", 1, "total 50362")], blocked), [])
            self.assertTrue(violations([("brief.md", 2, "got 44450")], blocked))

    def test_closing_a_commission_unblocks_its_values(self):
        """Once answered, the result is legitimately publishable. That is what
        closing means, and the check must not outlive the commission."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="closed",
                            values={"x": 44450}, bounds=[])
            self.assertEqual(withheld_sets(root), {})

    def test_small_integers_are_not_blocked(self):
        """A blocked set containing 2 or 7 would make every document a
        violation and the control would be turned off within a day."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live",
                            values={"tiny": 7, "real": 44450}, bounds=[])
            blocked = withheld_sets(root)
            self.assertEqual(violations([("doc.md", 1, "7 kernels remain")], blocked), [])
            self.assertTrue(violations([("doc.md", 2, "44450 worlds")], blocked))

    def test_a_live_commission_with_missing_results_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live", values={"x": 44450}, bounds=[])
            (root / "exp" / "result.json").unlink()
            with self.assertRaises(SystemExit):
                withheld_sets(root)

    def test_underscore_separated_literals_are_not_false_positives(self):
        """`WORLDS = 44_450` does not contain the value 44450. Uses a value above
        the collision floor, since values below it are reported unprotectable
        rather than enforced."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live", values={"n": 44450}, bounds=[])
            blocked = withheld_sets(root)
            self.assertEqual(violations([("m.py", 1, "WORLDS = 44_450")], blocked), [])
            self.assertTrue(violations([("m.py", 2, "count is 44450 exactly")], blocked))

    def test_values_below_the_collision_floor_are_reported_not_silently_dropped(self):
        """BL-057's L1-DISC histogram contains 120, which matched
        `stderr.strip()[:120]` in an unrelated script. Enforcing such values is
        noise; dropping them silently is a control quietly ceasing to cover
        something. It must say so."""
        from scripts.check_withheld_leak import UNPROTECTABLE
        UNPROTECTABLE.clear()
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live",
                            values={"small": 120, "large": 44450}, bounds=[])
            blocked = withheld_sets(root)["BL-TEST"]
            self.assertNotIn(120, blocked, "a colliding value must not be enforced")
            self.assertIn(44450, blocked)
            self.assertIn(120, UNPROTECTABLE.get("BL-TEST", []),
                          "and it must be reported as uncovered")

    def test_derivable_metadata_is_not_withheld(self):
        """prefixDigestCount is worlds // interval by definition. Blocking it
        would block a small round number across the whole repository."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live",
                            values={"prefixDigestCount": 100, "prefixDigestsEvery": 1000,
                                    "prefixDigests": ["a"], "real": 44450},
                            bounds=[])
            blocked = withheld_sets(root)["BL-TEST"]
            self.assertNotIn(100, blocked)
            self.assertNotIn(1000, blocked)
            self.assertIn(44450, blocked)

    def test_it_would_have_caught_the_leak_that_motivated_it(self):
        """The RUN-20260807-10 regression, replayed against the real LIN-000
        results file: had LIN-000 been declared live at the time, the draft run
        report's counter table would have been rejected."""
        results = ROOT / "research/knowledge-ledger/lineage/results/lin000-result.json"
        report = ROOT / ("research/knowledge-ledger/runs/2026-08-07/"
                         "RUN-20260807-10/DRAFT-RUN-REPORT-v1.md")
        if not (results.is_file() and report.is_file()):
            self.skipTest("LIN-000 artifacts not present in this checkout")
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(pathlib.Path(d), status="live",
                            values=json.loads(results.read_text()),
                            bounds=[50362, 20260808, 100000])
            blocked = withheld_sets(root)
            lines = [("RUN-10/DRAFT-RUN-REPORT-v1.md", i, text)
                     for i, text in enumerate(report.read_text().splitlines(), 1)]
            found = violations(lines, blocked)
            self.assertTrue(found, "the leak that motivated this check went undetected")


if __name__ == "__main__":
    unittest.main()
