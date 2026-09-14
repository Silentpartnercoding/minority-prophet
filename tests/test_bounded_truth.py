"""A claim is valid inside the system that measured it, and untested outside it.

The criterion this was built against: the module must have no way to express
"true everywhere", and an untested transport must never come back supportive.
"""

import unittest

from canon.bounded_truth import (
    BoundedClaim, Ontology, Standing, survey, transport,
)

WHEEL = Ontology(
    name="pu-erh flavour wheel",
    vocabulary=frozenset({"earthy", "camphor", "storage", "dry-leaf-appearance"}),
    instrument="trained panel",
    protocol="GB/T 14487-2017, five of six dimensions",
)

PANEL_B = Ontology(
    name="second trained panel",
    vocabulary=frozenset({"earthy", "camphor", "storage", "dry-leaf-appearance"}),
    instrument="different trained panel",
    protocol="GB/T 14487-2017, five of six dimensions",
)

GC_MS = Ontology(
    name="GC-MS volatile profile",
    vocabulary=frozenset({"methoxyphenol-ppm", "borneol-ppm"}),
    instrument="gas chromatograph",
    protocol="headspace extraction",
)

CLAIM = BoundedClaim(
    statement="Monascus fermentation increases the camphor note",
    established_in=WHEEL,
    terms=frozenset({"camphor"}),
    evidence="panel scoring across 40 cakes",
)


class NoWayToSayTrueEverywhereTest(unittest.TestCase):
    def test_the_standing_enum_cannot_express_unbounded_validity(self):
        """If the type could say it, somebody would eventually return it."""
        self.assertEqual(
            {s.value for s in Standing},
            {"established", "untested", "contradicted", "inexpressible"},
        )

    def test_a_claim_with_no_declared_terms_is_refused(self):
        with self.assertRaises(ValueError) as ctx:
            BoundedClaim("something happened", WHEEL, frozenset())
        self.assertIn("cannot be transported honestly", str(ctx.exception))

    def test_a_claim_cannot_use_terms_its_own_ontology_lacks(self):
        with self.assertRaises(ValueError):
            BoundedClaim("borneol rises", WHEEL, frozenset({"borneol-ppm"}))


class TransportTest(unittest.TestCase):
    def test_the_home_ontology_is_where_the_evidence_is(self):
        t = transport(CLAIM, WHEEL)
        self.assertIs(t.standing, Standing.ESTABLISHED)
        self.assertTrue(t.carries)

    def test_same_vocabulary_different_instrument_is_untested_not_supported(self):
        """The quiet failure: stateable there, never measured there."""
        t = transport(CLAIM, PANEL_B)
        self.assertIs(t.standing, Standing.UNTESTED)
        self.assertFalse(t.carries)
        self.assertIn("instrument", t.what_would_establish)

    def test_a_vocabulary_with_no_cell_is_inexpressible_not_contradicted(self):
        """The tea wheel's actual defect: no evidence, not contrary evidence."""
        t = transport(CLAIM, GC_MS)
        self.assertIs(t.standing, Standing.INEXPRESSIBLE)
        self.assertEqual(t.untranslatable, frozenset({"camphor"}))
        self.assertIn("produced no evidence", t.report())
        self.assertIn("not disagreement", t.report())
        self.assertIn("no cell", t.what_would_establish)

    def test_contradiction_requires_an_actual_contrary_result(self):
        t = transport(CLAIM, PANEL_B, contradicted_by="panel B scored it lower, n=40")
        self.assertIs(t.standing, Standing.CONTRADICTED)

    def test_an_empty_contradiction_string_does_not_become_support(self):
        self.assertIs(transport(CLAIM, PANEL_B, contradicted_by="").standing,
                      Standing.UNTESTED)


class SurveyTest(unittest.TestCase):
    def test_a_survey_reports_each_target_and_combines_none(self):
        s = survey(CLAIM, [WHEEL, PANEL_B, GC_MS])
        self.assertEqual(s.established_in, ("pu-erh flavour wheel",))
        self.assertEqual(s.untested_in, ("second trained panel",))
        self.assertFalse(hasattr(s, "score"))
        self.assertFalse(hasattr(s, "portability"))


if __name__ == "__main__":
    unittest.main()
