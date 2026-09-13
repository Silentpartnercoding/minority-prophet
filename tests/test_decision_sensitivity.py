"""Comparing surviving models by the action they imply, not by their likelihood.

The criterion this was built against: a case exists where the model disagreement
is unresolved and the system proceeds anyway, correctly, because the action does
not change.
"""

import unittest

from canon.decision_sensitivity import Action, Model, Resolution, compare


class NotMaterialTest(unittest.TestCase):
    """The case the plan asked for: unresolved, and correctly acted on anyway."""

    def setUp(self):
        self.s = compare([
            Model("copy-dominant regime", Action.BLOCK),
            Model("independent but thin", Action.BLOCK),
        ])

    def test_a_live_disagreement_that_does_not_change_the_action_is_not_material(self):
        self.assertFalse(self.s.is_material)
        self.assertEqual(self.s.actions, frozenset({Action.BLOCK}))

    def test_the_open_question_is_recorded_rather_than_closed(self):
        """The models were not separated and the report must not imply they were."""
        self.assertIn("remain unresolved", self.s.open_question)
        self.assertIn("recorded, not closed", self.s.open_question)

    def test_the_resolution_is_named_act_not_proceed(self):
        """`proceed` is already a Gate action. Reusing it for the disagreement
        would make the word carry two jobs, which is the collision this corpus
        exists to catch -- and here the shared action IS block."""
        self.assertIs(self.s.resolution, Resolution.ACT_NOTING_THE_OPEN_QUESTION)
        self.assertNotIn("Proceed", self.s.report())
        self.assertIn("block", self.s.report())


class MaterialTest(unittest.TestCase):
    def test_different_implied_actions_are_decision_material(self):
        s = compare([Model("a", Action.PROCEED), Model("b", Action.BLOCK)])
        self.assertTrue(s.is_material)
        self.assertIn("DECISION-MATERIAL", s.report())

    def test_the_split_names_which_models_sit_on_which_action(self):
        """Not a bare bit: a caller must be able to see who disagreed and how."""
        s = compare([Model("a", Action.PROCEED), Model("b", Action.BLOCK),
                     Model("c", Action.BLOCK)])
        self.assertEqual(dict(s.split),
                         {Action.BLOCK: ("b", "c"), Action.PROCEED: ("a",)})

    def test_experiment_when_every_model_names_a_discriminating_observation(self):
        s = compare([Model("a", Action.PROCEED, "run the ablation"),
                     Model("b", Action.BLOCK, "run the ablation")])
        self.assertIs(s.resolution, Resolution.EXPERIMENT)

    def test_gather_when_only_some_models_name_one(self):
        s = compare([Model("a", Action.PROCEED, "run the ablation"),
                     Model("b", Action.BLOCK)])
        self.assertIs(s.resolution, Resolution.GATHER)

    def test_abstain_when_nothing_available_would_separate_them(self):
        """Actions differ and no observation distinguishes the models. Abstaining
        is the honest outcome, not a failure to try harder."""
        s = compare([Model("a", Action.PROCEED), Model("b", Action.ESCALATE)])
        self.assertIs(s.resolution, Resolution.ABSTAIN)


class ShapeTest(unittest.TestCase):
    def test_one_model_is_not_a_disagreement(self):
        with self.assertRaises(ValueError):
            compare([Model("only", Action.PROCEED)])

    def test_the_result_is_not_merely_a_boolean(self):
        """PROGRAM.md's warning: a single material-or-not bit rebuilds the black
        box that confidence scores were, under a new name."""
        s = compare([Model("a", Action.PROCEED, "x"), Model("b", Action.BLOCK, "x")])
        for part in (s.models, s.actions, s.split, s.resolution):
            self.assertTrue(part)

    def test_the_action_vocabulary_is_the_gates_and_is_not_reinvented(self):
        self.assertEqual({a.value for a in Action},
                         {"proceed", "block", "escalate", "request_evidence"})


if __name__ == "__main__":
    unittest.main()
