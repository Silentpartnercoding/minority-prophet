# ORIENTATION — RUN-20260807-9

Opened 2026-08-08T00:59:38Z on HEAD `eacc2f6` (RUN-8's close). Clean tree.
Subject: the provenance break between the paper and the specifications.

## The finding, verified first (both facts hold)

1. `papers/minority-prophet-v1.0.3.md` §3 (line 53): *"The
   **evidence-root aggregator** computes S_a(W) = {root(c) : assert(c) = a}
   and returns 1 if |S₁| > |S₀|, 0 if reversed, abstaining on ties
   (optionally below a margin threshold). The **margin** is
   ||S₁| − |S₀||."* Theorem 4 (line 67): *"the verdict is a threshold
   function of the side-count margin"* — and its [E2]: *"reversal costs
   ⌊margin/2⌋+1, not margin+1."*
2. Zero citations: "paper", "aggregator", "abstain" appear nowhere in
   PROTOCOL-v1.1.0/-v1.2.0/-v1.3.0.md or preregistration-v1.1.0/-v1.3.0.json
   (grep, all zero).

## What the paper settles — determined before correcting anything

- **R1 (tie rule): SETTLED.** §3's aggregator abstains on ties and returns
  a side verdict only on strict majority. KL-000's `not_established` on
  ties/minorities is that rule; the independent implementation's existential
  reading contradicts the published aggregator on all 22,440 divergent
  worlds (ties: abstain, not supported; minorities: "0 if reversed", not
  supported). The v1.1.0 characterisation "could defensibly have gone the
  other way" is FALSE as to derivability: the rule was derivable from the
  paper; the specification lost the connection; the owner happened to choose
  what the paper says.
- **R5.2 (margin absolute): SETTLED.** §3 defines margin = ||S₁| − |S₀||,
  explicitly absolute. Same correction: derivable, not open. (Minor paper
  finding: Theorem 4's T5-correction writes "|margin| > k" — bars on an
  already-absolute quantity; a notation redundancy for the owner, not
  repaired here.)
- **F4 (conversionsToReverse): SETTLED for decisive worlds.** Theorem 4
  [E2] publishes ⌊margin/2⌋+1 — the formula the record calls
  "reverse-engineered, defined nowhere". Partially settled only: E2 measured
  4,638/4,638 *decisive* worlds; the margin-0/empty-ledger edge (value 1)
  is outside the theorem's measurement, so the implementer's F4 objection
  stands exactly there.
- **A1: NOT settled by the paper** (§8 requires declared scope and coverage
  for absence; silent on whether supporting evidence is also required). The
  RUN-8 owner-decision characterisation of A1 SURVIVES this audit.
- **A2: bears paper evidence but remains an owner decision.** §3's verdict
  function has no coverage input, and §8 imposes coverage on absence only —
  the registered no-coverage-for-presence reading matches the paper; the
  alternative has no paper basis. Recorded as evidence in the map; NOT
  decided here (A2 stays open per standing instruction).

## Plan

1. Corrections, appended never rewritten: amendment-log entries in
   PROTOCOL-v1.1.0 (R1) and PROTOCOL-v1.2.0 (R5.2, F4), a note in
   PROTOCOL-v1.3.0's log; STATUS and FINAL-RECORD appended. Behaviour
   unchanged everywhere — provenance only. Preregistrations untouched.
2. TRC-101 registered: every normative rule cites the paper or declares
   itself specification-local with a reason.
3. The map: `KL-000/TRACEABILITY-v1.3.0.json`, both directions, with
   verbatim quotes; enforcement in `tests/test_traceability.py`.
4. Packet per `tests/test_closing_packets.py::REQUIRED`, validated before
   the close commit.

## Boundaries

No behaviour change; no paper edit (paper findings are recorded for the
owner); KL-000 stays adversarial-passed at v1.3.0; eleven kernels stay
seeded; 124 tests keep passing; chains keep verifying; nothing pushed.
