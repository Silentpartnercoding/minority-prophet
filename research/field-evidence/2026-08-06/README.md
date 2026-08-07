# Sanitized internal field-evidence reproduction — 2026-08-06

## Status and boundary

This is a **field observation and deterministic reproduction**, not a canonical
experiment and not a new proof. The source run occurred on an internal system.
Raw records are intentionally not published. `claims.generic.json` is a
structural derivative: private labels and payloads were replaced while claim
values, subject-observer relationships, and evidence-root multiplicity were
preserved.

No canonical manifest, theorem, aggregation rule, or prior result is changed.

## Reproduce

From the repository root:

```bash
python3 research/field-evidence/2026-08-06/reproduce.py \
  > /tmp/minority-prophet-field-report.json
diff -u research/field-evidence/2026-08-06/results.json \
  /tmp/minority-prophet-field-report.json
cd research/field-evidence/2026-08-06 && shasum -a 256 -c SHA256SUMS
```

## Findings

Claim labels below distinguish what the artifacts establish.

### F1 — The run exposes root identity as an operational choice

- **Read:** The fixture contains 17 claims.
- **Derived:** Under observer-keyed roots, 8 subject-only observations abstain
  and 9 decided claims have exactly one evidence root.
- **Derived:** Six supporting records for `claim-009` count as one root when
  keyed by observer, but six roots when keyed by event. The resulting margin
  changes from 1 to 6 without changing any claim value.
- **Inferred:** A deployment must define and defend its root-identity rule
  before the theorem's margin can carry operational meaning. This is a field
  instance of the repository's existing U1 limitation, not a resolution of U1.

### F2 — Partial correlation is not representable

- **Read:** The correlation probe has two named observers sharing a transport
  relay and control plane.
- **Derived:** The current binary root model can collapse them to one root or
  treat them as two roots.
- **Inferred:** It cannot express an intermediate independence value. Any
  fractional weighting would require new semantics and proofs; this packet does
  not introduce them.

### F3 — Observer concentration is visible and decision-relevant

- **Read:** One observer supplies 8 of 17 claim groups; another supplies all six
  records in the repeated-record case.
- **Derived:** Repetition does not improve the observer-keyed margin.
- **Inferred:** Claim count is not evidence diversity. Operational reporting
  should expose root concentration alongside verdicts.

### F4 — Attack-cost units must remain separate

- **Derived:** In the six-root event-keyed counterfactual, `flip_budget` is 6
  while `conversions_to_reverse` is 4.
- **Inferred:** Reporting only `flip_budget` would overstate the cheapest
  reversal cost. This reproduces the distinction already documented as CE-03.

## What this evidence does not establish

- It does not prove that observer-keyed or event-keyed identity is universally
  correct.
- It does not prove independence between observers.
- It does not assign a valid fractional weight to shared infrastructure.
- It does not validate the truth of the private source claims.
- It does not promote this packet to canonical experimental evidence.

## Files

- `SOURCE-COMMITMENT.json` — SHA-256 commitments to the unpublished source
  input, source output, and source evaluator. These permit later integrity
  verification without disclosing private content.
- `claims.generic.json` — sanitized structural fixture and correlation probe.
- `reproduce.py` — deterministic evaluator using `aggregation.root_vote`.
- `results.json` — committed output from the evaluator.
- `SHA256SUMS` — integrity hashes for the fixture, runner, and output.
