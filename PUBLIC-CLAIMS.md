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

## Open boundaries

- Root identity is operationally assigned, not semantically proved.
- Partial dependence between roots is not represented.
- Expiry, revocation, and key compromise sit outside the counting theorems.
- Synthetic and replay evidence does not establish real-world truth recovery.
- Released-implementation comparisons, matched-coverage analysis, and primary-
  source citation verification remain incomplete.
- EXP009's selective challenger is preregistered but has no confirmatory result.
- The project makes no claim about cognition or consciousness.

The detailed status is controlled by [`CANONICAL-RECORDS.md`](CANONICAL-RECORDS.md),
[`EVIDENCE-ALIGNMENT.md`](EVIDENCE-ALIGNMENT.md), and
[`formal/THEOREM-LEDGER.json`](formal/THEOREM-LEDGER.json).
