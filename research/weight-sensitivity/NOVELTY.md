# Novelty audit for the weighting work

Stated before it can be misread as discovery, per `canon/PROGRAM.md`. `KNOWN RESULT` is
the expected verdict for most candidates and is not a failure.

**The crossover is a rediscovery, and a well-documented one.** That equal weights often
beat estimated optimal weights is the **forecast combination puzzle**, recognised in the
forecasting literature since the 1980s and reviewed repeatedly since. The accepted
explanation is exactly the one measured here: estimating weights introduces variance that
outweighs the bias it removes, so the simple average wins whenever the true weights are
close to equal or the estimates are noisy.

**Verdict: `KNOWN RESULT`.** Nothing in `frames.py` about the crossover should be
presented as new. What the measurement adds is a number for *this* setting rather than a
finding: roughly fifteen percentage points of competence error, in a nine-source binary
vote with competence uniform in 0.45 to 0.95.

Governing prior art: the forecast combination puzzle and the combination literature
around it; Nitzan and Paroush for log-odds being the optimal weighting of independent
binary judges; Condorcet for the underlying jury structure.

**The readiness threshold is a derivation, not a discovery.** `k >= 0.25 / tolerance^2`
is the standard error of a binomial proportion rearranged. Anyone who wanted it could
write it down. **Verdict: `KNOWN RESULT`.** Its only merit is being tied to a measured
crossover so it produces an operational number rather than a shrug.

**The ranking-versus-level split is the part worth examining.** The finding is that
weighting tolerates competence collapsing almost completely, provided the order of
sources survives, and breaks once the order is scrambled about half the time. The
underlying fact is not surprising once stated -- weighting is a function of relative
magnitude, so a shared scale factor cannot hurt it -- but the framing as the *transfer
condition* for carrying a weight between domains, with a cheap pairwise test attached, is
not something the audit located in the combination literature, which is generally
concerned with one domain at a time.

**Verdict: `UNRESOLVED`, leaning `NOVEL COMBINATION`.** Not claimed as novel. The audit
here was a targeted search, not a systematic review, and the rank-correlation and ordinal
ensemble literatures were not searched properly. That must happen before any claim.

**The adversarial framing is the genuinely different setting, and it is untested.** The
combination literature assumes weights are estimated from data by an honest analyst. Ours
assumes an adversary may choose them, may launder their provenance, and may concentrate
weight on a single source they control. None of the simulations here model an adversary
at all. **Verdict: `UNRESOLVED`.** The interesting question is whether the crossover moves
under attack, and it has not been asked.

**What none of this is.** No theorem. No preregistration. No real data. One synthetic
generator, uniform and independent, which is the most likely thing to be driving the
numbers. Against this repository's own standards -- `ASSAYER.md` A3, the test published
before the sample -- this is exploratory work and must not be cited as evidence for
anything.
