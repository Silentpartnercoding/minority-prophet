# When weighting matters, and why bounding it does not scale

Exploratory. `probe.py` beside this file reproduces every number; the generator is
uniform and symmetric with independent draws, which is the main thing that could be
driving the answers and is stated rather than buried. Not preregistered, so these are
observations about a synthetic generator and not claims about the world.

The question behind them: `aggregation/zero_weight.py` reconciled what a zero weight
means, but a reconciliation is not an answer to weighting. These ask whether the same
move generalises.

**Weighting only changes the verdict when weights are extreme.** With every weight known
exactly and no zeros anywhere, the weighted verdict and the plain count agree almost
always unless the weights differ by a large factor.

| weight spread | 3 claims | 9 claims | 25 claims |
|---|---|---|---|
| 0.8 to 1.0 | 0.0% | 0.0% | 0.4% |
| 0.4 to 1.0 | 4.0% | 8.7% | 10.2% |
| 0.05 to 1.0 | 17.0% | 19.6% | 21.1% |

Read the top row first. Where the heaviest source is worth about a quarter more than the
lightest, weighting is ceremony: it never changes the answer. It starts to bite only
where one source is worth many times another, and that is exactly the concentration
regime `EXTENSION-SOCKETS.md` section 2 names as the new attack surface. **Weighting
matters precisely where it is most dangerous, and is inert everywhere else.**

**Bounding the uncertainty is honest and gets worse with more evidence.** If weights are
not known exactly, the natural move is the one the corpus already makes for witness
counts in `effective_witness_bounds`: report a range instead of a number, and treat the
answer as determined when both ends agree. Applied to weights, it collapses.

| weight uncertainty | 3 claims | 9 claims | 25 claims | 60 claims |
|---|---|---|---|---|
| plus or minus 0.1 | 83% | 66% | 45% | 24% |
| plus or minus 0.25 | 55% | 27% | 6% | 0.4% |
| plus or minus 0.5 | 24% | 3% | 0% | 0% |

That is backwards. Gathering more evidence should make a verdict more determined, and
here it makes it less. The reason is in the construction: a worst-case bracket assumes
every source's weight error leans the same way at the same time, so the width grows with
the number of sources while an honest margin grows more slowly. Worst cases compound.

The consequence is worth stating plainly. **Any method that treats weights as unknown
within a range becomes useless at scale**, and the only escape is to know something about
how the weight errors relate to one another. That is a new declared quantity, which is
the provenance-of-the-weight problem returning one level down.

**The courtroom alternative was proposed and is refuted.** A jury weights nothing; the
judge controls admissibility. Put all the discrimination at the gate, admit or exclude,
then count equally. It sounds better and it measures worse.

| weight uncertainty | 9 claims, weighted | 9 claims, filter | 60 claims, weighted | 60 claims, filter |
|---|---|---|---|---|
| plus or minus 0.1 | 66% | 49% | 24% | 19% |
| plus or minus 0.25 | 27% | 14% | 0.4% | 0.1% |
| plus or minus 0.5 | 4% | 0% | 0% | 0% |

The filter is more brittle everywhere, and the reason is granularity. A source sitting
near the admission threshold is worth a whole vote or nothing, so being unsure about it
costs a full unit. Under weighting the same wobble costs only the size of the wobble.
Rounding to zero or one maximises the damage of being near the line.

**What this leaves.** Of the six framings put to the owner, the courtroom one is out on
the evidence. The crossover framing is now partly answered: there is a regime where
weighting provably does nothing, and it is wider than expected. The recursion framing is
the live one, because every route out of the bracket collapse needs a claim about how
weight errors correlate, and that claim needs its own provenance.

Nothing here proves anything about a weighted aggregator. `U3` stays underspecified.
