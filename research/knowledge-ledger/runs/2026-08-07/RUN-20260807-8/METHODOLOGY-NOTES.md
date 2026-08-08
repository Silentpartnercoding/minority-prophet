# Methodology notes — RUN-20260807-8

M1–M26 in force. Two additions.

## M27 — A check that cannot stop the action it guards is decoration: wire exit status, not output

The suite failed and the commit landed anyway, because `pytest | tail`
reports tail's exit status (VER-102). The guard that failed was itself a
good one — the program's own a-seeded-experiment-must-not-look-preregistered
test, rejecting an invented vocabulary — so the incident stacked two
lessons: the *check* layer was right twice (the guard, and NAM-101's
one-vocabulary rule it enforced), and the *wiring* layer defeated both.
Rule: verification gates on its own exit status (`pipefail` when piped, or
unpiped), and a close procedure never reaches `commit` past a nonzero.
Enforcement has a stack; every layer of it can be muzzled by the layer
below.

## M28 — "Unanswered because X" is a field's honest value; null is its absence

The v0.2 migration's core move: a required field a seeded kernel cannot
answer is recorded as `{"status": "unanswered", "reason": …}` with the
reason grounded in what will determine the answer — never null, never an
empty collection. Eleven kernels' documents now carry their own gaps as
information: what each registration must supply is written inside the
document that will receive it, and the conformance test rejects reasonless
gaps the way I12 rejects rule-breaking receipts. The general form: a schema
that permits null permits silent ignorance; a schema that demands a reason
converts every gap into a to-do with provenance. (Bare null survives in
exactly one place — `protocolCommit` — because there the null *is* the
registered design, and even it must carry its note.)
