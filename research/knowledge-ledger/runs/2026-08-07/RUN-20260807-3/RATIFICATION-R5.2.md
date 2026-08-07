# Ratification of R5.2 — margin is the absolute difference

**Post-close addendum to RUN-20260807-3.** After the closing packet was
committed (`252bfb0`), the owner ratified R5.2.

Owner instruction, verbatim (agent-transcribed, same capture caveat as all
prompt text this run):

> Ratify absolute

## What this changes

R5.2 was registered in `preregistration-v1.2.0.json` as an owner-*style*
decision, recommended and adopted by RUN-20260807-3 under the run
instruction's delegation ("Recommend one, record the rejected reading"). It
is now an owner-*ratified* decision. The handoff had flagged the asymmetry
(approval #4): reversal was cheap before IND-20260807-3 and expensive after.
With ratification, the question is closed **before** the commission runs, so
the IND-20260807-3 target is fully owner-endorsed and frozen:

- `margin = |count(supportingRoots) − count(opposingRoots)|`, never negative.
- The rejected signed reading remains preserved with its rationale
  (independent implementation's F5; `PROTOCOL-v1.2.0.md` R5.2).
- C12's pin (`sha256:61000a9b…aa3b6e`) stands as the registered
  cross-implementation test of the ratified rule.

## What this does not change

No registered document is edited (v1.2.0 remains frozen at `7e9e55f` +
Amendment 1); no number, fixture, or digest changes; the commission
instructions in `NEXT-RUN-PROPOSAL-v1.md` are unchanged. This file, a STATUS
note, and the handoff approvals table are the entire footprint.
