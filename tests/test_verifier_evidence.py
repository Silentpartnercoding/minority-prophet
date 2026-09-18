"""Tests for the draft-he-agentproto-verifier-evidence negative vectors.

Each test names the input that would flip it, so none is single-valued. That is
not decoration here: this package exists to argue that a check which has only
ever returned one value has not been tested, so a test suite for it that could
not fail would refute the package it ships with.

The load-bearing pairs are the degenerate/sound pairs inside each vector. A
vector whose two halves agreed would demonstrate nothing.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "research/verifier-evidence"

_spec = importlib.util.spec_from_file_location("ve_vectors", PKG / "vectors.py")
vec = importlib.util.module_from_spec(_spec)
# Registered before exec: dataclasses resolves annotations through
# sys.modules[cls.__module__], which is absent for a bare importlib load.
sys.modules["ve_vectors"] = vec
_spec.loader.exec_module(vec)


class ExerciseStatusTests(unittest.TestCase):
    """The helper every vector depends on. Flip: change which outcomes appear."""

    def test_one_value_everywhere_is_unexercised(self):
        self.assertEqual(vec.exercise_status([vec.ACCEPT], [vec.ACCEPT]), vec.UNEXERCISED)

    def test_rejecting_everywhere_is_also_unexercised(self):
        """A check that only ever rejects is equally untested. Flip: add an accept."""
        self.assertEqual(vec.exercise_status([vec.REJECT], [vec.REJECT]), vec.UNEXERCISED)

    def test_both_outcomes_is_implemented(self):
        self.assertEqual(vec.exercise_status([vec.REJECT], [vec.ACCEPT]), vec.IMPLEMENTED)


class V1Tests(unittest.TestCase):
    def test_narrow_check_is_unexercised_and_sound_check_is_not(self):
        r = vec.v1()
        self.assertEqual(r["narrow"]["status"], vec.UNEXERCISED)
        self.assertEqual(r["sound"]["status"], vec.IMPLEMENTED)

    def test_the_pair_disagrees(self):
        """If these ever agree the vector has stopped demonstrating anything."""
        r = vec.v1()
        self.assertNotEqual(r["narrow"]["status"], r["sound"]["status"])

    def test_narrow_check_accepts_the_defective_population(self):
        """Flip: widen NARROW_FIELDS to include 'd'."""
        r = vec.v1()
        self.assertEqual(set(r["narrow"]["positive"]), {vec.ACCEPT})

    def test_sound_check_rejects_the_defective_population(self):
        r = vec.v1()
        self.assertEqual(set(r["sound"]["positive"]), {vec.REJECT})

    def test_negative_control_is_genuinely_clean(self):
        """Both checks must accept the control, or the control is not one."""
        r = vec.v1()
        self.assertEqual(set(r["sound"]["negativeControl"]), {vec.ACCEPT})


class V2Tests(unittest.TestCase):
    def test_constant_probe_is_unexercised(self):
        self.assertEqual(vec.v2()["constant"]["status"], vec.UNEXERCISED)

    def test_counting_probe_is_exercised(self):
        self.assertEqual(vec.v2()["counting"]["status"], vec.IMPLEMENTED)

    def test_constant_probe_reports_the_same_number_on_both_populations(self):
        """Flip: make probe_constant depend on its argument."""
        r = vec.v2()["constant"]["reported"]
        self.assertEqual(r["positive"], r["negativeControl"])

    def test_counting_probe_reports_different_numbers(self):
        r = vec.v2()["counting"]["reported"]
        self.assertNotEqual(r["positive"], r["negativeControl"])


class V4Tests(unittest.TestCase):
    """Outcomes follow draft-sergeev-claim-boundaries-00 S11, adopted after it
    was published; see research/verifier-evidence/ADOPTED-EXTERNAL.md.

    The axis under test is COMPLETENESS - what the detector can see - which is
    separate from independence, who attests. Bradley B drew that line on the
    agentproto list on 2026-09-16 and it is the reason these keys are named for
    field of view rather than for party.
    """

    def test_limited_view_downgrades_rather_than_only_failing(self):
        """The improvement taken from Sergeev: report what IS supported.

        Flip: return a bare UNESTABLISHED with no supported claim, as this
        package did before 2026-09-18.
        """
        r = vec.v4()["limitedFieldOfView"]["twoUsesOneWithheld"]
        self.assertEqual(r["outcome"], vec.DOWNGRADED)
        self.assertEqual(r["supported"], "at least one use, each disclosed use valid")
        self.assertEqual(r["asserted"], "at most one use")

    def test_limited_view_cannot_tell_the_two_worlds_apart(self):
        """The whole point: a curated set looks the same either way.

        Flip: give the detector sight of undisclosed records.
        """
        v = vec.v4()["limitedFieldOfView"]
        self.assertEqual(v["twoUsesOneWithheld"]["outcome"],
                         v["genuinelySingleUse"]["outcome"])

    def test_full_view_separates_them(self):
        f = vec.v4()["fullFieldOfView"]
        self.assertEqual(f["twoUsesOneWithheld"]["outcome"], vec.FAILED)
        self.assertEqual(f["genuinelySingleUse"]["outcome"], vec.ESTABLISHED)
        self.assertNotEqual(f["twoUsesOneWithheld"]["outcome"],
                            f["genuinelySingleUse"]["outcome"])

    def test_downgraded_is_not_failed(self):
        """'We could not check' and 'we checked and it failed' are different
        findings, and collapsing them costs the relying party the difference."""
        self.assertNotEqual(vec.v4()["limitedFieldOfView"]["twoUsesOneWithheld"]["outcome"],
                            vec.FAILED)

    def test_every_result_names_the_basis_it_ranged_over(self):
        """A verdict over a named evidence basis is a verdict over that basis."""
        r = vec.v4()
        for group in ("limitedFieldOfView", "fullFieldOfView"):
            for case in r[group].values():
                self.assertTrue(case["evidenceBasis"])

    def test_every_disclosed_signature_is_valid(self):
        """The attack works with no invalid artifact anywhere."""
        self.assertTrue(vec.v4()["allDisclosedSignaturesValid"])


class PolarityTests(unittest.TestCase):
    """EXR-1 requires the expected outcome on each half of a discriminating pair
    to be declared before the run, and warns it is not implied by the labels.

    These two vectors declare OPPOSITE polarity, which is why. V1 checks that a
    defect is absent, so the population carrying the defect must reject. V2 checks
    that a property is present, so the population lacking it must reject. A reader
    who assumed "positive population always accepts" would get one of them
    backwards.
    """

    def test_v1_rejects_where_the_defect_is_present(self):
        self.assertEqual(vec.V1_EXPECTED["defectPresent"], vec.REJECT)
        self.assertEqual(vec.V1_EXPECTED["defectAbsent"], vec.ACCEPT)

    def test_v2_rejects_where_the_property_is_absent(self):
        self.assertEqual(vec.V2_EXPECTED["propertyAbsent"], vec.REJECT)
        self.assertEqual(vec.V2_EXPECTED["propertyPresent"], vec.ACCEPT)

    def test_the_two_vectors_are_opposite(self):
        """Flip: make both vectors assert the same direction. Then the draft's
        warning would have no worked example behind it."""
        self.assertNotEqual(vec.V1_EXPECTED["defectPresent"],
                            vec.V2_EXPECTED["propertyPresent"])

    def test_sound_checks_match_their_declared_expectations(self):
        r1, r2 = vec.v1(), vec.v2()
        self.assertEqual(set(r1["sound"]["positive"]), {vec.V1_EXPECTED["defectPresent"]})
        self.assertEqual(set(r1["sound"]["negativeControl"]), {vec.V1_EXPECTED["defectAbsent"]})
        self.assertEqual(set(r2["counting"]["positive"]), {vec.V2_EXPECTED["propertyPresent"]})
        self.assertEqual(set(r2["counting"]["negativeControl"]), {vec.V2_EXPECTED["propertyAbsent"]})

    def test_expectations_are_recorded_as_declared_in_advance(self):
        self.assertTrue(vec.v1()["expectationsDeclaredBeforeRun"])
        self.assertTrue(vec.v2()["expectationsDeclaredBeforeRun"])


class V3Tests(unittest.TestCase):
    """V3 reads the frozen KL-005 artifact rather than recomputing it."""

    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(PKG / "run_vectors.py")], cwd=ROOT,
            capture_output=True, check=True,
        )
        cls.doc = json.loads((PKG / "results.json").read_text())
        cls.v3 = next(v for v in cls.doc["vectors"] if v["id"] == "V3")

    def test_silent_ties_for_best_one_sided(self):
        self.assertTrue(self.v3["silentTiesForBestOneSided"])

    def test_silent_is_not_last_under_two_sided(self):
        """Recorded because the prose elsewhere in this repository says it is.

        silent scores 1.000 and the count-based system scores 1.033, so silent
        is second of three. Flip: change the fixture so count-based confirms
        fewer false events.
        """
        self.assertFalse(self.v3["silentIsLastUnderTwoSided"])

    def test_silent_stops_winning_under_two_sided(self):
        self.assertEqual(self.v3["silentBeatenUnderTwoSidedBy"], ["root_aware"])

    def test_pinned_artifact_digest_is_recorded(self):
        self.assertRegex(self.v3["source"]["sha256"], r"^[0-9a-f]{64}$")


class DeterminismTests(unittest.TestCase):
    def test_rerun_is_byte_identical(self):
        out = PKG / "results.json"
        subprocess.run([sys.executable, str(PKG / "run_vectors.py")], cwd=ROOT,
                       capture_output=True, check=True)
        first = out.read_bytes()
        subprocess.run([sys.executable, str(PKG / "run_vectors.py")], cwd=ROOT,
                       capture_output=True, check=True)
        self.assertEqual(first, out.read_bytes())


if __name__ == "__main__":
    unittest.main()
