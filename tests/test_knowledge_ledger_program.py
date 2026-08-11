import json
import unittest
from pathlib import Path

from knowledge_ledger import evaluate_transaction, verify_content_digest
from scripts.run_knowledge_transaction import render_transmission


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "research" / "knowledge-ledger"
REFERENCE_INPUT = PROGRAM / "interoperability" / "reference-input.json"


def _governing_registration(directory, status):
    """The registration matching this experiment's protocolVersion.

    Falls back to preregistration.json when no version is declared, which is the
    case for every seeded experiment and for those registered before the
    versioned-registration convention existed.
    """
    version = str(status.get("protocolVersion") or "")
    if version:
        token = version.split()[0].lstrip("v")
        candidate = directory / f"preregistration-v{token}.json"
        if candidate.is_file():
            return json.loads(candidate.read_text())
    return json.loads((directory / "preregistration.json").read_text())


class KnowledgeLedgerProgramTests(unittest.TestCase):
    def test_every_experiment_is_seeded_with_required_fields(self):
        registry = json.loads((PROGRAM / "EXPERIMENT-REGISTRY.json").read_text())
        experiments = registry["experiments"]
        self.assertEqual(
            [experiment["id"] for experiment in experiments],
            [f"KL-{index:03d}" for index in range(12)],
        )
        for experiment in experiments:
            for field in ("realm", "question", "null", "target", "primaryEndpoint", "firstGate"):
                self.assertTrue(experiment[field])

    def load_reference_input(self):
        return json.loads(REFERENCE_INPUT.read_text())

    def test_incomplete_search_cannot_become_absence(self):
        result = evaluate_transaction(self.load_reference_input())
        self.assertEqual(result["conclusion"], "not_established")
        self.assertFalse(result["search"]["complete"])
        self.assertEqual(result["evidence"]["records"], 4)
        self.assertEqual(result["evidence"]["distinctRoots"], 2)
        self.assertEqual(result["evidence"]["repeatedRecordsCollapsed"], 2)
        self.assertTrue(verify_content_digest(result))

    def test_digest_rejects_mutated_receipt(self):
        result = evaluate_transaction(self.load_reference_input())
        result["conclusion"] = "absent_within_declared_scope"
        self.assertFalse(verify_content_digest(result))

    def test_human_transmission_preserves_claim_limits(self):
        result = evaluate_transaction(self.load_reference_input())
        transmission = render_transmission(result)
        self.assertIn("Not established", transmission)
        self.assertIn(result["contentDigest"], transmission)
        self.assertIn("JSON receipt is authoritative", transmission)
        self.assertNotIn("proved absent", transmission.lower())

    def test_complete_search_permits_only_bounded_absence(self):
        payload = self.load_reference_input()
        for location in payload["searchLedger"]["locations"]:
            location["status"] = "searched"
        result = evaluate_transaction(payload)
        self.assertEqual(result["conclusion"], "absent_within_declared_scope")
        self.assertIn("declared search space", result["limits"][1])

    def test_copy_multiplication_is_invariant(self):
        payload = self.load_reference_input()
        baseline = evaluate_transaction(payload)
        payload["evidenceLedger"]["records"].extend(
            {"id": f"copy-{index}", "rootId": "scanner-family-1", "side": "support"}
            for index in range(1000)
        )
        multiplied = evaluate_transaction(payload)
        self.assertEqual(multiplied["evidence"]["distinctRoots"], baseline["evidence"]["distinctRoots"])
        self.assertEqual(multiplied["evidence"]["margin"], baseline["evidence"]["margin"])
        self.assertEqual(multiplied["conclusion"], baseline["conclusion"])

    def test_one_root_cannot_cross_sides(self):
        payload = self.load_reference_input()
        payload["evidenceLedger"]["records"].append(
            {"id": "contradiction", "rootId": "scanner-family-1", "side": "oppose"}
        )
        with self.assertRaises(ValueError):
            evaluate_transaction(payload)

    # The kernel-state ladder. A state outside this list is a typo or an
    # invented stage, and either way must not pass silently.
    LADDER = (
        "seeded", "preregistered", "fixture-passed", "exhaustive-passed",
        "randomized-passed", "adversarial-passed", "retrospective-passed",
        "shadow-passed", "bounded-pilot-passed", "failed", "incomplete",
        "blocked-safety",
    )

    def test_no_experiment_claims_progress_without_the_evidence_for_it(self):
        """Every experiment's declared state must be backed by artifacts.

        This replaces an earlier assertion that all twelve experiments were
        literally `seeded`. That version encoded a snapshot rather than an
        invariant: it passed because nothing had advanced, and it would have
        failed the moment anything did -- including a legitimate advance. It
        could not distinguish "KL-000 advanced with a confirmatory result" from
        "someone edited a status field", which is the thing actually worth
        protecting against.
        """
        for index in range(12):
            directory = PROGRAM / "experiments" / f"KL-{index:03d}"
            status = json.loads((directory / "STATUS.json").read_text())
            # The registration that governs an experiment is the one matching its
            # protocolVersion, which is not always preregistration.json. KL-011's
            # base file is the original SEED and was never a registration; its
            # registration is preregistration-v0.2.json, frozen and pinned by
            # PROTOCOL-COMMIT-v0.2.txt. Reading only the base file would have
            # forced a choice between editing a seed to say "preregistered" --
            # which is false -- and refusing to advance an experiment that is
            # properly registered. Both are worse than looking in the right place.
            preregistration = _governing_registration(directory, status)

            self.assertIn(status["state"], self.LADDER, directory.name)
            self.assertTrue(status["nextGate"], f"{directory.name} has no next gate")
            self.assertTrue(status.get("claimAllowed"), directory.name)

            if status["state"] == "seeded":
                # A seeded experiment must not look preregistered.
                self.assertEqual(preregistration["status"], "incomplete-seed", directory.name)
                self.assertFalse(
                    (directory / "results").exists() and any((directory / "results").iterdir()),
                    f"{directory.name} is seeded but carries results",
                )
            else:
                # Anything past seeded owes a frozen protocol and real output.
                self.assertEqual(preregistration["status"], "preregistered", directory.name)
                self.assertTrue(
                    any(directory.glob("PROTOCOL-COMMIT*.txt")),
                    f"{directory.name} advanced past seeded without a frozen protocol commit",
                )
                self.assertTrue(
                    (directory / "results").is_dir() and any((directory / "results").iterdir()),
                    f"{directory.name} advanced past seeded with no results",
                )
                self.assertIsNone(
                    preregistration["protocolCommit"],
                    f"{directory.name} preregistration was edited after registration; "
                    "the commit binding belongs in PROTOCOL-COMMIT.txt",
                )

    def test_every_experiment_still_declares_a_falsifiable_next_gate(self):
        for index in range(12):
            directory = PROGRAM / "experiments" / f"KL-{index:03d}"
            status = json.loads((directory / "STATUS.json").read_text())
            self.assertGreater(
                len(status["nextGate"]), 40,
                f"{directory.name} next gate is too vague to falsify",
            )


if __name__ == "__main__":
    unittest.main()
