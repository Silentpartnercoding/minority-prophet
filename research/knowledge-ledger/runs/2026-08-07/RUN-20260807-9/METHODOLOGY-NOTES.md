# Methodology notes — RUN-20260807-9

M1–M28 in force. Two additions.

## M29 — Derivations are artifacts: a rule cites its source with a verbatim quote, or declares itself local

The program's four document layers have each now exhibited the same defect
once — expectation (REG-101), specification (SPEC-108), instruction
(BRF-101), and derivation (BRK-101) — and the repair is the same shape each
time: the connection becomes an artifact checked by machine. For
derivations, the artifact is TRC-101's citation-with-verbatim-quote: the
quote travels with the rule, so drift on either side becomes a diff instead
of a silent divergence. The quote requirement is load-bearing, not
decorative — the enforcement test's byte-check caught two paraphrased
quotes in the very map that introduced it, on first execution. A reference
without a quote would have passed both times.

## M30 — "Owner decision" is a provenance claim and gets audited like one

R1 and R5.2 were recorded, in good faith and with the rejected readings
carefully preserved, as decisions that "could have gone the other way". The
paper had already decided both. Nothing in the decision-recording
discipline was wrong — it is why the correction was easy — but the
characterisation itself was an unverified provenance claim: *this choice
was free* asserts that no upstream document fixes it, and nobody checked.
The audit rule going forward: before recording a decision as free, search
the program's own upstream documents for it; and where the search finds
silence (A1), say the search happened. A free choice that was actually
fixed upstream is the stale-self-description family pointing backward in
time.
