# Result: weighting does not survive an adversary who chooses the weights

Run against `PREREGISTRATION.md`, hash `8671097dd612e27d...`, which the experiment
verifies before it will execute. Fifteen sources, forty thousand trials a cell, seed
1401. Every threshold below was fixed before the run.

## Verdicts against the frozen conditions

| | hypothesis | verdict |
|---|---|---|
| **H1** | weighting lowers the breakdown point | **SUPPORTED** |
| **H2** | capping at `2/n` restores it to within 0.05 | **NOT SUPPORTED** |
| **H3** | trimming beats plain weighting at every `f` from 0.10 to 0.40 | **SUPPORTED** |
| **H4** | the honest crossover tightens under attack | **SUPPORTED**, and more strongly than stated |

**H1 holds under both attacks.** Uniform counting first drops below a coin flip at an
adversary fraction of 0.40. Weighting by declared competence breaks at 0.20, and under
the sleeper attack at 0.25. So handing the adversary the weights **halves the corruption
it needs**.

**H2 fails, and the failure is instructive.** Capping every source at `2/n` of total
weight cost almost nothing when no adversary was present, 0.9932 against 0.9935, which
satisfies half the condition. But it did not move the breakdown point at all: capped
breaks at 0.20 under declaration, exactly where uncapped does. The cap was frozen at
`2/n` before the run and `2/n` is too loose. Three adversaries in fifteen, each capped
at 0.133 of the total, still hold 0.40 of the weight between them. A cap only helps
against **one** heavy source, and the attack that matters is a coordinated block of
merely-heavy ones. This is a real negative result and the threshold is not being moved
after the fact.

**H3 holds everywhere, and trimming beats even uniform counting.** Discarding the
highest and lowest weights and counting the remainder equally scores above plain
weighting at every fraction tested, often enormously: 0.9754 against 0.1375 at `f = 0.20`
under declaration. Its breakdown point is **0.45**, better than uniform counting's 0.40.

The cost is real and worth stating. With no adversary at all, trimming scores 0.9474
against uniform's 0.9829. It throws away good sources along with bad ones, so it buys
robustness with about three and a half points of ordinary accuracy.

**H4 holds so strongly the crossover disappears.** Without an adversary, weighting by an
earned record beats counting while competence estimates stay within about 0.10, which
agrees with the earlier exploratory figure. Under a twenty percent sleeper attack it
**never** beats counting, at any tolerance tested.

| estimate tolerance | honest: earned | honest: count | attacked: earned | attacked: count |
|---|---|---|---|---|
| 0.05 | 0.9911 | 0.9829 | 0.5587 | 0.8420 |
| 0.10 | 0.9857 | 0.9822 | 0.6057 | 0.8428 |
| 0.15 | 0.9783 | 0.9841 | 0.6301 | 0.8421 |
| 0.25 | 0.9516 | 0.9828 | 0.6498 | 0.8424 |

There is no tolerance tight enough to make weighting worth doing here. The condition for
weighting is not "estimate competence well enough". Under attack there is no well enough.

## Three things nobody registered, marked as exploratory

These emerged from the run and were not hypotheses. They are reported as observations and
must not be treated as tested claims.

**A weight that cannot be self-declared is immune to the declaration attack, obviously
and by construction.** Earned weighting never falls below 0.94 under declaration even at
half the sources adversarial, because an adversary who never earned a record carries no
weight no matter what it claims. That is not a discovery, it is the definition, and it is
worth stating only because it locates precisely where the vulnerability lives: in reading
a number the source supplied.

**Under attack, a worse estimate scores better.** Attacked accuracy rises from 0.5587 at
tolerance 0.05 to 0.6498 at 0.25. Noise partially blurs the sleepers' earned advantage,
so precision helps the attacker. Anything that sharpens weights sharpens the attack too.

**The median tracked the capped aggregator exactly.** Both broke at the same fraction in
both attacks. The implementation computes the weighted median over capped weights, so
this is likely an artifact of that choice rather than a finding about medians, and it
should not be read as one.

## What this does and does not establish

It refutes, under these assumptions, the idea that weighting can be made adversarially
safe by estimating competence carefully or by capping any single share. It does not
establish that any scheme is safe. Synthetic worlds, conditionally independent honest
sources, one coordinated adversary, no theorem. `U3` stays `underspecified`.

The practical reading is narrow and firm. Where an adversary may be present, prefer
counting, and prefer trimmed counting if the loss of three and a half accuracy points is
affordable. Weighting is for settings you already believe are honest, and it is precisely
those settings where it buys the least.
