# What is actually established

This is a reader-oriented status guide, not a new source of claim authority.
When wording conflicts, defer to [`PUBLIC-CLAIMS.md`](../../PUBLIC-CLAIMS.md),
[`EVIDENCE-ALIGNMENT.md`](../../EVIDENCE-ALIGNMENT.md),
[`CANONICAL-RECORDS.md`](../../CANONICAL-RECORDS.md), and the formal ledgers.

Current record status: EXP001–EXP002 are canonical derived records;
EXP003R–EXP006R and EXP008R are canonical archived-implementation replays;
EXP007R is canonically incomplete; EXP007A is the canonical synthetic adversary
completion. None establishes real-world provenance recovery.

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

These are narrow mathematical results under stated assumptions. They are not a
proof of real-world truth recovery.

## Measured

One world-facing quantity has been measured at scale, without labeling whether
the inferred roots are truly independent observations.

Among 60.8 million journal articles from 2015–2024, 46.2% record no ancestry.
Each therefore becomes an evidence root under the recorded-lineage rule. In the
copy-dominant regime studied here, the resulting over-count floor is `u × N`,
with `u` ranging from 33% in medicine to 74% in arts and humanities. This is a
lower bound under the model, not an estimate of average causal duplication.

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

## Not established

- Whether one recorded evidence root corresponds to one real observation in the
  typical case. The relevant ground truth is absent precisely where ancestry is
  missing. See the
  [`HRI-1 blocker`](../../research/knowledge-ledger/experiments/KL-014/HRI1-BLOCKER-20260816.md).
- Whether missing provenance can be recovered reliably in open real-world
  systems.
- Whether a model can choose the correct causal or decision-relative
  independence cut in deployment.
- Whether the current reference runtime is production-ready infrastructure.

Accordingly, `flip_budget` is publishable as a count of root-set units, which is
what it provably is, and not as an operational security budget.

## Not claimed

Minority Prophet does not claim that it discovers truth, that agreement implies
independence, or that the approach has been validated as a general solution
outside synthetic worlds and public bibliographic metadata.
