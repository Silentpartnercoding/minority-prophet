from experiments.hes1.run_hes1 import cppcheck_votes, outcome_name
from experiments.hgd1.run_hgd1 import assess, receipt


def test_duplicate_origin_cannot_mint_independence():
    original = assess([receipt("a", 1), receipt("b", 0)], [], "interval")
    duplicate = assess([receipt("a", 1), receipt("b", 0), receipt("b", 0)], [], "interval")
    assert duplicate == original


def test_contradictory_root_does_not_override_two_roots():
    outcome = assess([receipt("a", 1), receipt("b", 1), receipt("c", 0)], [], "interval")
    assert outcome["state"] == "ANSWER"
    assert outcome["answer"] == 1


def test_unknown_acquired_evidence_escalates():
    outcome = assess([receipt("a", 1), receipt("new", 0, support="unknown")], [], "interval")
    assert outcome["state"] == "ESCALATE"


def test_cppcheck_packet_is_complete_and_parseable():
    votes = cppcheck_votes()
    assert len(votes) == 46
    assert all(support == "supported" and vote in {0, 1} for support, vote in votes.values())


def test_recovery_labels_do_not_turn_abstention_into_success():
    assert outcome_name("ABSTAIN", None, 1) == "still_abstain"
    assert outcome_name("ESCALATE", None, 1) == "escalate"
