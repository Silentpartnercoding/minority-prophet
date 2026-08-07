import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "research" / "field-evidence" / "2026-08-06"


def test_reproduction_matches_committed_result() -> None:
    completed = subprocess.run(
        [sys.executable, str(PACKET / "reproduce.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    expected = json.loads((PACKET / "results.json").read_text())
    assert json.loads(completed.stdout) == expected


def test_report_preserves_the_observed_structural_counts() -> None:
    report = json.loads((PACKET / "results.json").read_text())
    assert report["summary"] == {
        "claims_total": 17,
        "one_root_decisions": 9,
        "primary_observer_claim_share": "8/17",
        "self_attestation_abstentions": 8,
        "verdicts": {"abstain": 8, "false": 2, "true": 7},
    }
    probe = report["root_identity_probe"]
    assert probe["observer_keyed"]["distinct_roots"] == 1
    assert probe["event_keyed"]["distinct_roots"] == 6
    assert probe["event_keyed"]["conversions_to_reverse"] == 4


if __name__ == "__main__":
    test_reproduction_matches_committed_result()
    test_report_preserves_the_observed_structural_counts()
