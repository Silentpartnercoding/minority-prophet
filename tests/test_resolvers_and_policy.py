"""Doormen, and the cost of an answer nobody could give.

Closes three holes the stack map listed as open: no resolver existed, nothing
acted on a high unverifiable rate, and the newest gates had no callers.
"""

import hashlib
import pathlib
import subprocess
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from knowledge_ledger.pipeline import assemble  # noqa: E402
from provenance.resolvers import (  # noqa: E402
    content_store_resolver, file_resolver, first_answer, git_object_resolver,
    http_resolver, local_resolver,
)
from provenance.unverifiable_policy import (  # noqa: E402
    ABSTAIN_UNDERPOWERED, ABSTAIN_UNVERIFIABLE, SETTLE, UnverifiablePolicy, apply_policy,
)

WARRANT = {"warrant_version": "1", "claim_type": "cited", "verify_determinism": "deterministic"}


# ---- resolvers -------------------------------------------------------------

def test_content_store_finds_by_digest_and_reports_absence():
    with tempfile.TemporaryDirectory() as store:
        (pathlib.Path(store) / "a.txt").write_text("hello\n")
        resolve = content_store_resolver(store)
        assert resolve("hash", hashlib.sha256(b"hello\n").hexdigest()) is True
        assert resolve("hash", "f" * 64) is False


def test_a_resolver_returns_none_for_forms_it_does_not_own():
    """Not 'absent'. A doorman for hashes has no opinion about DOIs."""
    with tempfile.TemporaryDirectory() as store:
        assert content_store_resolver(store)("doi", "10.1/x") is None


def test_missing_store_is_unanswerable_not_absent():
    """'I have nowhere to look' must never read as 'it is not there'."""
    assert content_store_resolver("/nonexistent/store")("hash", "a" * 64) is None


def test_git_resolver_answers_only_where_a_repository_is_readable():
    with tempfile.TemporaryDirectory() as d:
        repo = pathlib.Path(d) / "r"
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
        (repo / "f").write_text("x")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "c"], check=True)
        sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert git_object_resolver([str(repo)])("hash", sha) is True
        assert git_object_resolver([str(repo)])("hash", "0" * 40) is False
        assert git_object_resolver(["/nope"])("hash", sha) is None


def test_file_resolver_refuses_to_answer_outside_its_declared_roots():
    """A resolver that stats any path it is handed is a disk oracle."""
    with tempfile.TemporaryDirectory() as d:
        inside = pathlib.Path(d) / "in.txt"
        inside.write_text("x")
        resolve = file_resolver([d])
        assert resolve("url", f"file://{inside}") is True
        assert resolve("url", f"file://{inside}.missing") is False
        assert resolve("url", "file:///etc/hosts") is None


def test_http_resolver_stays_inside_its_allowlist_and_never_raises():
    def opener(url, timeout=None):
        raise RuntimeError("network down")
    resolve = http_resolver(["doi.org"], opener=opener)
    assert resolve("doi", "10.1/x") is None            # transport failure -> cannot tell
    assert resolve("url", "https://elsewhere.test/a") is None   # not allowlisted

    def not_found(url, timeout=None):
        raise RuntimeError("HTTP Error 404: Not Found")
    assert http_resolver(["doi.org"], opener=not_found)("doi", "10.1/x") is False


def test_first_answer_prefers_the_first_doorman_that_can_speak():
    a = lambda form, ref: None
    b = lambda form, ref: True
    c = lambda form, ref: False
    assert first_answer(a, b, c)("hash", "x") is True
    assert first_answer(a, a)("hash", "x") is None


def test_local_resolver_with_nothing_configured_answers_nothing():
    assert local_resolver()("hash", "a" * 64) is None


# ---- the policy ------------------------------------------------------------

def test_a_clean_population_settles():
    assert apply_policy({"verified": 4, "rejected": 0, "unverifiable": 0})["decision"] == SETTLE


def test_a_rejected_root_does_not_block_settlement():
    """The policy governs unverifiability, not guilt. A demonstrated absence is
    the evaluator's business."""
    assert apply_policy({"verified": 3, "rejected": 1, "unverifiable": 0})["decision"] == SETTLE


def test_fog_can_never_withhold_action_on_a_confirmed_finding():
    """The guard. Something was actually found; fog around it does not un-find
    it. Withholding here would mean sitting on a real finding because its
    neighbours were unreachable — and deferring is the harmful act whenever the
    status quo is exposure."""
    heavy_fog_with_a_finding = {"verified": 1, "rejected": 1, "unverifiable": 7}
    decision = apply_policy(heavy_fog_with_a_finding)
    assert decision["decision"] == SETTLE
    assert decision["unverifiableShare"] > 0.5, "the ceiling was crossed and deliberately ignored"
    assert "cannot withhold it" in decision["note"]


def test_withholding_a_CLEAN_verdict_over_fog_is_still_enforced():
    """The narrowing, from the other side. Refusing to certify `nothing here`
    when most evidence is unreachable sits on no finding, so it is safe in every
    domain — and it is the whole defence against citing only unreachable
    sources. An earlier draft gated this behind a declaration and reopened the
    attack."""
    attack = {"verified": 0, "rejected": 0, "unverifiable": 9}
    assert apply_policy(attack)["decision"] != SETTLE


def test_the_two_kinds_of_withholding_are_treated_differently():
    """Stated as a property: a finding always settles, fog alone never does."""
    with_finding = {"verified": 1, "rejected": 1, "unverifiable": 7}
    without = {"verified": 1, "rejected": 0, "unverifiable": 7}
    assert apply_policy(with_finding)["decision"] == SETTLE
    assert apply_policy(without)["decision"] != SETTLE


def test_the_attack_now_costs_something():
    """Cite only unreachable sources and the settlement stops, though nothing is
    condemned. This is the hole the schema named and no code answered."""
    decision = apply_policy({"verified": 0, "rejected": 0, "unverifiable": 9})
    assert decision["decision"] == ABSTAIN_UNDERPOWERED
    assert decision["condemnsAnything"] is False
    assert decision["wouldLiftIf"]


def test_fog_above_the_ceiling_abstains_once_enough_roots_were_answered():
    decision = apply_policy({"verified": 2, "rejected": 0, "unverifiable": 5})
    assert decision["decision"] == ABSTAIN_UNVERIFIABLE
    assert decision["unverifiableShare"] == 0.714


def test_all_three_decisions_are_reachable():
    """A policy with one outcome is a decoration."""
    got = {apply_policy(o)["decision"] for o in (
        {"verified": 4, "rejected": 0, "unverifiable": 0},
        {"verified": 2, "rejected": 0, "unverifiable": 5},
        {"verified": 0, "rejected": 0, "unverifiable": 9})}
    assert got == {SETTLE, ABSTAIN_UNVERIFIABLE, ABSTAIN_UNDERPOWERED}


def test_the_policy_never_condemns_and_only_ever_withholds():
    """Abstention cannot cause a wrong effect; that asymmetry is what makes this
    safe to apply at all."""
    for outcomes in ({"verified": 0, "rejected": 0, "unverifiable": 9},
                     {"verified": 2, "rejected": 0, "unverifiable": 5},
                     {"verified": 4, "rejected": 0, "unverifiable": 0}):
        assert apply_policy(outcomes)["condemnsAnything"] is False


def test_thresholds_are_declared_and_validated():
    with pytest.raises(ValueError):
        UnverifiablePolicy(max_unverifiable_share=1.5)
    with pytest.raises(ValueError):
        UnverifiablePolicy(min_checked_roots=0)


# ---- the pipeline now calls both ------------------------------------------

def _payload(records, claim="presence"):
    return {"transactionId": "t", "claim": {"type": claim, "statement": "s"},
            "searchLedger": {"locations": [{"id": "l1", "status": "searched"}]},
            "evidenceLedger": {"records": records}}


def test_the_pipeline_actually_calls_a_resolver_and_the_policy():
    """The 'no callers' hole: these gates now run inside the assembled path."""
    real = {**WARRANT, "doi": "10.1038/real"}
    fog = {**WARRANT, "doi": "10.1038/unreachable"}
    docs = {"SRC-0": {"isOriginal": True}, "C1": {"derivedFrom": "SRC-0"},
            "C2": {"derivedFrom": "SRC-0"}, "A": {"isOriginal": True}}
    resolver = lambda form, ref: True if ref == "10.1038/real" else None
    records = [{"id": "C1", "side": "support", "rootId": "C1", "evidence": real},
               {"id": "C2", "side": "support", "rootId": "C2", "evidence": fog},
               {"id": "A", "side": "oppose", "rootId": "A", "evidence": real}]
    result = assemble(_payload(records), docs, resolver=resolver)
    assert result["stages"]["recheck"]["outcomes"]["verified"] == 2
    assert result["stages"]["recheck"]["outcomes"]["unverifiable"] == 1
    assert result["stages"]["settlement"]["decision"] == SETTLE


def test_an_all_fog_population_makes_the_pipeline_withhold_settlement():
    fog = {**WARRANT, "doi": "10.1038/unreachable"}
    docs = {"SRC-0": {"isOriginal": True}, **{f"C{i}": {"derivedFrom": "SRC-0"} for i in (1, 2, 3)}}
    records = [{"id": f"C{i}", "side": "support", "rootId": f"C{i}", "evidence": fog}
               for i in (1, 2, 3)]
    result = assemble(_payload(records), docs, resolver=lambda f, r: None)
    assert result["stages"]["settlement"]["actionable"] is False
    assert result["stages"]["settlement"]["decision"] == ABSTAIN_UNDERPOWERED


def test_the_receipt_says_when_the_root_count_did_not_decide_anything():
    """The absence hole: surfaced rather than fixed. An absence verdict turns on
    whether ANY opposing root survives, so the root rule can move the margin and
    leave the answer alone -- and a reader should not credit it either way."""
    docs = {"SRC-0": {"isOriginal": True},
            **{f"C{i}": {"derivedFrom": "SRC-0"} for i in range(1, 6)},
            "A": {"isOriginal": True}}
    records = ([{"id": f"C{i}", "side": "support", "rootId": f"S{i}"} for i in range(1, 6)]
               + [{"id": "A", "side": "oppose", "rootId": "A"}])
    result = assemble(_payload(records, "absence"), docs)["stages"]["evaluation"]
    assert result["conclusionChanged"] is False
    assert result["marginMovedWithoutVerdict"] is True
