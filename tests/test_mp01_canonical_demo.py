import json
from pathlib import Path

from experiments.mp01.run_mp01 import build_graph, run


def test_five_agent_votes_collapse_to_one_recorded_root():
    graph = build_graph()
    for claim_id in ("claim-a1", "claim-a2", "claim-a3", "claim-a4", "claim-a5"):
        assert graph.roots(claim_id) == frozenset({"claim-a1"})
    assert graph.roots("claim-b1") == frozenset({"claim-b1"})


def test_canonical_demo_preserves_minority_and_requests_evidence():
    result = run()
    assert result["agent_votes"] == {
        "answer_a": 5,
        "answer_b": 1,
        "naive_result": "answer_a",
    }
    assert result["independent_evidence"]["effective_ratio"] == "1:1"
    assert result["epistemic_assessment"]["verdict"] == "abstain"
    assert result["epistemic_assessment"]["interventions"] == [
        "PRESERVE_MINORITY",
        "REQUIRE_INDEPENDENT_SOURCE",
    ]
    assert "ground_truth" not in result


def test_public_artifact_matches_the_runner_exactly():
    artifact = Path("public/research/mp01-canonical-demo.json")
    assert json.loads(artifact.read_text()) == run()

