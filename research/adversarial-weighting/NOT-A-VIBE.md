# The chain does not end in a judgment. It ends in a named impossibility.

`TRIM-DEPTH.md` finished on "how sure are you that the room is clean". That is a
probability somebody has to supply, and a supplied probability is not a derivation. The
objection was correct and this is the repair.

**What was already mathematics, stated plainly so the boundary is visible.** The
breakdown point is a defined quantity from robust statistics, not a coinage. Log-odds
being the optimal weighting of independent binary judges is a theorem. The readiness
threshold is the binomial standard error rearranged. Trim depth equalling the adversary
count is a known optimal result. All of that stands on its own.

**What was not mathematics.** Everything above was *measured* rather than proved: these
are simulations of a stated generator, not theorems about it. And the final step took a
prior as an input. Those are two different weaknesses and only the second is repaired
here.

**The prior is removable, by a classical route.** Two rules choose a depth with no
probability at all.

| adversaries possible up to | minimax picks | guarantees at least | regret rule picks | never behind by |
|---|---|---|---|---|
| 0.10 | trim 2 | 0.9637 | trim 2 | 0.0185 |
| 0.20 | trim 2 | 0.9508 | trim 2 | 0.0261 |
| 0.30 | trim 3 | 0.9425 | trim 3 | 0.0358 |
| 0.40 | trim 5 | 0.8873 | trim 5 | 0.0899 |

Minimax takes the depth whose worst case is best. Minimax regret takes the depth whose
worst shortfall against the ideal choice is smallest. Neither asks how you feel. Both
agree on every row, which is what a well-behaved surface looks like rather than a
finding.

**But this relocates the judgment rather than abolishing it, and saying otherwise would
be a cheat.** You must still declare the range: adversaries are possible up to *what*.
A bound is a smaller and more auditable object than a belief, and declaring one is the
same move `canon/U1-PROXIMATE-ROOTS.md` makes when it borrows proximate cause, which is
a declared cut and says so. But it is still declared.

**One more step and the declaration stops being an opinion.** If an identity costs
something, the bound is arithmetic. An attacker with a budget, facing a per-identity
cost, can field a computable number of sources and no more.

| attacker budget | cost per identity | maximum adversary fraction |
|---|---|---|
| 1000 | 500 | 0.118 |
| 1000 | 200 | 0.250 |
| 1000 | 50 | 0.571 |
| 1000 | **0** | **1.000** |

The last row is the whole thing. At zero cost the bound is everything and no aggregation
rule survives, which is Douceur's Sybil result from 2002. The paper already cites it as
an inherited endpoint and already says the theorems are vacuous without importing cost or
cryptography.

**So the chain closes and it closes on a theorem, not a mood.** The trim depth follows
from the bound; the bound follows from the cost of an identity; and if identities are
free, a named impossibility says stop. The only local input is what an identity costs in
this deployment, which is a fact about the world rather than an opinion about the room.

That is also why the independence vocabulary already grades identity from anonymous to
bonded. It is not describing how much to trust someone. It is pricing how hard they are
to duplicate, which is the quantity the bound actually needs.

Same limits as the parent work. The surface these rules are computed over is measured
from a synthetic generator, so the rules are exact given the surface and the surface is
not a theorem. `U3` stays `underspecified`.
