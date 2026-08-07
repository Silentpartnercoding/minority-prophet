# Methodology notes — RUN-20260807-4 (final)

Continuing M1–M6 (RUN-1), M7–M12 (RUN-2), M13–M17 (RUN-3), all in force.

## M18 — An artifact's self-description is a claim, not a fact; identity is verified from content

The decisive result artifact of the program arrived carrying its
predecessor's `runId` and `protocolVersion` — ten stale metadata sections
from an updated-in-place workflow (ART-101) — while its content was correct
and internally consistent. The header was wrong exactly where a consumer
would look first and check least. Rule: attribute an imported artifact by
verifying its content against independent expectations (pins, counts,
cross-checks), never by reading its header; and record header/content
disagreements as findings even when the content passes, because the next
artifact's disagreement may run the other way.

## M19 — Enforcement is a property of invariants, not fixtures; every registered decision gets an inversion ablation

The program's two owner decisions are enforced by zero invariants and
survive on two pinned inputs (SPEC-112). The measurement that revealed this
— corrupt one decision, run the full checker, count what notices — costs
minutes and should be part of registering any decision: if the inversion
ablation produces zero invariant violations, the decision is prose, and the
registration should either add the invariant or state plainly that the
decision is fixture-pinned only. R3/I11 did this right by construction; R1
and R5.2 did not, and it took an independent implementer to measure the
difference. A fixture catching a broken rule is a coincidence of inputs; an
invariant catching it is enforcement.

## M20 — A close-out report leads with what is unenforced and undecided, beside the pass, not behind it

This program ends with a genuine cross-implementation reproduction and with
its two decisions unenforced and its largest ambiguity (A2, 19,152 worlds)
undecided. The final record states all three with equal prominence, because
the reader who inherits this work needs the gaps more than the pass: the
pass cannot be un-passed, but the gaps can be silently inherited. "A final
report that records an unenforced decision and an undecided ambiguity is
worth more than one that reads as completion" — the owner's sentence, and
the operating rule for every future close-out.

## M21 — Projected verification values are labelled as projections until executed

Run-1's HANDOFF projected 74 root tests for the cherry-picked branch; the
true value on that base is 63 (TEST-101). The projection was plausible,
specific, wrong, and sat unexecuted in the handoff for three runs. Any
expected value in a handoff either was measured on the exact configuration
it describes, or says "projected, not executed". The same discipline the
program applies to scientific numbers applies to its own operational ones.
