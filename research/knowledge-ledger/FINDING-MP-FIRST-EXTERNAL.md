# MP-EXT-001 — the evaluator collapses manufactured independence in data it did not generate

First time this programme has pointed its own evaluator at a population it did not
construct. It caught the thing it was built to catch.

## The setup

34 Solana tokens that exceeded $10M market cap, and the wallets holding top
positions in them. A wallet appearing as a top holder in several winners looks
like several pieces of evidence that it picks winners.

MP's claim is that this is wrong when the several are not independent. Two tokens
are the **same root** when their creators share a funding ancestor, or when one
creator made both. Evidence is counted per root, not per record.

Receipts produced by `knowledge_ledger/transaction_v2.py`.

## The result

    11 non-custodial wallets holding positions in >=2 winners
    29 tokens claimed as evidence
    24 independent roots
    1.21x inflation

**Three of eleven collapsed below the two-root bar.**

| wallet | tokens | MP roots |
|---|---|---|
| `AGVhmrhD…` | 3 | **1** |
| `AgnaNYcN…` | 2 | **1** |
| `8wM44Ryv…` | 2 | **1** |
| `9ZPsRWGk…` | 6 | 5 |

`AGVhmrhD` looked like a wallet with a three-winner record. All three tokens trace
to one operator. Counted honestly that is one signal about one person's launches,
not three signals about picking winners — and the collapse was computed from
funding lineage the wallet does not control and cannot present differently.

`9ZPsRWGk` survives strongest: 6 tokens, 5 independent roots, flip budget 5. An
adversary would need to forge five independent roots to overturn it.

## What this establishes

**The mechanism works outside a fixture.** Every prior demonstration of
root-collapse ran on worlds this programme generated. This one ran on wallets and
tokens chosen by nobody here, and separated a real multi-source record from one
that only looked like several.

That is the whole thesis of the ledger, tested where it could have failed
silently: nothing would have flagged `AGVhmrhD` as three-for-one. Counting records
gives 3. Counting roots gives 1.

## What this does NOT establish

**That collapsed counts predict anything.** A companion comparison against control
tokens found no difference in root-collapse survival between winner-holders and
control-holders once the custodian confound was removed: 8/11 against 8/9,
p=0.59. The mechanism is sound; it is not a predictor.

**That the eleven are a clean sample.** Their custodian filter was tuned after
seeing exchange profiles. Top-holder status was measured at analysis time, not at
the time each position was taken.

**Anything about the conclusion field.** Every wallet returned `present`, because a
single counterexample root refutes an absence claim. The informative outputs were
`distinctRoots` and `flipBudget`. Posing it as an absence claim was a modelling
choice made here, not a property of the data.

## Why it is worth recording separately

The programme has spent its life proving things about its own constructions. This
is one paragraph of evidence that the central operation survives contact with data
that was not built to be collapsed — and it arrived on a day when five registered
attempts to predict token outcomes all failed.

The prediction attempts failing and the mechanism working are not in tension. The
ledger's claim was always that it can tell manufactured independence from the real
thing, never that independence predicts success.
