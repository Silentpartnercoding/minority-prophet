# XRP-101 — cross-repository alignment of the shared attack-price quantities

Executed by RUN-20260808-1. Evidence regenerated at write time into
`runs/2026-08-08/RUN-20260808-1/logs/xrp101-evidence.txt`; the counts below are
computed, not transcribed.

## Why this exists

The owner asked whether Gate, Border and the research repository agree. Three
codebases carry the same quantities: this repository's reference aggregator
(`aggregation/root_vote.py`), the knowledge-ledger evaluator
(`knowledge_ledger/transaction.py`), and the Gate product
(`minority_prophet/aggregator.py`). Nothing had ever compared them. The paper is
the only artifact that constrains all three, and no test crossed a repository
boundary.

## The rule this establishes

> **XRP-101.** A quantity named by the paper and implemented in more than one
> repository is not verified by any single repository's test suite. Agreement
> across implementations must be measured on identical inputs and recorded, or
> the shared definition is unowned.

Corollary, learned the hard way below: a published *correction* does not
propagate to the products by being published. Someone has to carry it.

## Method

77 root configurations (supporting 1–11 × opposing 0–11, supporting ≥ opposing),
each evaluated by all three implementations on equivalent inputs, comparing
`flip_budget` / `margin`, `conversions_to_reverse`, and the conversion-parity
flag. Gate at merge commit `70f7d342`.

## Result — the products were behind their own paper

| quantity | research | ledger | Gate, before |
|---|---|---|---|
| `flip_budget` / `margin` | present | present | present |
| `conversions_to_reverse` | present | present | **absent** |
| conversion-parity flag | present | derivable | **absent** |

Paper v1.0.4 §6 R3 requires **both** first quantities "surfaced with every
verdict". Gate surfaced one. `conversions_to_reverse`, `abstention_reachable`,
`CE-03` and `parity` appeared **zero times** in the Gate repository.

The consequence is not presentational. On 5 supporting roots vs 2 opposing,
measured on Gate's own aggregator:

    flip_budget = 3.0   ->  4 forgeries reverse the verdict   (what Gate published)
    conversions_to_reverse = 2   ->  2 compromises reverse it  (what it costs)

Gate's README priced the attack at 4; the cheapest attack costs 2. Border's
`SECURITY.md` opened with "the central threat is root-key compromise" and then
quoted the forgery price — pricing its own stated central threat at ~2×. This
repository had already proved it as **CE-03** and shipped
`conversions_to_reverse`; the correction had been public in paper v1.0.3 and
never reached the products.

**Parity, the sharper half.** Conversions move the margin in steps of two and
preserve its parity, so from an odd margin a tie is unreachable. Verified
against Gate's aggregator:

    start margin 2 (even):  2 -> 0(abstain) -> 2 -> 4 -> 6    abstention reached
    start margin 3 (odd):   3 -> 1 -> 1 -> 3 -> 5             never reaches 0

Abstention is the safe outcome — it escalates to a human. At odd margins the
cheapest compromise attack skips it entirely and lands on a confident wrong
answer. Both products asserted abstention-at-`flip_budget` unconditionally.

**Unit defect, third.** `flip_budget` is root *mass*. Under Gate's documented
migration weight (`unbound_root_weight=0.5`) it returns `1.5`, while the README
called it "the number of forged independent attested roots". Half a forged root
is not a purchase an attacker can make, so the claim was false in exactly the
configuration the migration path recommends.

## After the repair

    configurations compared:                77
    flip_budget    research=ledger=gate:    77/77
    conversions    research=ledger=gate:    77/77
    parity flag    research=gate:           77/77
    mismatches:                             []

Gate now computes the conversion price by re-aggregating the converted input
rather than applying a closed-form margin formula, so it holds under weights,
more than two assertion values, and any `abstain_margin`; its tests pin the two
outputs to this repository's closed form across 54 configurations *without
importing this repository*, so drift in either direction now fails in Gate's CI.

Landed as gate#7 (`70f7d342`) and border#8 (`76579d0f`).

## What was NOT checked

Three further quantities are shared across the same three implementations and
were not compared: `immunity_applicable`, the **T5 floor**, and
`unbound_root_weight`. Their agreement is unmeasured. Recorded as **BL-046**
rather than left as a caveat, because the defect XRP-101 documents is precisely
a shared definition nobody was measuring.

The ledger receipt was deliberately not modified. It already satisfies R3
(`margin` + `conversionsToReverse`) and the parity flag is derivable as
`margin % 2 == 0`; adding a field was shown to change `contentDigest`
(`sha256:dede0197…` → `sha256:aadcb8f6…`), which would invalidate the C11/C12
pins and the cross-implementation conformance result behind them. A derived
boolean is not worth spending that.

## Honest note on how this was found

Not by the run system. RUN-10 had closed; the check ran in an owner conversation
and its result existed only as merged pull requests in two product repositories
until this run recorded it. The finding is real and the repair is landed, but the
program did not surface it — a direct owner question did.
