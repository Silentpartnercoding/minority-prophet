"""Phase 1 synthetic benchmark harness.

Loads the true prophet and false prophet fixtures, records every report in
the canonical evidence graph, counts distinct roots with root_vote, routes
each candidate with rh_decision.decide, and evaluates H2.1 to H2.4 against a
majority-vote baseline.

Deterministic. No zeta math. No unrecomputed numbers. No scores or
weights: every action comes from a root count plus recorded verification
facts. Does not call Gate decide() or TrustAllVerifier. Confirmations and
counterexamples are different propositions. RH_PROVEN is not a
representable state.
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ledger_adapter import (  # noqa: E402
    CLAIM_STATES,
    build_ledger_from_reports,
)
from rh_decision import (  # noqa: E402
    TowerRecheck,
    UniversalLedger,
    VerificationRecord,
    decide,
    universal_with_confirmations,
)

ROOT = os.path.dirname(HERE)
FIXTURES = os.path.join(ROOT, "fixtures")
SEED = 20260817

# Actions that count as "retained for verification" (H2.1).
RETAIN_ACTIONS = frozenset({"verify", "escalate"})
# Actions that are not a terminal truth commitment (H2.4).
NONCOMMIT_ACTIONS = frozenset({"verify", "abstain", "reject"})
# Actions allowed for false prophets (never escalate to FALSIFIED).
FP_ALLOWED_ACTIONS = frozenset({"reject", "verify", "abstain"})


def _load_json(name: str) -> dict:
    with open(os.path.join(FIXTURES, name)) as fh:
        return json.load(fh)


def _cand(
    claim_id: str,
    agent_id: str,
    result_hash: str,
    method: str,
    claim_type: str = "candidate_counterexample",
) -> dict:
    return {
        "claim_id": claim_id,
        "agent_id": agent_id,
        "claim_type": claim_type,
        "method": method,
        "result_hash": result_hash,
        "parent_evidence_ids": [],
    }


def materialize_control_reports(control: dict) -> List[dict]:
    """Minority / candidate side only.

    Confirmations are a different proposition and are not mixed into
    the candidate ledger. Majority-vote uses fixture counts, not these
    rows.
    """
    cid = control["control_id"]
    if cid == "CONTROL_A":
        return [_cand("min_1", "agent_min_1", "hash_A_min", "method_alpha")]
    if cid == "CONTROL_B":
        return [_cand("fp_1", "agent_fp_1", "hash_B_fake", "method_lowprec")]
    if cid == "CONTROL_C":
        return [
            _cand("min_1", "agent_min_1", "hash_C_find", "method_alpha"),
            _cand("ver_1", "agent_ver_1", "hash_C_repro", "method_beta", "counterexample"),
        ]
    if cid == "CONTROL_D":
        # 100 recorded copies of one work-product; parents omitted (hostile).
        return [
            _cand(f"copy_{i}", f"agent_{i}", "hash_D_shared", "method_copy")
            for i in range(100)
        ]
    if cid == "CONTROL_E":
        return [
            _cand("min_1", "agent_min_1", "hash_E_1", "method_alpha"),
            _cand("min_2", "agent_min_2", "hash_E_2", "method_beta"),
            _cand("min_3", "agent_min_3", "hash_E_3", "method_gamma"),
        ]
    if cid == "CONTROL_F":
        return [_cand("anom_1", "agent_anom_1", "hash_F_anom", "method_unstable", "anomaly")]
    if cid == "CONTROL_G":
        return [_cand("min_1", "agent_min_1", "hash_G_find", "method_alpha")]
    if cid == "CONTROL_H":
        return [_cand("fp_8", "agent_fp_8", "hash_H_forged", "method_forged")]
    raise ValueError(f"unknown control {cid}")


def materialize_fp_reports(case: dict) -> List[dict]:
    fp_id = case["fp_id"]
    if fp_id == "FP5":
        return [
            _cand(f"fp5_{i}", f"agent_fp5_{i}", "fp5_shared_work_product", "replay")
            for i in range(20)
        ]
    injected = case.get("injected_report", {})
    result_hash = injected.get("result_hash") or ""
    method = injected.get("method") or ""
    # FP6 is the no-method / no-hash hallucination: leave it unattributed.
    # Other single-report FPs get a stand-in fingerprint so quarantine
    # does not erase an otherwise-attributed (but false) calculation.
    if fp_id != "FP6":
        result_hash = result_hash or f"hash_{fp_id}"
        method = method or f"method_{fp_id}"
    return [
        {
            "claim_id": f"{fp_id}_0",
            "agent_id": f"agent_{fp_id}",
            "claim_type": injected.get("claim_type", "candidate_counterexample"),
            "method": method or "",
            "result_hash": result_hash or "",
            "parent_evidence_ids": [],
        }
    ]


def majority_vote_from_counts(blocks: Dict[str, dict]) -> Tuple[str, int, int]:
    """Plurality of claim_type. Mixes confirmations and counterexamples
    into one ballot, which is the error this experiment exists to beat.
    Consensus is never truth; this baseline exists to lose H2.1.
    """
    counts: Counter = Counter()
    for block in blocks.values():
        counts[block["claim_type"]] += int(block["count"])
    winner, n = counts.most_common(1)[0]
    return winner, n, sum(counts.values())


def majority_vote_from_reports(reports: List[dict]) -> Tuple[str, int, int]:
    counts = Counter(r["claim_type"] for r in reports)
    winner, n = counts.most_common(1)[0]
    return winner, n, len(reports)


def _record(level: int, reproducibility: str, stable: bool, consistent: bool = True,
            external_certificate: str = "", tower_recheck=None):
    return VerificationRecord(
        level=level,
        reproducibility=reproducibility,
        numerically_stable=stable,
        internally_consistent=consistent,
        external_certificate=external_certificate,
        tower_recheck=tower_recheck,
    )


def _fixture_record(control: dict) -> VerificationRecord:
    """Record for a world whose fixture states its verification outcome."""
    v = control["verification"]
    return _record(
        v["level"], "reproduced", True,
        external_certificate=v["external_certificate"],
        tower_recheck=TowerRecheck(**v["tower_recheck"]),
    )


# Verification facts per fixture world. These are what the verification
# plane would have recorded; the decision layer reads them as yes or no facts.
_CONTROL_RECORDS = {
    "CONTROL_A": ("candidate_counterexample", _record(0, "not_attempted", True)),
    "CONTROL_B": ("candidate_counterexample", _record(2, "failed", False)),
    "CONTROL_C": ("candidate_counterexample", _record(1, "reproduced", True)),
    "CONTROL_D": ("candidate_counterexample", _record(2, "failed", False)),
    "CONTROL_E": ("candidate_counterexample", _record(1, "reproduced", True)),
    "CONTROL_F": ("anomaly", _record(2, "partial", True)),
}


def _fp_record(case: dict):
    fp_id = case["fp_id"]
    if fp_id == "FP6":
        return _record(0, "not_attempted", True)
    if fp_id == "FP7":
        return _record(2, "failed", False, consistent=False)
    return _record(2, "failed", False)


def _confirming_root_count(blocks: Dict[str, dict]) -> int:
    return sum(int(b["count"]) for b in blocks.values() if b["claim_type"] == "confirmation")


def evaluate_control(control: dict, unattributed_policy: str = "quarantine") -> dict:
    cid = control["control_id"]
    reports = materialize_control_reports(control)
    ledger = build_ledger_from_reports(reports, unattributed_policy=unattributed_policy)
    ids = [r["claim_id"] for r in reports]
    if "verification" in control:
        claim_type, record = "candidate_counterexample", _fixture_record(control)
    else:
        claim_type, record = _CONTROL_RECORDS[cid]
    universal = universal_with_confirmations(
        f"world:{cid}", _confirming_root_count(control["reports"]), cid
    )
    d = decide(ledger, ids, claim_type=claim_type, record=record, universal=universal)
    maj_winner, maj_n, maj_total = majority_vote_from_counts(control["reports"])
    return {
        "control_id": cid,
        "independent_support_count": d.independent_roots,
        "raw_support_count": d.raw_reports,
        "unattributed_count": d.unattributed,
        "mp_action": d.action,
        "mp_next_state": d.next_state,
        "mp_reason": d.reason,
        "universal_outcome": d.universal_outcome,
        "ignored_confirming_roots": d.ignored_confirming_roots,
        "majority_winner": maj_winner,
        "majority_winner_n": maj_n,
        "majority_total": maj_total,
        "majority_retains_minority": maj_winner
        in ("candidate_counterexample", "counterexample", "anomaly"),
    }


def evaluate_fp(case: dict, unattributed_policy: str = "quarantine") -> dict:
    reports = materialize_fp_reports(case)
    ledger = build_ledger_from_reports(reports, unattributed_policy=unattributed_policy)
    ids = [r["claim_id"] for r in reports]
    universal = UniversalLedger(f"rh:{case['fp_id']}")
    d = decide(
        ledger,
        ids,
        claim_type="candidate_counterexample",
        record=_fp_record(case),
        universal=universal,
    )
    maj_winner, maj_n, maj_total = majority_vote_from_reports(reports)
    # The evaluator applies the fixture's verification outcome. The decision
    # layer never sees expected_terminal_state; it is used only to grade.
    terminal = case["expected_terminal_state"]
    if d.action == "escalate":
        terminal = "FALSIFIED"  # hard failure: a fake was treated as decisive
    return {
        "fp_id": case["fp_id"],
        "independent_support_count": d.independent_roots,
        "raw_support_count": d.raw_reports,
        "unattributed_count": d.unattributed,
        "mp_action": d.action,
        "mp_next_state": d.next_state,
        "mp_reason": d.reason,
        "universal_outcome": d.universal_outcome,
        "majority_winner": maj_winner,
        "majority_winner_n": maj_n,
        "majority_total": maj_total,
        "terminal_for_scoring": terminal,
        "must_never_reach": case["must_never_reach"],
    }


@dataclass
class HypothesisOutcome:
    hypothesis_id: str
    success: bool
    failure: bool
    mp_metric: float
    baseline_metric: float
    detail: str

    def as_dict(self) -> dict:
        return {
            "hypothesis_id": self.hypothesis_id,
            "success": self.success,
            "failure": self.failure,
            "mp_metric": self.mp_metric,
            "baseline_metric": self.baseline_metric,
            "detail": self.detail,
        }


def _h21(control_rows: List[dict]) -> HypothesisOutcome:
    targets = [r for r in control_rows
               if r["control_id"] in ("CONTROL_A", "CONTROL_C", "CONTROL_E", "CONTROL_G")]
    mp_keep = sum(1 for r in targets if r["mp_action"] in RETAIN_ACTIONS)
    base_keep = sum(1 for r in targets if r["majority_retains_minority"])
    n = len(targets)
    mp_rate = mp_keep / n
    base_rate = base_keep / n
    suppressed = [
        r["control_id"]
        for r in targets
        if r["mp_action"] not in RETAIN_ACTIONS
    ]
    failure = mp_rate <= base_rate or bool(suppressed)
    success = mp_rate > base_rate and not suppressed
    return HypothesisOutcome(
        "H2.1",
        success,
        failure,
        mp_rate,
        base_rate,
        f"MP retained {mp_keep}/{n}; majority retained {base_keep}/{n}; suppressed={suppressed}",
    )


def _h22(fp_rows: List[dict]) -> HypothesisOutcome:
    n = len(fp_rows)
    reached_falsified = [r["fp_id"] for r in fp_rows if r["terminal_for_scoring"] == "FALSIFIED"]
    escalated = [r["fp_id"] for r in fp_rows if r["mp_action"] == "escalate"]
    rejected_or_abstained = [
        r
        for r in fp_rows
        if r["terminal_for_scoring"] in ("REJECTED_FALSE_POSITIVE", "ABSTAIN")
        and r["mp_action"] in FP_ALLOWED_ACTIONS
    ]
    fp5 = next(r for r in fp_rows if r["fp_id"] == "FP5")
    fp5_ok = fp5["independent_support_count"] == 1
    mp_rate = len(rejected_or_abstained) / n
    # Majority "accepts" a fake when the plurality is a candidate type.
    base_accept = sum(
        1
        for r in fp_rows
        if r["majority_winner"] in ("candidate_counterexample", "counterexample")
    )
    base_reject_rate = 1.0 - (base_accept / n)
    failure = bool(reached_falsified) or bool(escalated) or not fp5_ok
    success = (len(rejected_or_abstained) == n) and fp5_ok and not failure
    return HypothesisOutcome(
        "H2.2",
        success,
        failure,
        mp_rate,
        base_reject_rate,
        f"rejected_or_abstained={len(rejected_or_abstained)}/{n}; "
        f"FP5_count={fp5['independent_support_count']}; "
        f"escalated={escalated}; falsified={reached_falsified}",
    )


def _h23(control_rows: List[dict]) -> HypothesisOutcome:
    d = next(r for r in control_rows if r["control_id"] == "CONTROL_D")
    e = next(r for r in control_rows if r["control_id"] == "CONTROL_E")
    d_ok = d["independent_support_count"] == 1
    e_ok = e["independent_support_count"] == 3
    # Majority treats raw copies as votes; its "independence" is raw count.
    failure = (d["independent_support_count"] > 1) or (e["independent_support_count"] < 3)
    success = d_ok and e_ok
    return HypothesisOutcome(
        "H2.3",
        success,
        failure,
        float(int(d_ok) + int(e_ok)),
        0.0,
        f"D count={d['independent_support_count']} (want 1, raw={d['raw_support_count']}); "
        f"E count={e['independent_support_count']} (want 3)",
    )


def _h24(control_rows: List[dict]) -> HypothesisOutcome:
    f = next(r for r in control_rows if r["control_id"] == "CONTROL_F")
    mp_ok = f["mp_action"] in NONCOMMIT_ACTIONS and f["mp_action"] != "escalate"
    # Majority commits to confirmation = a terminal truth commitment.
    base_commits = f["majority_winner"] == "confirmation"
    failure = not mp_ok
    success = mp_ok
    return HypothesisOutcome(
        "H2.4",
        success,
        failure,
        1.0 if mp_ok else 0.0,
        0.0 if base_commits else 1.0,
        f"MP action={f['mp_action']}; majority_winner={f['majority_winner']}",
    )


def _h25(control_rows: List[dict], fp_rows: List[dict]) -> HypothesisOutcome:
    """Certified path: the tower's recheck is the only way to a counterexample
    root, a failed recheck rejects, and nothing reaches FALSIFIED."""
    g = next(r for r in control_rows if r["control_id"] == "CONTROL_G")
    h = next(r for r in control_rows if r["control_id"] == "CONTROL_H")
    g_ok = (g["mp_action"] == "escalate"
            and g["mp_next_state"] == "CANDIDATE_FALSIFIER"
            and g["universal_outcome"] == "refuted"
            and g["ignored_confirming_roots"] == 999)
    h_ok = h["mp_action"] == "reject" and h["universal_outcome"] == "not_refuted"
    others = [r for r in control_rows if r["control_id"] != "CONTROL_G"]
    only_g_refutes = all(r["universal_outcome"] == "not_refuted" for r in others)
    never_falsified = all(r["mp_next_state"] != "FALSIFIED" for r in control_rows + fp_rows)
    ok = g_ok and h_ok and only_g_refutes and never_falsified
    base_g = g["majority_retains_minority"]
    return HypothesisOutcome(
        "H2.5",
        ok,
        not ok,
        1.0 if ok else 0.0,
        1.0 if base_g else 0.0,
        f"G action={g['mp_action']} state={g['mp_next_state']} universal={g['universal_outcome']}; "
        f"H action={h['mp_action']} reason={h['mp_reason']}; majority_winner_G={g['majority_winner']}",
    )


def run_phase1(seed: int = SEED, unattributed_policy: str = "quarantine") -> Dict[str, Any]:
    rng = random.Random(seed)
    # Seed is consumed so replay is pinned even if later shuffles appear.
    rng.random()

    if "RH_PROVEN" in CLAIM_STATES:
        raise RuntimeError("RH_PROVEN must not be a representable state")

    controls = _load_json("true_prophet_cases.json")["controls"]
    fp_cases = _load_json("false_prophet_cases.json")["cases"]

    control_rows = [evaluate_control(c, unattributed_policy) for c in controls]
    fp_rows = [evaluate_fp(c, unattributed_policy) for c in fp_cases]

    outcomes = [
        _h21(control_rows),
        _h22(fp_rows),
        _h23(control_rows),
        _h24(control_rows),
        _h25(control_rows, fp_rows),
    ]
    return {
        "seed": seed,
        "phase": 1,
        "unattributed_policy": unattributed_policy,
        "synthetic_only": True,
        "zeta_math": False,
        "unrecomputed_numbers": False,
        "gate_path": "forbidden",
        "scores_or_weights": False,
        "verdict_rule": "distinct root count; universal claim by asymmetric_verdict",
        "controls": control_rows,
        "false_prophets": fp_rows,
        "hypotheses": [o.as_dict() for o in outcomes],
        "all_success": all(o.success and not o.failure for o in outcomes),
    }


def main() -> int:
    result = run_phase1()
    print(json.dumps(result, indent=2, sort_keys=True))
    print()
    for h in result["hypotheses"]:
        flag = "PASS" if h["success"] and not h["failure"] else "FAIL"
        print(f"{h['hypothesis_id']} {flag}: {h['detail']}")
    print("ALL_SUCCESS" if result["all_success"] else "ALL_SUCCESS=false")
    return 0 if result["all_success"] else 1


if __name__ == "__main__":
    sys.exit(main())
