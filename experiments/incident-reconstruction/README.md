# Incident reconstruction demo

**Lane: EXPLORATORY.** A prototype and clearly labeled synthetic fixture. Not a
canonical result; no claim here is promoted.

A five-minute demonstration of what Minority Prophet can do **today**, on evidence
we control, without waiting for production systems to emit provenance.

This exists because of the P4 result: on three real corpora the frozen policy
returned zero coverage, correctly, because the required lineage does not exist in
production telemetry. That is honest and it is also undemonstrable to a buyer. A
controlled incident with manufactured ground truth sidesteps the gap without
overstating anything.

## Run it

```
python3 experiments/incident-reconstruction/run_incident_reconstruction.py
```

Two reports are printed from the same incident.

**Full record.** Three supporting reports resolve to one independent evidentiary
root. An independent contradiction was dropped at the aggregator before the
decision. The counterfactual is the finding that matters: had that contradiction
survived, the verdict over independent roots would have been *abstain*, not *true*.

**Degraded record.** Identical incident, lineage removed. The reconstruction
returns INDETERMINATE and names the telemetry it would have needed. It does not
guess. That refusal is the product claim, not a limitation of it.

A self-check runs both against held-out ground truth the reconstructor never sees.

## Boundaries

- `GroundTruth` is never passed to `reconstruct()`. Only `ForensicRecord` is.
- Evidence independence is decided by `aggregation.root_vote.verdict`, the
  function the compiled proofs are about, at its fail-closed default policy.
- Nothing here touches product code. It is additive and can be deleted without
  effect on any canonical record.
- The incident is synthetic. It is a demonstration of method, not evidence about
  any real system or vendor.
