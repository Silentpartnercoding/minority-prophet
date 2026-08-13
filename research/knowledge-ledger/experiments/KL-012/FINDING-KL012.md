# KL-012 — funding-cluster membership does not reproducibly predict token outcome

Three registered attempts on real Solana data. Three different answers. The
measure is unstable across windows, and the most useful thing produced was a
post-hoc lead that failed to replicate.

## The runs

| | population | prediction | result | verdict |
|---|---|---|---|---|
| **v0.1** | 1,570 mints from 6,000 blocks | — | **2 of 1,570 ever tradeable**, both zero liquidity | abandoned |
| **v0.2** | 1,050 graduated vs 735 not | losers cluster MORE | 27.9% vs 24.2%, p=0.20 | **null** |
| **v0.3** | 34 winners ≥$10M vs 2,015 | winners cluster MORE | 5.9% vs 19.2%, p=0.048 | **failed — reversed** |

## v0.1: the population was noise

Scanning `initializeMint` catches every token creation on Solana, overwhelmingly
spam and tests. An external check found **2 of 1,570 had ever been tradeable, both
with zero liquidity**. Reaching 100 tradeable tokens that way needs ~302,000
blocks — about six days of continuous scanning.

The check cost minutes. It is the second time BL-060 has paid for itself and the
second time the population, not the hypothesis, was the thing that was wrong.

## v0.2: the outcome was wrong, and the owner caught it

`complete` means a bonding curve filled, not that a token succeeded. The **median
graduated token had a market cap of $1,539**. Both arms were overwhelmingly
failures, so the comparison was failures-that-graduated against
failures-that-did-not. A null was the only available answer.

Recorded as a null. Not withdrawn.

## v0.3: the lead did not replicate — it inverted

An exploratory re-analysis of v0.2's data using market cap, at thresholds chosen
**after seeing the distribution**, found the opposite of v0.2's prediction: above
$10M, 50% of winning creators sat in a shared-funding cluster against 21% of the
rest, p=0.010 raw and 0.040 after Bonferroni.

v0.3 registered that reversal in advance — winners cluster MORE — fixed one
threshold, required ≥30 winners, and drew from a window that **cannot overlap**
v0.2's, written into the spec as timestamps.

    v0.2 exploratory   16 winners,  8 clustered, 50.0%, p=0.0100
    v0.3 registered    34 winners,  2 clustered,  5.9%, p=0.0479

**Same measure, same threshold, non-overlapping windows. 50% became 5.9%.**

The lead was noise. The registration caught it, which is precisely what
registering a post-hoc lead on fresh data is for.

## What is claimed

That the v0.3 endpoint failed. Winners cluster *less*, significantly, opposite to
the prediction.

## What is not claimed

**That v0.2's original hypothesis is now supported.** The new direction happens to
agree with it, but v0.2's own registered test was null at p=0.20, and a direction
emerging *after* a failed prediction is the same post-hoc move that produced the
lead this run just destroyed. Adopting it would repeat the error while the
evidence against doing so is on the same page.

**That the v0.3 result is solid.** 2 of 34. One more clustered winner takes p from
0.048 to 0.183 — as thin as the lead it replaced, and presumably as unreliable.

## What is established

**One-hop funding-cluster membership on pump.fun does not carry a reproducible
signal at these sample sizes, in either direction.** Three tests produced null,
strongly positive, and significantly negative. That instability is the result.

Every guard fired correctly: fresh population by construction, direction committed
in advance, a single threshold, a minimum winner count enforced, hubs excluded
failing closed. The infrastructure worked and the answer was still no. That is
what a working experimental setup looks like when the hypothesis is wrong.

## Limitations

**One hop.** v0.2 specified three and implemented one; v0.3 registered one
honestly rather than carrying the mismatch. Operators use intermediate wallets
precisely to defeat depth-1 linkage, so the measure may be blind by construction.

**pump.fun only** — one launchpad, not "memecoins".

**Hub exclusion fails closed**, which pushes every measured effect toward null by
design.

**Market cap at a single observation time**, not peak or return.

## Not tested

A depth-0 measure noticed before any funder was traced and never registered:
graduated tokens averaged **1.22 tokens per creator**, non-graduated **2.05**. It
needs no funding graph, so it is immune to the one-hop limitation, and it looked
larger than anything measured here. It is a hypothesis for a new registration on
a fresh window — not a rescue of this one.
