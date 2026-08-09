"""Ablated baselines for the commission pre-flight (BL-054).

KL-000 proves its checker is not vacuous by requiring four deliberately broken
evaluators to fail. The pre-flight needs the same discipline, and needed it
urgently: the first version passed 6/6 on a package that had been *weakened* --
one field relabelled, one deleted, the citation list emptied, the invalidation
list emptied. Nothing about the experiment changed. A trap that can be passed by
making the experiment worse launders weakening as compliance, and is worse than
no trap.

Each mutant below reproduces a defect actually committed in this programme. A
mutant that passes is a hole in the pre-flight, not a well-formed package.

Stdlib only; CI runs `unittest discover`.
"""
import json
import pathlib
import tempfile
import unittest

from scripts.preflight_commission import (
    trap_amendment, trap_closure, trap_reachability, trap_self_valid,
    trap_terms, trap_vacuity,
)

GOOD_TEST = {
    "id": "T-REAL", "mustBe": 0, "citesPaperClaim": "Theorem 9",
    "witness": {"input": "-|0;-|1;0|1 rewired to -|0;-|1;1|1",
                "observedOutcome": "verdict 1 -> abstain"},
}


def _package(tmp: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    for name, body in files.items():
        (tmp / name).write_text(body)
    return tmp


class TestPreflightIsNotVacuous(unittest.TestCase):

    def test_M1_a_referenced_document_that_is_not_shipped_is_caught(self):
        """LIN-000 v0.3: carried v0.2's draw schedule 'unchanged' by reference and
        shipped neither. The regression arm could not be attempted."""
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            reg = tmp / "REG.md"
            reg.write_text("The draw schedule is carried unchanged from "
                           "`REGISTRATION-v0.2.md`.\n")
            _package(tmp, {})
            t = trap_closure(tmp, [reg])
            self.assertTrue(t.failures, "an unshipped normative reference must fail")
            self.assertIn("REGISTRATION-v0.2.md", t.failures[0])

    def test_M1_control_a_shipped_reference_passes(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            reg = tmp / "REG.md"
            reg.write_text("Carried unchanged from `REGISTRATION-v0.2.md`.\n")
            (tmp / "REGISTRATION-v0.2.md").write_text("x")
            self.assertEqual(trap_closure(tmp, [reg]).failures, [])

    def test_M2_an_invalidation_clause_red_on_a_correct_run_is_caught(self):
        """LIN-000 v0.3: invalidated the run for zero rejections at a modulus
        whose rejection probability is 3.7e-9 -- the correct outcome."""
        t = trap_self_valid({"invalidationReasons": ["modulus 20 never rejected"],
                             "valid": False})
        self.assertTrue(t.failures)

    def test_M3_a_self_declared_falsifiability_label_is_not_accepted(self):
        """THE GAMING MUTANT. The first pre-flight passed when 'assumed' was
        relabelled 'argued' and impliedBy was deleted -- no experiment changed."""
        gamed = {"tests": [{"id": "T1-POS", "mustBe": 0,
                            "citesPaperClaim": "Theorem 1",
                            "falsifiability": "argued"}]}
        t = trap_vacuity(gamed)
        self.assertTrue(t.failures, "a relabelled string must not buy a pass")
        self.assertIn("witness", t.failures[0])

    def test_M3b_a_witness_that_cannot_be_replayed_is_caught(self):
        t = trap_vacuity({"tests": [dict(GOOD_TEST, witness={"input": "trust me"})]})
        self.assertTrue(t.failures)

    def test_M4_a_test_implied_by_another_cannot_be_cited_as_evidence(self):
        """LIN-000 v0.3's T1-POS: a corollary of L1-POS, so it cannot go red while
        L1-POS is green, yet it was listed as Theorem 1 evidence."""
        t = trap_vacuity({"tests": [dict(GOOD_TEST, impliedBy="L1-POS")]})
        self.assertTrue(any("independent evidential load" in f for f in t.failures))

    def test_M5_citing_nothing_no_longer_buys_a_pass(self):
        """The first pre-flight passed an empty citation list. Citations are now
        harvested from the registration prose instead of supplied."""
        claims = {"_registrationTexts": [
            "That agreement, reached blind, matches the paper's own published "
            "check of 121,944 rewirings exactly."]}
        t = trap_reachability(claims, {"someCount": 116032})
        self.assertTrue(t.failures, "a validation figure absent from results must fail")
        self.assertIn("121,944", t.failures[0])

    def test_M6_an_asserted_paper_claim_with_no_test_behind_it_is_caught(self):
        t = trap_vacuity({"tests": [], "paperClaimsAsserted": ["Theorem 1"]})
        self.assertTrue(t.failures)

    def test_M7_a_decorative_invalidation_clause_is_caught(self):
        """BL-055. A clause nothing can trigger passed the first T2, because T2
        read the reference's own reasons and a weak clause reports nothing."""
        t = trap_self_valid({"invalidationReasons": [], "valid": True},
                            {"clauses": {"C1": ["M1 fires it"], "C2": []},
                             "clauseText": {"C2": "a clause with no teeth"}})
        self.assertTrue(t.failures)
        self.assertIn("decorative", t.failures[0])

    def test_M8_omitting_the_mutation_report_is_itself_a_failure(self):
        """A trap that is optional is a trap that will be omitted on the day it
        matters."""
        t = trap_self_valid({"invalidationReasons": [], "valid": True}, None)
        self.assertTrue(t.failures)
        self.assertIn("BL-055", t.failures[0])

    def test_M9_clause_strength_control_a_fully_triggerable_set_passes(self):
        t = trap_self_valid({"invalidationReasons": [], "valid": True},
                            {"clauses": {"C1": ["M1"], "C2": ["M2"]}})
        self.assertEqual(t.failures, [])

    def test_M10_a_saturated_must_be_positive_control_is_caught(self):
        """The dual of M3/M4, and the one T4 originally missed. LIN-000 v0.3's
        L1-NEG fires on 44,450 of 44,450 eligible worlds -- provably all of them --
        so it measures the population, not the checker."""
        t = trap_vacuity({"tests": [{"id": "L1-NEG", "mustBe": ">0", "saturates": True,
                                     "saturationNote": "44,450 of 44,450"}]})
        self.assertTrue(t.failures)
        self.assertIn("fixed by construction", t.failures[0])

    def test_M10b_a_must_be_positive_control_that_declares_nothing_is_caught(self):
        t = trap_vacuity({"tests": [{"id": "ABL-X", "mustBe": ">0"}]})
        self.assertTrue(t.failures)
        self.assertIn("does not declare", t.failures[0])

    def test_M11_a_term_no_document_defines_is_caught(self):
        """LIN-000 v0.3 states four tests in terms of 'the verdict' and defines it
        nowhere. Document closure (T1) cannot see this: every file was present."""
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            (tmp / "REG.md").write_text("T1-POS: the verdict MUST NOT change.\n")
            t = trap_terms(tmp, {"termsUsedByTests": ["the verdict"]})
            self.assertTrue(t.failures)

    def test_M11_control_a_defined_term_passes(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            (tmp / "REG.md").write_text("**the verdict** is 1 if |S1| > |S0|.\n"
                                        "T1-POS: the verdict MUST NOT change.\n")
            self.assertEqual(trap_terms(tmp, {"termsUsedByTests": ["the verdict"]}).failures, [])

    def test_M12_an_erratum_that_misses_an_artifact_is_caught(self):
        """v0.3.1 corrected 33-40% to 19.6-40.0% and declared the traceability
        unchanged. The traceability still carries the superseded figure."""
        with tempfile.TemporaryDirectory() as d:
            tmp = pathlib.Path(d)
            (tmp / "TRACE.json").write_text('{"note": "Moduli chosen so 33-40% reject"}')
            t = trap_amendment(tmp, {"corrections": [
                {"supersededText": "33-40%", "correctedText": "19.6-40.0%", "by": "E1"}]})
            self.assertTrue(t.failures)
            self.assertIn("TRACE.json", t.failures[0])

    def test_control_a_well_formed_claims_file_passes(self):
        """The traps must still admit a good package, or they are merely noisy."""
        claims = {"tests": [GOOD_TEST], "paperClaimsAsserted": ["Theorem 9"],
                  "_registrationTexts": ["This matches the computed 116,032 exactly."]}
        self.assertEqual(trap_vacuity(claims).failures, [])
        self.assertEqual(trap_reachability(claims, {"n": 116032}).failures, [])


if __name__ == "__main__":
    unittest.main()
