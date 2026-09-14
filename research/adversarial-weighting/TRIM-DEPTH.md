# How deep to trim, and whether it is worth it in a room you trust

`RESULTS.md` showed trimming survives an adversary where weighting does not, at one
frozen depth. It did not say how to pick the depth, which is the question anyone
actually has, and it did not price the insurance. Three answers, measured.

Exploratory characterisation of a parameter, not hypothesis testing. `trim_depth.py`
reproduces every number.

**One. If adversaries are present, the best depth is exactly their number.**

| adversary fraction | adversaries present | best depth |
|---|---|---|
| 0.00 | 0 | 0 |
| 0.10 | 2 | 2 |
| 0.20 | 3 | 3 |
| 0.30 | 4 | 4 |
| 0.40 | 6 | 6 |

That is not a new discovery. It is the known result from the robust-aggregation
literature, that discarding the `k` highest and lowest reports is optimal against at
most `k` adversaries, confirming itself in our setting. Adopting it was the right call
and it behaves as advertised.

Useless on its own, of course, because nobody knows how many liars are in the room.

**Two. Not knowing, the rule is roughly one trim per ten percent of suspicion.**

Expected accuracy against `p`, the probability that the room is attacked at all. Each
row picks the depth that maximises it.

| p that the room is attacked | best fixed depth |
|---|---|
| under 0.10 | 0, do not trim |
| about 0.20 | 1 |
| 0.50 and above | 3 |

The break-evens are sharper than the table:

| depth | pays off above |
|---|---|
| 1 | p = 0.10 |
| 2 | p = 0.15 |
| 3 | p = 0.21 |

**Three. Trimming is not more precise, and it is very cheap insurance.**

In a genuinely clean room, trimming is strictly worse. Depth 0 scores 0.9822; depth 3
scores 0.9464. So the answer to "do you even need it in a room you trust" is no, you do
not, and using it costs you real accuracy.

But look at the price of the first cut.

| depth | costs in a clean room | saves at 20% adversarial |
|---|---|---|
| 1 | 0.0074 | +0.0654 |
| 2 | 0.0185 | +0.1089 |
| 3 | 0.0358 | +0.1351 |

**Trimming one voice from each end costs less than a single accuracy point and buys
roughly nine.** That is a ratio you would take in almost any other part of life.

**The practical rule, stated as narrowly as the evidence allows.** Unless you are more
than ninety percent confident the room is clean, trim one from each end. If you think
attack is as likely as not, trim about a fifth of the panel from each end. And if you
are genuinely certain nobody has a reason to lie, do not trim, because then it is pure
loss.

Which puts the difficulty exactly where it belongs. The hard part was never choosing the
depth. It is knowing how sure you are that the room is clean, and that is a judgment
somebody has to own and publish, the same as every other weight in this programme.

Same limits as the parent experiment. Synthetic worlds, conditionally independent honest
sources, one coordinated adversary declaring maximum weight. No theorem. `U3` stays
`underspecified`.
