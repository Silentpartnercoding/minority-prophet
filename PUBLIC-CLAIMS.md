# Public claims

## Invariants

1. **Recorded copies add no evidence.** A copy with its parent recorded does not
   change an evidence-root verdict.
2. **Safe rewiring is harmless.** Reassigning same-side parent links does not
   change a verdict when the root set is preserved.
3. **Margin is the safety budget.** A decision survives only while root-set
   change remains below its honest root margin, with assertions fixed. This
   holds for the symmetric true-or-false question only. Universal and
   existential claims are answered by a separate asymmetric rule, where the
   margin is not a measure of decision sensitivity.

These statements are proved under their stated assumptions. They do not prove
that a deployment identified its roots correctly. `flip_budget` counts root-set
units; it is not an operational security budget.

## Required guarantees

- **R1 — Root integrity:** copies and fabricated identities cannot mint roots.
- **R2 — Side separation:** one root and its descendants cannot span opposing
  sides.
- **R3 — Margin sufficiency:** honest root margin exceeds adversarial capacity.

## Evidence

- Constructed worlds show that declared lineage can recover grounded minority
  truth where head counting fails.
- A preregistered synthetic adversary found failures concentrated at thinner
  margins. This is not evidence of an external exploit.
- In 5,729 resolved weather markets, dependence adjustment did not beat market
  price. It produced fewer false reversals but rarely overruled correctly.
- A sanitized 17-claim field observation found 8 self-attestation abstentions
  and 9 one-root decisions. Six records from one observer still formed one root.
- The reference registry authenticates and bounds root issuance. It limits
  forgery capacity; it does not prove truth or independence.
- A preregistered selective hybrid recovered 1.98% of copied-minority cases in
  its frozen attack model while losing 0.11 percentage points of accuracy and
  remaining below its 1% false-reversal ceiling. This is a synthetic result.
- A preregistered shared-control experiment prevented names, keys, services,
  labels, and self-verification from adding roots when supported controller
  provenance was available. Unknown control always escalated.
- A preregistered evidence-origin experiment prevented supported copies,
  paraphrases, translations, summaries, and model transformations from adding
  roots. Unknown and forged origin claims always escalated.
- A closed lineage-inference series found that text and time alone did not
  recover recorded PHEME reply roots, while retained reply-target author
  identity did. Removing that identity from half of hidden-edge records reduced
  recall from 1.0 to 0.4329 while precision remained 1.0. This is recorded
  platform lineage, not causal evidence independence or truth.

The results below are **not canonical records**. They are listed so that
adverse and null outcomes stay visible alongside the positive ones; none of
them may be cited as validation.

- **Weighting does not survive an adversary** (preregistered, synthetic). Uniform
  root counting first fell below a coin flip at an adversary fraction of 0.40;
  weighting by declared competence broke at 0.20, and at 0.25 under a sleeper
  attack. Capping each source's weight did not move the breakdown point.
  Trimming extremes held to 0.45. This does not establish that any scheme is
  safe.
- **Decision-relative cut selection was not supported** (preregistered,
  synthetic, not canonical). Using the declared failure domain's cut reduced
  false settlement by 0.1307 against two fixed cuts, short of the frozen 0.15
  margin, and a fixed upstream-component cut settled falsely less often than
  the oracle by abstaining far more often.
- **Real citation literature is mostly derived** (descriptive, real data). For
  four mathematical conjectures, 57% to 87% of the literature citing each one
  before its resolution descended from other literature citing the same
  conjecture; unrelated literature from the same eras was 0%. No predictive,
  belief, or independence claim is permitted from this.
- **Model lift is a development result only.** On 32 synthetic development
  worlds, adding the Minority Prophet receipt to provenance improved two models
  by 28.1 and 21.9 points. The worlds were designed alongside the analysis; a
  hidden, independently audited benchmark is required before any public
  empirical claim.
- **A registered endpoint can pass and still be wrong.** A preregistered
  copy-trading test met its endpoint (35 positive, 0 negative) and was then
  refuted by its own before-and-after control (p = 0.087).

## Open boundaries

- Root identity is defined: two sources sharing an ancestor remain independent
  witnesses if each re-established the claim through a channel not running
  through that ancestor, and the count is a maximum independent set over the
  declared dependence graph. Independence is always relative to a class of
  error, never a single score.
- The system does not detect dependence it was not told about. A laundered
  provenance record removes edges, and a sparser graph over-reports the count;
  a report may say "no dependence trace was found", never "these are
  independent".
- Separate supported controllers do not prove causally independent evidence:
  matched separate controllers carrying one adverse claim remained separate.
- Expiry, revocation, and key compromise sit outside the counting theorems.
- Synthetic and replay evidence does not establish real-world truth recovery.
- Weighted aggregation is closed by decision, not solved: no theorem covers any
  weighted aggregator.
- Whether a model or person can choose the correct independence cut in
  deployment is not established.
- The lineage series does not establish resistance to forged provenance: the
  final PHEME safety diagnostic had only one multi-root case and was underpowered.
- Released-implementation comparisons, matched-coverage analysis, and primary-
  source citation verification remain incomplete.

The detailed status is controlled by [`CANONICAL-RECORDS.md`](CANONICAL-RECORDS.md),
[`EVIDENCE-ALIGNMENT.md`](EVIDENCE-ALIGNMENT.md), and
[`formal/THEOREM-LEDGER.json`](formal/THEOREM-LEDGER.json).
