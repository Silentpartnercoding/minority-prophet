# EAA-P5 out-of-tree unified dependence-auditor protocol

`EAA-P5` means phase 5 of the Evidence-Aware Aggregation evaluation program.
The namespace distinguishes this experiment from other records that use the
label `P5`.

This document is the public protocol snapshot imported after completion of an
out-of-tree run. The complete harness was intentionally maintained outside the
Minority Prophet repository to separate the system under evaluation from its
development and confirmation environment. Out-of-tree does not mean that an
independent third party performed the evaluation.

## Question

Can one provider-neutral dependence auditor, composed from Minority Prophet's
public distinctions among source, evidence origin, controller, transformation,
and partial dependence, outperform an earlier root-voting auditor under forged
roots and retain a selective-risk benefit on disjoint non-generated data?

The public Minority Prophet source was pinned at commit
`4776da971b786ba9da9743532e0dcb29b24a5ed3` before the run.

## Separation

Development data selected calibration and abstention behavior. Confirmation
used untouched synthetic seeds and the next 128 eligible, non-overlapping NIST
Juliet base files, producing 256 paired software tasks. Confirmation labels
were not used to tune the candidate.

## Auditor signals

The tested composition reported these signals separately:

1. supported shared controller;
2. supported shared evidence root;
3. supported citation or derivation;
4. mutation or stemma similarity;
5. timing or cascade structure;
6. shared-error evidence;
7. stylometry, when supported; and
8. externally witnessed provenance, when supplied by the data contract.

Supported shared controller or root evidence produced `DEPENDENT`. Supported
direct derivation produced strong dependence evidence. Behavioral evidence
could produce `PARTIALLY_DEPENDENT` or `UNKNOWN`. No tested path inferred
`INDEPENDENT` merely because dependence was not detected.

## Comparators

- `no_collapse`: count every source;
- `hard_collapse`: count each strongly evidenced dependent component once;
- `weighted_collapse`: reduce source mass using pairwise dependence weights;
- `auditor_abstention`: weighted collapse plus a development-selected answer
  threshold; and
- `auditor_v0`: the pinned earlier parent-inference and root-voting method when
  its input contract applied.

## Frozen gate

The unified candidate could pass only if all six conditions held:

1. its synthetic 5% false-answer collapse point exceeded `auditor_v0` by at
   least three forged roots;
2. pre-collapse coverage remained at least 80%;
3. false `INDEPENDENT` classifications remained at most 1%;
4. selective risk on the disjoint software packet improved by at least 10%
   relative to the best matched-coverage comparator;
5. Brier score was no more than 0.01 worse than that comparator; and
6. unknown-controller, unsupported-root, forged-separation, source-order, and
   adaptive shared-controller controls passed.

Failure of any condition rejected the gate and skipped the planned incentive
simulation. A dependence assessment did not establish truth, authority, or
permission to execute an effect.

## Amendments before confirmation

Implementation-only retries repaired import and artifact-preservation defects.
Two committed development amendments expanded an exact-tie threshold and fit
source competence on development data for every comparator. The candidate was
then frozen before the single confirmation run. No confirmation outcome was
used to alter the candidate, gate, comparator, or interpretation.
