# Machine-checked proofs: copy invariance and the Immunity Theorem

## Definitions
World W = (C, parent, assert) where C is a finite set of claims, parent is a
partial function C -> C with parent(c).t < c.t (acyclicity via time), and
assert: C -> {0,1}. A claim with no parent is a ROOT. root(c) = the unique
ancestor of c with no parent. W is SIDE-CONSISTENT if every edge joins
same-assertion claims: assert(parent(c)) = assert(c) for all non-roots.
(The generative model satisfies this: copies inherit assertions.)

Evidence-root aggregator: S_a(W) = { root(c) : assert(c) = a }.
Verdict F(W) = 1 if |S_1| > |S_0|, 0 if |S_0| > |S_1|, ABSTAIN if equal.

## Lemma 1 (side-locality). If W is side-consistent then
S_a(W) = { r : r is a root and assert(r) = a }.
Proof. Chains preserve assertion (induction on chain length using
side-consistency), so root(c) asserts assert(c); hence S_a contains only
a-asserting roots. Conversely every a-asserting root r satisfies root(r) = r
and assert(r) = a, so r is in S_a. QED.

## Theorem 1 (Immunity). Let W' be obtained from side-consistent W by ANY
rewiring of parent edges that (i) preserves the set of roots (only re-targets
existing edges, never deletes or creates), and (ii) preserves
side-consistency (new parents share the child's assertion). Then
S_a(W') = S_a(W) for both a, hence F(W') = F(W).
Proof. W' is side-consistent with the same claims, same assertions, and the
same root set. By Lemma 1 applied to each, S_a(W') = { a-asserting roots }
= S_a(W). The verdict is a function of (|S_0|, |S_1|). QED.

Interpretation: the aggregator is invariant under arbitrary corruption of
WHO-COPIED-WHOM, provided corruption never crosses sides and never
manufactures or destroys roots. Lineage accuracy is irrelevant;
side-separation is the only load-bearing guarantee. This is the exact
mechanism behind the flat Mode-C curve in EXP005 (attribution 1.0 -> 0.59,
accuracy never below 0.98; residual wobble = abstention ties, not violations
-- the exhaustive checker below confirms zero violations).

## Theorem 2 (copy invariance of root counting). Adding a duplicate claim d
with parent(d) = c and assert(d) = assert(c) leaves S_a and F unchanged.
Proof. root(d) = root(c), already a member of S_assert(c). QED.

## Theorem 3 (majority is not copy-invariant). Counterexample: two claims
asserting 1, one asserting 0: majority = 1. Duplicate the 0-claim twice:
majority = 0. QED.

## Scope and honesty
These are theorems about the SPECIFIED aggregator on finite side-consistent
worlds. They do NOT claim: that inference recovers side-consistent lineage
under adversaries (EXP003 shows composed attacks break inference); that
root-manufacturing (sybil orphans) is harmless (it is excluded by (i) and is
exactly what attestation must prevent); or anything about real markets.
Machine verification below: exhaustive over all worlds with n <= 6 claims
and all side-preserving rewirings, plus 100,000 randomized larger instances.
`MinorityProphetV2.lean` contains an uncompiled Lean proof candidate for
Lemma 1 and Theorems 1 and 3. It has no compiler-ratified status yet; until a
Lean toolchain compiles it in-repository, the exhaustive check remains the
machine-led inspection of record.

## Theorem 4 (margin flip condition -- promoted from H5's rejection).
For side-consistent W and any rewiring W' preserving claims and assertions,
define phantom flow p_a = |S_a(W') \ S_a(W)| - |S_a(W) \ S_a(W')| (net root
gain of side a). Then F(W') differs from F(W)=1 only if p_0 - p_1 >=
|S_1(W)| - |S_0(W)| (and symmetrically). Proof: immediate from F being a
threshold function of the side-count margin. QED.
Consequence: no scalar corruption statistic independent of the per-world
margin can collapse corruption modes (EXP006/H5 REJECTED as preregistered,
max cross-mode spread 0.651). Adversaries are worse than noise at matched
confusion because they need only meet the margin in thin-margin worlds.
Security translation: the attestation budget an attacker must defeat equals
the true root margin -- so the defender's lever is margin, not lineage purity.


## Theorem 4' (tightness -- from C. He's independent verification, Aug 2026).
Net cross-side phantom root flow of exactly the margin forces ABSTENTION;
reversal requires margin+1. (Exhaustive: flow==margin yielded abstain in
4,638/4,638 decisive worlds, reversal in 0.) Security reading: denial costs
the margin; deception costs margin+1.

## Theorem 5 (root-error tolerance; universal form of T4').
Any single side-consistent edge edit that disturbs the root set changes
exactly one side's root count by exactly 1 (it either orphans a claim --
adding a root to that claim's side -- or de-orphans a root, removing one).
Hence k root-integrity errors, ACCIDENTAL OR ADVERSARIAL, cannot change a
verdict with margin > k, and cannot reverse one with margin > k-1. QED.
Empirical shadow (n=6, sampled jointly-applied random errors): P(change)=0
for all k<margin across 237,720+ trials/bucket; at k=margin, P(change)~0.51
(margin 1). Doctrine: min_flip_budget >= 2 confers proved immunity to any
single key compromise or ops error.

## Scope notes from independent verification (C. He)
- "Attribution is irrelevant" holds AMONG NON-ROOTS: a single root-set-
  disturbing edit flips verdicts 33.0% of the time pooled (9,364/28,368,
  n=6) -- entirely concentrated on margin-1 decisions per Theorem 5.
- Outside side-consistency the literal S_a places some root in both S_0 and
  S_1 in every non-SC world tested (44,450/44,450); formalizations must
  restrict flow accounting to SC comparisons or use multiset accounting.
