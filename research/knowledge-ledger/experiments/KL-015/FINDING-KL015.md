# KL-015 — the registered endpoint passed, and its own control refuted it

Both results are recorded. A registered pass that fails a confound check is not a
finding, and reporting the p-value without the control column would have been the
most misleading thing this programme produced.

## The registered result

    events measured 46, discarded 10 (outside reachable history)
    followers after a subject event : median 25
    that token's baseline median    : median 18
    paired difference               : median +19
    sign test  35 positive, 0 negative, p = 0.00000
    predicted direction             : HELD

**ENDPOINT MET.** Every gate the spec required was satisfied: tradeability
verified externally, recency verified before registering, baseline built first,
direction predicted in advance, one test, no sweeping.

## The control that refutes it

Subjects are top holders, so they bought **early — during the launch burst**. The
baseline sampled random windows across a token's whole life, including quiet
stretches. So the comparison measured *when subjects buy*, not *who follows them*.

Measuring the 60 seconds immediately **before** each event, same token, same era:

    60s BEFORE : median 25, mean 24.4
    60s AFTER  : median 25, mean 32.5
    after - before: median +0, sign test p = 0.087

Activity was already elevated before the subject acted. Nobody was reacting to
them. The p = 0.00000 was the difference between *burst periods* and *ordinary
periods*, which is a fact about token lifecycles rather than about influence.

## What was wrong with the registration

Not the sequencing. The baseline was built first, which is what caught KL-014.

**The contrast was wrong.** A random window across a token's life is not the right
comparison for an event that systematically occurs during a burst. The right
comparison is the immediately preceding minute, and that was not in the frozen
spec. Freezing the wrong control still freezes the wrong control.

## The one honest caveat in the other direction

The mean difference is **+8.1 followers** and the sign test on before-versus-after
gives **p = 0.087** — suggestive rather than empty. There may be a small genuine
effect underneath the burst.

Establishing it needs each event matched to its **local** activity level rather
than a global baseline. That is a different registration, not a reinterpretation
of this one.

## The pattern this closes

Six failures, one shape: a comparison whose control could not expose the confound.

    v0.1 population   2 of 1,570 tokens ever tradeable
    exchange result   controls that never reach an exchange
    root-collapse     a control arm left unprofiled
    combined stat     two filters, significance belonging to the other
    KL-014            a baseline that could not reach the events
    KL-015            a baseline sampling the wrong part of the lifecycle

The first four produced numbers before the flaw surfaced. KL-014 was stopped
before any number existed. KL-015 produced a number and then destroyed it with a
control that was not required by its own spec.

That is the progression worth keeping: from finding the flaw after publishing,
to finding it before measuring, to measuring the confound as a matter of routine.
