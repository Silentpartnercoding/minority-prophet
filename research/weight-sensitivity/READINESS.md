# Can we define the moment we are allowed to weight?

Yes, and it splits into two conditions that behave nothing alike. One is a calculation
you can do right now with no data and no truth. The other cannot be calculated at all,
only tested, and it is the one that actually binds.

`readiness.py` reproduces every number. Exploratory, not preregistered.

**Condition one is computable from a tally, and needs no ground truth.** A competence
estimated from `k` scored outcomes has a standard error of at most `sqrt(0.25 / k)`. That
formula contains no truth. It contains a count. Set it equal to the crossover `frames.py`
measured, about fifteen percentage points, and the threshold falls out:

    k >= 0.25 / tolerance^2   ->   k >= 12 scored outcomes

The prediction holds. Below it, weighting is worse than counting; above it, better.

| scored outcomes | predicted error | accuracy | against counting |
|---|---|---|---|
| 1 | 0.500 | 0.7765 | **−0.124** |
| 3 | 0.289 | 0.8638 | **−0.037** |
| 7 | 0.189 | 0.9071 | +0.007 |
| 12 | 0.144 | 0.9257 | +0.025 |
| 60 | 0.065 | 0.9460 | +0.045 |
| 200 | 0.035 | 0.9532 | +0.053 |

So the first half of the answer is unglamorous and exact. Count how many times this
source has been scored against a resolved outcome. Below about twelve, weigh it the same
as everyone else, and know that doing otherwise costs accuracy rather than buying it.

**Condition two cannot be computed, and it is not the one people expect.** A source can
only be scored where truth arrives. Weighting it anywhere else assumes competence
transfers. There are two ways transfer can fail and they are not equally dangerous.

If the *level* collapses -- everyone becomes nearly a coin flip in the new domain, the
expert only slightly less so -- weighting keeps paying almost the whole way down. It only
loses when competence reaches an exact coin flip, at which point nothing works and the
difference is noise.

| competence pulled toward a coin flip by | weighted | counting |
|---|---|---|
| nothing | 0.9475 | 0.9019 |
| half | 0.7700 | 0.7305 |
| ninety percent | 0.5535 | 0.5471 |
| completely | 0.4980 | 0.5059 |

If the *ranking* is scrambled -- the best source in the scored domain is not the best
source here -- weighting breaks quickly, and being wrong half the time is already too
much.

| ranking scrambled | weighted | counting |
|---|---|---|
| never | 0.9482 | 0.9034 |
| a quarter of the time | 0.9173 | 0.9015 |
| **half the time** | **0.8871** | **0.9035** |
| always | 0.8261 | 0.9034 |

**That is the real condition, and it is much weaker than it sounds.** Weighting does not
need competence to carry over. It needs the *order* to carry over. Whether the expert is
still excellent does not matter; whether the expert is still the best one in the room
does. Everything else is a scale factor and weighting is indifferent to scale.

**How to test it, since it cannot be calculated.** Score sources in two different domains
where truth arrives, and compare the two orderings. If they agree, transfer to a third
domain is licensed by evidence rather than by hope. If they disagree, the ordering is
domain-specific and a weight earned in one place must not travel. That is a real
experiment somebody has to run, and it has not been run here.

**The honest limit.** For a proposition class where truth never arrives anywhere, no
source can ever be scored, so no weight can ever be earned, and uniform is not a
placeholder but the permanent and correct answer. That is not a gap in the method. It is
the method saying something true about the class of question.

**So the moment is definable.** Weigh when you have scored this source at least a dozen
times against resolved outcomes, and when the ranking those scores produce has been shown
to hold in a second domain. Until both, count equally, and say plainly that counting
equally is a decision rather than an abstention.
