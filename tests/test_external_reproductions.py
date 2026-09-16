"""Tests for the cross-repository external-reproduction staleness check.

Half of these are ablations, matching test_gate_coverage.py. A check that only
ever passes is untested however often it runs. The load-bearing pair is
test_fires_when_an_entry_ages_out against test_passes_inside_the_review_interval:
same index, same entries, different notion of today, opposite outcome. Without
that pair the cadence rule could be a no-op.
"""

import copy
import json
import os
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "research/knowledge-ledger/EXTERNAL-REPRODUCTIONS.json"
SCRIPT = ROOT / "scripts/check_external_reproductions.py"

# Fixed so the cadence tests do not drift as the calendar moves. The committed
# entries are reconciled 2026-09-16 and the interval is 30 days.
INSIDE = "2026-10-10"
OUTSIDE = "2026-11-01"


def _run(today=INSIDE):
    environment = dict(os.environ, EXTERNAL_REPRODUCTIONS_TODAY=today)
    return subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True, env=environment
    )


class ExternalReproductionTests(unittest.TestCase):
    def setUp(self):
        self.original = INDEX.read_text(encoding="utf-8")

    def tearDown(self):
        INDEX.write_text(self.original, encoding="utf-8")

    def _with(self, mutate, today=INSIDE):
        document = json.loads(self.original)
        mutate(document)
        INDEX.write_text(json.dumps(document, indent=2), encoding="utf-8")
        return _run(today)

    def test_passes_as_committed(self):
        result = _run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # --- the cadence pair --------------------------------------------------

    def test_fires_when_an_entry_ages_out(self):
        """The thirteen-day cross-repository miss, scaled to the interval."""
        result = _run(OUTSIDE)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Re-derive it against its source repository", result.stdout)

    def test_passes_inside_the_review_interval(self):
        self.assertEqual(_run(INSIDE).returncode, 0)

    # --- ablations ---------------------------------------------------------

    def test_fires_when_an_entry_omits_what_it_does_not_discharge(self):
        """A reproduction without its negative space reads as transferable."""
        result = self._with(lambda d: d["reproductions"][0].pop("doesNotDischarge"))
        self.assertEqual(result.returncode, 1)

    def test_fires_when_control_domain_independence_is_upgraded(self):
        """A reproduction never establishes organizational independence by
        existing; the upgrade must be a deliberate amendment, not a field edit."""
        result = self._with(
            lambda d: d["reproductions"][2].__setitem__("controlDomainIndependence", "established")
        )
        self.assertEqual(result.returncode, 1)

    def test_fires_when_a_local_detail_record_moves(self):
        """An index citing a record that is gone is worse than no index."""
        result = self._with(
            lambda d: d["reproductions"][2].__setitem__(
                "detailRecord", "research/knowledge-ledger/experiments/KL-011/GONE.md"
            )
        )
        self.assertEqual(result.returncode, 1)

    def test_fires_on_an_unknown_strength(self):
        result = self._with(
            lambda d: d["reproductions"][0].__setitem__("strength", "independently-certified")
        )
        self.assertEqual(result.returncode, 1)

    def test_fires_on_a_duplicate_entry(self):
        result = self._with(
            lambda d: d["reproductions"].append(copy.deepcopy(d["reproductions"][0]))
        )
        self.assertEqual(result.returncode, 1)

    def test_fires_when_a_reproduction_is_unpinned(self):
        result = self._with(lambda d: d["reproductions"][0].__setitem__("pin", {}))
        self.assertEqual(result.returncode, 1)

    def test_fires_on_a_future_reconciliation_date(self):
        result = self._with(
            lambda d: d["reproductions"][0].__setitem__("lastReconciled", "2027-01-01")
        )
        self.assertEqual(result.returncode, 1)

    # --- the boundary the check refuses to overstate ------------------------

    def test_reports_that_a_pass_is_not_completeness(self):
        """The check indexes; it does not crawl. It must say so on success, or
        a green run reads as 'we have them all'."""
        result = _run()
        self.assertIn("cannot discover a reproduction that was never entered", result.stdout)

    def test_reports_detail_records_it_cannot_check_from_here(self):
        """Records in other repositories are named as unchecked rather than
        silently counted as verified."""
        result = _run()
        self.assertIn("NOT CHECKED from this repository", result.stdout)


if __name__ == "__main__":
    unittest.main()
