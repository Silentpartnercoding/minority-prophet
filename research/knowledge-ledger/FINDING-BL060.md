# BL-060 — a pre-flight trap for populations that cannot exhibit the effect

Built in response to KL-001 v0.3, which measured the failure rather than arguing
it. `scripts/check_effect_reachability.py`, nine tests, and two recorded
declarations that replay the verdict.

## The failure this catches

KL-001 v0.2 did everything the programme's existing controls ask for:

- the protocol was preregistered and commit-pinned before the run
- both arms were byte-identically instrumented — the same scanner, only the
  aggregation differing
- the checker was not vacuous; planted defects made it fail
- the pass condition was executable and rejected corrupted output

And its primary endpoint could not move. The dual ledger reduces false-clean by
exactly one mechanism — returning `not_established` when the scanner found nothing
*and* silently skipped a file — and corpus v1 contained **zero** unreadable files.
The endpoint was pinned to its baseline before any data existed.

Every control listed above interrogates the **instrument**. The instrument was
fine. Nothing looked at the **population**.

## What the check asks

Not "can this population exhibit the effect" — that requires knowing the effect,
which is the thing under study. It asks the author to name the **population
property their own mechanism depends on**, which they must already know in order
to explain why the mechanism works at all, and then counts it.

    mechanism: "returns not_established when the scanner skipped a file"
    property:  "a repository containing a source file the scanner cannot decode"
    frozen-v1: 0        frozen-v2: 22

A probe is an argument array, not a shell string — same reasoning as Epistemic
CI's configuration format: no implicit expansion, no quoting ambiguity. It prints
one integer.

## The trap is trapped

The obvious way to defeat this is a probe that reports a large number for
anything. That is the vacuity that made a MUST-be-0 assertion decoration in
LIN-000, and it would apply here unchanged.

So every declaration must also name a **negative control** population where the
property is absent, and the probe must report *below* the minimum there. A probe
that cannot tell the two apart is rejected as unfalsifiable, and that verdict is
reported *before* any reachability verdict — because if the probe cannot fail,
the reachability result is meaningless in both directions.

Measured: a declaration whose probe is `print(999)` is refused, on a population
that genuinely has the property.

## Silence is a failure, not a skip

A preregistration with no `effectRequires` is refused. "This mechanism depends on
no property of its population" is a strong claim, and an author who means it can
declare it explicitly. Treating an absent declaration as consent is precisely how
v0.2 shipped.

## Retroactive verdicts

Recorded in `experiments/KL-001/reachability/` so they replay. v0.2's frozen
preregistration is **not** modified; the retrospective file is a declaration
v0.2 would have had to make, and is labelled as such.

    DECLARATION-v0.2-retrospective.json   EFFECT UNREACHABLE  (0, needs 1)
    DECLARATION-v0.3.json                 verified            (22, control 0)

The check would have refused the v0.2 run.

## What it does not do

It does not certify that the population is representative, that the minimum is
well chosen, or that the named property is the *only* one the mechanism needs. An
author who names a property the mechanism does not actually depend on will pass
this check and learn nothing. It narrows the failure from "the population was
never examined" to "the population was examined against a property the author
stated" — which is smaller, checkable, and was enough to catch v0.2.

Related: **BL-061** (the endpoint books the rescue and is blind to the three
clean repositories it refused to certify) and **BL-062** (the 95%-preservation
target cannot fail).
