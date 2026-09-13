# U3, weighted roots: what the solutions one level up actually fix

**Status: analysis, not result.** Nothing here is proved and nothing is implemented.
It asks one question -- do the moves that closed U1 and shaped the canon also work when
roots carry weights -- and answers it per move, because the answers differ and the
disagreement is the useful part.

`formal/EXTENSION-SOCKETS.md` section 2 already states the mechanics: Lemma 1, T1 and T2
survive verbatim because they are set equalities proved before any counting; T4, T4' and
T5 generalise from *k errors* to *k weight-units of error*; T6 is lost outright because
parity is an artefact of unit weights. This document is about the doctrine rather than
the algebra.

**First, a defect that is already shipped.** `aggregation/baselines.py::weighted_vote`
weights each vote by `confidence * competence`, both declared numbers, with no
provenance and no de-duplication by root. The independence vocabulary in
`aggregation/independence_axes.py` classifies a declared quantity as `DepthBasis.DECLARED`
and comments it, in the code, as *"free, therefore worthless alone"*. So the shipped
weighted baseline weights by precisely the thing this corpus says carries no weight. It
scores 0.000 on the benchmark, and that is not a coincidence to be explained away; it is
the doctrine being right in a place nobody connected it to.

**What transfers.**

**The backing ladder transfers directly, and it is the single most useful one.** A weight
is worth what its backing is worth, which is the same sentence `DepthBasis` already makes
about depth: `DECLARED`, `PROCEDURAL`, `ARTIFACT`, `DEVICE_ATTESTED`. A confidence a
source types in is free. A stake it has bonded is not. `IDENTITY_STAKE` already maps
`BONDED` to `DEVICE_ATTESTED` for exactly this reason. The move is to refuse a bare
scalar weight and require every weight to arrive with the rung its backing reaches, then
never let a `DECLARED` weight outrank an `ARTIFACT` one however large its number.

**The decomposition primitive transfers, and says weight is not one thing.** Expertise,
money at risk, historical accuracy, recency, calibration and reputation are six different
quantities that usually travel together, which is the exact shape of `age` in
`canon/WHEEL-WORKED-EXAMPLE.md`'s companion anecdote and of `flip` in `GLOSSARY.md`. A
scalar weight is a coat with six people inside it. The decision usually turns on one of
them, and which one is not recoverable after they have been multiplied together.

**Decision sensitivity transfers and makes the whole thing cheaper.** Extension socket 2
already asks for both budgets to be reported, weight-margin and count-margin.
`canon/decision_sensitivity.py` supplies what to do with two surviving numbers: if the
weighted and unweighted verdicts imply the same action, the weighting is not
decision-material and no argument about the weights is required. Only where they diverge
does the weighting have to be defended. That converts an unbounded argument about
correct weights into a bounded one about the cases where weights change what gets done.

**The wheel transfers as the test to run on any weighting scheme.** Ask what observation
would make this scheme report that a weight was wrong. If there is no cell for it, the
scheme cannot return evidence against itself, and every run confirms.

**What does not transfer, and this is the hole.**

**The trout does not transfer, and its failure to transfer is the problem itself.** The
trout works because content is expensive to reproduce and records are cheap to forge, so
when the two disagree you believe the content. A weight has no content. It is a number in
a record and nothing else. There is no idiosyncratic marker inside a `0.83`, no shared
typo, nothing an honest weigher would produce and a dishonest one could not. The one
instrument in this corpus that beats forged paperwork has nothing to grip on here.

The substitute is not detection but cost, which is the backing ladder above. That is a
weaker guarantee and should be described as one: it does not catch a lying weight, it
makes an unearned weight expensive to obtain. Per `ASSAYER.md` A5 detection can only ever
report that no trace was found, so replacing detection with cost is the honest direction
rather than a compromise.

**What gets worse.**

**Maximum independent set becomes maximum-*weight* independent set, and that is a
different adversary.** Under unit weights, collapsing a dependence clique to one member
is indifferent to which member survives; each contributes one. Under weights it is not,
and any sane implementation selects the heaviest, because that is what maximising the sum
means. So an adversary who controls one clique attaches a large weight to a single member
and the counting rule itself elects it. Unit weights were accidentally protecting against
this, and nobody chose that protection.

**The laundering residual stops being bounded by a count.** `U1`'s pinned attack,
`test_ATTACK_laundered_provenance_inflates_the_count`, costs an attacker one unit per
laundered root today. Under weights it yields whatever weight the fake root can claim, so
the residual scales with the weight an attacker can manufacture rather than with the
number of identities. `R3` margin sufficiency absorbs the unit-weight residual; whether it
absorbs a weighted one is not established and must not be assumed.

**Concentration replaces counting as the binding budget.** Socket 2 states it: unweighted,
an attacker corrupts `⌈m/2⌉` roots; weighted, they corrupt the heaviest, which may be one.
Two budgets exist per verdict and the smaller binds. Reporting only the weight budget
hides the count budget and vice versa.

**The shortest honest next step.**

Not the Lean generalisation, though socket 2 is right that it is mechanical. First
reconcile the contradiction socket 2 names, where a zero-weight root is counted at full
strength in one place and at zero in another, because a theorem stated over an
inconsistent definition is worth nothing. Then require weights to carry a `DepthBasis`
rung before any weighted verdict is computed, which costs nothing and immediately
demotes the shipped `confidence * competence` baseline to what it is. Then report both
budgets and let decision sensitivity decide whether the difference matters.

Only after that is the maximum-weight independent set worth formalising, and it should be
stated with the elected-heaviest attack in the same breath, because that attack is
created by the fix rather than found afterwards.
