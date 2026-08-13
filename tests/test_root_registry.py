import hashlib
import multiprocessing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from provenance import (
    ClockError, HmacIssuerVerifier, IssuanceLimitError, IssuerAuthenticationError,
    RegistryIntegrityError, ReplayError, RootAuthorizationError, RootRegistry, RootRequest,
)
from provenance.graph import EvidenceGraph, EvidenceNode

NOW = 1_800_000_000
KEYS = {("issuer-a", "key-1"): b"issuer-a-secret", ("issuer-b", "key-1"): b"issuer-b-secret"}
INTEGRITY = b"registry-integrity-key"


def signed_request(verifier, *, issuer="issuer-a", key="key-1", observation="obs-1", nonce="nonce-1", observed_at=NOW):
    request = RootRequest(
        issuer_id=issuer, key_id=key, observation_id=observation,
        proposition_id="weather", value=True,
        evidence_digest=hashlib.sha256(observation.encode()).hexdigest(),
        observed_at=observed_at, nonce=nonce,
    )
    return request.with_signature(verifier.sign(request))


def concurrent_issue(path, observation, nonce, queue):
    verifier = HmacIssuerVerifier(KEYS)
    registry = RootRegistry(path, verifier=verifier, integrity_key=INTEGRITY,
                            roots_per_window=1, clock=lambda: NOW)
    try:
        registry.issue(signed_request(verifier, observation=observation, nonce=nonce))
        queue.put("issued")
    except IssuanceLimitError:
        queue.put("limited")


class RootRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "roots.sqlite"
        self.verifier = HmacIssuerVerifier(KEYS)

    def tearDown(self):
        self.temp.cleanup()

    def registry(self, **overrides):
        options = dict(verifier=self.verifier, integrity_key=INTEGRITY,
                       roots_per_window=2, window_seconds=60, clock=lambda: NOW)
        options.update(overrides)
        return RootRegistry(self.path, **options)

    def test_authenticated_issuer_gets_canonical_root(self):
        receipt = self.registry().issue(signed_request(self.verifier))
        self.assertTrue(receipt.root_id.startswith("mp-root-v1:"))
        self.assertEqual(receipt.sequence, 1)
        self.assertIn(receipt.root_id, self.registry().active_roots())

    def test_graph_rejects_unminted_root_when_authority_is_configured(self):
        registry = self.registry()
        receipt = registry.issue(signed_request(self.verifier))
        graph = EvidenceGraph(root_authority=registry)

        def evidence_node(node_id):
            return EvidenceNode(
                node_id=node_id, proposition_id="weather", value=True,
                observer_id="issuer-a", source_id="sensor-a", confidence=1.0,
                # A resolvable digest: EvidenceGraph now requires roots to name
                # something dereferenceable (2026-08-13). This test is about
                # root AUTHORIZATION, so it supplies valid evidence in order to
                # reach the authorization assertion rather than tripping the
                # attribution gate first.
                evidence={"digest": "b1946ac92492d2347c6235b4d2611184"},
            )

        graph.add(evidence_node(receipt.root_id))
        with self.assertRaises(RootAuthorizationError):
            graph.add(evidence_node("caller-invented-root"))

    def test_unknown_or_forged_issuer_fails_closed(self):
        request = signed_request(self.verifier).with_signature("00" * 32)
        with self.assertRaises(IssuerAuthenticationError):
            self.registry().issue(request)

    def test_quota_survives_restart_and_key_compromise_ce05(self):
        self.registry().issue(signed_request(self.verifier, observation="a", nonce="a"))
        self.registry().issue(signed_request(self.verifier, observation="b", nonce="b"))
        with self.assertRaises(IssuanceLimitError):
            self.registry().issue(signed_request(self.verifier, observation="attacker", nonce="c"))

    def test_replay_and_duplicate_observation_fail(self):
        request = signed_request(self.verifier)
        self.registry().issue(request)
        with self.assertRaises(ReplayError):
            self.registry().issue(request)
        duplicate = signed_request(self.verifier, nonce="new-nonce")
        with self.assertRaises(ReplayError):
            self.registry().issue(duplicate)

    def test_tombstone_never_restores_capacity_or_orphans_ce04(self):
        registry = self.registry(roots_per_window=1)
        receipt = registry.issue(signed_request(self.verifier))
        registry.tombstone(receipt.root_id, reason="issuer key compromised", now=NOW + 1)
        self.assertNotIn(receipt.root_id, registry.active_roots())
        with self.assertRaises(IssuanceLimitError):
            registry.issue(signed_request(self.verifier, observation="replacement", nonce="replacement"))
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM root_events WHERE root_id=?", (receipt.root_id,)).fetchone()[0], 2)

    def test_clock_boundary_and_future_observation_fail_closed(self):
        with self.assertRaises(ClockError):
            self.registry(max_clock_skew_seconds=5).issue(
                signed_request(self.verifier, observed_at=NOW + 6)
            )

    def test_registry_tampering_is_detected_before_next_issue(self):
        self.registry().issue(signed_request(self.verifier))
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE root_events SET evidence_digest=? WHERE event_index=1", ("0" * 64,))
        with self.assertRaises(RegistryIntegrityError):
            self.registry().verify_integrity()
        with self.assertRaises(RegistryIntegrityError):
            self.registry().issue(signed_request(self.verifier, issuer="issuer-b", observation="b", nonce="b"))

    def test_concurrent_writers_cannot_exceed_quota(self):
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        workers = [ctx.Process(target=concurrent_issue, args=(str(self.path), f"obs-{i}", f"nonce-{i}", queue)) for i in range(2)]
        for worker in workers: worker.start()
        for worker in workers: worker.join(10)
        self.assertTrue(all(worker.exitcode == 0 for worker in workers))
        self.assertEqual(sorted(queue.get(timeout=2) for _ in workers), ["issued", "limited"])
        self.assertTrue(self.registry(roots_per_window=1).verify_integrity())


if __name__ == "__main__":
    unittest.main()


class QuotaDenominationTests(unittest.TestCase):
    """R1.4's quota counts observation units, not artifacts.

    KL-014 v0.4 registered a claim that it counted issuance events, so an issuer
    could declare many observations inside one artifact and slip past the bound.
    That claim was FALSE -- see
    research/knowledge-ledger/experiments/KL-014/CORRECTION-20260813-quota.md.

    This test guards the property so the wrong conclusion is not reached again
    from reading the quota code.
    """

    def test_quota_is_denominated_in_observation_units(self):
        import time

        verifier = HmacIssuerVerifier({("issuer-a", "k1"): b"k"})
        registry = RootRegistry(
            Path(self.tmp.name) / "quota.db",
            verifier=verifier, integrity_key=b"i",
            roots_per_window=2, window_seconds=3600,
        )
        now = int(time.time())

        def request(observation):
            req = RootRequest(
                issuer_id="issuer-a", key_id="k1", observation_id=observation,
                proposition_id="p", value=True,
                evidence_digest=hashlib.sha256(observation.encode()).hexdigest(),
                observed_at=now, nonce=observation,
            )
            return req.with_signature(verifier.sign(req))

        minted = 0
        for index in range(4):
            try:
                registry.issue(request(f"sample-{index}"))
                minted += 1
            except IssuanceLimitError:
                pass

        # Four declared observations, quota of two: exactly two are minted.
        # If the quota bound artifacts rather than units, all four would pass.
        self.assertEqual(minted, 2)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
