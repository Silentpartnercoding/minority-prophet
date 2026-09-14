# What is actually established

This is a reader-oriented status guide, not a new source of claim authority.
When wording conflicts, defer to [`PUBLIC-CLAIMS.md`](../../PUBLIC-CLAIMS.md),
[`EVIDENCE-ALIGNMENT.md`](../../EVIDENCE-ALIGNMENT.md),
[`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md), and the formal ledgers.

Current record status is listed in full in
[`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md): the EXP series, HVI-1,
HEO-1, HGD-1, HGD-2, HES-1, EAA-P5 and the LIR series, including every rejected
and incomplete record. None establishes real-world provenance recovery. Results
added after 2026-08-09 are not canonical records; they are summarized below with
their own labels.

## Proved

The formal statements compile in Lean 4.32.2 against pinned Mathlib with zero
`sorry` and no added axioms. Full scope is in
[`formal/CLAIM-SCOPE.md`](../../formal/CLAIM-SCOPE.md), with statuses in
[`formal/THEOREM-LEDGER.json`](../../formal/THEOREM-LEDGER.json).

- Under side-consistency, `S_a` is exactly the `a`-asserting roots.
- Lineage may be arbitrarily wrong without moving a verdict when no edge crosses
  sides, no root is created or destroyed, and assertions are unchanged.
- Copies whose parent edge is recorded are free: they add no new root vote.
- A verdict flips only if net per-side root flow reaches the margin; flow equal
  to the margin abstains, while reversal needs margin plus one.
- With assertions fixed, `k` units of root-set change cannot move a verdict of
  margin greater than `k`.
- Conversions preserve margin parity, so conversion alone cannot drive an odd
  margin to abstention.
- Root identity (U1, closed): the independent-root count is a maximum
  independent set over the declared dependence graph, with dependence defined by
  proximate cause and always relative to a class of error. This bounds the count
  relative to that graph; it does not show the graph reflects real lineage, and a
  laundered record that removes edges makes the count over-report. See
  [`CLAIM-SCOPE.md`](../../formal/CLAIM-SCOPE.md).
- Asymmetric claims (AC1–AC5): universal and existential claims need a separate
  verdict rule. The symmetric margin answers a different question and is not a
  decision-sensitivity measure for them.

These are narrow mathematical results under stated assumptions. They are not a
proof of real-world truth recovery.

## Measured

Two world-facing quantities have been measured, without labeling whether the
inferred roots are truly independent observations.

Among 60.8 million journal articles from 2015–2024, 46.2% record no ancestry.
Each therefore becomes an evidence root under the recorded-lineage rule. In the
copy-dominant regime studied here, the resulting over-count floor is `u × N`,
with `u` ranging from 33% in medicine to 74% in arts and humanities. This is a
lower bound under the model, not an estimate of average causal duplication.

For four mathematical conjectures, 57% to 87% of the literature citing each one
before it was resolved descended from other literature citing the same
conjecture, against 0% for unrelated literature from the same eras. The control
arm collapsed to one case, and no predictive, belief, or independence claim is
permitted. See
[`KL-016 v0.2`](../../research/knowledge-ledger/experiments/KL-016/FINDING-v0.2.md).

## Established only in constructed or replay settings

The benchmark, archived replays, and finite Łoś-inspired pilot demonstrate
specific implementation behavior under recorded or injected lineage. In the
frozen synthetic pilot, root-aware and semantic aggregation recovered all
copied-majority worlds under correct declared lineage. All methods failed under
sufficiently corrupted lineage.

See [`experiments/EXPERIMENT-001.md`](../../experiments/EXPERIMENT-001.md) and
[`results/los-inspired-v0.1.md`](../../results/los-inspired-v0.1.md). This is an
implementation check on constructed data, not a literal ultraproduct and not a
general truth-discovery result.

Later constructed results, none canonical:

- **Adversarial weighting** (preregistered and hash-frozen before code). Weighting
  by declared competence halved the adversary fraction needed to break the
  verdict, from 0.40 to 0.20; capping weights did not help; trimming extremes
  held to 0.45 at a cost of about three and a half points with no adversary.
  See [`RESULTS.md`](../../research/adversarial-weighting/RESULTS.md).
- **Capability tournament** (preregistered conformance run). The deterministic
  root vote returned 128 of 128 expected dispositions; the best model scored 116.
  This checks conformance to the method, not truth in the world. See
  [`results`](../../evaluations/multi-model-v1/CAPABILITY-TOURNAMENT-V1-RESULTS.md).
- **Epistemic lift v1.1** (frozen candidate on development worlds). Adding the
  receipt to provenance improved two models by 28.1 and 21.9 points on 32 worlds.
  The worlds were designed alongside the analysis. See
  [`result`](../../evaluations/multi-model-v1/EPISTEMIC-LIFT-V11-RESULT.md).
- **Honest citation** is now recordable as ancestry. A claim that names what it
  read in `read_from` becomes a descendant of that source, so five honest readers
  of one paper count as one root. The field is opt-in and no shipped caller
  supplies it yet.

## Not established

- Whether one recorded evidence root corresponds to one real observation in the
  typical case. The relevant ground truth is absent precisely where ancestry is
  missing. See the
  [`HRI-1 blocker`](../../research/knowledge-ledger/experiments/KL-014/HRI1-BLOCKER-20260816.md).
- Whether missing provenance can be recovered reliably in open real-world
  systems.
- Whether a model can choose the correct causal or decision-relative
  independence cut in deployment. The preregistered DRI-1A run did not support
  even the oracle-supplied version against every fixed cut; it is recorded as an
  adverse, non-canonical result. See
  [`DRI-1A`](../../results/dri1a-v1/README.md).
- Whether any weighted aggregator is safe. Weighted roots are closed by decision
  (`not_pursued`), not solved.
- Whether the development-set model lift survives a hidden, independently
  audited benchmark. That study is designed but not run.
- Whether the current reference runtime is production-ready infrastructure.

Accordingly, `flip_budget` is publishable as a count of root-set units, which is
what it provably is, and not as an operational security budget.

## Not claimed

Minority Prophet does not claim that it discovers truth, that agreement implies
independence, or that the approach has been validated as a general solution
outside synthetic worlds and public bibliographic metadata.
