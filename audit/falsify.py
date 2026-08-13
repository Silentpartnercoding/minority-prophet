"""Adversarial falsification of the Minority Prophet formal core (Workstream C).

Every function here either CONFIRMS a statement over a bounded finite domain
(which is a finite exhaustive check, NOT a proof) or produces a WITNESS that
refutes a statement (which IS a proof of refutation, since a single
counterexample suffices).

Run:  python3 audit/falsify.py            # human readable
      python3 audit/falsify.py --json     # machine readable

Nothing in this file is evidence that a universally quantified statement is
true. Read CLAIM-SCOPE.md before citing any number printed here.
"""

from __future__ import annotations

import json
import sys
from itertools import product

from core_models import (
    dag_S,
    dag_all_worlds,
    dag_margin,
    dag_roots,
    dag_roots_of,
    dag_side_consistent,
    dag_verdict,
    forest_S,
    forest_all_parent_fns,
    forest_all_worlds,
    forest_margin,
    forest_root,
    forest_roots,
    forest_side_consistent,
    forest_verdict,
    verdict_of,
)

RESULTS: dict[str, object] = {}
WITNESSES: list[dict] = []


def witness(cid, title, target, kind, data, reading):
    """kind: 'refutes_theorem' | 'refutes_doctrine' | 'violates_assumption'."""
    w = dict(id=cid, title=title, target=target, kind=kind, witness=data, reading=reading)
    WITNESSES.append(w)
    return w


# ==========================================================================
# PART 1 — reproduce the forest results (sanity: do we agree with the repo?)
# ==========================================================================


def repro_forest_lemma1_t1(nmax=6):
    n_sc = l1_viol = t1_pairs = t1_viol = 0
    for n in range(1, nmax + 1):
        for p, a in forest_all_worlds(n):
            if not forest_side_consistent(p, a):
                continue
            n_sc += 1
            for side in (0, 1):
                if forest_S(p, a, side) != frozenset(
                    r for r in forest_roots(p) if a[r] == side
                ):
                    l1_viol += 1
            v = forest_verdict(p, a)
            R = forest_roots(p)
            for q in forest_all_parent_fns(n):
                if q == p or not forest_side_consistent(q, a):
                    continue
                if forest_roots(q) == R:
                    t1_pairs += 1
                    if forest_verdict(q, a) != v:
                        t1_viol += 1
    return dict(
        model="forest",
        side_consistent_worlds=n_sc,
        lemma1_violations=l1_viol,
        t1_rewirings_checked=t1_pairs,
        t1_violations=t1_viol,
    )


# ==========================================================================
# PART 2 — H0a: does the forest/DAG mismatch break anything?
# ==========================================================================


def dag_lemma1_t1_t2(nmax=4):
    """Same three statements, re-run in the multi-parent DAG the code implements."""
    n_sc = l1_viol = t1_pairs = t1_viol = 0
    t2_tested = t2_viol = 0
    from core_models import dag_all_parent_sets

    for n in range(1, nmax + 1):
        worlds = [(ps, a) for ps, a in dag_all_worlds(n) if dag_side_consistent(ps, a)]
        for ps, a in worlds:
            n_sc += 1
            for side in (0, 1):
                if dag_S(ps, a, side) != frozenset(
                    r for r in dag_roots(ps) if a[r] == side
                ):
                    l1_viol += 1
            v = dag_verdict(ps, a)
            R = dag_roots(ps)
            for qs in dag_all_parent_sets(n):
                if qs == ps or not dag_side_consistent(qs, a):
                    continue
                if dag_roots(qs) == R:
                    t1_pairs += 1
                    if dag_verdict(qs, a) != v:
                        t1_viol += 1
            # T2 in the DAG: append a claim whose parents are any non-empty
            # same-side subset of existing claims.
            for c in range(n):
                ps2 = tuple(list(ps) + [frozenset({c})])
                a2 = tuple(list(a) + [a[c]])
                t2_tested += 1
                if dag_verdict(ps2, a2) != v:
                    t2_viol += 1
    return dict(
        model="dag",
        side_consistent_worlds=n_sc,
        lemma1_violations=l1_viol,
        t1_rewirings_checked=t1_pairs,
        t1_violations=t1_viol,
        t2_duplications_tested=t2_tested,
        t2_violations=t2_viol,
    )


def dag_single_edge_edit_pm1(nmax=4):
    """T5's edge lemma in the DAG: does one edge add/remove move exactly one
    side's root count by exactly 1 (or 0 when the root set is untouched)?"""
    checked = bad = 0
    worst = 0
    for n in range(1, nmax + 1):
        for ps, a in dag_all_worlds(n):
            if not dag_side_consistent(ps, a):
                continue
            s1, s0 = len(dag_S(ps, a, 1)), len(dag_S(ps, a, 0))
            for c in range(n):
                for parent in range(c):
                    if a[parent] != a[c]:
                        continue  # would break side-consistency
                    new = set(ps[c])
                    new ^= {parent}  # toggle the single edge
                    qs = tuple(list(ps[:c]) + [frozenset(new)] + list(ps[c + 1 :]))
                    t1, t0 = len(dag_S(qs, a, 1)), len(dag_S(qs, a, 0))
                    d = abs(t1 - s1) + abs(t0 - s0)
                    checked += 1
                    worst = max(worst, d)
                    if d > 1:
                        bad += 1
    return dict(single_edge_edits_checked=checked, edits_moving_more_than_one=bad,
                max_total_root_count_movement=worst)


# ==========================================================================
# PART 3 — H0b: "adding copied claims cannot change the verdict"
# ==========================================================================


def t2_unrecorded_copy_witness():
    """The proved T2 requires the copy's parent edge to be RECORDED.
    A copy whose provenance is not recorded is parentless, i.e. a root."""
    # 2 honest roots asserting 1, 1 honest root asserting 0.
    p = (-1, -1, -1)
    a = (1, 1, 0)
    before = forest_verdict(p, a)
    m = forest_margin(p, a)
    # Two copies of claim 2 (assert 0) are added. Their parent edge is recorded:
    p_rec = (-1, -1, -1, 2, 2)
    a_rec = (1, 1, 0, 0, 0)
    after_recorded = forest_verdict(p_rec, a_rec)
    # Same two copies, provenance NOT recorded (this is what an undetected copy
    # looks like to the aggregator): they are parentless.
    p_unrec = (-1, -1, -1, -1, -1)
    a_unrec = (1, 1, 0, 0, 0)
    after_unrecorded = forest_verdict(p_unrec, a_unrec)
    data = dict(
        world_before=dict(parent=list(p), assert_=list(a), S1=sorted(forest_S(p, a, 1)),
                          S0=sorted(forest_S(p, a, 0)), verdict=before, margin=m),
        copies_with_recorded_provenance=dict(parent=list(p_rec), assert_=list(a_rec),
                                             verdict=after_recorded),
        copies_with_unrecorded_provenance=dict(parent=list(p_unrec), assert_=list(a_unrec),
                                               verdict=after_unrecorded),
    )
    refuted = after_unrecorded != before
    if refuted:
        witness(
            "CE-01",
            "Adding copies changes the verdict when the copy edge is not recorded",
            "T2, plain-English form: 'Adding copied claims cannot change the verdict'",
            "refutes_theorem",
            data,
            "The proved T2 is untouched: it quantifies only over copies whose "
            "parent edge is present in the graph. An undetected copy is "
            "indistinguishable from a root and is governed by T4/T5, not T2. "
            "Repair belongs to input validation / attestation (R1), not to the "
            "mathematics.",
        )
    return dict(refuted=refuted, **data)


# ==========================================================================
# PART 4 — H0c / the sharp one: cross-side conversion costs 2, not 1
# ==========================================================================


def cross_side_conversion_witness():
    """T4' says flow == margin forces ABSTENTION and reversal costs margin+1.
    T5 says k errors cannot change a verdict of margin > k.

    Both measure the adversary in units of `p_0 - p_1` (net per-side gain).
    A single SC-preserving adversary ACTION that converts one root (and its
    whole descendant subtree) from side 1 to side 0 contributes 2 to p_0 - p_1.
    So one action can do what the doctrine budgets two for."""
    # margin 2: roots 0,1,2 assert 1 ; root 3 asserts 0
    p = (-1, -1, -1, -1)
    a = (1, 1, 1, 0)
    v0, m0 = forest_verdict(p, a), forest_margin(p, a)
    # ONE action: root 0 is converted to the other side (key compromise on one
    # root, or one mislabelled observation). Side-consistency is preserved
    # because root 0 has no descendants here.
    a1 = (0, 1, 1, 0)
    v1 = forest_verdict(p, a1)
    # TWO actions at margin 2 -> full reversal (doctrine budgets margin+1 = 3)
    a2 = (0, 0, 1, 0)
    v2 = forest_verdict(p, a2)
    p01 = len(forest_S(p, a1, 0)) - len(forest_S(p, a, 0))
    p11 = len(forest_S(p, a1, 1)) - len(forest_S(p, a, 1))
    data = dict(
        base=dict(parent=list(p), assert_=list(a), S1=sorted(forest_S(p, a, 1)),
                  S0=sorted(forest_S(p, a, 0)), verdict=v0, margin=m0),
        one_conversion=dict(assert_=list(a1), S1=sorted(forest_S(p, a1, 1)),
                            S0=sorted(forest_S(p, a1, 0)), verdict=v1,
                            p0_gain=p01, p1_gain=p11, flow_p0_minus_p1=p01 - p11),
        two_conversions=dict(assert_=list(a2), S1=sorted(forest_S(p, a2, 1)),
                             S0=sorted(forest_S(p, a2, 0)), verdict=v2),
        doctrine_t5=("k=1 error, margin=2 > k, so T5's 'k root-integrity errors "
                     "cannot change a verdict with margin > k' predicts verdict "
                     "unchanged"),
        doctrine_t4prime=("reversal predicted to require margin+1 = 3 units"),
    )
    refuted_t5 = (m0 > 1) and (v1 != v0)
    refuted_t4p = v2 is not None and v2 != v0
    if refuted_t5:
        witness(
            "CE-02",
            "One SC-preserving side conversion changes a margin-2 verdict",
            "T5 security corollary: 'k root-integrity errors, accidental or "
            "adversarial, cannot change a verdict with margin > k'",
            "refutes_theorem",
            data,
            "T5's underlying EDGE lemma is fine. The corollary is false because "
            "it silently equates one adversary action with one unit of "
            "p_0 - p_1. A conversion is worth 2 units: -1 to the losing side, "
            "+1 to the gaining side. Repair is a definition change: state the "
            "budget in units of p_0 - p_1 and state which physical actions cost "
            "1 (root creation/destruction) and which cost 2 (root conversion).",
        )
    if refuted_t4p:
        witness(
            "CE-03",
            "Reversal at cost = margin (not margin+1) under root conversion",
            "T4' as stated: 'flow of exactly the margin forces ABSTENTION; "
            "reversal requires margin+1'",
            "refutes_theorem",
            data,
            "T4' is true when 'flow' means p_0 - p_1 and false when 'flow' means "
            "the number of roots that cross sides -- the reading its own name "
            "('cross-side phantom root flow') invites. The two differ by a "
            "factor of 2. Security impact: the attested-root budget an attacker "
            "must defeat is ceil((margin+1)/2) conversions, not margin+1.",
        )
    return dict(refuted_t5_corollary=refuted_t5, refuted_t4_prime=refuted_t4p, **data)


def conversion_budget_scan(max_margin=8):
    """How many single conversions reverse a verdict of margin m, vs doctrine?"""
    rows = []
    for m in range(1, max_margin + 1):
        n1, n0 = m + 1, 1  # |S1| - |S0| = m
        need_abstain = need_reverse = None
        for f in range(0, n1 + 1):
            v = verdict_of(n1 - f, n0 + f)
            if v is None and need_abstain is None:
                need_abstain = f
            if v == 0 and need_reverse is None:
                need_reverse = f
        rows.append(dict(margin=m, conversions_to_abstain=need_abstain,
                         conversions_to_reverse=need_reverse,
                         doctrine_says_abstain_at=m, doctrine_says_reverse_at=m + 1))
    return rows


# ==========================================================================
# PART 5 — one deleted record orphans an unbounded number of claims
# ==========================================================================


def single_deletion_witness(fanout=5):
    """A single lost/deleted claim record is ONE ops error but is not one edge
    edit: it orphans every child at once."""
    # 4 honest roots assert 1 ; claim 0 is a root asserting 0 with `fanout`
    # recorded copies hanging off it. Margin = 4 - 1 = 3.
    p = tuple([-1] + [0] * fanout + [-1, -1, -1, -1])
    a = tuple([0] * (1 + fanout) + [1, 1, 1, 1])
    v0, m0 = forest_verdict(p, a), forest_margin(p, a)
    # delete claim 0: children are orphaned (their parent edge dangles ->
    # EvidenceGraph.add would have rejected the dangling edge, so the only
    # representable repair is to promote them to roots)
    p_del = tuple([-1] * (1 + fanout) + [-1, -1, -1, -1])
    v1 = forest_verdict(p_del, a)
    data = dict(
        fanout=fanout,
        before=dict(parent=list(p), assert_=list(a), S1=sorted(forest_S(p, a, 1)),
                    S0=sorted(forest_S(p, a, 0)), verdict=v0, margin=m0),
        after_one_deletion=dict(parent=list(p_del), assert_=list(a),
                                S1=sorted(forest_S(p_del, a, 1)),
                                S0=sorted(forest_S(p_del, a, 0)), verdict=v1),
        root_count_movement=abs(len(forest_S(p_del, a, 0)) - len(forest_S(p, a, 0))),
    )
    refuted = v1 != v0
    if refuted:
        witness(
            "CE-04",
            "One deleted claim record moves a side count by the deleted node's "
            "fan-out (unbounded)",
            "T5 doctrine: 'min_flip_budget >= 2 confers proved immunity to any "
            "single key compromise or ops error'",
            "refutes_doctrine",
            data,
            "T5's lemma is about a single EDGE edit. Deleting one NODE is one "
            "ops error and an arbitrary number of edge edits. Immunity to "
            "'any single ops error' therefore does not follow from margin >= 2. "
            "Repair is infrastructural (append-only storage, no hard delete) "
            "plus a definition change naming the unit of error.",
        )
    return dict(refuted=refuted, **data)


def key_compromise_witness(minted=4):
    """One compromised root-signing key mints many roots -- again one 'error'."""
    p = tuple([-1] * (3 + minted))
    a = tuple([1, 1, 1] + [0] * minted)
    base_p, base_a = (-1, -1, -1), (1, 1, 1)
    data = dict(
        minted_roots=minted,
        before=dict(parent=list(base_p), assert_=list(base_a),
                    verdict=forest_verdict(base_p, base_a),
                    margin=forest_margin(base_p, base_a)),
        after_one_key_compromise=dict(parent=list(p), assert_=list(a),
                                      verdict=forest_verdict(p, a)),
    )
    refuted = forest_verdict(p, a) != forest_verdict(base_p, base_a)
    if refuted:
        witness(
            "CE-05",
            "One compromised root-signing key mints unboundedly many roots",
            "T5 doctrine: immunity to 'any single key compromise'",
            "refutes_doctrine",
            data,
            "The number of roots an attacker can create is a property of the "
            "attestation layer's rate limiting, not of the aggregator. R1 must "
            "bound roots-per-key; the theorems say nothing about it and become "
            "vacuous if it fails.",
        )
    return dict(refuted=refuted, **data)


# ==========================================================================
# PART 6 — assumption-boundary probes (violations, not theorem refutations)
# ==========================================================================


def non_sc_root_on_both_sides(nmax=5):
    """Outside side-consistency the literal S_a puts a root on both sides."""
    total = both = decisive_from_one_root = 0
    example = None
    for n in range(2, nmax + 1):
        for p, a in forest_all_worlds(n):
            if forest_side_consistent(p, a):
                continue
            total += 1
            s0, s1 = forest_S(p, a, 0), forest_S(p, a, 1)
            if s0 & s1:
                both += 1
                if example is None:
                    example = dict(parent=list(p), assert_=list(a),
                                   S1=sorted(s1), S0=sorted(s0),
                                   shared=sorted(s0 & s1))
            if len(forest_roots(p)) == 1 and forest_verdict(p, a) is not None:
                decisive_from_one_root += 1
    if example:
        witness(
            "CE-06",
            "Without side-consistency a single root is counted for both sides",
            "Lemma 1 (side-locality) and every theorem downstream of it",
            "violates_assumption",
            dict(non_sc_worlds=total, worlds_with_root_on_both_sides=both,
                 decisive_verdicts_from_a_single_root=decisive_from_one_root,
                 smallest_example=example),
            "This is not a refutation: side-consistency is an explicit "
            "hypothesis. It is a statement about how load-bearing that "
            "hypothesis is -- the aggregator does not degrade gracefully, it "
            "double-counts. Repair belongs to input validation: reject or "
            "quarantine non-side-consistent edges at ingest.",
        )
    return dict(non_sc_worlds=total, worlds_with_root_on_both_sides=both,
                fraction=round(both / max(total, 1), 4),
                decisive_verdicts_from_a_single_root=decisive_from_one_root,
                smallest_example=example)


def dag_synthesis_is_forbidden_witness():
    """Side-consistency in the DAG forbids a claim that cites evidence from
    both sides -- i.e. it forbids synthesis, not just 'camp blending'."""
    ps = (frozenset(), frozenset(), frozenset({0, 1}))
    a = (1, 0, 1)
    data = dict(
        parents=[sorted(s) for s in ps], assert_=list(a),
        side_consistent=dag_side_consistent(ps, a),
        S1=sorted(dag_S(ps, a, 1)), S0=sorted(dag_S(ps, a, 0)),
        verdict=dag_verdict(ps, a),
        note="claim 2 asserts 1 after weighing evidence 0 (asserts 1) and 1 "
             "(asserts 0); it is rejected by side-consistency and, if admitted, "
             "puts root 1 into S1 as well as S0",
    )
    witness(
        "CE-07",
        "Side-consistency forbids any claim derived from both sides",
        "R2 as described in PROVENANCE-REQUIREMENTS.md ('camps must not blend')",
        "violates_assumption",
        data,
        "In the single-parent forest this case is inexpressible, so the "
        "restrictiveness of R2 is invisible in the formalization. In the "
        "multi-parent DAG that provenance/graph.py implements, R2 excludes the "
        "ordinary act of forming a conclusion from conflicting evidence. This "
        "is a scope limit on applicability, not a false theorem.",
    )
    return data


def duplicate_root_identity_witness():
    """Set semantics: two distinct observations that are assigned the same root
    ID collapse to one; one identity decision moves a side count."""
    ids_distinct = ["r1", "r2", "r3"]
    ids_merged = ["r1", "r1", "r3"]
    a = [1, 1, 0]
    s1_d = len({i for i, v in zip(ids_distinct, a) if v == 1})
    s0_d = len({i for i, v in zip(ids_distinct, a) if v == 0})
    s1_m = len({i for i, v in zip(ids_merged, a) if v == 1})
    s0_m = len({i for i, v in zip(ids_merged, a) if v == 0})
    data = dict(
        distinct_ids=dict(ids=ids_distinct, S1=s1_d, S0=s0_d,
                          verdict=verdict_of(s1_d, s0_d)),
        merged_ids=dict(ids=ids_merged, S1=s1_m, S0=s0_m,
                        verdict=verdict_of(s1_m, s0_m)),
    )
    refuted = verdict_of(s1_d, s0_d) != verdict_of(s1_m, s0_m)
    if refuted:
        witness(
            "CE-08",
            "Root identity is an unstated parameter of every theorem",
            "All theorems: S_a is a SET of roots, so the verdict depends on the "
            "identity criterion, which is nowhere defined",
            "violates_assumption",
            data,
            "Neither PROOFS.md nor the Lean file defines when two roots are the "
            "same root. The Lean model makes identity definitionally the index, "
            "which assumes the question away. provenance/graph.py makes it an "
            "opaque caller-supplied string. Any semantic/canonical de-duplication "
            "step is therefore INSIDE the trusted base, not outside it.",
        )
    return dict(refuted=refuted, **data)


def sequence_independence_check(max_units=6):
    """'Different sequences producing the same net phantom flow' -- confirm the
    verdict depends only on the net, given the counts."""
    mismatches = 0
    checked = 0
    for s1 in range(0, max_units):
        for s0 in range(0, max_units):
            for d1 in range(-s1, max_units):
                for d0 in range(-s0, max_units):
                    checked += 1
                    if verdict_of(s1 + d1, s0 + d0) != verdict_of(s1 + d1, s0 + d0):
                        mismatches += 1
    return dict(order_dependence_found=mismatches, combinations_checked=checked,
                note="F is by construction a function of (|S1|,|S0|) only, so "
                     "path-independence is definitional, not empirical")


def weight_boundary_probe():
    """Zero / negative / unbounded weights: the CORE has no weights at all."""
    return dict(
        core_has_weights=False,
        note="PROOFS.md's F is a pure cardinality comparison. Weights appear only "
             "in aggregation/baselines.weighted_vote and aggregation/semantic "
             "(clamped to [0,1] by max(0,min(1,.))). No theorem covers weighted "
             "roots. Zero-weight roots are therefore counted at full strength by "
             "F and at zero by weighted_vote -- two different aggregators, one "
             "name. Negative weights are clamped to 0 silently, which is an "
             "implementation decision with no formal justification.",
    )


# ==========================================================================
# PART 7 — implementation probes (H1a, H1b)
# ==========================================================================


def probe_implementation():
    """NOTE (2026-08-05): CE-09 and CE-10 were repaired, so this function now
    emits 10 witnesses rather than 12. A witness that stops witnessing because
    the hole was closed is a pass, not a regression. CE-11/CE-12 still fire
    because they probe aggregation.semantic.evidence_root_vote, retained
    byte-identical for canonical-record binding; the corrected aggregator is
    aggregation.root_vote.verdict."""
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
    out: dict[str, object] = {}

    from provenance.graph import EvidenceGraph, EvidenceNode

    def node(nid, value, parents=()):
        return EvidenceNode(node_id=nid, proposition_id="p", value=value,
                            observer_id="o", source_id="s", confidence=1.0,
                            evidence={"ref": f"https://example.org/{nid}"},
                            copied_from=tuple(parents))

    # H1b: is side-consistency enforced anywhere?
    g = EvidenceGraph()
    g.add(node("r", True))
    try:
        g.add(node("c", False, ("r",)))   # child asserts the OPPOSITE of its parent
        sc_enforced = False
    except ValueError:
        sc_enforced = True
    out["side_consistency_enforced_by_EvidenceGraph"] = sc_enforced
    out["cross_side_edge_accepted_roots"] = sorted(g.roots("c")) if not sc_enforced else None
    if not sc_enforced:
        witness(
            "CE-09",
            "EvidenceGraph.add accepts a cross-side edge",
            "R2 (side-separation), declared a HARD requirement in "
            "PROVENANCE-REQUIREMENTS.md",
            "violates_assumption",
            dict(parent=dict(id="r", value=True), child=dict(id="c", value=False),
                 accepted=True, resulting_roots_of_child=sorted(g.roots("c"))),
            "The single hypothesis that every theorem depends on has no "
            "enforcement point in the implementation. Repair is input "
            "validation: EvidenceGraph.add must reject, or explicitly mark, an "
            "edge whose endpoints disagree on the same proposition.",
        )

    # Same-proposition check: is proposition_id even compared across an edge?
    g2 = EvidenceGraph()
    g2.add(node("r2", True))
    n2 = EvidenceNode(node_id="c2", proposition_id="DIFFERENT", value=True,
                      observer_id="o", source_id="s", confidence=1.0,
                      evidence={"ref": "https://example.org/c2"}, copied_from=("r2",))
    try:
        g2.add(n2)
        prop_checked = False
    except ValueError:
        prop_checked = True
    out["proposition_identity_enforced_across_edges"] = prop_checked
    if not prop_checked:
        witness(
            "CE-10",
            "A claim may be derived from a claim about a DIFFERENT proposition",
            "Proposition identity: the model assumes one proposition per world; "
            "the implementation does not",
            "violates_assumption",
            dict(parent=dict(id="r2", proposition_id="p"),
                 child=dict(id="c2", proposition_id="DIFFERENT"), accepted=True),
            "Every theorem is stated for a single proposition. The graph is "
            "global. Subject substitution -- swapping which proposition a root "
            "attests -- is therefore unconstrained at the data layer. Repair is "
            "input validation.",
        )

    # H1a: is evidence_root_vote order-dependent?
    from aggregation.semantic import evidence_root_vote

    class MC:
        def __init__(self, assignment, root_id, confidence=1.0, competence=1.0):
            self.assignment = assignment
            self.root_id = root_id
            self.confidence = confidence
            self.competence = competence

    a1 = MC((True,), "R")
    a2 = MC((False,), "R")
    b = MC((False,), "B")
    fwd = evidence_root_vote([a1, a2, b], lambda x: True)
    rev = evidence_root_vote([a2, a1, b], lambda x: True)
    order_dependent = fwd.assignment != rev.assignment
    out["evidence_root_vote_order_dependent_on_duplicate_root_id"] = order_dependent
    out["evidence_root_vote_forward"] = str(fwd.assignment)
    out["evidence_root_vote_reversed"] = str(rev.assignment)
    if order_dependent:
        witness(
            "CE-11",
            "evidence_root_vote is order-dependent when one root ID carries two "
            "different assignments",
            "Implementation invariant (determinism), not a theorem",
            "violates_assumption",
            dict(claims=[dict(root_id="R", assignment=[True]),
                         dict(root_id="R", assignment=[False]),
                         dict(root_id="B", assignment=[False])],
                 forward_result=str(fwd.assignment), reversed_result=str(rev.assignment)),
            "roots.setdefault(root_id, claim) makes the first writer win. That "
            "is exactly the non-side-consistent case, so the aggregator resolves "
            "an R2 violation silently and non-deterministically instead of "
            "failing closed. Repair is implementation: detect the conflict and "
            "abstain or raise.",
        )

    # rootless claims are dropped silently
    only_rootless = evidence_root_vote([MC((True,), None), MC((True,), None)],
                                       lambda x: True)
    out["evidence_root_vote_drops_root_id_None"] = only_rootless.roots_used == 0
    if only_rootless.roots_used == 0:
        witness(
            "CE-12",
            "Claims with root_id=None are silently discarded, not abstained on",
            "Abstention semantics: 'insufficient evidence should permit no "
            "decision' (FOUNDATIONS.md desideratum 5)",
            "violates_assumption",
            dict(claims=[dict(root_id=None, assignment=[True])] * 2,
                 roots_used=only_rootless.roots_used,
                 assignment=str(only_rootless.assignment)),
            "Unattributable claims vanish rather than forcing abstention. "
            "Combined with CE-01 this is the whole undetected-copy threat: "
            "provenance absent -> either dropped (here) or promoted to a root "
            "(in the PROOFS.md model). The two components disagree about what "
            "'no provenance' means.",
        )
    return out


# ==========================================================================
# driver
# ==========================================================================


def main():
    RESULTS["repro_forest_lemma1_t1_nmax6"] = repro_forest_lemma1_t1(6)
    RESULTS["dag_lemma1_t1_t2_nmax4"] = dag_lemma1_t1_t2(4)
    RESULTS["dag_single_edge_edit_pm1_nmax4"] = dag_single_edge_edit_pm1(4)
    RESULTS["t2_unrecorded_copy"] = t2_unrecorded_copy_witness()
    RESULTS["cross_side_conversion"] = cross_side_conversion_witness()
    RESULTS["conversion_budget_scan"] = conversion_budget_scan(8)
    RESULTS["single_deletion"] = single_deletion_witness(5)
    RESULTS["key_compromise"] = key_compromise_witness(4)
    RESULTS["non_sc_root_on_both_sides_nmax5"] = non_sc_root_on_both_sides(5)
    RESULTS["dag_synthesis_forbidden"] = dag_synthesis_is_forbidden_witness()
    RESULTS["duplicate_root_identity"] = duplicate_root_identity_witness()
    RESULTS["sequence_independence"] = sequence_independence_check()
    RESULTS["weight_boundary"] = weight_boundary_probe()
    RESULTS["implementation_probe"] = probe_implementation()

    payload = dict(results=RESULTS, witnesses=WITNESSES,
                   witness_count=len(WITNESSES))
    if "--json" in sys.argv:
        print(json.dumps(payload, indent=2, default=str))
        return
    for k, v in RESULTS.items():
        print(f"\n== {k} ==")
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(f"  {kk}: {vv}")
        else:
            print(f"  {v}")
    print(f"\n\n===== {len(WITNESSES)} WITNESSES =====")
    for w in WITNESSES:
        print(f"\n[{w['id']}] {w['title']}\n  kind:   {w['kind']}\n  target: {w['target']}")


if __name__ == "__main__":
    main()
