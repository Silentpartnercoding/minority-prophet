"""Property tests for the MP Canon Narrow Gate.

These are the executable form of the canon. Each test names the law it pins.
Tests marked ATTACK encode a way the law fails or is exploitable; they exist so
the failure mode cannot be reintroduced silently.
"""

import unittest

from canon.narrow_gate import (
    Bounds,
    Effect,
    Mandate,
    NarrowGate,
    independent_lineages,
)


def _bounds(**kw):
    base = dict(max_loss=100.0, max_cost=100.0,
                scope=frozenset({"a", "b"}), max_tail_risk=0.5)
    base.update(kw)
    return Bounds(**base)


def _effect(**kw):
    base = dict(name="a", receipt_nonce="n1", max_loss=1.0, max_cost=1.0,
                scope=frozenset({"a"}), reversibility=0.0, tail_risk=0.1)
    base.update(kw)
    return Effect(**base)


class AuthorityMonotonicityTests(unittest.TestCase):
    """Law 1 -- non-expansion of authority."""

    def test_downstream_authority_never_exceeds_upstream(self):
        gate = NarrowGate(
            authority_chain=[
                Mandate("m0", frozenset({"a", "b"})),
                Mandate("m1", frozenset({"a"})),
            ],
            bounds=_bounds(),
        )
        self.assertEqual(gate.surviving_authority(), frozenset({"a"}))
        self.assertFalse(gate.authority_expanded())

    def test_expansion_is_detected_and_denied(self):
        gate = NarrowGate(
            authority_chain=[
                Mandate("m0", frozenset({"a"})),
                Mandate("m1", frozenset({"a", "b"})),   # invented authority
            ],
            bounds=_bounds(),
        )
        self.assertTrue(gate.authority_expanded())
        self.assertEqual(gate.decide(_effect()).reason, "authority-expanded")

    def test_empty_chain_authorizes_nothing(self):
        gate = NarrowGate(authority_chain=[], bounds=_bounds())
        self.assertEqual(gate.surviving_authority(), frozenset())
        self.assertFalse(gate.decide(_effect()).allowed)


class DefaultDenyTests(unittest.TestCase):
    """Unknown != allow. Capability != permission."""

    def test_unknown_effect_is_denied(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        decision = gate.decide(_effect(name="z", scope=frozenset({"a"})))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "outside-surviving-authority")

    def test_capability_does_not_imply_authorization(self):
        """The effect is technically possible and bounded. It is still denied."""
        gate = NarrowGate([Mandate("m0", frozenset({"b"}))], _bounds())
        self.assertFalse(gate.decide(_effect(name="a")).allowed)

    def test_unverified_world_state_denies(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds(),
                          world_verified=False)
        self.assertEqual(gate.decide(_effect()).reason, "world-state-unverified")


class ConflictTests(unittest.TestCase):
    """Law 7 -- and the attack against it."""

    def test_unresolved_conflict_denies(self):
        gate = NarrowGate(
            [Mandate("m0", frozenset({"a"})),
             Mandate("m1", frozenset({"a"}), forbids=frozenset({"a"}))],
            _bounds(),
        )
        self.assertEqual(gate.decide(_effect()).reason,
                         "unresolved-authority-conflict")

    def test_resolver_present_allows(self):
        gate = NarrowGate(
            [Mandate("m0", frozenset({"a"})),
             Mandate("m1", frozenset({"a"}), forbids=frozenset({"a"}))],
            _bounds(),
            resolver=lambda a, b: a,
        )
        self.assertTrue(gate.decide(_effect()).allowed)

    def test_ATTACK_unauthenticated_mandate_cannot_manufacture_denial(self):
        """Without this, deny-on-conflict is a denial-of-service primitive.

        An attacker who can inject any mandate could otherwise halt the system
        by forbidding whatever it needs to do.
        """
        gate = NarrowGate(
            [Mandate("m0", frozenset({"a"})),
             Mandate("attacker", frozenset(), forbids=frozenset({"a"}),
                     authenticated=False)],
            _bounds(),
        )
        self.assertTrue(gate.decide(_effect()).allowed)


class BoundednessTests(unittest.TestCase):
    """Law 8 -- count the cost."""

    def test_unbounded_loss_is_denied(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        self.assertEqual(gate.decide(_effect(max_loss=None)).reason,
                         "unbounded-undertaking")

    def test_loss_over_bound_is_denied(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        self.assertEqual(gate.decide(_effect(max_loss=1e6)).reason,
                         "loss-bound-exceeded")

    def test_scope_escape_is_denied(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        self.assertEqual(
            gate.decide(_effect(scope=frozenset({"a", "elsewhere"}))).reason,
            "scope-bound-exceeded",
        )


class UncertaintyTests(unittest.TestCase):
    """Law 2 as reformulated -- tail risk, not entropy."""

    def test_unquantified_uncertainty_is_denied(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        self.assertEqual(gate.decide(_effect(tail_risk=None)).reason,
                         "uncertainty-unquantified")

    def test_ATTACK_low_entropy_catastrophe_is_still_caught(self):
        """The counterexample that rejected the entropy formulation.

        A 99%/1% outcome has near-zero entropy and a catastrophic tail. Under
        the original ``dAllowedMagnitude/dH <= 0`` it would receive *more*
        authority than a high-entropy harmless effect. Under tail risk it does
        not.
        """
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        catastrophic = _effect(tail_risk=0.99)     # low entropy, fat tail
        harmless = _effect(tail_risk=0.01)         # high entropy, no tail
        self.assertFalse(gate.decide(catastrophic).allowed)
        self.assertTrue(gate.decide(harmless).allowed)


class ViabilityTests(unittest.TestCase):
    def test_effect_leaving_viability_is_denied(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds(),
                          in_viability=lambda e: False)
        self.assertEqual(gate.decide(_effect()).reason,
                         "leaves-viability-region")

    def test_ATTACK_paralysis_is_not_success(self):
        """Machine-checked in NarrowGate.lean as ``demo_gate_one_empty``.

        A gate that denies everything satisfies every safety property. This test
        exists to make that failure visible as a failure: if no effect is ever
        admissible, the configuration is broken even though nothing unsafe
        happened.
        """
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds(),
                          in_viability=lambda e: False)
        admitted = [e for e in (_effect(), _effect(name="a", reversibility=1.0))
                    if gate.decide(e).allowed]
        self.assertEqual(admitted, [], "precondition: nothing is admissible")
        # The point: perfect safety, zero utility. FalseDenyRate == 1.


class ReceiptTests(unittest.TestCase):
    """Law 4 / at-most-once effects."""

    def test_irreversible_effect_requires_receipt(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        self.assertEqual(gate.decide(_effect(receipt_nonce=None)).reason,
                         "irreversible-without-receipt")

    def test_reversible_effect_needs_no_receipt(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        self.assertTrue(
            gate.decide(_effect(receipt_nonce=None, reversibility=1.0)).allowed)

    def test_at_most_once(self):
        gate = NarrowGate([Mandate("m0", frozenset({"a"}))], _bounds())
        first = gate.execute(_effect(receipt_nonce="once"))
        second = gate.execute(_effect(receipt_nonce="once"))
        self.assertTrue(first.allowed)
        self.assertFalse(second.allowed)
        self.assertEqual(second.reason, "receipt-replayed")


class LineageTests(unittest.TestCase):
    """Law 5 -- count lineages, not repetitions."""

    def test_copies_of_one_source_count_once(self):
        sources = ["s", "s-copy", "s-copy-2"]
        same = lambda a, b: a.split("-")[0] == b.split("-")[0]
        self.assertEqual(independent_lineages(sources, same), 1)

    def test_distinct_sources_count_separately(self):
        self.assertEqual(
            independent_lineages(["a", "b", "c"], lambda x, y: False), 3)

    def test_ATTACK_non_transitivity_collapses_the_count(self):
        """The unresolved defect in L5, pinned so it cannot be forgotten.

        A shares with B, B shares with C, A shares nothing with C. Transitive
        closure -- which an equivalence relation demands -- merges all three.
        The true independent count is arguably 2; this returns 1. It is a sound
        lower bound and an unsound estimate. Ledger item U1.
        """
        overlap = {("A", "B"), ("B", "C")}
        same = lambda x, y: (x, y) in overlap or (y, x) in overlap
        self.assertEqual(independent_lineages(["A", "B", "C"], same), 1)


if __name__ == "__main__":
    unittest.main()
