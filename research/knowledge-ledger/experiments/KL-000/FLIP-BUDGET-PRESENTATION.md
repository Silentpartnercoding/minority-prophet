# flip_budget — registered derived presentation value (RUN-20260807-10)

Closes RCP-101 (the traceability map's one receipt-contradicts-paper
finding) **without touching the receipt**: the paper's §6 R3 promises
*"Metrics: `flip_budget` in units of net per-side root change and
`conversions_to_reverse` in side-conversion actions; both are surfaced with
every verdict"* — and no receipt has ever carried `flip_budget`.

## Why not a tenth receipt member

Adding a member changes the hashed bytes of every receipt, breaks the
C11/C12 pins (`sha256:84e63c21…33eafe`, `sha256:61000a9b…aa3b6e`), and
re-opens the cross-implementation byte agreement — the program's hardest-won
result — over a value **derivable from a member already present**. The
receipt object stays the registered nine members; the evaluator stays at its
frozen hash.

## The registered derivation

```
flip_budget = margin          units: net per-side root gain (p0 − p1)
```

Basis (TRC-101 citation): Theorem 4 — *"The attacker's budget equals the
margin in units of net per-side root gain (p₀ − p₁)"*. Since v1.2.0/R5.2
registered `margin` as the absolute distinct-root-count difference (itself
the paper's §3 definition), `flip_budget` is a rename-with-units of an
existing registered member, computed at presentation time by
`knowledge_ledger/presentation.py` — a module the evaluator never imports.

## Constraint CE-03, registered

**`flip_budget` is reported beside `conversionsToReverse`, never instead of
it.** One side-conversion action moves a root off one side and onto the
other — two units of net per-side gain — so a reader who takes
`flip_budget` as an action count overstates the attacker's cost by ~2×.
`conversionsToReverse = ⌊margin/2⌋ + 1` (Theorem 4 [E2]) is the
action-denominated cost. The presentation API exports exactly one function
that surfaces `flip_budget`, and it returns both metrics with unit labels;
no lone-flip_budget variant exists.

## Pass condition and evidence

`tests/test_flip_budget.py`: C11 and C12 reproduce **byte-for-byte** with
this module loaded (digests equal to their registered pins); the evaluator
and package-init hashes are unchanged; the derivation equals `margin` on
every fixture receipt and across an exhaustive sample; the pairing
constraint holds structurally (the API returns both or nothing).
