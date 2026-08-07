# Methodology notes — RUN-20260807-5

M1–M21 in force. Two additions from the gate run.

## M22 — A committed gate survives program closure, and paying it is a reopening, not a continuation

The program closed at RUN-20260807-4 with one committed gate outstanding —
committed precisely so closure could not silently retire it. This run
reopened the program for that gate alone, on owner direction, executed it,
and closed again. The record says all of this explicitly rather than
pretending the program was never closed. The alternative — treating closure
as elastic — would make every "final" record provisional and every committed
gate droppable by ending the program around it. Closure is a state; a gate
is a debt; paying a debt reopens the ledger for exactly the payment.

## M23 — An enforcement change is validated by the union of two predictions: exact catches and exact stillness

I12's registration predicted both what must change (the two ablations caught
at exactly 22,440 and 38,760, previously measured on both sides) and what
must not (every count, conclusion, baseline preserved total, and both pinned
digests). Either half alone is insufficient: exact catches without stillness
could mean the invariant altered evaluation; stillness without exact catches
could mean the invariant is vacuous. The pair, both registered before
execution with a halt-and-report condition in each direction — including
catching *more* than registered — is what makes "enforcement, not semantics"
a tested claim rather than a description. The baseline continuity split
(preserved I1–I11 totals beside reported-only I12 counts) is the same
principle applied to reporting: new information is added next to preserved
metrics, never folded into them.
