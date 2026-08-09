# Public claims

## Invariants

1. **Recorded copies add no evidence.** A copy with its parent recorded does not
   change an evidence-root verdict.
2. **Safe rewiring is harmless.** Reassigning same-side parent links does not
   change a verdict when the root set is preserved.
3. **Margin is the safety budget.** A decision survives only while root-set
   change remains below its honest root margin, with assertions fixed.

These statements are proved under their stated assumptions. They do not prove
that a deployment identified its roots correctly.

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

## Open boundaries

- Root identity is operationally assigned, not semantically proved.
- Partial dependence between roots is not represented.
- Separate supported controllers do not prove causally independent evidence:
  matched separate controllers carrying one adverse claim remained separate.
- Expiry, revocation, and key compromise sit outside the counting theorems.
- Synthetic and replay evidence does not establish real-world truth recovery.
- The lineage series does not establish resistance to forged provenance: the
  final PHEME safety diagnostic had only one multi-root case and was underpowered.
- Released-implementation comparisons, matched-coverage analysis, and primary-
  source citation verification remain incomplete.

The detailed status is controlled by [`CANONICAL-RECORDS.md`](CANONICAL-RECORDS.md),
[`EVIDENCE-ALIGNMENT.md`](EVIDENCE-ALIGNMENT.md), and
[`formal/THEOREM-LEDGER.json`](formal/THEOREM-LEDGER.json).
